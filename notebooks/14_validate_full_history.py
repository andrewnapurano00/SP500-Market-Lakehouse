# Databricks notebook source
"""Full-cloud feature/cohort/target reconciliation against the read-only export."""
from pathlib import Path
import json,hashlib
from pyspark.sql import functions as F
from sp500_lakehouse.config import LakehouseConfig
from sp500_lakehouse.releases import read_bound
for k,v in [('catalog','workspace'),('prefix','sp500'),('manifest_path','')]:dbutils.widgets.text(k,v)
get=dbutils.widgets.get;cfg=LakehouseConfig(get('catalog'),get('prefix'))
path=get('manifest_path');cfg.require_volume_path('exports',path)
manifest=json.loads(Path(path).read_text());root=Path(path).parent;reports={}
keys=['security_id','signal_month']
for family,item in manifest['files'].items():
    source=root/item['name']
    if hashlib.sha256(source.read_bytes()).hexdigest()!=item['sha256']:raise ValueError('Expected-file checksum mismatch')
    expected=spark.read.parquet(str(source));actual=read_bound(spark,manifest['binding'],family).select(*expected.columns)
    count=expected.count()
    if actual.count()!=count:raise ValueError('Row count differs: '+family)
    if expected.select(*keys).exceptAll(actual.select(*keys)).limit(1).count() or actual.select(*keys).exceptAll(expected.select(*keys)).limit(1).count():raise ValueError('Cohort keys differ: '+family)
    joined=expected.alias('e').join(actual.alias('a'),on=keys,how='inner')
    checks=[]
    for index,column in enumerate(c for c in expected.columns if c not in keys):
        a,b=F.col('e.`'+column+'`'),F.col('a.`'+column+'`')
        dtype=expected.schema[column].dataType.simpleString()
        if dtype in ['double','float','bigint','int','smallint'] or dtype.startswith('decimal'):
            bad=(a.isNull()!=b.isNull())|((F.abs(a-b)>F.lit(1e-10)+F.lit(1e-8)*F.abs(a))&a.isNotNull()&b.isNotNull())
        elif dtype.startswith(('date','timestamp')):bad=~F.to_date(a).eqNullSafe(F.to_date(b))
        else:bad=~a.eqNullSafe(b)
        checks.append(F.sum(F.when(bad,1).otherwise(0)).alias('c'+str(index)))
    stats=joined.agg(*checks).first().asDict()
    if any(stats.values()):raise ValueError('Value/NULL mismatches: '+family+' '+str(stats))
    reports[family]=dict(passed=True,rows=count,columns=len(expected.columns))
dbutils.notebook.exit(json.dumps(dict(passed=True,binding=manifest['binding'],comparisons=reports,original_vintage_certified=False)))
