# Frozen pure source functions for synthetic parity tests.
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
