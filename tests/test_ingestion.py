import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'ingestion/src'))
from sp500_ingest.landing import write_records, Checkpoints, digest
from sp500_ingest.fmp import HTTPClient, FMPClient
from sp500_ingest.membership import normalize_membership
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'lakehouse/src'))
from sp500_lakehouse.delta import event_identity


class IngestionTests(unittest.TestCase):
    def test_composite_keys_match_delta_and_utc_paths(self):
        with tempfile.TemporaryDirectory() as folder:
            path=write_records(folder,'postgres','prices',[{'security_id':'S1','date':'2026-10-30'}],
                               source_kind='postgres_reconstruction',retrieved_at='2026-10-31T23:30:00-04:00',
                               source_record_key=lambda row: [row['security_id'],row['date']])
            meta=json.loads(path.read_text())['meta']
            self.assertIsInstance(meta['source_record_key'],str)
            self.assertEqual(meta['source_record_key'],'["S1","2026-10-30"]')
            self.assertEqual(meta['event_id'],event_identity(meta['source'],meta['entity'],meta['source_record_key'],meta['payload_hash']))
            self.assertEqual(meta['dt'],'2026-11-01')
            self.assertTrue(meta['retrieved_at'].endswith('+00:00'))
            fallback=write_records(folder,'postgres','other',[{'a':1}])
            self.assertEqual(json.loads(fallback.read_text())['meta']['source_key_strategy'],'payload_hash_business_key_unresolved')
            for timestamp in ('2026-10-30', '2026-10-30T12:00:00', '../../bad'):
                with self.assertRaises(ValueError):
                    write_records(folder,'postgres','x',[],retrieved_at=timestamp)
            with self.assertRaises(ValueError):
                write_records(folder,'postgres','x',[],source_kind='unmarked')

    def test_immutable_revisions_and_verified_resume(self):
        with tempfile.TemporaryDirectory() as folder:
            payload={'date':'2026-10-30','value':None,'nested':{'raw':'unchanged'}}
            a=write_records(folder,'fmp','prices',[payload],run_id='first',request_parameters={'apikey':'secret','nested':{'token':'hidden','symbol':'A'}})
            b=write_records(folder,'fmp','prices',[payload],run_id='second')
            first=json.loads(a.read_text())
            self.assertEqual(first['data'],payload)
            self.assertEqual(first['meta']['payload_hash'],digest(payload))
            self.assertEqual(first['meta']['event_id'],json.loads(b.read_text())['meta']['event_id'])
            self.assertNotIn('secret',a.read_text())
            self.assertNotIn('hidden',a.read_text())
            with self.assertRaises(FileExistsError):
                write_records(folder,'fmp','prices',[payload],run_id='first')
            cp=Checkpoints(Path(folder)/'checkpoints')
            cp.commit({'job':1},a)
            self.assertEqual(cp.completed({'job':1}),a.resolve())
            a.write_text('corrupt')
            with self.assertRaises(ValueError):
                cp.completed({'job':1})

    def test_failed_http_budget_and_secrets(self):
        session=Mock()
        session.get.return_value.status_code=429
        client=HTTPClient(session=session,max_requests=1,attempts=4,interval=0)
        with patch('sp500_ingest.fmp.time.sleep'):
            with self.assertRaisesRegex(RuntimeError,'budget'):
                client.get_json('https://example.test',{'apikey':'secret'})
        self.assertEqual(session.get.call_count,1)

    def test_fmp_preserves_wrappers_and_validates_ranges(self):
        http=Mock()
        payload={'symbol':'A','historical':[{'date':'2026-10-30','adjClose':None}]}
        http.get_json.return_value=payload
        client=FMPClient('secret',http)
        actual,params=client.fetch('prices','A','2026-10-01','2026-10-31')
        self.assertIs(actual,payload)
        self.assertEqual(params,{'from':'2026-10-01','to':'2026-10-31'})
        with self.assertRaises(ValueError):
            client.fetch('market_cap','A','2010-01-01','2026-10-31')

    def test_membership_never_invents_identity(self):
        with self.assertRaises(ValueError):
            normalize_membership([{'ticker':'A','date':'2026-10-30'}])
        row={'security_id':'reviewed-1','ticker':'A','date':'2026-10-30'}
        self.assertEqual(normalize_membership([row]),[row])
        with self.assertRaises(ValueError):
            normalize_membership([row,row])

if __name__=='__main__':
    unittest.main()
