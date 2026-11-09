"""Read immutable Gold versions through a supplied SQL transport; no PostgreSQL."""
import hashlib
import json
import re
import pandas as pd
from .config import identifier
from .transforms import is_outcome_column, _unique


def _table(value):
    parts = value.split('.')
    if len(parts) != 3: raise ValueError('Fully qualified catalog.schema.table required')
    return '.'.join(identifier(p) for p in parts)


def binding_sha256(binding):
    return hashlib.sha256(json.dumps(binding,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


class GoldReader:
    """Binding pins feature/cohort/optional target tables AND Delta versions.

    query(sql)->DataFrame is deliberately injectable for Spark, Statement API or
    tests. The caller records binding_sha256 with every model/research artifact.
    """
    def __init__(self, query, binding):
        self.query, self.binding = query, json.loads(json.dumps(binding))
        columns = self.binding.get('feature_columns')
        if not columns or len(columns) != len(set(columns)) or any(is_outcome_column(c) or c in {'security_id','signal_month'} for c in columns):
            raise ValueError('Unique outcome-free predictor manifest required')
        for column in columns: identifier(column)
        for family in ('features','cohort'):
            if family not in binding: raise ValueError('Required Gold source: '+family)
        for family in ('features','cohort','targets'):
            if family not in binding: continue
            item = binding[family]; _table(item['table'])
            if isinstance(item['version'],bool) or not isinstance(item['version'],int) or item['version'] < 0:
                raise ValueError('Nonnegative immutable Delta version required')
        if not binding.get('snapshot_id') or not binding.get('manifest_sha256') or not re.fullmatch('[a-f0-9]{64}',binding['manifest_sha256']):
            raise ValueError('Snapshot identity and manifest SHA256 required')
        self.sha256 = binding_sha256(self.binding)

    def _read(self, family, columns, months):
        item = self.binding[family]
        sql = 'SELECT '+','.join('`'+identifier(c)+'`' for c in columns)+' FROM '+_table(item['table'])+' VERSION AS OF '+str(item['version'])
        if months is not None:
            if not months or any(not isinstance(m,str) or not re.fullmatch(r'\d{4}-(0[1-9]|1[0-2])',m) for m in months):
                raise ValueError('Explicit canonical signal months required')
            sql += ' WHERE signal_month IN ('+','.join("'"+m+"'" for m in sorted(set(months)))+')'
        frame = self.query(sql)
        if not isinstance(frame,pd.DataFrame) or list(frame) != list(columns):
            raise ValueError('SQL transport returned unexpected columns')
        _unique(frame,['security_id','signal_month'])
        if months is not None and set(frame.signal_month) - set(months): raise ValueError('Transport returned unrequested month')
        return frame.copy()

    def read(self, months=None, *, include_targets=False):
        requested=months if months is not None else self.binding.get('signal_months')
        if requested is not None:
            if not requested or any(not isinstance(m,str) or not re.fullmatch(r'\d{4}-(0[1-9]|1[0-2])',m) for m in requested):raise ValueError('Explicit canonical signal months required')
            requested=sorted(set(requested))
            if len(requested)>1:
                # Statement API INLINE is capped by response bytes. Bound each
                # transport to one month instead of truncating a wide history.
                result=pd.concat([self.read([month],include_targets=include_targets) for month in requested],ignore_index=True)
                _unique(result,['security_id','signal_month'])
                result.attrs['source_binding_sha256']=self.sha256
                result.attrs['source_provider']='databricks_gold'
                return result
            months=requested
        keys = ['security_id','signal_month']
        features = self.binding['feature_columns']
        values = self._read('features',keys+features,months)
        extras=self.binding.get('cohort_extra_columns',[])
        from .history import COHORT_CONTEXT_COLUMNS
        if len(extras)!=len(set(extras)) or set(extras)-{'historical_ticker',*COHORT_CONTEXT_COLUMNS}:raise ValueError('Unsupported cohort metadata')
        cohort = self._read('cohort',keys+['signal_date','ticker','sector']+extras,months)
        joined = cohort.merge(values,on=keys,how='outer',validate='one_to_one',indicator=True)
        if not joined._merge.eq('both').all(): raise ValueError('Gold feature/cohort key sets differ')
        joined = joined.drop(columns='_merge')
        joined['signal_date'] = pd.to_datetime(joined.signal_date,errors='raise')
        if joined.signal_date.dt.tz is not None or not joined.signal_date.dt.to_period('M').astype(str).eq(joined.signal_month).all():
            raise ValueError('Cohort signal date/month mismatch')
        for column in features: joined[column] = pd.to_numeric(joined[column],errors='raise')
        if include_targets:
            if 'targets' not in self.binding: raise ValueError('No explicit target binding')
            targets = self._read('targets',keys+['outcome_date','next_month_return','benchmark_return','target_top20','target_beat_voo'],months)
            audit = joined[keys].merge(targets[keys],on=keys,how='outer',indicator=True)
            if not audit._merge.eq('both').all(): raise ValueError('Gold target cohort differs')
            joined = joined.merge(targets,on=keys,how='left',validate='one_to_one')
        joined.attrs['source_binding_sha256'] = self.sha256
        joined.attrs['source_provider'] = 'databricks_gold'
        return joined.sort_values(['signal_month','security_id']).reset_index(drop=True)


class StatementQuery:
    """Databricks SDK Statement Execution with inline result chunk pagination.

    Auth uses the SDK's configured credentials. No tokens are handled here.
    Server result truncation fails rather than silently shortening a dataset.
    """
    def __init__(self, workspace_client, warehouse_id, *, max_rows=1000000):
        if not warehouse_id or max_rows < 1: raise ValueError('Warehouse and positive row bound required')
        self.client,self.warehouse_id,self.max_rows = workspace_client,warehouse_id,max_rows

    def __call__(self, sql):
        from databricks.sdk.service.sql import Disposition, Format, StatementState
        response = self.client.statement_execution.execute_statement(statement=sql,
            warehouse_id=self.warehouse_id,wait_timeout='50s',disposition=Disposition.INLINE,
            format=Format.JSON_ARRAY)
        # Let a slow query fail visibly; callers can inspect/retry the statement ID.
        if response.status.state != StatementState.SUCCEEDED:
            raise RuntimeError('Gold SQL not successful: '+str(response.status.state)+' statement '+str(response.statement_id))
        manifest = response.manifest
        if manifest.truncated or manifest.total_row_count > self.max_rows:
            raise ValueError('Gold SQL result truncated/exceeds safe row bound')
        columns = manifest.schema.columns
        chunks, chunk = [], response.result
        seen = set()
        while chunk is not None:
            if chunk.chunk_index in seen: raise ValueError('Repeated SQL result chunk')
            seen.add(chunk.chunk_index)
            chunks.extend(chunk.data_array or [])
            if len(chunks)>self.max_rows: raise ValueError('Gold SQL row bound exceeded')
            if chunk.next_chunk_index is None: break
            chunk = self.client.statement_execution.get_statement_result_chunk_n(response.statement_id, chunk.next_chunk_index)
        if len(chunks) != manifest.total_row_count: raise ValueError('Incomplete Gold SQL result')
        frame = pd.DataFrame(chunks,columns=[c.name for c in columns])
        for column in columns:
            kind = str(getattr(column.type_name,'value',column.type_name))
            if kind in {'DOUBLE','FLOAT','DECIMAL','INT','LONG','SHORT','BYTE'}:
                frame[column.name] = pd.to_numeric(frame[column.name],errors='raise')
            elif kind == 'DATE': frame[column.name] = pd.to_datetime(frame[column.name],errors='raise')
            elif kind == 'BOOLEAN':
                def boolean(value):
                    if value is None or isinstance(value,bool):return value
                    if value not in ('true','false','TRUE','FALSE'):raise ValueError('Malformed SQL boolean')
                    return value.lower()=='true'
                frame[column.name]=frame[column.name].map(boolean)
        return frame
