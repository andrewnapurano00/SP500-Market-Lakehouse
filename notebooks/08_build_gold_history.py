# Databricks notebook source
"""Full immutable PostgreSQL-import history -> separate Gold features/cohort/targets.

Explicit baseline run and schema contracts prevent mixing imports/revisions.
Only monthly dates are collected; the multi-million-row daily table stays Spark.
"""
import hashlib
import json
import pandas as pd
import pandas_market_calendars as mcal
from pyspark.sql import functions as F
from sp500_lakehouse.config import LakehouseConfig, identifier
from sp500_lakehouse.delta import publish_gold_snapshot
from sp500_lakehouse.history import FAMILIES, COHORT_CONTEXT_COLUMNS, assemble_history, historical_targets
from sp500_lakehouse.identity import route_prices_spark
from sp500_lakehouse.spark_frames import pandas_to_spark

DEFAULTS={'catalog':'','prefix':'sp500','snapshot_id':'','baseline_run_id':'',
          'baseline_manifest_sha256':'','as_of':'','feature_columns_json':'[]',
          'sector_aliases_json':'{}','max_month_rows':'10000'}
for name,default in DEFAULTS.items(): dbutils.widgets.text(name,default)
params={name:dbutils.widgets.get(name) for name in DEFAULTS}
cfg=LakehouseConfig(params['catalog'],params['prefix'])
snapshot=identifier(params['snapshot_id'])
if not params['baseline_run_id']: raise ValueError('Explicit immutable import run required')
features=json.loads(params['feature_columns_json'])
bound=int(params['max_month_rows'])
if not 1<=bound<=100000: raise ValueError('Invalid pandas bound')
spark.conf.set('spark.sql.session.timeZone','UTC')


def payload(table):
    target=cfg.table('bronze','pg_'+identifier(table))
    props={row.key:row.value for row in spark.sql('SHOW TBLPROPERTIES '+target).collect()}
    if not params['baseline_manifest_sha256'] or props.get('sp500.manifest_sha256')!=params['baseline_manifest_sha256']:
        raise ValueError('Imported table manifest mismatch: '+table)
    raw=spark.table(target)
    if not raw.limit(1).count(): raise ValueError('Missing baseline rows: '+table)
    return raw


sources={family:payload(table) for family,(table,date) in FAMILIES.items()}
population=sources['population']
days=sorted(str(row[0])[:10] for row in population.select('week_end').distinct().collect())
if not days or len(days)>2400: raise ValueError('Invalid history date range')
cached={}
for family,(_,column) in FAMILIES.items():
    selected=sources[family]
    if family!='macro': selected=selected.where(F.to_date(column).isin(days))
    if selected.limit(bound*len(days)+1).count()>bound*len(days):raise ValueError('Historical collection bound exceeded')
    frame=selected.toPandas()
    for name in frame:
        if name==column or name.endswith(('_source_date','_fiscal_period_end')):
            frame[name]=pd.to_datetime(frame[name],errors='raise')
        elif name in {'source_release_at','eligible_at','first_seen_at','ingested_at','feature_cutoff_at'} or name.endswith('_available_at'):
            frame[name]=pd.to_datetime(frame[name],errors='raise',utc=True)
    cached[family]=frame


def load(family,signal_date):
    column=FAMILIES[family][1]
    day=pd.Timestamp(signal_date)
    source=cached[family]
    mask=source[column].between(day-pd.Timedelta(days=7),day) if family=='macro' else source[column].eq(day)
    frame=source.loc[mask].copy()
    if len(frame)>bound:raise ValueError('Monthly input bound exceeded: '+family)
    return frame


panel,cohort,evidence=assemble_history(load,days,features,as_of_utc=params['as_of'],
    sector_aliases=json.loads(params['sector_aliases_json']))
calendar=mcal.get_calendar('NYSE')
exit_days=[]
for day in days:
    period=pd.Timestamp(day).to_period('M')+1
    schedule=calendar.schedule(start_date=period.start_time,end_date=period.end_time)
    if schedule.market_close.iloc[-1]<=pd.Timestamp(params['as_of']): exit_days.append(str(schedule.index[-1].date()))
# Reviewed ticker routes are not allowed to collapse distinct stable securities.
routes=cohort[['security_id','ticker']].drop_duplicates()
prices=payload('sp500_prices_daily').where(F.to_date('date').isin(sorted(set(days+exit_days))))
prices=route_prices_spark(prices.select('ticker_latest','date','adj_close'),
    pandas_to_spark(spark,cfg,routes.rename(columns={'ticker':'ticker_latest'})))
if prices.limit(len(cohort)*3+1).count()>len(cohort)*3: raise ValueError('Monthly price bound exceeded')
stock=prices.select('security_id','date','adj_close').toPandas()
bench=payload('voo_quarterley_returns').select(F.col('last_trading_day').alias('date'),F.col('voo_adj_close').alias('adj_close')).toPandas()
targets=historical_targets(cohort,stock,bench,as_of_utc=params['as_of'])
manifest=dict(run_id=params['baseline_run_id'],feature_version='precomputed-factor-history-v1',
    as_of=params['as_of'],source_hashes=evidence['source_hashes'],feature_columns=features,
    original_vintage_certified=False,scope='retrospective_import_replay',policy=evidence['policy'],
    baseline_manifest_sha256=params['baseline_manifest_sha256'])
feature_table=publish_gold_snapshot(spark,cfg,pandas_to_spark(spark,cfg,panel),snapshot,manifest)
digest=hashlib.sha256(json.dumps(manifest,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()


def immutable_side(frame,kind):
    table=cfg.table('gold',kind+'_'+snapshot)
    source=pandas_to_spark(spark,cfg,frame)
    if spark.catalog.tableExists(table):
        existing=spark.table(table)
        props={r.key:r.value for r in spark.sql('SHOW TBLPROPERTIES '+table).collect()}
        if props.get('sp500.manifest_sha256')!=digest or set(existing.columns)!=set(source.columns):
            raise FileExistsError('Conflicting side-table manifest/schema')
        if existing.select(*source.columns).exceptAll(source).limit(1).count() or source.exceptAll(existing.select(*source.columns)).limit(1).count():
            raise FileExistsError('Conflicting immutable Gold side table')
    else:
        source.writeTo(table).using('delta').tableProperty('delta.appendOnly','true').tableProperty('sp500.manifest_sha256',digest).create()
    version=spark.sql('DESCRIBE HISTORY '+table).select('version').first()[0]
    return dict(table=table,version=int(version))


binding=dict(snapshot_id=snapshot,manifest_sha256=digest,feature_columns=features,cohort_extra_columns=['historical_ticker']+COHORT_CONTEXT_COLUMNS,
    signal_months=sorted({day[:7] for day in days}),
    features=dict(table=feature_table,version=int(spark.sql('DESCRIBE HISTORY '+feature_table).select('version').first()[0])),
    cohort=immutable_side(cohort,'cohort'),targets=immutable_side(targets,'targets'))
dbutils.notebook.exit(json.dumps(dict(binding=binding,months=evidence['months'],rows=len(panel),
    predictors=len(features),known_outcomes=int(targets.next_month_return.notna().sum()),
    unknown_outcomes=int(targets.next_month_return.isna().sum()),cutover_approved=False)))
