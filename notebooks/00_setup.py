# Databricks notebook source
import json
from sp500_lakehouse.config import LakehouseConfig, identifier
from sp500_lakehouse.delta import setup_unity_catalog, ingest_bronze, normalize_silver
for name, default in [("catalog", ""), ("prefix", "sp500"), ("landing_path", ""), ("entity", ""), ("fields_json", "{}"), ("business_keys_json", "[]")]:
    dbutils.widgets.text(name, default)
cfg = LakehouseConfig(dbutils.widgets.get("catalog"), dbutils.widgets.get("prefix"))
setup_unity_catalog(spark, cfg)
