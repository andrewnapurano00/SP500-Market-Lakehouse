# Databricks notebook source
"""Real Delta vertical slice; explicit PostgreSQL reconstruction, never cutover."""
import json
from pathlib import Path
import pandas as pd
from sp500_lakehouse.config import LakehouseConfig
from sp500_lakehouse.delta import ingest_bronze, normalize_silver, publish_gold_snapshot
from sp500_lakehouse.transforms import monthly_cohort, monthly_targets, project_features
from sp500_lakehouse.legacy import stock_technicals
from sp500_lakehouse.reconcile import reconcile_frames

dbutils.widgets.text('catalog','workspace')
dbutils.widgets.text('prefix','sp500')
dbutils.widgets.text('plan_path','')
cfg=LakehouseConfig(dbutils.widgets.get('catalog'),dbutils.widgets.get('prefix'))
plan_path=Path(cfg.require_volume_path('exports',dbutils.widgets.get('plan_path')))
plan=json.loads(plan_path.read_text())
spark.conf.set('spark.sql.session.timeZone','UTC')
row_counts={}
for entity,spec in plan['entities'].items():
    path=cfg.volume('landing')+'/'+spec['relative_file']
    ingest_bronze(spark,cfg,path,entity)
    before=spark.table(cfg.table('bronze',entity)).count()
    ingest_bronze(spark,cfg,path,entity)
    if spark.table(cfg.table('bronze',entity)).count()!=before:
        raise AssertionError('Bronze retry changed row count')
    normalize_silver(spark,cfg,entity,spec['fields'],spec['business_keys'])
    before_silver=spark.table(cfg.table('silver',entity)).count()
    normalize_silver(spark,cfg,entity,spec['fields'],spec['business_keys'])
    if spark.table(cfg.table('silver',entity)).count()!=before_silver:
        raise AssertionError('Silver retry changed row count')
    row_counts[entity]={'bronze':before,'silver':before_silver}

def frame(entity):
    spec=plan['entities'][entity]
    source=spark.table(cfg.table('silver',entity))
    if source.limit(10001).count()>10000:
        raise ValueError('Validation slice is no longer bounded')
    # Exactly one input payload revision per key is required, not an arbitrary latest.
    result=source.select(*spec['fields']).toPandas()
    if len(result)!=spec['rows']:
        raise AssertionError('Multiple revisions or missing Silver rows require review')
    for column,dtype in spec['fields'].items():
        if dtype=='date':result[column]=pd.to_datetime(result[column])
        elif dtype=='timestamp':result[column]=pd.to_datetime(result[column],utc=True)
    return result

membership=frame('slice_membership')
prices=frame('slice_prices')
sessions=frame('slice_sessions')
benchmark=frame('slice_benchmark')
cohort=monthly_cohort(membership,prices,sessions,[plan['signal_month']],as_of=plan['as_of'])
sample=prices[prices.security_id.isin(plan['sample_security_ids']) & prices.date.le(cohort.date.max())]
technicals=stock_technicals(sample,plan['legacy_source_directory'])
feature_columns=[c for c in technicals if c not in {'security_id','date'}]
feature_values=cohort.merge(technicals,on=['security_id','date'],how='left',validate='one_to_one')
features=project_features(feature_values,feature_columns)
targets=monthly_targets(cohort,prices,benchmark,sessions)
expected_features=pd.read_json(plan['expected_features'],orient='table')
expected_targets=pd.read_json(plan['expected_targets'],orient='table')
feature_report=reconcile_frames(expected_features[list(features)],features,['security_id','signal_month'],atol=1e-9,rtol=1e-8)
target_report=reconcile_frames(expected_targets,targets,['security_id','signal_month'])
manifest={'run_id':'cloud_slice_'+plan['snapshot_id'],'feature_version':'legacy-technicals-proof-v1',
          'source_hashes':plan['source_hashes'],'as_of':plan['as_of'],
          'scope':'bounded_reconstructed_slice_three_stock_technicals_full_monthly_cohort',
          'cutover_approved':False,'availability_quality':'historical_vintage_unknown'}
table=publish_gold_snapshot(spark,cfg,spark.createDataFrame(features),plan['snapshot_id'],manifest)
if publish_gold_snapshot(spark,cfg,spark.createDataFrame(features),plan['snapshot_id'],manifest)!=table:
    raise AssertionError('Snapshot retry mismatch')
# Outcomes are a separate Delta asset, keyed by immutable snapshot identity.
target_table=cfg.table('gold','targets_'+plan['snapshot_id'])
target_frame=spark.createDataFrame(targets)
if spark.catalog.tableExists(target_table):
    existing=spark.table(target_table).select(*target_frame.columns)
    if existing.exceptAll(target_frame).limit(1).count() or target_frame.exceptAll(existing).limit(1).count():
        raise FileExistsError('Immutable target evidence conflict')
else:
    target_frame.write.format('delta').mode('error').saveAsTable(target_table)
    spark.sql(f"ALTER TABLE {target_table} SET TBLPROPERTIES ('delta.appendOnly'='true')")
result={'passed':True,'features':feature_report,'targets':target_report,'tables':row_counts,
        'gold_table':table,'target_table':target_table,'cutover_approved':False}
result_path=plan_path.with_name('cloud_validation_result.json')
if result_path.exists() and json.loads(result_path.read_text())!=result:
    raise FileExistsError('Cloud validation evidence conflict')
result_path.write_text(json.dumps(result,indent=2))
dbutils.notebook.exit(json.dumps(result))
