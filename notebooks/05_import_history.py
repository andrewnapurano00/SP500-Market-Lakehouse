# Databricks notebook source
"""Import immutable full-history baseline; never replaces an existing table.

Upload the complete export directory to a UC Volume first. No FMP calls.
Tables are PostgreSQL reconstruction evidence, not newly computed Silver facts.
Rollback: remove only newly created pg_* tables with matching manifest digest;
retain uploaded Parquet and manifest as the immutable recovery source.
"""
import hashlib
import json
import re
from pathlib import Path
from pyspark.sql import functions as F

dbutils.widgets.text('manifest_path', '')
dbutils.widgets.text('catalog', 'workspace')
dbutils.widgets.text('schema', 'sp500_bronze')
dbutils.widgets.text('table_names_json', '[]')
manifest_path = dbutils.widgets.get('manifest_path')
catalog = dbutils.widgets.get('catalog')
namespace = dbutils.widgets.get('schema')
for value in (catalog, namespace):
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', value):
        raise ValueError('Invalid catalog/schema identifier')
if not manifest_path.startswith('/Volumes/'):
    raise ValueError('manifest_path must be on a governed Unity Catalog Volume')
root = Path(manifest_path).parent
manifest_bytes = Path(manifest_path).read_bytes()
manifest = json.loads(manifest_bytes)
digest = hashlib.sha256(manifest_bytes).hexdigest()
if manifest['status'] != 'complete' or manifest['format_version'] != 1:
    raise ValueError('Only completed supported export manifests can be imported')
selected=json.loads(dbutils.widgets.get('table_names_json'))
if not isinstance(selected,list) or any(n not in {t['table'] for t in manifest['tables']} for n in selected):
    raise ValueError('Unknown explicit import table selection')


def quote(value):
    return '`' + value.replace('`', '``') + '`'


def validate(frame, item):
    expressions = [F.count(F.lit(1)).alias('row_count')]
    expressions += [F.sum(F.when(F.col(quote(name)).isNull(), 1).otherwise(0)).alias('n'+str(i)) for i,name in enumerate(item['null_counts'])]
    for i,name in enumerate(item['date_ranges']):
        expressions += [F.min(F.col(quote(name))).alias('lo'+str(i)), F.max(F.col(quote(name))).alias('hi'+str(i))]
    stats = frame.agg(*expressions).first().asDict()
    if stats['row_count'] != item['row_count']: raise ValueError('Row count mismatch: '+item['table'])
    for i,(name,count) in enumerate(item['null_counts'].items()):
        if (stats['n'+str(i)] or 0) != count: raise ValueError('NULL count mismatch: '+name)
    for i,(name,bounds) in enumerate(item['date_ranges'].items()):
        for prefix,label in [('lo','min'),('hi','max')]:
            observed=stats[prefix+str(i)]
            expected=bounds[label]
            # Compare date/time values independent of JSON timezone formatting.
            if observed is None or expected is None:
                if observed is not None or expected is not None: raise ValueError('Date coverage mismatch: '+name)
            elif str(observed).replace('+00:00','') != str(expected).replace('+00:00',''):
                raise ValueError('Date coverage mismatch: '+name)
    for key in item['keys']:
        duplicates = frame.groupBy(*[F.col(quote(c)) for c in key['columns']]).count().where('count > 1').agg(F.sum(F.col('count')-1)).first()[0] or 0
        if duplicates != key['duplicate_excess_rows']: raise ValueError('Key multiplicity mismatch')


spark.sql(f'CREATE SCHEMA IF NOT EXISTS {quote(catalog)}.{quote(namespace)}')
results=[]
for item in manifest['tables']:
    if selected and item['table'] not in selected:continue
    name='pg_'+item['table']
    if not re.fullmatch(r'[a-zA-Z_][a-zA-Z0-9_]*',name): raise ValueError('Invalid table name')
    target=f'{quote(catalog)}.{quote(namespace)}.{quote(name)}'
    paths=[]
    for chunk in item['files']:
        path=(root/chunk['path']).resolve()
        if not path.is_relative_to(root.resolve()): raise ValueError('Manifest path escapes root')
        checksum=hashlib.sha256()
        with path.open('rb') as stream:
            for block in iter(lambda:stream.read(8*1024*1024),b''): checksum.update(block)
        if path.stat().st_size != chunk['bytes'] or checksum.hexdigest()!=chunk['sha256']:
            raise ValueError('Chunk integrity mismatch: '+chunk['path'])
        paths.append(str(path))
    frame=spark.read.parquet(*paths)
    validate(frame,item)
    if spark.catalog.tableExists(target):
        properties={r['key']:r['value'] for r in spark.sql(f'SHOW TBLPROPERTIES {target}').collect()}
        if properties.get('sp500.manifest_sha256') != digest:
            raise ValueError('Existing table belongs to another snapshot; choose a new namespace: '+target)
        validate(spark.table(target),item)
        results.append(dict(table=target,status='verified_existing',rows=item['row_count']))
        continue
    # V2 create commits data + ownership properties together. Concurrent create
    # conflicts fail rather than overwriting a table belonging to another run.
    (frame.writeTo(target).using('delta')
        .tableProperty('sp500.manifest_sha256',digest)
        .tableProperty('sp500.pg_snapshot',manifest['snapshot'])
        .tableProperty('sp500.classification',item['classification'])
        .tableProperty('sp500.reconstruction_only','true')
        .tableProperty('sp500.schema_sha256',item['schema_sha256']).create())
    validate(spark.table(target),item)
    results.append(dict(table=target,status='created_verified',rows=item['row_count']))
dbutils.notebook.exit(json.dumps(dict(manifest_sha256=digest,results=results)))
