import tempfile
import unittest
import pandas as pd
from sp500_lakehouse.snapshots import write_snapshot


class SnapshotTests(unittest.TestCase):
    def test_outcome_gate_does_not_reject_realized_vol(self):
        f=pd.DataFrame({'security_id':['a'],'signal_month':['2026-09'],'realized_vol_21d':[1.]})
        with tempfile.TemporaryDirectory() as root:
            for column in ['target','actual_return','realized_return','benchmark_price','next_close']:
                with self.assertRaises(ValueError):write_snapshot(f.assign(**{column:1}),root,'v1','r','s',{'s':'a'*64})
            self.assertEqual(write_snapshot(f,root,'v1','r','s',{'s':'a'*64},feature_columns=['realized_vol_21d'])['rows'],1)

    def test_immutable_idempotent_and_lineage(self):
        f=pd.DataFrame({'security_id':['a'],'signal_month':['2026-09'],'momentum':[1.]})
        with tempfile.TemporaryDirectory() as root:
            kwargs=dict(root=root,feature_version='v1',run_id='run1',data_snapshot_id='s1',source_hashes={'source':'a'*64})
            a=write_snapshot(f,**kwargs)
            self.assertEqual(a,write_snapshot(f,**kwargs))
            f['momentum']=2
            with self.assertRaises(FileExistsError):write_snapshot(f,**kwargs)
            kwargs['data_snapshot_id']='../bad'
            with self.assertRaises(ValueError):write_snapshot(f,**kwargs)
