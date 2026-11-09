"""Portable assembly of already-computed PostgreSQL factor projections.

Join and relative-sector formulas follow production/monthly_capture.py and
sector_technical_features.join_frame. This is not factor-computation parity or
proof of historical vintage. No repository-local imports or I/O occur here.
"""
import hashlib
import json
import numpy as np
import pandas as pd
from .transforms import _unique, _dates, project_features, is_outcome_column

_DATE = {'population':'week_end','technical':'date','financial':'month_end','sector':'date','macro':'date'}
_CLOCKS = ('source_release_at','eligible_at','first_seen_at','ingested_at')


def _aware(value, name):
    parsed = pd.Timestamp(value)
    if pd.isna(parsed) or parsed.tzinfo is None:
        raise ValueError(name + ' requires an aware timestamp')
    return parsed.tz_convert('UTC')


def assemble_model_inputs(population, technical, financial, sector, macro, signal_date,
                          feature_columns, *, signal_cutoff_at, as_of_utc,
                          mode='retrospective', sector_aliases=None):
    """Return (full-population label-free frame, JSON-safe coverage/evidence).

    Missing source rows/features remain NULL. Duplicate grains, routing conflicts
    and known future clocks fail closed. Unknown legacy clocks are replay-only;
    strict mode requires observed_vintage on every supplied source row and all
    four knowledge clocks <= signal cutoff. Outcome columns in raw tables are
    ignored and never influence eligibility, feature values or lineage hashes.
    """
    signal = pd.Timestamp(signal_date)
    if pd.isna(signal) or signal.tzinfo is not None or signal != signal.normalize():
        raise ValueError('signal_date must be an exchange date')
    cutoff, asof = _aware(signal_cutoff_at,'signal_cutoff_at'), _aware(as_of_utc,'as_of_utc')
    if cutoff > asof or signal.date() > cutoff.date() or mode not in ('retrospective','strict'):
        raise ValueError('Invalid signal/cutoff/asof/mode')
    aliases = sector_aliases or {}
    frames, hashes, uncertain = {}, {}, []
    for family, raw in dict(population=population,technical=technical,financial=financial,sector=sector,macro=macro).items():
        f=raw.loc[:,[c for c in raw if not is_outcome_column(c)]].copy()
        if not f.empty:
            f=_dates(f,_DATE[family])
            dates=f[_DATE[family]]
            valid=dates.between(signal-pd.Timedelta(days=7),signal) if family=='macro' else dates.eq(signal)
            if not valid.all():raise ValueError('Stale/future source date: '+family)
            for column in f:
                if column.endswith('_source_date') or column.endswith('_fiscal_period_end'):
                    observed=pd.to_datetime(f[column],errors='raise')
                    if observed.gt(signal).any():raise ValueError('Future observation: '+family+'.'+column)
                if column in _CLOCKS or column.endswith('_available_at') or column=='feature_cutoff_at':
                    # A labeled retrospective replay may use a later observed
                    # vendor revision, but never a release after the signal or
                    # an observation after the declared replay as-of. Strict
                    # observed-vintage inputs require every clock at cutoff.
                    limit = asof if mode=='retrospective' and column == 'ingested_at' else cutoff
                    for value in f[column].dropna():
                        if _aware(value,column)>limit:raise ValueError('Future source clock: '+family+'.'+column)
            if family=='sector' and 'proxy_source_date' in f:
                if not pd.to_datetime(f.proxy_source_date).eq(signal).all():raise ValueError('Stale/missing sector proxy')
            verified=all(c in f and f[c].notna().all() for c in _CLOCKS)
            verified=verified and 'availability_quality' in f and f.availability_quality.eq('observed_vintage').all()
            verified=verified and all(all(_aware(v,c)<=cutoff for v in f[c].dropna()) for c in _CLOCKS if c in f)
            if not verified:uncertain.append(family)
            if mode=='strict' and not verified:raise ValueError('Unverified historical vintage: '+family)
            if 'sector' in f:f['sector']=f.sector.map(lambda value:aliases.get(value,value))
        if family=='macro' and not f.empty:
            # Reject duplicate daily rows before selecting the backward latest date.
            _unique(f,['date'])
            f=f.loc[f.date.eq(f.date.max())].copy()
        frames[family]=f
        ordered=f.reindex(sorted(f.columns),axis=1)
        # JSON preserves NULLs and column boundaries; delimiter joins can collide
        # and pandas nullable-string casts can leave non-string NaN sentinels.
        records=json.loads(ordered.to_json(orient='records',date_format='iso'))
        canonical=sorted(json.dumps(row,sort_keys=True,separators=(',',':'),allow_nan=False) for row in records)
        hashed_payload={'columns':list(ordered.columns),'rows':canonical}
        hashes[family]=hashlib.sha256(json.dumps(hashed_payload,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
    member=frames['population']
    if member.empty or not {'security_id','ticker_latest','sector'}<=set(member):raise ValueError('Missing reviewed population identity')
    _unique(member,['security_id'])
    _unique(member,['ticker_latest'])
    result=member[['security_id','ticker_latest','sector']].copy()
    missing={}
    metadata={'security_id','ticker_latest','historical_ticker','sector','date','week_end','month_end','signal_date','signal_month',*_CLOCKS,'availability_quality'}
    owners={}
    # Explicit source feature ownership prevents silent suffix/coalesce precedence.
    for family in ('technical','financial','sector','macro'):
        for column in frames[family]:
            if column in metadata or column.endswith(('_available_at','_source_date','_fiscal_period_end')) or column=='feature_cutoff_at':continue
            if column in feature_columns:
                if column in owners:raise ValueError('Ambiguous feature ownership: '+column)
                owners[column]=family
    for family in ('technical','financial','sector'):
        source=frames[family]
        key='sector' if family=='sector' else 'security_id' if 'security_id' in source or family=='financial' else 'ticker_latest'
        if source.empty:
            missing[family]=result.security_id.tolist()
            continue
        _unique(source,[key])
        if key=='security_id' and 'ticker_latest' in source:
            routed=result[['security_id','ticker_latest']].merge(source[['security_id','ticker_latest']],on='security_id',suffixes=('_member','_source'),validate='one_to_one')
            if not routed.ticker_latest_member.eq(routed.ticker_latest_source).all():raise ValueError('Security/ticker route mismatch: '+family)
        elif family=='financial':raise ValueError('Financial source requires reviewed ticker route')
        missing[family]=result.loc[~result[key].isin(source[key]),'security_id'].tolist()
        cols=[c for c,owner in owners.items() if owner==family]
        # Relative factors need their actual precomputed inputs, even if not output.
        deps={'technical':['return_21d','return_63d','realized_vol_63d'],'sector':['sector_return_21d','sector_return_63d','sector_realized_vol_63d']}.get(family,[])
        cols=list(dict.fromkeys(cols+[c for c in deps if c in source]))
        result=result.merge(source[[key]+cols],on=key,how='left',validate='many_to_one' if family=='sector' else 'one_to_one')
    macro_frame=frames['macro']
    missing['macro']=result.security_id.tolist() if macro_frame.empty else []
    macro_values={column:macro_frame.iloc[0][column] if not macro_frame.empty else np.nan for column,owner in owners.items() if owner=='macro'}
    if macro_values:
        result=pd.concat([result,pd.DataFrame({k:[v]*len(result) for k,v in macro_values.items()},index=result.index)],axis=1)
    # These three exact formulas are the assembly calculations in the existing
    # production materializer; no other source factors are recomputed here.
    for horizon in (21,63):
        target=f'stock_excess_sector_return_{horizon}d'
        a,b=f'return_{horizon}d',f'sector_return_{horizon}d'
        if target in feature_columns and a in result and b in result:result[target]=pd.to_numeric(result[a])-pd.to_numeric(result[b])
    if 'stock_to_sector_vol_ratio_63d' in feature_columns and {'realized_vol_63d','sector_realized_vol_63d'}<=set(result):
        result['stock_to_sector_vol_ratio_63d']=pd.to_numeric(result.realized_vol_63d)/pd.to_numeric(result.sector_realized_vol_63d).replace(0,np.nan)
    for column in feature_columns:
        if column not in result:result[column]=np.nan
        result[column]=pd.to_numeric(result[column],errors='raise').replace([np.inf,-np.inf],np.nan)
    result=result.copy()
    result['signal_month']=str(signal.to_period('M'))
    result=project_features(result,feature_columns).sort_values('security_id').reset_index(drop=True)
    if set(result.security_id)!=set(member.security_id):raise ValueError('Population changed during assembly')
    evidence=dict(signal_date=str(signal.date()),signal_cutoff_at=cutoff.isoformat(),as_of_utc=asof.isoformat(),
                  population_count=len(member),materialized_count=len(result),source_hashes=hashes,
                  missing_sources=missing,component_row_counts={k:len(v) for k,v in frames.items()},
                  availability_quality='UNVERIFIED_VINTAGE' if uncertain else 'observed_vintage',
                  unverified_components=uncertain,original_vintage_certified=False,
                  missing_outcomes_affect_predictor_eligibility=False,
                  policy='FULL_MEMBERSHIP_NO_SILENT_DROPS',factor_scope='precomputed_input_assembly_only',
                  field_coverage={c:{'present':int(result[c].notna().sum()),'missing':int(result[c].isna().sum())} for c in feature_columns})
    json.dumps(evidence,allow_nan=False)
    return result,evidence
