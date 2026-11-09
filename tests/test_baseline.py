import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'ingestion/src'))
from sp500_ingest.baseline import identifier, where_clause, validate_business_key


class BaselineTests(unittest.TestCase):
    def test_override_requires_observed_unique_nonnull_columns(self):
        columns=['security_id','week_end']
        validate_business_key(columns,columns,dict(security_id=0,week_end=0),0)
        for key in ([],['invented'],['security_id','security_id']):
            with self.assertRaises(ValueError):
                validate_business_key(key,columns)
        with self.assertRaises(ValueError):
            validate_business_key(columns,columns,dict(security_id=1,week_end=0),0)
        with self.assertRaises(ValueError):
            validate_business_key(columns,columns,dict(security_id=0,week_end=0),1)

    def test_filters_are_parameterized_and_catalog_checked(self):
        where,params=where_clause(['date'],'date','2026-01-01','2026-01-31')
        self.assertNotIn('2026',where)
        self.assertEqual(params['end'],'2026-01-31')
        with self.assertRaises(ValueError):
            where_clause(['date'],'date; DROP TABLE x','2026-01-01','2026-01-31')
        with self.assertRaises(ValueError):
            where_clause(['date'],'date','2026-01-01',None)
        self.assertEqual(identifier('a"b'),'"a""b"')

if __name__=='__main__':
    unittest.main()
