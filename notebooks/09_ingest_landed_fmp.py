# Databricks notebook source
"""Verify a local collector commit, then ingest its normalized observations."""
import hashlib,json
from pathlib import Path
from sp500_lakehouse.config import LakehouseConfig
from sp500_lakehouse.delta import ingest_bronze,normalize_silver
from sp500_lakehouse.delta import _insert_only
for name,default in [('catalog','workspace'),('prefix','sp500'),('collector_manifest','')]:dbutils.widgets.text(name,default)
get=dbutils.widgets.get
cfg=LakehouseConfig(get('catalog'),get('prefix'))
path=get('collector_manifest');cfg.require_landing_path(path)
manifest=json.loads(Path(path).read_text())
if manifest.get('provider')!='fmp_local_to_databricks':raise ValueError('Unexpected collector')
entities=set()
for item in manifest['files']:
    cfg.require_landing_path(item['path'])
    if hashlib.sha256(Path(item['path']).read_bytes()).hexdigest()!=item['sha256']:raise ValueError('Collector checksum mismatch')
    entity=item['path'].split('/fmp/',1)[1].split('/',1)[0]
    entities.add(entity)
fields={'entity':'string','security_id':'string','api_lookup_ticker':'string','observation_date':'date','source_business_key':'string','observation_id':'string','payload_revision':'string','retrieved_at':'timestamp','run_id':'string','availability_quality':'string','statement_period':'string','values':'string'}
fields['source_ordinal']='long'
for entity in sorted(entities):
    # Only the committed files for this capture are read; no concurrent-run glob.
    paths=[item['path'] for item in manifest['files'] if '/fmp/'+entity+'/' in item['path']]
    ingest_bronze(spark,cfg,paths,entity)
    if not entity.startswith('raw_'):normalize_silver(spark,cfg,entity,fields,['observation_id'])
commit=spark.createDataFrame([(manifest['run_id'],hashlib.sha256(Path(path).read_bytes()).hexdigest(),manifest['observed_at'],path)],'run_id string, manifest_sha256 string, observed_at string, manifest_path string')
_insert_only(spark,commit,cfg.table('ops','fmp_capture_commits'),['run_id'],['manifest_sha256','observed_at','manifest_path'])
dbutils.notebook.exit(json.dumps(dict(run_id=manifest['run_id'],entities=sorted(entities),verified_files=len(manifest['files']))))
