"""Bounded full-membership historical replay using the monthly production contract.

Legacy histories are revision uncertain. Replaying them never certifies original
filing vintage and never changes the eligibility universe based on outcomes.
"""
import hashlib
import json
import numpy as np
import pandas as pd
from .model_inputs import assemble_model_inputs
from .transforms import _unique

FAMILIES = {'population': ('sp500_monthly_population', 'week_end'),
            'technical': ('sp500_daily_technicals_ml', 'date'),
            'financial': ('sp500_monthly_fundamental_features', 'month_end'),
            'sector': ('sector_technicals_daily', 'date'),
            'macro': ('macro_cross_asset_features_daily', 'date')}
MODEL_CONTEXT_COLUMNS=[f+'_applicable' for f in ['debt_to_equity','debt_to_assets','net_debt_to_ebitda','interest_coverage','cash_to_assets','current_ratio','ocf_to_debt','equity_to_assets']]+['debt_free','nonpositive_equity','no_interest_expense']
from .fundamental_features import ALL_FACTORS
COHORT_CONTEXT_COLUMNS=[f+'_applicable' for f in ALL_FACTORS]+['debt_free','nonpositive_equity','no_interest_expense','growth_unavailable_negative_base','growth_unavailable_small_base']


def assemble_history(source_loader, signal_dates, feature_columns, *, as_of_utc,
                     sector_aliases=None, cutoff_loader=None):
    """Load only one signal's source rows at a time; return features, cohort, evidence.

    source_loader(family, ISO signal date) must filter exact dates, or the preceding
    seven days for macro. NYSE official closes supply cutoffs unless overridden.
    """
    import pandas_market_calendars as mcal
    dates = pd.DatetimeIndex(pd.to_datetime(list(signal_dates), errors='raise'))
    if dates.empty or dates.tz is not None or dates.has_duplicates or not dates.equals(dates.normalize()):
        raise ValueError('Unique nonempty exchange signal dates required')
    if dates.to_period('M').has_duplicates:
        raise ValueError('Only one signal per month')
    calendar = mcal.get_calendar('NYSE')
    features, cohorts, evidence = [], [], []
    for signal in dates.sort_values():
        period = signal.to_period('M')
        schedule = calendar.schedule(start_date=period.start_time, end_date=period.end_time)
        if schedule.empty or schedule.index[-1] != signal:
            raise ValueError('Signal is not final NYSE session: ' + str(signal.date()))
        cutoff = cutoff_loader(signal) if cutoff_loader else schedule.market_close.iloc[-1].isoformat()
        inputs = {family: source_loader(family, str(signal.date())) for family in FAMILIES}
        frame, proof = assemble_model_inputs(**inputs, signal_date=str(signal.date()),
            feature_columns=feature_columns, signal_cutoff_at=cutoff, as_of_utc=as_of_utc,
            mode='retrospective', sector_aliases=sector_aliases)
        member = inputs['population'][['security_id', 'ticker_latest', 'sector']].copy()
        member['historical_ticker']=inputs['population'].get('historical_ticker',pd.Series(None,index=member.index))
        context=inputs['financial'][['security_id']+[c for c in COHORT_CONTEXT_COLUMNS if c in inputs['financial']]].copy()
        member=member.merge(context,on='security_id',how='left',validate='one_to_one')
        for column in COHORT_CONTEXT_COLUMNS:
            if column not in member:member[column]=None
        member = member.rename(columns={'ticker_latest': 'ticker'})
        if sector_aliases: member['sector'] = member.sector.replace(sector_aliases)
        member['signal_date'], member['signal_month'] = signal, str(period)
        features.append(frame); cohorts.append(member); evidence.append(proof)
    panel = pd.concat(features, ignore_index=True)
    cohort = pd.concat(cohorts, ignore_index=True)
    _unique(panel, ['security_id', 'signal_month'])
    hashes = {e['signal_date']: hashlib.sha256(json.dumps(e['source_hashes'], sort_keys=True).encode()).hexdigest() for e in evidence}
    return panel, cohort, dict(months=len(evidence), rows=len(panel), source_hashes=hashes,
        monthly=evidence, original_vintage_certified=False,
        policy='FULL_MEMBERSHIP_NO_SILENT_DROPS', factor_scope='precomputed_input_assembly_only')


def historical_targets(cohort, stock_closes, benchmark_closes, *, as_of_utc):
    """Exact next NYSE-month prices; all members retained, unknown exits stay NULL.

    stock_closes grain security_id/date/adj_close; benchmark date/adj_close. Prices
    must be routed by reviewed stable identity before this function. Ties follow
    the existing descending-first rank after sorting ticker (then stable ID).
    """
    import pandas_market_calendars as mcal
    keys = ['security_id', 'signal_month']
    _unique(cohort, keys)
    p, b = stock_closes.copy(), benchmark_closes.copy()
    for frame in (p,b):
        frame['date'] = pd.to_datetime(frame.date, errors='raise')
        if frame.date.dt.tz is not None or not frame.date.equals(frame.date.dt.normalize()):
            raise ValueError('Exchange dates required')
        frame['adj_close'] = pd.to_numeric(frame.adj_close, errors='raise')
        if ((~np.isfinite(frame.adj_close) | frame.adj_close.le(0)) & frame.adj_close.notna()).any():
            raise ValueError('Positive finite or NULL prices required')
    _unique(p, ['security_id','date']); _unique(b, ['date'])
    asof = pd.Timestamp(as_of_utc)
    if pd.isna(asof) or asof.tzinfo is None: raise ValueError('Aware as_of required')
    out = cohort[keys + ['signal_date','ticker']].copy()
    out['signal_date'] = pd.to_datetime(out.signal_date)
    calendar = mcal.get_calendar('NYSE')
    exits = {}
    for month in out.signal_month.unique():
        period = pd.Period(month, freq='M') + 1
        schedule = calendar.schedule(start_date=period.start_time, end_date=period.end_time)
        exits[month] = schedule.index[-1] if schedule.market_close.iloc[-1] <= asof else pd.NaT
    out['outcome_date'] = out.signal_month.map(exits)
    for date, value in [('signal_date','signal_close'), ('outcome_date','exit_close')]:
        out = out.merge(p.rename(columns={'date':date,'adj_close':value})[['security_id',date,value]],
                        on=['security_id',date], how='left', validate='many_to_one')
    bench = b.set_index('date').adj_close
    out['next_month_return'] = out.exit_close / out.signal_close - 1
    out['benchmark_return'] = out.outcome_date.map(bench) / out.signal_date.map(bench) - 1
    out = out.sort_values(['signal_month','ticker','security_id']).reset_index(drop=True)
    out['target_top20'] = np.nan
    for _, group in out.groupby('signal_month', sort=False):
        valid = group.next_month_return.dropna()
        out.loc[valid.index,'target_top20'] = valid.rank(ascending=False,method='first').le(np.ceil(len(valid)*.2)).astype(float)
    out['target_beat_voo'] = np.nan
    valid = out.next_month_return.notna() & out.benchmark_return.notna()
    out.loc[valid,'target_beat_voo'] = out.loc[valid,'next_month_return'].gt(out.loc[valid,'benchmark_return']).astype(float)
    return out[keys + ['outcome_date','next_month_return','benchmark_return','target_top20','target_beat_voo']]


def audit_reference_cohort(features, reference, feature_columns):
    """Compare common keys without mistaking the old outcome-filtered cohort for truth."""
    keys = ['security_id','signal_month']
    _unique(features, keys); _unique(reference, keys)
    merged = features[keys].merge(reference[keys], on=keys, how='outer', indicator=True)
    from .reconcile import reconcile_frames
    common = merged.loc[merged._merge.eq('both'),keys]
    a = common.merge(features[keys+list(feature_columns)],on=keys,validate='one_to_one')
    b = common.merge(reference[keys+list(feature_columns)],on=keys,validate='one_to_one')
    return dict(common_rows=len(common), gold_only=int(merged._merge.eq('left_only').sum()),
                reference_only=int(merged._merge.eq('right_only').sum()),
                values=reconcile_frames(b,a,keys), cohort_policy='NO_OUTCOME_ELIGIBILITY_FILTER')
