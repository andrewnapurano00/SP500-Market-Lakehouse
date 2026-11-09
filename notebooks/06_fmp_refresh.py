# Databricks notebook source
# This job lands observations only; it does not switch model consumers.
import json
from sp500_ingest.fmp import FMPClient, HTTPClient
from sp500_ingest.refresh import plan_requests, refresh
from sp500_lakehouse.config import LakehouseConfig
from sp500_lakehouse.delta import ingest_bronze, normalize_silver
for name, default in [('catalog',''),('prefix','sp500'),('identities_table',''),('start_date','2012-01-01'),('end_date',''),('run_id',''),('max_requests','1'),('include_context','true')]:
    dbutils.widgets.text(name,default)
get = dbutils.widgets.get
cfg = LakehouseConfig(get('catalog'),get('prefix'))
# Validated qualified names only: no caller SQL expressions.
from sp500_lakehouse.config import identifier
identity_table = '.'.join(identifier(p) for p in get('identities_table').split('.'))
identities = [r.asDict() for r in spark.table(identity_table).select('security_id','api_lookup_ticker').distinct().limit(5001).collect()]
if len(identities)>5000:
    raise ValueError('Identity request cap exceeded')
jobs = plan_requests(identities,get('start_date'),get('end_date'),include_context=get('include_context')=='true')
budget = int(get('max_requests'))
if budget < len(jobs):
    raise ValueError(f'Planned {len(jobs)} requests exceed explicit request budget')
key = dbutils.secrets.get('sp500','fmp-api-key')
client = FMPClient(key,HTTPClient(max_requests=budget))
root = f"/Volumes/{get('catalog')}/{get('prefix')}_files/landing"
checkpoints = f"/Volumes/{get('catalog')}/{get('prefix')}_files/checkpoints/fmp"
audit = refresh(client,jobs,root,checkpoints,get('run_id'))
fields = {'entity':'string','security_id':'string','api_lookup_ticker':'string','observation_date':'date','source_business_key':'string','observation_id':'string','payload_revision':'string','retrieved_at':'timestamp','run_id':'string','availability_quality':'string','statement_period':'string','values':'string'}
fields['source_ordinal']='long'
for entity in sorted({j['entity'] for j in jobs}):
    ingest_bronze(spark,cfg,f'{root}/fmp/{entity}/dt=*/*.jsonl',entity)
    normalize_silver(spark,cfg,entity,fields,['observation_id'])
print(json.dumps({'run_id':get('run_id'),'planned_requests':len(jobs),'completed_requests':len(audit)}))
