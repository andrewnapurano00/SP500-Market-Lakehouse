import tempfile
import unittest
from pathlib import Path
import pandas as pd
from sp500_lakehouse.reader import GoldReader
from sp500_lakehouse.consumer import export_consumer_panel, read_consumer_export, frozen_score_transport_parity


class ReaderTests(unittest.TestCase):
    def setUp(self):
        self.binding=dict(snapshot_id='x',manifest_sha256='a'*64,feature_columns=['momentum'],
            features=dict(table='workspace.sp500_gold.features',version=3),
            cohort=dict(table='workspace.sp500_gold.cohort',version=4))
        self.features=pd.DataFrame(dict(security_id=['a','b'],signal_month=['2026-09']*2,momentum=[.2,None]))
        self.cohort=pd.DataFrame(dict(security_id=['a','b'],signal_month=['2026-09']*2,
            signal_date=['2026-09-30']*2,ticker=['AAA','BBB'],sector=['Energy']*2))
        self.sql=[]

    def query(self,sql):
        self.sql.append(sql)
        return self.cohort.copy() if '.cohort ' in sql else self.features.copy()

    def test_version_pinned_outcome_free_full_cohort(self):
        reader=GoldReader(self.query,self.binding)
        frame=reader.read(['2026-09'])
        self.assertEqual(len(frame),2)
        self.assertIn('VERSION AS OF 3',self.sql[0])
        self.assertIn("'2026-09'",self.sql[0])
        self.assertNotIn('next_month_return',frame)
        self.assertEqual(frame.attrs['source_binding_sha256'],reader.sha256)
        with self.assertRaises(ValueError): reader.read(["2026-09' OR 1=1"])
        self.cohort=self.cohort.iloc[:1]
        with self.assertRaises(ValueError): reader.read()

    def test_reject_outcome_manifest_or_unpinned_version(self):
        self.binding['feature_columns']=['target_top20']
        with self.assertRaises(ValueError): GoldReader(self.query,self.binding)
        self.binding['feature_columns']=['momentum'];self.binding['features']['version']='latest'
        with self.assertRaises(ValueError): GoldReader(self.query,self.binding)

    def test_export_hash_and_frozen_transport(self):
        reader=GoldReader(self.query,self.binding)
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)/'history.parquet'
            export_consumer_panel(reader,path)
            frame=read_consumer_export(path,expected_binding_sha256=reader.sha256)
            self.assertEqual(len(frame),2)
            proof=frozen_score_transport_parity(frame,frame.copy(),['momentum'],lambda f:f.momentum.fillna(0).to_numpy())
            self.assertTrue(proof['passed'])
            path.write_bytes(b'corrupt')
            with self.assertRaises(ValueError):read_consumer_export(path,expected_binding_sha256=reader.sha256)


if __name__=='__main__':unittest.main()
