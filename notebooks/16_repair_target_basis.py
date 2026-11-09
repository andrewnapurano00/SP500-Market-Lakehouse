# Databricks notebook source
"""Repair refreshed target bases using the independently reconciled baseline."""
import json,hashlib
from pathlib import Path
from sp500_lakehouse.config import LakehouseConfig,identifier
from sp500_lakehouse.releases import read_bound,preserve_known_targets
from sp500_lakehouse.reader import binding_sha256
from sp500_lakehouse.delta import publish_gold_snapshot,validate_snapshot_contract
from sp500_lakehouse.spark_frames import pandas_to_spark
for k,v in [('catalog','workspace'),('prefix','sp500'),('parent_binding_path',''),('anchor_binding_path',''),('snapshot_id',''),('as_of','')]:dbutils.widgets.text(k,v)
get=dbutils.widgets.get;cfg=LakehouseConfig(get('catalog'),get('prefix'))
for name in ['parent_binding_path','anchor_binding_path']:cfg.require_volume_path('exports',get(name))
parent=json.loads(Path(get('parent_binding_path')).read_text());anchor=json.loads(Path(get('anchor_binding_path')).read_text());snapshot=identifier(get('snapshot_id'))
cohort=read_bound(spark,parent,'cohort');old=read_bound(spark,parent,'targets').toPandas();reference=read_bound(spark,anchor,'targets').toPandas()
targets=preserve_known_targets(old,reference,cohort.select('security_id','signal_month','ticker').toPandas())
manifest=dict(run_id=snapshot,feature_version='known-target-basis-repair-v2',as_of=get('as_of'),feature_columns=parent['feature_columns'],source_hashes=dict(parent_binding=binding_sha256(parent),target_anchor=binding_sha256(anchor)),parent_binding_sha256=binding_sha256(parent),target_policy='preserve_known_returns_v2',original_vintage_certified=False)
features=read_bound(spark,parent,'features');table=publish_gold_snapshot(spark,cfg,features,snapshot,manifest);digest=validate_snapshot_contract(features.columns,manifest)
def side(frame,kind):
 target=cfg.table('gold',kind+'_'+snapshot)
 frame.writeTo(target).using('delta').tableProperty('delta.appendOnly','true').tableProperty('sp500.manifest_sha256',digest).create()
 return dict(table=target,version=0)
binding=dict(parent,snapshot_id=snapshot,manifest_sha256=digest,as_of=get('as_of'),features=dict(table=table,version=0),cohort=side(cohort,'cohort'),targets=side(pandas_to_spark(spark,cfg,targets),'targets'))
keys=['security_id','signal_month'];m=reference.merge(targets,on=keys,suffixes=('_old','_new'),validate='one_to_one')
for col in ['next_month_return','benchmark_return']:
 known=m[col+'_old'].notna()
 if not m.loc[known,col+'_old'].eq(m.loc[known,col+'_new']).all():raise ValueError('Target anchor mismatch')
result=dict(binding=binding,rows=len(targets),anchor_verified=True,changed_returns=int((old.next_month_return.fillna(-999).to_numpy()!=targets.next_month_return.fillna(-999).to_numpy()).sum()))
dbutils.notebook.exit(json.dumps(result))
