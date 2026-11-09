# Databricks notebook source
import json
from sp500_lakehouse.config import LakehouseConfig, identifier
from sp500_lakehouse.delta import setup_unity_catalog, ingest_bronze, normalize_silver
for name, default in [("catalog", ""), ("prefix", "sp500"), ("landing_path", ""), ("entity", ""), ("fields_json", "{}"), ("business_keys_json", "[]")]:
    dbutils.widgets.text(name, default)
cfg = LakehouseConfig(dbutils.widgets.get("catalog"), dbutils.widgets.get("prefix"))
# Supply a bounded source/security/date partition path. No source API calls here.
entity = identifier(dbutils.widgets.get("entity"))
fields = json.loads(dbutils.widgets.get("fields_json"))
keys = json.loads(dbutils.widgets.get("business_keys_json"))
if not fields or not keys:
    raise ValueError("Explicit typed mapping and business keys required before ingestion")
ingest_bronze(spark, cfg, dbutils.widgets.get("landing_path"), entity)
normalize_silver(spark, cfg, entity, fields, keys)
