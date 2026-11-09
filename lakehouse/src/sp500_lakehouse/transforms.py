"""Pure pandas reference transforms. These do not certify legacy feature parity."""
import re
import numpy as np
import pandas as pd


def is_outcome_column(column):
    return bool(re.search(r'target|label|fwd|forward|outcome|next_|beats_|benchmark|actual_return|realized_return|top_quintile|ret_week', str(column), re.I))


def _unique(frame, keys):
    if frame[keys].isna().any().any() or frame.duplicated(keys).any():
        raise ValueError(f'Null or duplicate keys: {keys}')


def _dates(frame, column='date'):
    result = frame.copy()
    result[column] = pd.to_datetime(result[column], errors='raise')
    if result[column].dt.tz is not None:
        raise ValueError('Session dates must be timezone-naive exchange dates')
    if not result[column].equals(result[column].dt.normalize()):
        raise ValueError('Intraday session date')
    return result


def _valid_prices(frame):
    values = pd.to_numeric(frame.adj_close, errors='raise')
    if ((~np.isfinite(values) | values.le(0)) & values.notna()).any():
        raise ValueError('Adjusted prices must be positive finite or NULL')


def month_sessions(sessions):
    """Caller supplies a complete exchange schedule, not observed price dates."""
    s = _dates(sessions, 'session_date')
    _unique(s, ['session_date'])
    if any(pd.notna(v) and pd.Timestamp(v).tzinfo is None for v in s.close_at):
        raise ValueError('Exchange closes must include timezone')
    s['close_at'] = pd.to_datetime(s.close_at, utc=True, errors='raise')
    if s.close_at.isna().any():
        raise ValueError('Missing exchange close')
    s['signal_month'] = s.session_date.dt.to_period('M').astype(str)
    return s.sort_values('session_date').groupby('signal_month', as_index=False).tail(1)


def monthly_cohort(membership, prices, sessions, signal_months=None, as_of=None):
    """Membership at exact final session; missing prices remain auditable rows."""
    m, p = _dates(membership), _dates(prices)
    _valid_prices(p)
    _unique(m, ['security_id', 'date'])
    _unique(p, ['security_id', 'date'])
    if not m.is_member.map(lambda v: isinstance(v, (bool, np.bool_))).all():
        raise ValueError('Membership must be reviewed boolean')
    ends = month_sessions(sessions)
    if signal_months is not None:
        wanted = set(signal_months)
        if not wanted.issubset(set(ends.signal_month)):
            raise ValueError('Missing calendar month')
        ends = ends[ends.signal_month.isin(wanted)]
    # An observed/incomplete schedule must not turn a midmonth date into month-end.
    import pandas_market_calendars as mcal
    exchange = mcal.get_calendar('NYSE')
    if as_of is not None:
        as_of = pd.Timestamp(as_of)
        if as_of.tzinfo is None:
            raise ValueError('as_of must include timezone')
    for _, end in ends.iterrows():
        period = pd.Period(end.signal_month, freq='M')
        official = exchange.schedule(start_date=period.start_time, end_date=period.end_time)
        if official.empty or end.session_date != official.index[-1] or end.close_at != official.market_close.iloc[-1]:
            raise ValueError('Incomplete or incorrect NYSE month-end calendar')
        if as_of is not None and end.close_at > as_of:
            raise ValueError('Signal month has not closed as of cutoff')
    out = m[m.is_member.eq(True)].merge(ends, left_on='date', right_on='session_date', validate='many_to_one')
    out = out.rename(columns={'close_at': 'signal_at'})
    out = out.merge(p[['security_id', 'date', 'adj_close']], on=['security_id', 'date'], how='left', validate='one_to_one')
    out['price_missing'] = out.adj_close.isna()
    _unique(out, ['security_id', 'signal_month'])
    return out.sort_values(['signal_month', 'security_id']).reset_index(drop=True)


def exploratory_technicals(prices, sessions, window=21):
    """Exploratory only: session-aligned adjusted-price momentum and volatility."""
    if window < 2:
        raise ValueError('window must be >= 2')
    p = _dates(prices)
    _valid_prices(p)
    _unique(p, ['security_id', 'date'])
    calendar = _dates(sessions, 'session_date').session_date.sort_values()
    _unique(pd.DataFrame({'date': calendar}), ['date'])
    parts = []
    for security, group in p.groupby('security_id', sort=True):
        z = group.set_index('date')[['adj_close']].reindex(calendar).rename_axis('date')
        z['momentum'] = z.adj_close / z.adj_close.shift(window) - 1
        z['volatility'] = z.adj_close.pct_change(fill_method=None).rolling(window, min_periods=window).std(ddof=1) * np.sqrt(252)
        z['security_id'] = security
        z['feature_status'] = 'exploratory_not_legacy_parity'
        parts.append(z.reset_index())
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()


def monthly_targets(cohort, prices, benchmark_prices, sessions):
    """Separate outcomes: exact next calendar month close, never shift over gaps."""
    _unique(cohort, ['security_id', 'signal_month'])
    p, b = _dates(prices), _dates(benchmark_prices)
    _valid_prices(p)
    _valid_prices(b)
    _unique(p, ['security_id', 'date'])
    _unique(b, ['date'])
    # A partially observed following month is immature, never a shorter holding.
    import pandas_market_calendars as mcal
    exchange = mcal.get_calendar('NYSE')
    eligible_ends = []
    for _, candidate in month_sessions(sessions).iterrows():
        period = pd.Period(candidate.signal_month, freq='M')
        official = exchange.schedule(start_date=period.start_time, end_date=period.end_time)
        if not official.empty and candidate.session_date == official.index[-1] and candidate.close_at == official.market_close.iloc[-1]:
            eligible_ends.append(candidate)
    ends = pd.Series({row.signal_month: row.session_date for row in eligible_ends}, dtype='datetime64[ns]')
    out = cohort[['security_id', 'signal_month', 'date', 'adj_close']].copy()
    out['next_month'] = (pd.PeriodIndex(out.signal_month, freq='M') + 1).astype(str)
    out['outcome_date'] = out.next_month.map(ends)
    out = out.merge(p[['security_id', 'date', 'adj_close']].rename(columns={'date': 'outcome_date', 'adj_close': 'next_close'}), on=['security_id', 'outcome_date'], how='left', validate='many_to_one')
    benchmark = b.set_index('date').adj_close
    out['ret_month_fwd1'] = out.next_close / out.adj_close.where(out.adj_close.gt(0)) - 1
    out['benchmark_fwd1'] = out.outcome_date.map(benchmark) / out.date.map(benchmark).where(out.date.map(benchmark).gt(0)) - 1
    valid = out.ret_month_fwd1.notna() & out.benchmark_fwd1.notna()
    out['beats_benchmark'] = pd.Series(pd.NA, index=out.index, dtype='boolean')
    out.loc[valid, 'beats_benchmark'] = out.loc[valid, 'ret_month_fwd1'].gt(out.loc[valid, 'benchmark_fwd1'])
    return out.drop(columns=['adj_close', 'next_close'])


def asof_records(cohort, records):
    """Strict observed-vintage selection. Reconstructed uncertain rows excluded.

    Records grain is security/period_end/revision. All three knowledge clocks
    must be known and <= signal time; period-end alone never grants eligibility.
    """
    _unique(cohort, ['security_id', 'signal_month'])
    r = records.copy()
    _unique(r, ['security_id', 'period_end', 'source_revision'])
    clocks = ['eligible_at', 'source_release_at', 'first_seen_at', 'ingested_at']
    for c in clocks:
        if any(pd.notna(v) and pd.Timestamp(v).tzinfo is None for v in r[c]):
            raise ValueError('Knowledge timestamps must include timezone')
        r[c] = pd.to_datetime(r[c], utc=True, errors='raise')
    r['period_end'] = pd.to_datetime(r.period_end)
    rows = []
    for _, signal in cohort.iterrows():
        cutoff = pd.Timestamp(signal.signal_at)
        if cutoff.tzinfo is None:
            raise ValueError('signal_at must include timezone')
        available = r[r.security_id.eq(signal.security_id)].copy()
        for c in clocks:
            available = available[available[c].notna() & available[c].le(cutoff)]
        available = available[available.availability_quality.eq('observed_vintage') & available.period_end.le(cutoff.tz_localize(None))]
        row = {'security_id': signal.security_id, 'signal_month': signal.signal_month}
        if not available.empty:
            selected = available.sort_values(['period_end', 'eligible_at', 'first_seen_at', 'source_revision']).iloc[-1]
            row.update({k: v for k, v in selected.items() if k != 'security_id'})
        rows.append(row)
    return pd.DataFrame(rows)


def project_features(frame, feature_columns):
    """An explicit allowlist is mandatory; outcome-like names fail closed."""
    keys = ['security_id', 'signal_month']
    if not feature_columns or len(set(feature_columns)) != len(feature_columns):
        raise ValueError('Unique nonempty predictor allowlist required')
    if any(is_outcome_column(c) or c in keys for c in feature_columns):
        raise ValueError('Outcome/identifier in predictor allowlist')
    _unique(frame, keys)
    return frame[keys + list(feature_columns)].copy()
