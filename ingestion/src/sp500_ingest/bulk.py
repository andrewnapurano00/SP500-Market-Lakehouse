"""Immutable, snapshot-consistent full PostgreSQL reconstruction exports.

No API calls or database writes. An interrupted snapshot cannot be resumed after
its transaction closes: use a fresh directory, retaining the failed run for audit.
"""
import base64
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
from sqlalchemy import inspect, text
from .baseline import identifier


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def arrow_type(column):
    """Explicit conversions; unlimited numerics become exact decimal strings."""
    typ = column['type']
    name = str(typ).upper()
    if name == 'BOOLEAN': return pa.bool_(), None
    if name in ('SMALLINT', 'INTEGER', 'BIGINT'): return pa.int64(), None
    if name in ('REAL', 'DOUBLE PRECISION', 'FLOAT'): return pa.float64(), None
    if name == 'DATE': return pa.date32(), None
    if name.startswith('TIMESTAMP'): return pa.timestamp('us', tz='UTC' if getattr(typ, 'timezone', False) else None), None
    if name.startswith(('NUMERIC', 'DECIMAL')):
        precision, scale = getattr(typ, 'precision', None), getattr(typ, 'scale', None)
        if precision and precision <= 38 and scale is not None:
            return pa.decimal128(precision, scale), None
        return pa.string(), 'exact_numeric_text'
    if name == 'BYTEA': return pa.binary(), None
    if name in ('TEXT', 'VARCHAR', 'CHAR') or name.startswith(('VARCHAR(', 'CHAR(')): return pa.string(), None
    if name in ('JSON', 'JSONB'): return pa.string(), 'json_text'
    return pa.string(), 'postgres_text'


def atomic_json(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2, default=str), encoding='utf-8')
    temporary.replace(path)


def export_history(engine, output, contracts, batch_rows=50000):
    if not 1 <= batch_rows <= 1000000: raise ValueError('Invalid batch_rows')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    report = dict(format_version=1, status='incomplete', created_at=datetime.now(timezone.utc).isoformat(),
                  reconstruction_only=True, original_filing_vintage_proven=False, tables=[], views=[])
    progress = output / 'manifest.incomplete.json'
    atomic_json(progress, report)
    try:
        with engine.connect().execution_options(isolation_level='REPEATABLE READ') as conn:
            with conn.begin():
                conn.execute(text('SET TRANSACTION READ ONLY'))
                conn.execute(text("SET LOCAL TIME ZONE 'UTC'"))
                report['snapshot'] = conn.execute(text('SELECT txid_current_snapshot()::text')).scalar_one()
                inspector = inspect(conn)
                tables = sorted(inspector.get_table_names(schema='public'))
                if set(tables) != set(contracts['tables']):
                    raise ValueError('Observed tables differ from reviewed contract: ' + repr(set(tables) ^ set(contracts['tables'])))
                for view in inspector.get_view_names(schema='public'):
                    report['views'].append(dict(name=view, definition=inspector.get_view_definition(view, schema='public')))
                for table in tables:
                    started = time.monotonic()
                    cols = inspector.get_columns(table, schema='public')
                    conversions = [arrow_type(c) for c in cols]
                    schema = pa.schema([pa.field(c['name'], t, nullable=c['nullable']) for c, (t, _) in zip(cols, conversions)])
                    qualified = 'public.' + identifier(table)
                    primary = inspector.get_pk_constraint(table, schema='public').get('constrained_columns') or []
                    keys = [primary] if primary else []
                    keys += [k['column_names'] for k in inspector.get_unique_constraints(table, schema='public') if k.get('column_names')]
                    business = contracts['tables'][table].get('business_key') or []
                    if business and business not in keys: keys.append(business)
                    indexes = inspector.get_indexes(table, schema='public')
                    for index in indexes:
                        index_key = index.get('column_names') or []
                        # Expression/partial unique indexes are captured as metadata,
                        # not incorrectly asserted as global row-grain constraints.
                        if index.get('unique') and index_key and all(index_key) and not index.get('dialect_options', {}).get('postgresql_where') and index_key not in keys:
                            keys.append(index_key)
                    stats_sql = ['count(*) AS rows'] + [f'count(*) FILTER (WHERE {identifier(c["name"])} IS NULL) AS n{i}' for i,c in enumerate(cols)]
                    dates = [i for i,c in enumerate(cols) if str(c['type']).upper().startswith(('DATE', 'TIMESTAMP'))]
                    for i in dates: stats_sql += [f'min({identifier(cols[i]["name"])}) AS lo{i}', f'max({identifier(cols[i]["name"])}) AS hi{i}']
                    stats = conn.execute(text('SELECT '+','.join(stats_sql)+' FROM '+qualified)).mappings().one()
                    item = dict(table=table, classification=contracts['tables'][table]['classification'], row_count=stats['rows'],
                                columns=[dict(name=c['name'], postgres_type=str(c['type']), nullable=c['nullable'], default=c.get('default'), identity=c.get('identity'), computed=c.get('computed'), conversion=cv) for c,(_,cv) in zip(cols,conversions)],
                                primary_key=primary, unique_constraints=inspector.get_unique_constraints(table,schema='public'),
                                indexes=indexes, foreign_keys=inspector.get_foreign_keys(table,schema='public'),
                                check_constraints=inspector.get_check_constraints(table,schema='public'),
                                arrow_schema=base64.b64encode(schema.serialize().to_pybytes()).decode(),
                                null_counts={c['name']:stats[f'n{i}'] for i,c in enumerate(cols)},
                                date_ranges={cols[i]['name']:dict(min=stats[f'lo{i}'],max=stats[f'hi{i}']) for i in dates}, keys=[], files=[])
                    for key in keys:
                        grouped = ','.join(identifier(k) for k in key)
                        duplicates = conn.execute(text(f'SELECT coalesce(sum(n-1),0)::bigint FROM (SELECT count(*) n FROM {qualified} GROUP BY {grouped} HAVING count(*)>1) d')).scalar_one()
                        item['keys'].append(dict(columns=key, duplicate_excess_rows=duplicates))
                    # PostgreSQL casts preserve exact unsupported representations, including arrays.
                    select = ','.join(identifier(c['name']) + ('::text' if cv else '') + ' AS ' + identifier(c['name']) for c,(_,cv) in zip(cols,conversions))
                    result = conn.execution_options(stream_results=True, max_row_buffer=batch_rows).execute(text('SELECT '+select+' FROM '+qualified))
                    directory = output/table
                    directory.mkdir()
                    exported = 0
                    for index, rows in enumerate(result.partitions(batch_rows)):
                        arrays = [pa.array([row[i] for row in rows], type=field.type) for i,field in enumerate(schema)]
                        arrow = pa.Table.from_arrays(arrays, schema=schema)
                        path = directory / f'part-{index:06d}.parquet'
                        pq.write_table(arrow, path, compression='zstd', row_group_size=batch_rows)
                        item['files'].append(dict(path=path.relative_to(output).as_posix(), rows=len(rows), bytes=path.stat().st_size, sha256=sha256_file(path)))
                        exported += len(rows)
                    result.close()
                    if not item['files']:
                        path = directory/'part-000000.parquet'
                        pq.write_table(pa.Table.from_batches([],schema=schema),path,compression='zstd')
                        item['files'].append(dict(path=path.relative_to(output).as_posix(), rows=0, bytes=path.stat().st_size,sha256=sha256_file(path)))
                    if exported != item['row_count']: raise ValueError('Snapshot export count mismatch: '+table)
                    item['schema_sha256'] = hashlib.sha256(schema.serialize().to_pybytes()).hexdigest()
                    item['elapsed_seconds'] = time.monotonic()-started
                    report['tables'].append(item)
                    atomic_json(progress, report)
        report['status']='complete'
        report['total_rows']=sum(t['row_count'] for t in report['tables'])
        report['total_bytes']=sum(f['bytes'] for t in report['tables'] for f in t['files'])
        atomic_json(output/'manifest.json',report)
        progress.unlink()
        return report
    except Exception as error:
        report['failure_type']=type(error).__name__
        atomic_json(progress,report)
        raise
