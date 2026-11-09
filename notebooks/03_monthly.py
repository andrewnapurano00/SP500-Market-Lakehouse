# Databricks notebook source
import json
import pandas as pd
from sp500_lakehouse.config import LakehouseConfig, identifier
from sp500_lakehouse.delta import publish_gold_snapshot
from sp500_lakehouse.transforms import monthly_cohort, project_features
for name, default in [("catalog", ""), ("prefix", "sp500"), ("membership_entity", "membership"), ("prices_entity", "prices"), ("sessions_entity", "sessions"), ("signal_months_json", "[]"), ("snapshot_id", ""), ("manifest_json", "{}"), ("max_input_rows", "1000000")]:
    dbutils.widgets.text(name, default)
cfg = LakehouseConfig(dbutils.widgets.get("catalog"), dbutils.widgets.get("prefix"))
months = json.loads(dbutils.widgets.get("signal_months_json"))
if not months:
    raise ValueError("A bounded list of signal months is required")
limit = int(dbutils.widgets.get("max_input_rows"))
if not 0 < limit <= 1000000:
    raise ValueError("max_input_rows must be between 1 and 1000000")
def bounded(name):
    frame = spark.table(cfg.table("silver", dbutils.widgets.get(name)))
    if frame.limit(limit + 1).count() > limit:
        raise ValueError("Input exceeds safe pandas vertical-slice bound; stage a bounded input entity")
    return frame.toPandas()
# Slice creates historical monthly cohorts only. It does not claim parity for
# existing stock/fundamental/sector/macro production feature calculations.
spark.conf.set("spark.sql.session.timeZone", "UTC")
sessions = bounded("sessions_entity")
# Spark timestamps have UTC instants; toPandas drops timezone metadata.
sessions["close_at"] = pd.to_datetime(sessions["close_at"], utc=True, errors="raise")
manifest = json.loads(dbutils.widgets.get("manifest_json"))
if not manifest.get('as_of'):
    raise ValueError('Explicit completed-session as_of required')
cohort = monthly_cohort(bounded("membership_entity"), bounded("prices_entity"), sessions, signal_months=months, as_of=manifest['as_of'])
if cohort.empty:
    raise ValueError("No monthly cohort rows")
# Deliberate explicit projection: membership payload can contain legacy outcomes.
features = project_features(cohort, ['adj_close', 'price_missing'])
manifest["scope"] = "monthly_cohort_vertical_slice_only"
manifest["signal_months"] = months
publish_gold_snapshot(spark, cfg, spark.createDataFrame(features), dbutils.widgets.get("snapshot_id"), manifest)
