import unittest
import pandas as pd
import numpy as np
from sp500_lakehouse.releases import preserve_known_targets

class TargetBasisTests(unittest.TestCase):
 def test_known_return_basis_survives_vendor_revision_and_unknown_can_mature(self):
  keys=dict(security_id=['a','b'],signal_month=['2026-01']*2)
  targets=pd.DataFrame(dict(**keys,next_month_return=[.9,.2],benchmark_return=[.8,.8],target_top20=[1.,0.],target_beat_voo=[1.,0.]))
  anchor=targets.copy();anchor['next_month_return']=[.1,np.nan];anchor['benchmark_return']=.05
  cohort=pd.DataFrame(dict(**keys,ticker=['AAA','BBB']))
  result=preserve_known_targets(targets,anchor,cohort).set_index('security_id')
  self.assertEqual(result.loc['a','next_month_return'],.1);self.assertEqual(result.loc['b','next_month_return'],.2)
  self.assertTrue(result.benchmark_return.eq(.05).all());self.assertEqual(result.loc['b','target_top20'],1.)
  self.assertEqual(targets.loc[0,'next_month_return'],.9)
 def test_benchmark_anchor_applies_to_new_members_in_same_month(self):
  targets=pd.DataFrame(dict(security_id=['a','b'],signal_month=['2026-01']*2,next_month_return=[.1,.2],benchmark_return=[.8,.8]))
  anchor=targets.iloc[:1].copy();anchor['benchmark_return']=.05
  cohort=targets[['security_id','signal_month']].assign(ticker=['AAA','BBB'])
  result=preserve_known_targets(targets,anchor,cohort)
  self.assertTrue(result.benchmark_return.eq(.05).all())
 def test_unknown_remains_null_and_duplicate_keys_fail(self):
  targets=pd.DataFrame(dict(security_id=['a'],signal_month=['2026-01'],next_month_return=[np.nan],benchmark_return=[.05],target_top20=[np.nan],target_beat_voo=[np.nan]))
  cohort=targets[['security_id','signal_month']].assign(ticker='AAA')
  result=preserve_known_targets(targets,targets,cohort);self.assertTrue(result.next_month_return.isna().all());self.assertTrue(result.target_top20.isna().all())
  with self.assertRaises(ValueError):preserve_known_targets(pd.concat([targets,targets]),targets,cohort)
if __name__=='__main__':unittest.main()
