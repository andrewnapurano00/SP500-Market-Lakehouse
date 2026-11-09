import json
import tempfile
import unittest
from pathlib import Path
from sp500_ingest.refresh import plan_requests, refresh, windows
from sp500_ingest.fmp_normalize import normalize

class FakeClient:
    calls=0
    value=10
    def fetch_request(self,request):
        self.calls+=1
        return {'historical':[{'date':'2020-01-02','adjClose':self.value,'volume':5}]}, {'from':'2020-01-01'}

class FMPRefreshTests(unittest.TestCase):
    def request(self):
        return dict(entity='prices',ticker='A',security_id='reviewed-1',from_date='2020-01-01',to_date='2020-01-31')
    def test_wrapped_prices_and_identity(self):
        result=normalize({'historical':[{'date':'2020-01-02','adjClose':10}]},self.request(),'run','2026-11-08T00:00:00+00:00')
        self.assertEqual(result[0]['security_id'],'reviewed-1')
        self.assertEqual(result[0]['values']['adjclose'],10)
    def test_no_unadjusted_fallback(self):
        with self.assertRaises(ValueError): normalize([{'date':'2020-01-02','close':10}],self.request(),'r','t')
    def test_run_observations_keep_reversions(self):
        with tempfile.TemporaryDirectory() as root:
            c=FakeClient(); req=self.request()
            a=refresh(c,[req],root,root+'/checkpoints','a')
            refresh(c,[req],root,root+'/checkpoints','a')
            self.assertEqual(c.calls,1)
            c.value=20;refresh(c,[req],root,root+'/checkpoints','b')
            c.value=10;refresh(c,[req],root,root+'/checkpoints','c')
            envelopes=[json.loads(p.read_text()) for p in Path(root,'fmp','prices').glob('dt=*/*.jsonl')]
            self.assertEqual(len({e['data']['observation_id'] for e in envelopes}),3)
            self.assertEqual(len({e['data']['payload_revision'] for e in envelopes}),2)
            self.assertEqual(len(list(Path(root,'fmp','raw_prices').glob('dt=*/*.jsonl'))),3)
    def test_request_plan_routes_and_windows(self):
        plan=plan_requests([{'security_id':'s','api_lookup_ticker':'A'}],'2020-01-01','2026-11-08')
        self.assertEqual(sum(r['entity']=='treasury' for r in plan),83)
        self.assertTrue(any(r['entity']=='cashflow' and r['period']=='annual' for r in plan))
        self.assertTrue(any(r['entity']=='membership_history' for r in plan))
        self.assertEqual(list(windows('2020-02-10','2020-03-02','month')),[('2020-02-10','2020-02-29'),('2020-03-01','2020-03-02')])
    def test_unreviewed_identity_fails(self):
        with self.assertRaises(ValueError):plan_requests([{'security_id':'s'}],'2020-01-01','2020-02-01')
    def test_financial_response_revisions_preserve_vendor_order(self):
        request=dict(self.request(),entity='balance',period='quarter')
        payload=[{'date':'2020-01-02','symbol':'A','period':'Q4','totalAssets':12},{'date':'2020-01-02','symbol':'A','period':'Q3','totalAssets':13}]
        result=normalize(payload,request,'run','2026-11-08T00:00Z')
        self.assertEqual(len(result),2)
        self.assertEqual(result[0]['source_business_key'],result[1]['source_business_key'])
        self.assertNotEqual(result[0]['observation_id'],result[1]['observation_id'])
        self.assertEqual([r['source_ordinal'] for r in result],[0,1])
    def test_missing_financial_history_is_retained_as_empty_evidence(self):
        self.assertEqual(normalize([],dict(self.request(),entity='income'),'r','t'),[])
        with self.assertRaises(ValueError):normalize([],self.request(),'r','t')
