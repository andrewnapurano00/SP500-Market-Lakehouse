"""Portable original macro formulas; explicit one-business-day availability assumption."""
import json
import numpy as np
import pandas as pd
SOURCE_PATH = 'sp_macro_cross_asset_features.ipynb'
SOURCE_SHA256 = 'a9ef016766fe91e98458209c1235c3c27fdf8286a7299adb31e81a16379dd5fd'
SYMBOLS = dict(market='SPY', oil='USO', gold='GLD', dollar='UUP', treasury_intermediate='IEF', treasury_long='TLT', high_yield='HYG', investment_grade='LQD', volatility_proxy='VIXY')
RATE_FIELDS = dict(treasury_3m='month3', treasury_2y='year2', treasury_10y='year10', treasury_30y='year30')

def build_features(observations):
    if observations.duplicated(['series', 'date']).any():
        raise ValueError('Duplicate source keys')
    calendar = observations.loc[observations.series.eq('market'), ['date']].sort_values('date').copy()
    result = calendar.reset_index(drop=True)
    for name, g in observations.groupby('series', sort=True):
        g = g.sort_values('date').reset_index(drop=True)
        value = g.value
        f = g[['date']].copy()
        f[name + '_source_date'] = g.observation_date
        if name == 'vix':
            f['vix_level'] = value
            for window in [1, 5, 21, 63]:
                f[f'vix_change_{window}d_points'] = value.diff(window)
                f[f'vix_change_{window}d_fraction'] = value.pct_change(window, fill_method=None)
            for window in [21, 63]:
                f[f'vix_mean_{window}d'] = value.rolling(window).mean()
                f[f'vix_vs_mean_{window}d'] = value / value.rolling(window).mean() - 1
            f['vix_percentile_252d'] = value.rolling(252).rank(pct=True)
        elif name in RATE_FIELDS:
            f[name + '_yield_pct'] = value
            for window in [21, 63]:
                f[f'{name}_change_{window}d_bp'] = value.diff(window) * 100
        else:
            f[name + '_adj_close'] = value
            for window in [21, 63, 126, 252]:
                f[f'{name}_return_{window}d'] = value.pct_change(window, fill_method=None)
            daily = value.pct_change(fill_method=None)
            for window in [21, 63]:
                f[f'{name}_realized_vol_{window}d'] = daily.rolling(window).std(ddof=1) * np.sqrt(252)
            f[name + '_price_to_sma200'] = value / value.rolling(200).mean() - 1
            f[name + '_drawdown_252d'] = value / value.rolling(252).max() - 1
        result = pd.merge_asof(result.sort_values('date'), f.sort_values('date'), on='date', direction='backward', tolerance=pd.Timedelta(days=7))
    result = result.copy()
    result['curve_10y_2y_pp'] = result.treasury_10y_yield_pct - result.treasury_2y_yield_pct
    result['curve_10y_3m_pp'] = result.treasury_10y_yield_pct - result.treasury_3m_yield_pct
    for window in [21, 63]:
        result[f'credit_hyg_minus_lqd_return_{window}d'] = result[f'high_yield_return_{window}d'] - result[f'investment_grade_return_{window}d']
        result[f'gold_minus_oil_return_{window}d'] = result[f'gold_return_{window}d'] - result[f'oil_return_{window}d']
    return result.replace([np.inf, -np.inf], np.nan)

def feature_unit(column):
    if column == 'date':
        return 'assumed availability date'
    if column.endswith('_source_date'):
        return 'source observation date'
    if column == 'vix_level' or column.endswith('_points') or column in ['vix_mean_21d', 'vix_mean_63d']:
        return 'VIX index points'
    if column.endswith('_bp'):
        return 'basis points'
    if column.endswith('_pct') or column.endswith('_pp'):
        return 'percentage points'
    if column.endswith('_adj_close'):
        return 'adjusted ETF price (source units)'
    return 'fraction (annualized for realized volatility)'


def normalized_observations(frame, *, run_id, row_cap=10000):
    """Original macro observation projection from one explicit capture run."""
    frame=frame.loc[frame.run_id.eq(run_id) & frame.entity.isin(['macro_prices','vix','treasury'])].copy()
    output=[]
    symbol_to_name={v:k for k,v in SYMBOLS.items()}
    for _,row in frame.iterrows():
        values=json.loads(row['values']) if isinstance(row['values'],str) else row['values']
        day=pd.Timestamp(row.observation_date).normalize()
        if row.entity=='treasury':
            points=[(name,values.get(field)) for name,field in RATE_FIELDS.items()]
        elif row.entity=='vix':
            points=[('vix',values.get('close'))]
        else:
            if row.api_lookup_ticker not in symbol_to_name:
                raise ValueError('Unknown macro ETF')
            points=[(symbol_to_name[row.api_lookup_ticker],values.get('adjclose'))]
        for series,value in points:
            output.append(dict(series=series,observation_date=day,date=day+pd.offsets.BDay(1),value=value))
    result=pd.DataFrame(output)
    if result.empty or (result.groupby('series').size()>row_cap).any():
        raise ValueError('Empty macro data or per-series compute cap exceeded')
    result=result.drop_duplicates()
    if result.duplicated(['series','date']).any():
        raise ValueError('Conflicting macro observations within explicit run')
    if set(result.series)!=set(SYMBOLS)|set(RATE_FIELDS)|{'vix'}:
        raise ValueError('Missing required macro series')
    counts=result.groupby('series').size()
    reference=int(counts['market'])
    if counts['vix'] < .95*reference or any(counts[name] < .85*reference for name in RATE_FIELDS):
        raise ValueError('Sparse VIX/Treasury coverage relative to market')
    result['value']=pd.to_numeric(result.value,errors='raise')
    if result.value.isna().any() or not np.isfinite(result.value).all():
        raise ValueError('Missing/nonfinite macro values')
    if result.loc[~result.series.isin(RATE_FIELDS),'value'].le(0).any():
        raise ValueError('Invalid macro price/index level')
    return result.sort_values(['series','date']).reset_index(drop=True)


def from_observations(frame, *, run_id, row_cap=10000):
    return build_features(normalized_observations(frame,run_id=run_id,row_cap=row_cap))
