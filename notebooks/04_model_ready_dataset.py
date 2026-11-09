# Databricks notebook source
"""Publish precomputed Silver factor assembly as an immutable Gold candidate."""
import json
import pandas as pd
from pyspark.sql import functions as F
from sp500_lakehouse.config import LakehouseConfig, identifier
from sp500_lakehouse.model_inputs import assemble_model_inputs
from sp500_lakehouse.delta import publish_gold_snapshot
from sp500_lakehouse.reconcile import reconcile_frames

DEFAULTS = {
    "catalog": "", "prefix": "sp500", "population_entity": "model_population",
    "technical_entity": "model_technical", "financial_entity": "model_financial",
    "sector_entity": "model_sector", "macro_entity": "model_macro",
    "signal_date": "", "signal_cutoff_at": "", "as_of": "",
    "feature_columns_json": "[]", "snapshot_id": "", "mode": "retrospective",
    "max_input_rows": "1000000", "feature_version": "precomputed-factor-replay-v1",
    "run_id": "", "reference_entity": "",
}
for name, default in DEFAULTS.items():
    dbutils.widgets.text(name, default)
params = {name: dbutils.widgets.get(name) for name in DEFAULTS}
cfg = LakehouseConfig(params["catalog"], params["prefix"])
identifier(params["snapshot_id"])
signal = pd.Timestamp(params["signal_date"])
if pd.isna(signal) or signal.tzinfo is not None or signal != signal.normalize():
    raise ValueError("Explicit exchange-date signal_date required")
for name in ("signal_cutoff_at", "as_of"):
    stamp = pd.Timestamp(params[name])
    if pd.isna(stamp) or stamp.tzinfo is None:
        raise ValueError(name + " requires an explicit timezone")
features = json.loads(params["feature_columns_json"])
if not isinstance(features, list) or not features or not all(isinstance(v, str) for v in features):
    raise ValueError("Explicit nonempty predictor list required")
if params["mode"] not in {"retrospective", "strict"}:
    raise ValueError("mode must be retrospective or strict")
limit = int(params["max_input_rows"])
if not 0 < limit <= 1000000:
    raise ValueError("max_input_rows must be between 1 and 1000000")
spark.conf.set("spark.sql.session.timeZone", "UTC")


def restore_payload_dates(frame, observation):
    """Restore known UTC clocks only; observation dates retain date semantics."""
    frame = frame.copy()
    clocks = {"source_release_at", "eligible_at", "first_seen_at", "ingested_at"}
    for name in frame:
        if name == observation or name.endswith(("_source_date", "_fiscal_period_end")):
            values = pd.to_datetime(frame[name], errors="raise")
            if values.dt.tz is not None:
                values = values.dt.tz_convert("UTC").dt.tz_localize(None)
            frame[name] = values
        elif name in clocks or name.endswith("_available_at") or name == "feature_cutoff_at":
            # These fields have knowledge-clock semantics in the explicit Silver
            # contract. Missing clocks remain missing; no quality is fabricated.
            frame[name] = pd.to_datetime(frame[name], utc=True, errors="raise")
    return frame


frames = {}
counts = {}
observations = {"population": "week_end", "technical": "date", "financial": "month_end", "sector": "date", "macro": "date"}
for family, observation in observations.items():
    source = spark.table(cfg.table("silver", params[family + "_entity"]))
    payload = [c for c in source.columns if not c.startswith("_landing_")]
    if observation not in payload:
        raise ValueError("Missing observation date in " + family)
    day = F.to_date(F.col(observation))
    if family == "macro":
        source = source.where(day.between(F.lit((signal - pd.Timedelta(days=7)).date()), F.lit(signal.date())))
    else:
        source = source.where(day == F.lit(signal.date()))
    if source.limit(limit + 1).count() > limit:
        raise ValueError("Input exceeds safe pandas bound: " + family)
    # Retain every matching revision. The assembler rejects ambiguous grains;
    # never choose today's latest payload to resolve historical uncertainty.
    frames[family] = restore_payload_dates(source.select(*payload).toPandas(), observation)
    counts[family] = len(frames[family])

actual, evidence = assemble_model_inputs(
    **frames, signal_date=params["signal_date"], feature_columns=features,
    signal_cutoff_at=params["signal_cutoff_at"], as_of_utc=params["as_of"], mode=params["mode"])
comparison = {"performed": False, "passed": None}
if params["reference_entity"]:
    reference = spark.table(cfg.table("gold", params["reference_entity"]))
    if reference.limit(limit + 1).count() > limit:
        raise ValueError("Reference exceeds safe pandas bound")
    expected = reference.select(*actual.columns).toPandas()
    proof = reconcile_frames(expected, actual, ["security_id", "signal_month"])
    comparison = {"performed": True, "passed": bool(proof["passed"]), "rows": len(expected)}
manifest = {
    "run_id": params["run_id"] or "monthly_" + params["snapshot_id"],
    "feature_version": params["feature_version"], "as_of": params["as_of"],
    "signal_date": params["signal_date"], "signal_cutoff_at": params["signal_cutoff_at"],
    "source_hashes": evidence["source_hashes"], "mode": params["mode"],
    "scope": "precomputed_factor_replay_not_historical_vintage_certification",
    "availability_quality": evidence["availability_quality"], "cutover_approved": False,
    "reference_comparison": comparison,
}
table = publish_gold_snapshot(spark, cfg, spark.createDataFrame(actual), params["snapshot_id"], manifest)
coverage = evidence["field_coverage"]
result = {
    "table": table, "rows": len(actual), "predictors": len(features), "mode": params["mode"],
    "input_rows": counts, "comparison": comparison, "cutover_approved": False,
    "availability_quality": evidence["availability_quality"],
    "coverage": {"predictors_with_missing": sum(v["missing"] > 0 for v in coverage.values()),
                 "total_missing_values": sum(v["missing"] for v in coverage.values())},
}
dbutils.notebook.exit(json.dumps(result))
