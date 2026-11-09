"""Snapshot-consistent PostgreSQL inventory and bounded reconstruction export."""
import time
from datetime import date
from sqlalchemy import inspect, text
from .landing import digest, write_records


def identifier(value):
    return '"' + str(value).replace('"', '""') + '"'


def validate_business_key(override, column_names, null_counts=None, duplicate_excess_rows=0):
    if override is None:
        return
    if not override or len(set(override)) != len(override) or set(override)-set(column_names):
        raise ValueError('Business key override columns must exist and be distinct')
    if null_counts is not None and (any(null_counts[k] for k in override) or duplicate_excess_rows):
        raise ValueError('Business key override has NULLs or duplicates in filtered cohort')


def where_clause(columns, date_column=None, start=None, end=None):
    if bool(start) != bool(end) or (start and not date_column):
        raise ValueError('Both start/end and date column are required for filters')
    if date_column and date_column not in columns:
        raise ValueError('Date column does not exist in observed catalog')
    if start:
        date.fromisoformat(start)
        date.fromisoformat(end)
    if start and start > end:
        raise ValueError('Start must precede end')
    return (f' WHERE {identifier(date_column)} >= :start AND {identifier(date_column)} <= :end',
            dict(start=start, end=end)) if start else ('', {})


def inventory(engine, tables, *, output_root=None, export_limit=0, date_column=None,
              start=None, end=None, timeout_ms=60000, sample_size=20, business_keys=None):
    if not tables or export_limit < 0 or not 1 <= sample_size <= 1000 or timeout_ms < 1:
        raise ValueError('Explicit tables and valid bounds required')
    if export_limit and output_root is None:
        raise ValueError('Export requires landing output directory')
    results = []
    business_keys = business_keys or {}
    if set(business_keys) - set(tables):
        raise ValueError('Business key override table must be in explicit allowlist')
    with engine.connect().execution_options(isolation_level='REPEATABLE READ') as connection:
        with connection.begin():
            connection.execute(text('SET TRANSACTION READ ONLY'))
            connection.execute(text("SELECT set_config('statement_timeout', :timeout, true)"), {'timeout': str(timeout_ms)})
            snapshot = connection.execute(text('SELECT txid_current_snapshot()::text')).scalar_one()
            catalog = inspect(connection)
            available = set(catalog.get_table_names(schema='public'))
            for table in tables:
                if table not in available:
                    raise ValueError(f'Table absent from observed public catalog: {table}')
                started = time.monotonic()
                cols = catalog.get_columns(table, schema='public')
                names = [c['name'] for c in cols]
                where, params = where_clause(names, date_column, start, end)
                qualified = 'public.' + identifier(table)
                pk = catalog.get_pk_constraint(table, schema='public').get('constrained_columns') or []
                override = business_keys.get(table)
                validate_business_key(override,names)
                export_key = override or pk
                unique = catalog.get_unique_constraints(table, schema='public')
                keys = [pk] if pk else []
                keys += [u['column_names'] for u in unique if u.get('column_names')]
                if override and override not in keys:
                    keys.append(override)
                expressions = ['count(*) AS row_count']
                for i, column in enumerate(cols):
                    q = identifier(column['name'])
                    expressions.append(f'count(*) FILTER (WHERE {q} IS NULL) AS null_{i}')
                    if any(t in str(column['type']).upper() for t in ('DATE', 'TIMESTAMP')):
                        expressions.extend([f'min({q}) AS min_{i}', f'max({q}) AS max_{i}'])
                stats = dict(connection.execute(text('SELECT ' + ','.join(expressions) + ' FROM ' + qualified + where), params).mappings().one())
                count = stats.pop('row_count')
                nulls = {c['name']: dict(count=stats[f'null_{i}'], rate=stats[f'null_{i}']/count if count else None) for i,c in enumerate(cols)}
                dates = {c['name']: dict(min=stats[f'min_{i}'], max=stats[f'max_{i}']) for i,c in enumerate(cols) if f'min_{i}' in stats}
                duplicates = []
                for key in keys:
                    grouped = ','.join(identifier(k) for k in key)
                    sql = f'SELECT coalesce(sum(n-1),0)::bigint FROM (SELECT count(*) n FROM {qualified}{where} GROUP BY {grouped} HAVING count(*)>1) d'
                    duplicates.append(dict(columns=key, duplicate_excess_rows=connection.execute(text(sql),params).scalar_one()))
                # Keyless samples are snapshot-local, not cross-run fingerprints.
                # Avoid sorting multi-GB JSON payloads for a bounded row sample.
                order = (' ORDER BY '+','.join(identifier(k) for k in export_key)) if export_key else ''
                query = f'SELECT * FROM {qualified} t{where}{order} LIMIT :limit'
                sample = [dict(r) for r in connection.execute(text(query), {**params, 'limit': sample_size}).mappings()]
                item = dict(table=table, snapshot=snapshot, row_count=count,
                            columns=[dict(name=c['name'], type=str(c['type']), nullable=c['nullable']) for c in cols],
                            primary_key=pk, unique_constraints=unique, null_rates=nulls, date_ranges=dates,
                            business_key_override=override, export_key=export_key,
                            sample_order='reviewed_or_declared_key' if export_key else 'snapshot_only_unordered_not_cross_run_fingerprint',
                            duplicate_keys=duplicates, sample_count=len(sample), sample_checksum=digest(sample),
                            key_validation_status='declared_keys_checked' if keys else 'no_declared_key_business_key_unresolved',
                            filters=dict(date_column=date_column,start=start,end=end))
                if export_limit:
                    validate_business_key(override,names,{k:v['count'] for k,v in nulls.items()},
                                          sum(d['duplicate_excess_rows'] for d in duplicates if d['columns']==override))
                    rows = (dict(r) for r in connection.execute(text(query), {**params,'limit': export_limit}).mappings())
                    path = write_records(output_root, 'postgres', table, rows,
                                         source_kind='postgres_reconstruction',
                                         request_parameters=dict(snapshot=snapshot, table=table, limit=export_limit, **item['filters']),
                                         source_record_key=(lambda row: [row[k] for k in export_key]) if export_key else None,
                                         source_key_strategy='validated_business_key_override' if override else 'declared_primary_key' if pk else 'payload_hash_business_key_unresolved')
                    item.update(landing_file=str(path), export_limit=export_limit,
                                export_is_complete=count <= export_limit)
                item['elapsed_seconds'] = time.monotonic()-started
                results.append(item)
    return dict(snapshot=snapshot, consistency='repeatable_read_read_only', tables=results)
