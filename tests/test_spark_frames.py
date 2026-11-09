import unittest
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from sp500_lakehouse.spark_frames import parquet_bytes

class SparkFrameTransportTests(unittest.TestCase):
    def test_utc_microseconds_and_null_text_are_lossless_and_spark_compatible(self):
        stamp=pd.Timestamp('2026-11-08T12:30:45.123456Z')
        frame=pd.DataFrame(dict(observed_at=pd.to_datetime([stamp],utc=True),missing_metadata=[None],value=[None]))
        table=pq.read_table(pa.BufferReader(parquet_bytes(frame)))
        self.assertEqual(table.schema.field('observed_at').type,pa.timestamp('us',tz='UTC'))
        self.assertEqual(table.schema.field('missing_metadata').type,pa.string())
        self.assertEqual(table.column('observed_at')[0].as_py(),stamp.to_pydatetime())
    def test_submicrosecond_source_time_is_rejected_not_truncated(self):
        frame=pd.DataFrame(dict(observed_at=[pd.Timestamp('2026-11-08T12:30:45.123456789Z')]))
        with self.assertRaises(pa.ArrowInvalid):parquet_bytes(frame)

if __name__=='__main__':unittest.main()
