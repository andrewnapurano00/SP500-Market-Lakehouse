# Databricks notebook source
"""Register an explicit source-verified issuer/share-class route; never infer IDs."""
import json,hashlib
from pathlib import Path
from sp500_lakehouse.config import LakehouseConfig
from sp500_lakehouse.delta import _insert_only
from sp500_lakehouse.fundamental_features import norm_cik
for k,v in [('catalog','workspace'),('prefix','sp500'),('review_path',''),('review_sha256','')]:dbutils.widgets.text(k,v)
get=dbutils.widgets.get;cfg=LakehouseConfig(get('catalog'),get('prefix'));path=get('review_path');cfg.require_volume_path('exports',path)
data=Path(path).read_bytes();digest=hashlib.sha256(data).hexdigest()
if digest!=get('review_sha256'):raise ValueError('Identity review digest mismatch')
review=json.loads(data)
required=['security_id','api_lookup_ticker','ticker_latest','cik','currency','sector','industry','identity_valid_from','membership_effective_from','share_class','primary_sources','profile','reviewed_by']
if any(not review.get(k) for k in required):raise ValueError('Incomplete explicit identity review')
if norm_cik(review['profile'].get('cik'))!=norm_cik(review['cik']) or review['profile'].get('symbol')!=review['api_lookup_ticker']:raise ValueError('Profile/issuer identity mismatch')
if not any('sec.gov/' in url for url in review['primary_sources']) or not any('press.spglobal.com/' in url for url in review['primary_sources']):raise ValueError('SEC share-class and index membership evidence required')
keys=['security_id','api_lookup_ticker','ticker_latest','cik','currency','sector','industry','identity_valid_from','membership_effective_from','share_class','reviewed_by']
values={key:review[key] for key in keys}
values.update(primary_sources_json=json.dumps(review['primary_sources']),profile_json=json.dumps(review['profile']),review_sha256=digest)
frame=spark.createDataFrame([tuple(values.values())],','.join(k+' string' for k in values))
_insert_only(spark,frame,cfg.table('ops','reviewed_security_routes'),['security_id','api_lookup_ticker'],['review_sha256'])
dbutils.notebook.exit(json.dumps(dict(registered=True,security_id=review['security_id'],review_sha256=digest)))
