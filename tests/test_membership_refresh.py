import unittest
import pandas as pd
from sp500_lakehouse.membership_refresh import reconcile_month

class MembershipTests(unittest.TestCase):
    def test_rewinds_post_signal_changes_and_preserves_reviewed_identity(self):
        routes=pd.DataFrame(dict(security_id=['a','b'],api_lookup_ticker=['AAA','BBB'],ticker_latest=['AAA','BBB'],sector=['Energy','Energy']))
        events=pd.DataFrame([dict(entity='membership_current',run_id='r',values={'symbol':'BBB','sector':'Energy'}),
            dict(entity='membership_history',run_id='r',values={'date':'2026-11-02','symbol':'BBB','removedticker':'AAA'})])
        monthly=pd.DataFrame(columns=['week_end','security_id','ticker_latest'])
        result=reconcile_month(monthly,routes,events,run_id='r',signal_date='2026-10-30')
        self.assertEqual(result.security_id.tolist(),['a'])
        with self.assertRaises(ValueError):reconcile_month(monthly,routes.iloc[1:],events,run_id='r',signal_date='2026-10-30')

    def test_existing_cohort_disagreement_and_ambiguous_route_fail(self):
        routes=pd.DataFrame(dict(security_id=['a','b'],api_lookup_ticker=['AAA','AAA'],ticker_latest=['AAA','AAA'],sector=['Energy','Energy']))
        events=pd.DataFrame([dict(entity='membership_current',run_id='r',values={'symbol':'AAA','sector':'Energy'}),dict(entity='membership_history',run_id='r',values={'date':'2020-01-01','symbol':'AAA'})])
        monthly=pd.DataFrame(columns=['week_end','security_id','ticker_latest'])
        with self.assertRaises(ValueError):reconcile_month(monthly,routes,events,run_id='r',signal_date='2026-10-30')

if __name__=='__main__':unittest.main()
