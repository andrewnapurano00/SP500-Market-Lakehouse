import unittest
import numpy as np
import pandas as pd
from sp500_lakehouse.reconcile import reconcile_frames


class ReconcileTests(unittest.TestCase):
    def test_strict_cohort_null_and_tolerance(self):
        a=pd.DataFrame({'security_id':['a','b'],'signal_month':['2026-09']*2,'factor':[1.,np.nan]})
        self.assertTrue(reconcile_frames(a,a.iloc[::-1],['security_id','signal_month'])['passed'])
        b=a.copy();b.loc[0,'factor']+=1e-11
        self.assertTrue(reconcile_frames(a,b,['security_id','signal_month'])['passed'])
        for b in [a.iloc[:1],a.fillna(0),a.assign(factor=[2.,np.nan])]:
            with self.assertRaises(AssertionError):reconcile_frames(a,b,['security_id','signal_month'])
        with self.assertRaises(ValueError):reconcile_frames(a,pd.concat([a,a]),['security_id','signal_month'])
