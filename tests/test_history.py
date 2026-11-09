import unittest
import pandas as pd
from sp500_lakehouse.history import assemble_history, historical_targets


class HistoryTests(unittest.TestCase):
    def loader(self,family,day):
        if family=='population': return pd.DataFrame(dict(security_id=['a','b'],ticker_latest=['AAA','BBB'],sector=['Energy']*2,week_end=[day]*2,ret_week_fwd1=[999,None]))
        if family=='technical': return pd.DataFrame(dict(ticker_latest=['AAA'],date=[day],momentum=[.2]))
        if family=='financial': return pd.DataFrame(columns=['security_id','month_end'])
        if family=='sector': return pd.DataFrame(dict(sector=['Energy'],date=[day]))
        return pd.DataFrame(dict(date=[day]))

    def test_all_months_keep_unpriced_members_and_future_does_not_change_past(self):
        kwargs=dict(feature_columns=['momentum'],as_of_utc='2026-11-08T00:00Z')
        first,cohort,proof=assemble_history(self.loader,['2026-08-31'],**kwargs)
        both,_,_=assemble_history(self.loader,['2026-08-31','2026-09-30'],**kwargs)
        pd.testing.assert_frame_equal(first,both.iloc[:2].reset_index(drop=True))
        self.assertEqual(len(first),2)
        self.assertTrue(pd.isna(first.iloc[1].momentum))
        self.assertEqual(proof['months'],1)
        self.assertEqual(cohort.ticker.tolist(),['AAA','BBB'])
        with self.assertRaises(ValueError): assemble_history(self.loader,['2026-08-28'],**kwargs)

    def test_targets_exact_month_unknown_preserved_and_deterministic_ties(self):
        cohort=pd.DataFrame(dict(security_id=['b','a'],ticker=['BBB','AAA'],signal_month=['2026-08']*2,signal_date=pd.to_datetime(['2026-08-31']*2)))
        prices=pd.DataFrame(dict(security_id=['a','a','b','b'],date=['2026-08-31','2026-10-30','2026-08-31','2026-09-30'],adj_close=[100,110,100,120]))
        bench=pd.DataFrame(dict(date=['2026-08-31','2026-09-30'],adj_close=[100,105]))
        target=historical_targets(cohort,prices,bench,as_of_utc='2026-11-08T00:00Z').set_index('security_id')
        self.assertTrue(pd.isna(target.loc['a','next_month_return']))
        self.assertTrue(pd.isna(target.loc['a','target_top20']))
        self.assertAlmostEqual(target.loc['b','next_month_return'],.2)
        self.assertEqual(target.loc['b','target_top20'],1)
        self.assertEqual(target.loc['b','target_beat_voo'],1)
        immature=historical_targets(cohort,prices,bench,as_of_utc='2026-09-15T00:00Z')
        self.assertTrue(immature.next_month_return.isna().all())
        self.assertTrue(immature.target_beat_voo.isna().all())


if __name__=='__main__': unittest.main()
