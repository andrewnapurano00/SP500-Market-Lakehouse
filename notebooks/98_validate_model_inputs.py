# Databricks notebook source
"""Full precomputed model-input assembly parity, without consumer activation."""
import json
from pathlib import Path
import pandas as pd
from sp500_lakehouse.config import LakehouseConfig
from sp500_lakehouse.delta import ingest_bronze, normalize_silver, publish_gold_snapshot
from sp500_lakehouse.model_inputs import assemble_model_inputs
from sp500_lakehouse.reconcile import reconcile_frames

dbutils.widgets.text('catalog','workspace')
dbutils.widgets.text('prefix','sp500')
dbutils.widgets.text('plan_path','')
cfg=LakehouseConfig(dbutils.widgets.get('catalog'),dbutils.widgets.get('prefix'))
path=Path(cfg.require_volume_path('exports',dbutils.widgets.get('plan_path')))
plan=json.loads(path.read_text())
spark.conf.set('spark.sql.session.timeZone','UTC')
frames={};counts={}
for entity,spec in plan['entities'].items():
    ingest_bronze(spark,cfg,cfg.volume('landing')+'/'+spec['relative_file'],entity)
    normalize_silver(spark,cfg,entity,spec['fields'],spec['business_keys'])
    source=spark.table(cfg.table('silver',entity))
    if source.limit(10001).count()>10000:
        raise ValueError('Bounded validation requires at most 10000 input rows per family')
    frame=source.select(*spec['fields']).toPandas()
    if len(frame)!=spec['rows']:raise ValueError('Missing or multi-revision sources require explicit vintage selection')
    # Restore provenance clock awareness lost in Spark-to-pandas timestamp conversion.
    observation={'population':'week_end','technical':'date','financial':'month_end','sector':'date','macro':'date'}[spec['family']]
    for name,dtype in spec['fields'].items():
        if dtype=='date' or name==observation:
            frame[name]=pd.to_datetime(frame[name])
        elif dtype=='timestamp':
            source_type=spec.get('source_column_types',{}).get(name)
            frame[name]=pd.to_datetime(frame[name],utc=source_type=='timestamp with time zone')
    frames[spec['family']]=frame
    counts[spec['family']]=len(frame)
actual,evidence=assemble_model_inputs(**frames,signal_date=plan['signal_date'],feature_columns=plan['feature_columns'],
    signal_cutoff_at=plan['signal_cutoff_at'],as_of_utc=plan['as_of'])
expected=pd.read_json(cfg.require_volume_path('exports',plan['expected_features']),orient='table')
report=reconcile_frames(expected[list(actual)],actual,['security_id','signal_month'])
manifest={'run_id':'cloud_'+plan['snapshot_id'],'feature_version':'precomputed-factor-replay-v1',
    'source_hashes':plan['source_hashes'],'as_of':plan['as_of'],'cutover_approved':False,
    'scope':'Full precomputed factor input assembly, end-of-day replay; historical vintages unverified'}
table=publish_gold_snapshot(spark,cfg,spark.createDataFrame(actual),plan['snapshot_id'],manifest)
result={'passed':True,'rows':len(actual),'predictors':len(plan['feature_columns']),
    'parity':report,'gold_table':table,'input_counts':counts,'cutover_approved':False,
    'availability_quality':evidence['availability_quality'],'scope':manifest['scope']}
path.with_name('model_cloud_result.json').write_text(json.dumps(result,indent=2))
dbutils.notebook.exit(json.dumps(result))
