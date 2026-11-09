# Databricks notebook source
"""Publish typed baseline facts and reviewed identity bridges into Silver.

These are an immutable reconstruction baseline, separately named from observed
FMP revisions. All later feature releases bind this baseline plus committed FMP
captures. Unmapped vendor symbols are retained for identity review.
"""
import json
from pyspark.sql import functions as F,Window
from sp500_lakehouse.config import LakehouseConfig
for k,v in [('catalog','workspace'),('prefix','sp500'),('baseline_manifest_sha256','')]:dbutils.widgets.text(k,v)
get=dbutils.widgets.get;cfg=LakehouseConfig(get('catalog'),get('prefix'));digest=get('baseline_manifest_sha256')
def source(name):
    table=cfg.table('bronze','pg_'+name)
    props={r.key:r.value for r in spark.sql('SHOW TBLPROPERTIES '+table).collect()}
    if props.get('sp500.manifest_sha256')!=digest:raise ValueError('Baseline digest mismatch')
    return spark.table(table)
daily=source('sp500_population_daily_audit')
routes=daily.select('security_id',F.col('latest_ticker').alias('symbol')).distinct()
ambiguous=routes.groupBy('symbol').count().where('count>1').select('symbol')
routes=routes.join(ambiguous,on='symbol',how='left_anti')
latest=Window.partitionBy('security_id').orderBy(F.col('date').desc())
assets={'dim_security':daily.withColumn('_rn',F.row_number().over(latest)).where('_rn=1').drop('_rn'),
    'bridge_security_route_daily':daily,'bridge_membership_daily':daily,
    'bridge_membership_monthly':source('sp500_monthly_population')}
for name,table in {'fact_income_statement_quarterly':'income_statements_q','fact_cashflow_statement_quarterly':'cashflow_statements_q','fact_balance_sheet_quarterly':'balance_sheets_q','fact_market_cap_daily':'market_caps_d','fact_enterprise_value_quarterly':'enterprise_values_q'}.items():
    frame=source(table).join(routes,on='symbol',how='left')
    assets[name]=frame.withColumn('identity_status',F.when(F.col('security_id').isNull(),'unmapped_review_required').otherwise('reviewed_baseline_route'))
prices=source('sp500_prices_daily')
assets['fact_stock_prices_daily']=prices.join(routes.withColumnRenamed('symbol','ticker_latest'),on='ticker_latest',how='left').withColumn('identity_status',F.when(F.col('security_id').isNull(),'unmapped_review_required').otherwise('reviewed_baseline_route'))
results=[]
for name,frame in assets.items():
    target=cfg.table('silver',name)
    if spark.catalog.tableExists(target):
        props={r.key:r.value for r in spark.sql('SHOW TBLPROPERTIES '+target).collect()}
        if props.get('sp500.baseline_manifest_sha256')!=digest:raise ValueError('Conflicting immutable Silver baseline')
    else:
        frame.writeTo(target).using('delta').tableProperty('delta.appendOnly','true').tableProperty('sp500.baseline_manifest_sha256',digest).tableProperty('sp500.vintage','retrospective_vendor_reconstruction').create()
    count=spark.table(target).count()
    if count!=frame.count():raise ValueError('Silver baseline count mismatch')
    results.append(dict(table=target,rows=count))
dbutils.notebook.exit(json.dumps(dict(baseline_manifest_sha256=digest,assets=results)))
