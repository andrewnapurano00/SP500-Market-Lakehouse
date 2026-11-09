# Databricks notebook source
"""Recompute original formulas from an explicit baseline and FMP capture.
Creates a candidate snapshot; activation requires independent reconciliation.
"""
import json,hashlib
from pathlib import Path
import pandas as pd
import pandas_market_calendars as mcal
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from sp500_lakehouse.config import LakehouseConfig,identifier
from sp500_lakehouse.refresh_features import recompute
from sp500_lakehouse.fundamental_features import SOURCES
from sp500_lakehouse.model_inputs import assemble_model_inputs
from sp500_lakehouse.delta import publish_gold_snapshot
from sp500_lakehouse.membership_refresh import reconcile_month
from sp500_lakehouse.identity import route_prices_spark
from sp500_lakehouse.releases import publish_release,read_bound
from sp500_lakehouse.history import COHORT_CONTEXT_COLUMNS
from sp500_lakehouse.refresh_features import overlay,capture_rows
from sp500_lakehouse.spark_frames import pandas_to_spark
from sp500_lakehouse.delta import _insert_only
from sp500_lakehouse.feature_checkpoints import checkpoint_identity,load_checkpoint,save_checkpoint
defaults=dict(catalog='workspace',prefix='sp500',run_id='',signal_date='',snapshot_id='',
    baseline_manifest_sha256='',profiles_path='',profiles_sha256='',feature_columns_json='[]',
    as_of='',max_collect_rows='4000000')
defaults['previous_binding_path']=''
for k,v in defaults.items():dbutils.widgets.text(k,v)
p={k:dbutils.widgets.get(k) for k in defaults}
cfg=LakehouseConfig(p['catalog'],p['prefix']);cap=int(p['max_collect_rows'])
if not 1<=cap<=10000000:raise ValueError('Invalid compute bound')
spark.conf.set('spark.sql.session.timeZone','UTC')

def collect(frame):
    if frame.limit(cap+1).count()>cap:raise ValueError('Compute collection bound exceeded')
    result=frame.toPandas()
    for c in result:
        if c in {'date','week_end','month_end','observation_date'}:result[c]=pd.to_datetime(result[c])
    return result

def baseline(name):
    mapping={'sp500_monthly_population':'bridge_membership_monthly','sp500_population_daily_audit':'bridge_security_route_daily',
        'income_statements_q':'fact_income_statement_quarterly','cashflow_statements_q':'fact_cashflow_statement_quarterly',
        'balance_sheets_q':'fact_balance_sheet_quarterly','market_caps_d':'fact_market_cap_daily','enterprise_values_q':'fact_enterprise_value_quarterly',
        'sector_etf_prices_daily':'fact_sector_etf_prices_daily','macro_cross_asset_observations_daily':'fact_macro_observations_daily',
        'voo_quarterley_returns':'fact_benchmark_monthly','sp500_monthly_fundamental_features':'baseline_fundamental_features_monthly'}
    table=cfg.table('silver',mapping[name])
    props={r.key:r.value for r in spark.sql('SHOW TBLPROPERTIES '+table).collect()}
    if not p['baseline_manifest_sha256'] or props.get('sp500.baseline_manifest_sha256')!=p['baseline_manifest_sha256']:
        raise ValueError('Mixed historical baseline')
    return spark.table(table)

families=[]
if not p['previous_binding_path']:raise ValueError('Pinned parent release is required')
cfg.require_volume_path('exports',p['previous_binding_path'])
parent=json.loads(Path(p['previous_binding_path']).read_text())
commits=spark.table(cfg.table('ops','fmp_capture_commits'))
commit=commits.where(F.col('run_id')==p['run_id']).collect()
if len(commit)!=1:raise ValueError('A fully committed FMP capture is required')
capture_time=commit[0]['observed_at']
if pd.Timestamp(capture_time)>pd.Timestamp(p['as_of']):raise ValueError('Capture exceeds declared as-of')
eligible=commits.where(F.to_timestamp('observed_at')<=F.to_timestamp(F.lit(capture_time))).select('run_id')
for entity in ['prices','benchmark_prices','income','cashflow','balance','market_cap','enterprise','macro_prices','vix','treasury','membership_current','membership_history']:
    source=spark.table(cfg.table('silver',entity)).join(eligible,on='run_id',how='inner')
    if entity.startswith('membership'):
        source=source.where(F.col('run_id')==p['run_id'])
    else:
        # The original financial ingestion keeps the first returned fiscal-date
        # row. Preserve every revision in Silver, applying that policy only to
        # the explicitly bound factor projection.
        window=Window.partitionBy('source_business_key').orderBy(F.to_timestamp('retrieved_at').desc(),F.col('source_ordinal').asc_nulls_last(),F.col('observation_id').desc())
        source=source.withColumn('_revision_rank',F.row_number().over(window)).where('_revision_rank=1').drop('_revision_rank')
        source=source.withColumn('source_capture_run_id',F.col('run_id')).withColumn('run_id',F.lit(p['run_id']))
    families.append(collect(source))
observations=pd.concat(families,ignore_index=True)
monthly=collect(baseline('sp500_monthly_population'))
signal=pd.Timestamp(p['signal_date'])
route_window=Window.partitionBy('security_id').orderBy(F.col('date').desc())
reviewed_routes=collect(baseline('sp500_population_daily_audit').withColumn('_route_rank',F.row_number().over(route_window)).where('_route_rank=1').select('security_id','api_lookup_ticker',F.col('latest_ticker').alias('ticker_latest'),'sector'))
reviews=None
if spark.catalog.tableExists(cfg.table('ops','reviewed_security_routes')):
    reviews=collect(spark.table(cfg.table('ops','reviewed_security_routes')))
    reviewed_routes=pd.concat([reviewed_routes.loc[~reviewed_routes.security_id.isin(reviews.security_id)],reviews[['security_id','api_lookup_ticker','ticker_latest','sector']]],ignore_index=True)
additional=read_bound(spark,parent,'cohort').where(F.col('signal_date')>F.lit(monthly.week_end.max().date()))
extra=collect(additional.select('security_id','ticker','historical_ticker','sector','signal_date'))
if not extra.empty:
    extra=extra.rename(columns={'ticker':'ticker_latest','signal_date':'week_end'}).merge(reviewed_routes[['security_id','api_lookup_ticker']],on='security_id',how='left',validate='many_to_one')
    if extra.api_lookup_ticker.isna().any():raise ValueError('Parent membership lacks a reviewed lookup route')
    monthly=pd.concat([monthly,extra],ignore_index=True)
monthly=reconcile_month(monthly,reviewed_routes,observations,run_id=p['run_id'],signal_date=p['signal_date'])
member=monthly.loc[monthly.week_end.eq(signal)]
current=observations.loc[observations.entity.eq('membership_current')]
symbols={json.loads(v)['symbol'] if isinstance(v,str) else v['symbol'] for v in current['values']}
routes=monthly[['security_id','ticker_latest']].drop_duplicates()
price_table=cfg.table('silver','fact_stock_prices_daily_identity_v1')
price_props={r.key:r.value for r in spark.sql('SHOW TBLPROPERTIES '+price_table).collect()}
if price_props.get('sp500.baseline_manifest_sha256')!=p['baseline_manifest_sha256']:raise ValueError('Price baseline mismatch')
stock=spark.table(price_table)
stock=collect(stock.select('security_id','date','adj_close','volume'))
identity=collect(baseline('sp500_population_daily_audit').select('security_id','latest_ticker','cik','currency').distinct())
cfg.require_volume_path('exports',p['profiles_path'])
profile_bytes=Path(p['profiles_path']).read_bytes()
if hashlib.sha256(profile_bytes).hexdigest()!=p['profiles_sha256']:raise ValueError('Profile evidence hash mismatch')
profiles={r['symbol']:r for r in json.loads(profile_bytes) if isinstance(r,dict) and r.get('symbol')}
if reviews is not None:
    identity=pd.concat([identity,reviews.rename(columns={'ticker_latest':'latest_ticker'})[['security_id','latest_ticker','cik','currency']]],ignore_index=True).drop_duplicates()
    for _,row in reviews.iterrows():profiles[row.api_lookup_ticker]=json.loads(row.profile_json)
if spark.catalog.tableExists(cfg.table('silver','profile')):
    profile_window=Window.partitionBy('api_lookup_ticker').orderBy(F.to_timestamp('retrieved_at').desc(),F.col('observation_id').desc())
    current_profiles=collect(spark.table(cfg.table('silver','profile')).join(eligible,on='run_id',how='inner').withColumn('_profile_rank',F.row_number().over(profile_window)).where('_profile_rank=1').drop('_profile_rank'))
    from sp500_lakehouse.fundamental_features import norm_cik
    for _,row in current_profiles.iterrows():
        value=json.loads(row['values']) if isinstance(row['values'],str) else row['values']
        known=set(identity.loc[identity.security_id.eq(row.security_id),'cik'].map(norm_cik).dropna())
        if norm_cik(value.get('cik')) not in known:raise ValueError('Current profile conflicts with reviewed issuer: '+row.api_lookup_ticker)
        profiles[row.api_lookup_ticker]=value
financial={family:collect(baseline(spec['table'])) for family,spec in SOURCES.items()}
import sp500_lakehouse as package
package_root=Path(package.__file__).parent
code_hashes={name:hashlib.sha256((package_root/(name+'.py')).read_bytes()).hexdigest() for name in ['refresh_features','fundamental_features','stock_features','sector_features','macro_features']}
from sp500_lakehouse.reader import binding_sha256
cache_id=checkpoint_identity(dict(run_id=p['run_id'],commit_sha256=commit[0]['manifest_sha256'],
    signal_date=p['signal_date'],parent_binding=binding_sha256(parent),baseline=p['baseline_manifest_sha256'],
    profiles=profiles,identity_rows=json.loads(identity.sort_values(list(identity.columns)).to_json(orient='records')),code=code_hashes))
cached=load_checkpoint(cfg,cache_id)
if cached is None:
    inputs,evidence=recompute(baseline_financial=financial,baseline_stock=stock,
        baseline_sector=collect(baseline('sector_etf_prices_daily')),
        baseline_macro=collect(baseline('macro_cross_asset_observations_daily')),
        observations=observations,run_id=p['run_id'],monthly=monthly,identity=identity,
        profiles=profiles,signal_date=p['signal_date'])
    save_checkpoint(cfg,cache_id,inputs,evidence)
else:inputs,evidence=cached
schedule=mcal.get_calendar('NYSE').schedule(start_date=signal,end_date=signal)
stock_closes=inputs.pop('_stock_prices')[['security_id','date','adj_close']]
for name in ['quality','lineage','thresholds','calibration']:
    audit=inputs.pop('_audit_'+name)
    target=cfg.table('ops','factor_'+name+'_'+identifier(p['run_id']))
    staged=pandas_to_spark(spark,cfg,audit)
    if spark.catalog.tableExists(target):
        old=spark.table(target)
        if set(old.columns)!=set(staged.columns) or old.select(*staged.columns).exceptAll(staged).limit(1).count() or staged.exceptAll(old.select(*staged.columns)).limit(1).count():raise ValueError('Immutable factor audit conflict')
    else:staged.writeTo(target).using('delta').tableProperty('delta.appendOnly','true').tableProperty('sp500.capture_commit_sha256',commit[0]['manifest_sha256']).create()
canonical=inputs.pop('_canonical_financial')
for family,frame in canonical.items():
    frame=frame.copy();frame['canonical_capture_run_id']=p['run_id']
    staged=pandas_to_spark(spark,cfg,frame)
    for field in staged.schema.fields:
        if field.dataType.simpleString()=='void':staged=staged.withColumn(field.name,F.col(field.name).cast('string'))
    _insert_only(spark,staged,cfg.table('silver','canonical_'+family+'_observations'),['canonical_capture_run_id','source_row_id'],list(staged.columns))
for family in ['technical','financial','sector','macro']:
    frame=inputs[family].copy();frame['canonical_capture_run_id']=p['run_id']
    staged=pandas_to_spark(spark,cfg,frame)
    keys={'technical':['security_id','date'],'financial':['security_id','month_end'],'sector':['sector','date'],'macro':['date']}[family]
    _insert_only(spark,staged,cfg.table('silver',family+'_feature_observations'),['canonical_capture_run_id']+keys,list(staged.columns))
panel,assembly=assemble_model_inputs(**inputs,signal_date=p['signal_date'],
    feature_columns=json.loads(p['feature_columns_json']),signal_cutoff_at=schedule.market_close.iloc[-1].isoformat(),
    as_of_utc=p['as_of'],mode='retrospective')
manifest=dict(run_id=p['run_id'],feature_version='original-formulas-recomputed-v1',
    as_of=p['as_of'],source_hashes=assembly['source_hashes'],feature_columns=json.loads(p['feature_columns_json']),
    baseline_manifest_sha256=p['baseline_manifest_sha256'],profiles_sha256=p['profiles_sha256'],
    recomputation=evidence,original_vintage_certified=False,cutover_approved=False)
manifest['capture_commit_sha256']=commit[0]['manifest_sha256']
cohort=member[['security_id','ticker_latest','historical_ticker','sector']].rename(columns={'ticker_latest':'ticker'}).copy()
cohort['signal_date']=signal;cohort['signal_month']=str(signal.to_period('M'))
cohort=cohort.merge(inputs['financial'][['security_id']+COHORT_CONTEXT_COLUMNS],on='security_id',how='left',validate='one_to_one')
benchmark=collect(baseline('voo_quarterley_returns').select(F.col('last_trading_day').alias('date'),F.col('voo_adj_close').alias('adj_close')))
new_bench=[]
for _,r in capture_rows(observations,p['run_id'],'benchmark_prices').iterrows():
    values=json.loads(r['values']) if isinstance(r['values'],str) else r['values']
    new_bench.append(dict(date=pd.Timestamp(r.observation_date),adj_close=values['adjclose']))
benchmark=overlay(benchmark,pd.DataFrame(new_bench),['date'])
result=publish_release(spark,cfg,panel=panel,cohort=cohort,stock_closes=stock_closes,
    benchmark_closes=benchmark,parent=parent,snapshot_id=identifier(p['snapshot_id']),manifest=manifest,
    historical_context=baseline('sp500_monthly_fundamental_features').select('security_id',F.date_format('month_end','yyyy-MM').alias('signal_month'),*COHORT_CONTEXT_COLUMNS))
result['evidence']=evidence
result['assembly']=assembly
dbutils.notebook.exit(json.dumps(result))
