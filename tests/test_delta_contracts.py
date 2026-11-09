import hashlib
import json
import unittest
from sp500_lakehouse.config import LakehouseConfig, identifier
from sp500_lakehouse.delta import event_identity, validate_snapshot_contract, spark_dtype, validate_signal_months


class DeltaContracts(unittest.TestCase):
    def test_projected_gold_cannot_bypass_completed_month_gate(self):
        validate_signal_months(['2026-09'],'2026-09-30T20:00:00Z')
        for months,cutoff in [(['2026-09'],'2026-09-30T19:59:00Z'),(['2026-10'],'2026-10-15T20:00:00Z'),(['2026-9'],'2026-11-01T00:00Z')]:
            with self.assertRaises(ValueError):validate_signal_months(months,cutoff)
        cfg=LakehouseConfig('workspace')
        with self.assertRaises(ValueError):cfg.require_volume_path('exports',cfg.volume('exports')+'/../../other/file.json')
    def test_live_contract_sql_types_and_invalid_casts(self):
        self.assertEqual(spark_dtype('BIGINT'),'long')
        self.assertEqual(spark_dtype('INTEGER'),'int')
        self.assertEqual(spark_dtype('DECIMAL(20,4)'),'decimal(20,4)')
        for bad in ('decimal(80,4)','decimal(2,3)','string);DROP TABLE x','array<string>'):
            with self.assertRaises(ValueError):spark_dtype(bad)
    def test_snapshot_rejects_labels_and_requires_provenance(self):
        manifest = {"feature_version": "v1", "as_of": "2026-10-31T00:00:00Z", "run_id": "run1", "source_hashes": {"baseline": "a" * 64}}
        cols = ["security_id", "signal_month", "momentum"]
        self.assertEqual(validate_snapshot_contract(cols, manifest), validate_snapshot_contract(cols, dict(manifest)))
        with self.assertRaises(ValueError):
            validate_snapshot_contract(cols + ["ret_week_fwd1"], manifest)
        for outcome in ('next_close','actual_return','realized_return','benchmark_price'):
            with self.assertRaises(ValueError):
                validate_snapshot_contract(cols + [outcome], manifest)
        with self.assertRaises(ValueError):
            validate_snapshot_contract(cols, {**manifest, "source_hashes": {"x": "fake"}})
        with self.assertRaises(ValueError):
            validate_snapshot_contract(cols, {**manifest, "run_id": ""})
    def test_identifier_injection_and_path_escape(self):
        for name in ("", "abc.def", "abc;DROP", "../x", "a`b", " space"):
            with self.assertRaises(ValueError):
                identifier(name)
        cfg = LakehouseConfig("research")
        self.assertEqual(identifier('_landing_payload_revision'), '_landing_payload_revision')
        self.assertEqual(cfg.table("silver", "prices"), "research.sp500_silver.prices")
        for path in ("/tmp/x", cfg.volume("landing") + "/../exports/x"):
            with self.assertRaises(ValueError):
                cfg.require_landing_path(path)

    def test_retries_same_event_revisions_different(self):
        original = event_identity("fmp", "prices", "security/date", "old")
        self.assertEqual(original, event_identity("fmp", "prices", "security/date", "old"))
        self.assertNotEqual(original, event_identity("fmp", "prices", "security/date", "revision"))
        canonical = json.dumps(["fmp", "prices", "security/date", "old"], separators=(",", ":"), ensure_ascii=False)
        self.assertEqual(original, hashlib.sha256(canonical.encode()).hexdigest())

    def test_no_layer_or_volume_escape(self):
        cfg = LakehouseConfig("research")
        with self.assertRaises(ValueError):
            cfg.schema("gold;DROP")
        with self.assertRaises(ValueError):
            cfg.volume("../other")


if __name__ == "__main__":
    unittest.main()
