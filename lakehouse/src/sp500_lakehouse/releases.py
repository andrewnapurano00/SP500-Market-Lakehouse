"""Immutable full-history releases from a pinned parent and recomputed month."""
import json
import pandas as pd
from .config import identifier
from .reader import binding_sha256,_table
from .delta import publish_gold_snapshot,validate_snapshot_contract
from .history import historical_targets,COHORT_CONTEXT_COLUMNS
from .spark_frames import pandas_to_spark

def read_bound(spark,binding,family):
    item=binding[family]
    if isinstance(item['version'],bool) or not isinstance(item['version'],int) or item['version']<0:raise ValueError('Pinned parent Delta version required')
    return spark.sql('SELECT * FROM '+_table(item['table'])+' VERSION AS OF '+str(item['version']))

def preserve_known_targets(targets, anchor, cohort):
    """Keep known returns on their original adjustment basis; rank the full cohort."""
    import numpy as np
    keys=['security_id','signal_month']
    for frame in [targets,anchor,cohort]:
        if frame.duplicated(keys).any():raise ValueError('Duplicate target/cohort keys')
    out=targets.set_index(keys).copy();old=anchor.set_index(keys)
    for column in ['next_month_return','benchmark_return']:
        known=old[column].dropna();overlap=out.index.intersection(known.index)
        out.loc[overlap,column]=known.reindex(overlap).to_numpy()
    out=out.reset_index()
    benchmarks=anchor.loc[anchor.benchmark_return.notna(),['signal_month','benchmark_return']].drop_duplicates()
    if benchmarks.signal_month.duplicated().any():raise ValueError('Conflicting anchor benchmark within month')
    monthly_benchmark=out.signal_month.map(benchmarks.set_index('signal_month').benchmark_return)
    out.loc[monthly_benchmark.notna(),'benchmark_return']=monthly_benchmark.dropna().to_numpy()
    out=out.merge(cohort[keys+['ticker']],on=keys,validate='one_to_one')
    out=out.sort_values(['signal_month','ticker','security_id']).reset_index(drop=True)
    out['target_top20']=np.nan
    for _,group in out.groupby('signal_month',sort=False):
        valid=group.next_month_return.dropna()
        out.loc[valid.index,'target_top20']=valid.rank(ascending=False,method='first').le(np.ceil(len(valid)*.2)).astype(float)
    out['target_beat_voo']=np.nan
    valid=out.next_month_return.notna()&out.benchmark_return.notna()
    out.loc[valid,'target_beat_voo']=out.loc[valid,'next_month_return'].gt(out.loc[valid,'benchmark_return']).astype(float)
    return out.drop(columns='ticker')


def publish_release(spark,cfg,*,panel,cohort,stock_closes,benchmark_closes,parent,
                    snapshot_id,manifest,historical_context=None):
    from pyspark.sql import functions as F
    columns=['security_id','signal_month']+manifest['feature_columns']
    if manifest['feature_columns']!=parent['feature_columns']:raise ValueError('Parent predictor contract changed')
    properties={r.key:r.value for r in spark.sql('SHOW TBLPROPERTIES '+_table(parent['features']['table'])).collect()}
    parent_manifest=json.loads(properties.get('sp500.snapshot_manifest','{}'))
    if not parent_manifest.get('as_of') or pd.Timestamp(parent_manifest['as_of'])>pd.Timestamp(manifest['as_of']):raise ValueError('Parent release exceeds publication as-of')
    months=sorted(panel.signal_month.unique())
    incoming=pandas_to_spark(spark,cfg,panel[columns])
    previous=read_bound(spark,parent,'features').select(*columns)
    full=previous.where(~F.col('signal_month').isin(months)).unionByName(incoming)
    old_cohort=read_bound(spark,parent,'cohort')
    missing=set(cohort)-set(old_cohort.columns)
    if missing:
        if historical_context is None or missing-set(COHORT_CONTEXT_COLUMNS):raise ValueError('Parent context schema upgrade lacks evidence')
        old_cohort=old_cohort.join(historical_context.select('security_id','signal_month',*sorted(missing)),on=['security_id','signal_month'],how='left')
    if set(cohort)!=set(old_cohort.columns):raise ValueError('Parent cohort schema changed')
    full_cohort=old_cohort.where(~F.col('signal_month').isin(months)).unionByName(pandas_to_spark(spark,cfg,cohort).select(*old_cohort.columns))
    all_members=full_cohort.toPandas()
    targets=historical_targets(all_members,stock_closes,benchmark_closes,as_of_utc=manifest['as_of'])
    targets=preserve_known_targets(targets,read_bound(spark,parent,'targets').toPandas(),all_members)
    manifest=dict(manifest,parent_binding_sha256=binding_sha256(parent),target_policy='preserve_known_returns_v2')
    manifest['source_hashes']=dict(manifest['source_hashes'],parent_binding=binding_sha256(parent))
    table=publish_gold_snapshot(spark,cfg,full,snapshot_id,manifest)
    digest=validate_snapshot_contract(columns,manifest)
    def side(frame,kind):
        target=cfg.table('gold',kind+'_'+identifier(snapshot_id))
        if frame.where('security_id IS NULL OR signal_month IS NULL').limit(1).count() or frame.groupBy('security_id','signal_month').count().where('count>1').limit(1).count():raise ValueError('Invalid release side keys')
        if spark.catalog.tableExists(target):
            props={r.key:r.value for r in spark.sql('SHOW TBLPROPERTIES '+target).collect()}
            old=spark.table(target)
            if props.get('sp500.manifest_sha256')!=digest or set(old.columns)!=set(frame.columns):raise FileExistsError('Conflicting release side manifest')
            if old.select(*frame.columns).exceptAll(frame).limit(1).count() or frame.exceptAll(old.select(*frame.columns)).limit(1).count():raise FileExistsError('Conflicting release side rows')
        else:frame.writeTo(target).using('delta').tableProperty('delta.appendOnly','true').tableProperty('sp500.manifest_sha256',digest).create()
        return dict(table=target,version=int(spark.sql('DESCRIBE HISTORY '+target).select('version').first()[0]))
    binding=dict(snapshot_id=snapshot_id,manifest_sha256=digest,feature_columns=manifest['feature_columns'],
        as_of=manifest['as_of'],
        signal_months=sorted(all_members.signal_month.unique()),cohort_extra_columns=['historical_ticker']+COHORT_CONTEXT_COLUMNS,
        features=dict(table=table,version=int(spark.sql('DESCRIBE HISTORY '+table).select('version').first()[0])),
        cohort=side(full_cohort,'cohort'),targets=side(pandas_to_spark(spark,cfg,targets),'targets'))
    return dict(binding=binding,rows=len(all_members),months=len(binding['signal_months']),
        known_outcomes=int(targets.next_month_return.notna().sum()),unknown_outcomes=int(targets.next_month_return.isna().sum()),cutover_approved=False)
