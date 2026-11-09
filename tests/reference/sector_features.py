# Frozen pure source functions for synthetic parity tests.
def calculate(prices):
    px = prices.copy()
    px['date'] = pd.to_datetime(px.date).astype('datetime64[ns]')
    if px.duplicated(['date', 'proxy_ticker']).any():
        raise ValueError('Duplicate sector ETF prices')
    calendar = mcal.get_calendar('NYSE').valid_days(px.date.min(), px.date.max()).tz_localize(None)
    expected = set(PROXIES.values()) | {'SPY'}
    if set(px.proxy_ticker) != expected:
        raise ValueError('Missing/unknown ETF proxies')
    parts = []
    for ticker, g in px.groupby('proxy_ticker'):
        g = g.set_index('date').reindex(calendar).rename_axis('date')
        p = g.adj_close
        r = p.pct_change(fill_method=None)
        z = pd.DataFrame({'date': calendar, 'proxy_ticker': ticker, 'proxy_source_date': calendar})
        for n in [21, 63, 126, 252]:
            z[f'sector_return_{n}d'] = (p / p.shift(n) - 1).to_numpy()
        z['sector_momentum_12_1'] = (p.shift(21) / p.shift(252) - 1).to_numpy()
        for n in [21, 63]:
            z[f'sector_realized_vol_{n}d'] = (r.rolling(n, min_periods=n).std(ddof=1) * np.sqrt(252)).to_numpy()
        for n in [50, 200]:
            z[f'sector_price_to_sma{n}'] = (p / p.rolling(n, min_periods=n).mean() - 1).to_numpy()
        z['sector_drawdown_252d'] = (p / p.rolling(252, min_periods=252).max() - 1).to_numpy()
        z.loc[g.adj_close.isna().to_numpy(), 'proxy_source_date'] = pd.NaT
        parts.append(z)
    all_features = pd.concat(parts, ignore_index=True)
    market = all_features.loc[all_features.proxy_ticker.eq('SPY'), ['date'] + [f'sector_return_{n}d' for n in [21, 63, 126]]].rename(columns={f'sector_return_{n}d': f'market_return_{n}d' for n in [21, 63, 126]})
    out = all_features.loc[~all_features.proxy_ticker.eq('SPY')].merge(market, on='date', validate='many_to_one')
    out['sector'] = out.proxy_ticker.map({v: k for k, v in PROXIES.items()})
    for n in [21, 63, 126]:
        out[f'sector_excess_market_return_{n}d'] = out[f'sector_return_{n}d'] - out[f'market_return_{n}d']
    out['sector_strength_rank_63d'] = out.groupby('date').sector_return_63d.rank(method='average', pct=True)
    out = out[['date', 'sector', 'proxy_ticker', 'proxy_source_date'] + CONTEXT_FEATURES].sort_values(['date', 'sector']).reset_index(drop=True)
    assert not out.duplicated(['date', 'sector']).any()
    assert out.sector.nunique() == 11
    return out
