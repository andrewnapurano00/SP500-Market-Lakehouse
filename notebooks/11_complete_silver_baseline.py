# Databricks notebook source
"""Complete curated identity-routed prices, context facts and factor replay."""
import json
from sp500_lakehouse.config import LakehouseConfig
from sp500_lakehouse.identity import route_prices_spark
for k,v in [('catalog','workspace'),('prefix','sp500'),('baseline_manifest_sha256','')]:dbutils.widgets.text(k,v)
get=dbutils.widgets.get;cfg=LakehouseConfig(get('catalog'),get('prefix'));digest=get('baseline_manifest_sha256')
def source(name):
    table=cfg.table('bronze','pg_'+name)
    props={r.key:r.value for r in spark.sql('SHOW TBLPROPERTIES '+table).collect()}
    if props.get('sp500.manifest_sha256')!=digest:raise ValueError('Mixed baseline source')
    return spark.table(table)
routes=source('sp500_monthly_population').select('security_id','ticker_latest').distinct()
assets={'fact_stock_prices_daily_identity_v1':route_prices_spark(source('sp500_prices_daily'),routes)}
for target,table in {'fact_sector_etf_prices_daily':'sector_etf_prices_daily','fact_macro_observations_daily':'macro_cross_asset_observations_daily','fact_benchmark_monthly':'voo_quarterley_returns','baseline_fundamental_features_monthly':'sp500_monthly_fundamental_features'}.items():assets[target]=source(table)
results=[]
for name,frame in assets.items():
    target=cfg.table('silver',name)
    if spark.catalog.tableExists(target):
        props={r.key:r.value for r in spark.sql('SHOW TBLPROPERTIES '+target).collect()}
        if props.get('sp500.baseline_manifest_sha256')!=digest:raise ValueError('Conflicting Silver baseline')
    else:frame.writeTo(target).using('delta').tableProperty('delta.appendOnly','true').tableProperty('sp500.baseline_manifest_sha256',digest).tableProperty('sp500.identity_policy','reviewed_SKYD_2025_08_07_v1').tableProperty('sp500.vintage','retrospective_vendor_reconstruction').create()
    count=spark.table(target).count()
    if count!=frame.count():raise ValueError('Curated baseline count mismatch')
    results.append(dict(table=target,rows=count))
dbutils.notebook.exit(json.dumps(dict(passed=True,assets=results)))
