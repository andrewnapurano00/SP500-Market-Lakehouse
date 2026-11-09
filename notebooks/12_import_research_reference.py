# Databricks notebook source
"""Preserve the old research cohort for exact replay, separate from full Gold."""
import hashlib,json
import pandas as pd
from sp500_lakehouse.spark_frames import pandas_to_spark
from pathlib import Path
from sp500_lakehouse.config import LakehouseConfig
for k,v in [('catalog','workspace'),('prefix','sp500'),('manifest_path','')]:dbutils.widgets.text(k,v)
get=dbutils.widgets.get;cfg=LakehouseConfig(get('catalog'),get('prefix'))
path=get('manifest_path');cfg.require_volume_path('exports',path)
root=Path(path).parent;data=Path(path).read_bytes();manifest=json.loads(data)
digest=hashlib.sha256(data).hexdigest();suffix=manifest['source_sha256'][:12]
for name,expected in manifest['payload_hashes'].items():
    if Path(name).name!=name:raise ValueError('Unsafe reference path')
    if hashlib.sha256((root/name).read_bytes()).hexdigest()!=expected:raise ValueError('Reference content hash mismatch')
result={}
for family,name in [('features','declared_features.parquet'),('targets','targets.parquet'),('model_input','original_model_input.parquet')]:
    frame=pandas_to_spark(spark,cfg,pd.read_parquet(root/name));table=cfg.table('gold','reference_'+family+'_'+suffix)
    if frame.count()!=manifest['rows']:raise ValueError('Reference row count mismatch')
    if spark.catalog.tableExists(table):
        props={r.key:r.value for r in spark.sql('SHOW TBLPROPERTIES '+table).collect()}
        if props.get('sp500.reference_manifest_sha256')!=digest:raise ValueError('Reference manifest conflict')
        existing=spark.table(table)
        if existing.select(*frame.columns).exceptAll(frame).limit(1).count() or frame.exceptAll(existing.select(*frame.columns)).limit(1).count():raise ValueError('Reference content conflict')
    else:frame.writeTo(table).using('delta').tableProperty('delta.appendOnly','true').tableProperty('sp500.reference_manifest_sha256',digest).tableProperty('sp500.scope','legacy_outcome_conditioned_replay_only').create()
    result[family]=dict(table=table,version=int(spark.sql('DESCRIBE HISTORY '+table).select('version').first()[0]))
dbutils.notebook.exit(json.dumps(dict(tables=result,rows=manifest['rows'],source_sha256=manifest['source_sha256'],scope=manifest['scope'])))
