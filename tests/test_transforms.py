import unittest
from pathlib import Path
import numpy as np
import pandas as pd
from sp500_lakehouse.transforms import monthly_cohort, monthly_targets, exploratory_technicals, asof_records, project_features
from sp500_lakehouse.legacy import stock_technicals


class TransformTests(unittest.TestCase):
    def setUp(self):
        self.sessions = pd.DataFrame({'session_date': pd.to_datetime(['2026-09-30', '2026-10-30', '2026-11-30']), 'close_at': pd.to_datetime(['2026-09-30T20:00Z', '2026-10-30T20:00Z', '2026-11-30T21:00Z'])})
        self.members = pd.DataFrame({'security_id': ['a','b'], 'date': pd.to_datetime(['2026-09-30']*2), 'is_member': [True,True]})
        self.prices = pd.DataFrame({'security_id': ['a','a'], 'date': pd.to_datetime(['2026-09-30','2026-11-30']), 'adj_close': [100.,130.]})

    def test_cohort_preserves_missing_and_exact_next_month(self):
        c = monthly_cohort(self.members, self.prices, self.sessions, ['2026-09'])
        self.assertEqual(len(c),2)
        self.assertTrue(c.loc[c.security_id.eq('b'),'price_missing'].iloc[0])
        labels = monthly_targets(c, self.prices, self.prices.drop(columns='security_id'), self.sessions)
        self.assertTrue(labels.ret_month_fwd1.isna().all())
        self.assertTrue(labels.beats_benchmark.isna().all())

    def test_immature_next_month_does_not_create_short_return(self):
        sessions=self.sessions.iloc[:2].copy()
        sessions.loc[1,'session_date']=pd.Timestamp('2026-10-15')
        sessions.loc[1,'close_at']=pd.Timestamp('2026-10-15T20:00Z')
        p=self.prices.copy();p.loc[1,'date']=pd.Timestamp('2026-10-15')
        c=monthly_cohort(self.members,p,sessions,['2026-09'])
        labels=monthly_targets(c,p,p.drop(columns='security_id'),sessions)
        self.assertTrue(labels.outcome_date.isna().all())
        self.assertTrue(labels.ret_month_fwd1.isna().all())
        self.assertTrue(labels.beats_benchmark.isna().all())

    def test_knowledge_clock_future_and_uncertain(self):
        c = monthly_cohort(self.members, self.prices, self.sessions, ['2026-09'])
        r = pd.DataFrame({'security_id':['a']*3,'period_end':['2026-06-30']*3,'source_revision':['1','2','3'], 'eligible_at':['2026-08-01T00:00Z']*3,'first_seen_at':['2026-08-01T00:00Z','2026-10-01T00:00Z','2026-08-01T00:00Z'],'source_release_at':['2026-08-01T00:00Z']*3,'ingested_at':['2026-08-01T00:00Z']*3,'availability_quality':['observed_vintage','observed_vintage','revision_uncertain'], 'value':[1,100,200]})
        out=asof_records(c,r)
        self.assertEqual(out.loc[out.security_id.eq('a'),'value'].iloc[0],1)
        self.assertTrue(out.loc[out.security_id.eq('b'),'value'].isna().all())

    def test_features_outcome_poisoning(self):
        f=pd.DataFrame({'security_id':['a'],'signal_month':['2026-09'],'momentum':[1.], 'target':[0]})
        before=project_features(f,['momentum'])
        f['target']=999
        pd.testing.assert_frame_equal(before,project_features(f,['momentum']))
        for col in ['target','benchmark_fwd1','actual_return']:
            with self.assertRaises(ValueError):project_features(f,[col])

    def test_bad_dates_timezone_membership_duplicate(self):
        s=self.sessions.copy();s['close_at']=s.close_at.dt.tz_localize(None)
        with self.assertRaises(ValueError):monthly_cohort(self.members,self.prices,s)
        m=self.members.copy();m['is_member']=[1,1]
        with self.assertRaises(ValueError):monthly_cohort(m,self.prices,self.sessions)
        m=self.members.copy();m['date']=m.date+pd.Timedelta(hours=1)
        with self.assertRaises(ValueError):monthly_cohort(m,self.prices,self.sessions)
        with self.assertRaises(ValueError):monthly_cohort(pd.concat([self.members,self.members]),self.prices,self.sessions)

    def test_calendar_cutoff_and_partial_month(self):
        with self.assertRaises(ValueError):
            monthly_cohort(self.members,self.prices,self.sessions,['2026-09'],as_of='2026-09-30T19:59Z')
        with self.assertRaises(ValueError):
            monthly_cohort(self.members,self.prices,self.sessions,['2026-09'],as_of='2026-10-01')
        partial=self.sessions.iloc[:1].copy()
        partial['session_date']=pd.Timestamp('2026-09-15')
        partial['close_at']=pd.Timestamp('2026-09-15T20:00Z')
        with self.assertRaises(ValueError):monthly_cohort(self.members,self.prices,partial,['2026-09'])

    def test_future_rows_do_not_change_earlier_technicals(self):
        dates=pd.bdate_range('2025-01-01',periods=280)
        p=pd.DataFrame({'security_id':['stable']*280,'date':dates,'adj_close':100+np.arange(280,dtype=float),'volume':1000+np.arange(280,dtype=float)})
        workspace=Path(__file__).resolve().parents[1]
        a=stock_technicals(p,workspace)
        p.loc[270:,'adj_close']=10000
        b=stock_technicals(p,workspace)
        pd.testing.assert_frame_equal(a.iloc[:270],b.iloc[:270])
        self.assertEqual(len(a.columns),32)


if __name__ == '__main__':unittest.main()
