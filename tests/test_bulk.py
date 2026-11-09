import tempfile
import unittest
from pathlib import Path
from decimal import Decimal
import pyarrow as pa
import pyarrow.parquet as pq
from sqlalchemy import types
from sp500_ingest.bulk import arrow_type, atomic_json, sha256_file, export_history


class BulkTests(unittest.TestCase):
    def test_numeric_exact(self):
        self.assertEqual(arrow_type({'type':types.Numeric(28,8)}),(pa.decimal128(28,8),None))
        self.assertEqual(arrow_type({'type':types.Numeric()}),(pa.string(),'exact_numeric_text'))

    def test_nullable_decimal_roundtrip(self):
        with tempfile.TemporaryDirectory() as temporary:
            path=Path(temporary)/'part.parquet'
            table=pa.table({'value':pa.array([Decimal('123456789012345.12345678'),None],type=pa.decimal128(28,8))})
            pq.write_table(table,path,compression='zstd')
            self.assertEqual(pq.read_table(path).to_pylist(),table.to_pylist())
            before=sha256_file(path)
            path.write_bytes(path.read_bytes()+b'changed')
            self.assertNotEqual(before,sha256_file(path))

    def test_existing_output_cannot_mix_snapshots(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(FileExistsError): export_history(None,temporary,{'tables':{}})

    def test_atomic_metadata(self):
        with tempfile.TemporaryDirectory() as temporary:
            path=Path(temporary)/'manifest.json'
            atomic_json(path,{'status':'incomplete'})
            atomic_json(path,{'status':'complete'})
            self.assertIn('complete',path.read_text())
            self.assertFalse(path.with_suffix('.tmp').exists())


if __name__=='__main__': unittest.main()
