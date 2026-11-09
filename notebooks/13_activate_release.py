# Databricks notebook source
"""Activate a verified immutable release with one compare-and-swap pointer."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from delta.tables import DeltaTable
from pyspark.sql import functions as F
from sp500_lakehouse.config import LakehouseConfig
from sp500_lakehouse.reader import binding_sha256,_table
from sp500_lakehouse.delta import _insert_only
for k,v in [('catalog','workspace'),('prefix','sp500'),('binding_path',''),('validation_path',''),('expected_parent_sha256',''),('rollback','false')]:dbutils.widgets.text(k,v)
get=dbutils.widgets.get;cfg=LakehouseConfig(get('catalog'),get('prefix'))
for path in [get('binding_path'),get('validation_path')]:cfg.require_volume_path('exports',path)
binding=json.loads(Path(get('binding_path')).read_text());validation_bytes=Path(get('validation_path')).read_bytes();validation=json.loads(validation_bytes)
digest=binding_sha256(binding)
rollback=get('rollback')=='true'
if rollback:
    if not get('expected_parent_sha256'):raise ValueError('Rollback requires the current active parent digest')
    registry=cfg.table('ops','dataset_releases')
    if not spark.catalog.tableExists(registry) or spark.table(registry).where(F.col('binding_sha256')==digest).limit(2).count()!=1:raise ValueError('Rollback target must be a previously validated release')
if validation.get('passed') is not True or validation.get('source_binding_sha256')!=digest:raise ValueError('Matching successful release validation required')
quarantine=cfg.table('ops','quarantined_dataset_releases')
if spark.catalog.tableExists(quarantine) and spark.table(quarantine).where(F.col('binding_sha256')==digest).limit(1).count():
    raise ValueError('Release is quarantined; retain as evidence, never reactivate')
counts=[]
for family in ['features','cohort','targets']:
    item=binding[family];table=_table(item['table'])
    properties={r.key:r.value for r in spark.sql('SHOW TBLPROPERTIES '+table).collect()}
    if properties.get('sp500.manifest_sha256')!=binding['manifest_sha256']:raise ValueError('Release table manifest mismatch')
    if family=='features' and get('expected_parent_sha256') and not rollback:
        source_manifest=json.loads(properties.get('sp500.snapshot_manifest','{}'))
        if source_manifest.get('parent_binding_sha256')!=get('expected_parent_sha256'):raise ValueError('Release parent does not match activation parent')
    latest=int(spark.sql('DESCRIBE HISTORY '+table).select('version').first()[0])
    if latest!=item['version']:raise ValueError('Release table changed after validation')
    counts.append(spark.table(table).count())
if len(set(counts))!=1:raise ValueError('Release family counts disagree')
payload=json.dumps(binding,sort_keys=True,separators=(',',':'))
instant=datetime.now(timezone.utc).isoformat()
log=spark.createDataFrame([('sp500',binding['snapshot_id'],digest,payload,get('binding_path'),hashlib.sha256(validation_bytes).hexdigest(),instant)],'dataset_id string, snapshot_id string, binding_sha256 string, binding_json string, binding_path string, validation_sha256 string, activated_at string')
_insert_only(spark,log,cfg.table('ops','dataset_releases'),['dataset_id','snapshot_id'],['binding_sha256','binding_json','validation_sha256'])
pointer=cfg.table('ops','active_dataset')
spark.sql('CREATE TABLE IF NOT EXISTS '+pointer+' (dataset_id STRING, snapshot_id STRING, binding_sha256 STRING, binding_json STRING, binding_path STRING, activated_at STRING) USING DELTA')
existing=spark.table(pointer).where("dataset_id='sp500'").collect()
if len(existing)>1:raise ValueError('Ambiguous active dataset')
if not existing or existing[0]['binding_sha256']!=digest:
    staged=log.select('dataset_id','snapshot_id','binding_sha256','binding_json','binding_path','activated_at').withColumn('expected_parent_sha256',F.lit(get('expected_parent_sha256')))
    values={c:'s.'+c for c in ['dataset_id','snapshot_id','binding_sha256','binding_json','binding_path','activated_at']}
    (DeltaTable.forName(spark,pointer).alias('t').merge(staged.alias('s'),'t.dataset_id=s.dataset_id')
        .whenMatchedUpdate(condition='t.binding_sha256=s.expected_parent_sha256',set=values)
        .whenNotMatchedInsert(condition="s.expected_parent_sha256=''",values=values).execute())
active=spark.table(pointer).where("dataset_id='sp500'").collect()
if len(active)!=1 or active[0]['binding_sha256']!=digest:raise ValueError('Active pointer compare-and-swap failed')
dbutils.notebook.exit(json.dumps(dict(activated=True,source_binding_sha256=digest,rows=counts[0],registry=pointer)))
