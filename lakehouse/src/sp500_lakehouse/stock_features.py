"""Original observed-row stock formulas, vendored without notebook I/O."""
import numpy as np
import pandas as pd
ORIGINAL_SOURCE_SHA256 = '2b89bb38837019c9c826890ddc36bbe3f06576b363cab0455e1d12573a586fbc'
FEATURE_COLUMNS = ['return_5d', 'return_21d', 'return_63d', 'return_126d', 'return_252d', 'momentum_12_1', 'momentum_acceleration', 'reversal_5d', 'reversal_21d', 'realized_vol_21d', 'realized_vol_63d', 'downside_vol_63d', 'vol_ratio_21_63', 'return_skew_63d', 'return_kurtosis_63d', 'max_drawdown_63d', 'max_drawdown_252d', 'ulcer_index_63d', 'price_to_sma20', 'price_to_sma50', 'price_to_sma200', 'sma50_to_sma200', 'trend_r2_63d', 'price_position_252d', 'relative_volume_20d', 'volume_trend_21_63', 'signed_volume_pressure_21d', 'return_volume_corr_63d', 'log_dollar_volume_21d', 'amihud_illiquidity_21d']
KEY_COLUMNS = ['date', 'ticker_latest']

def normalize_keys(frame):
    frame = frame.copy()
    frame['date'] = pd.to_datetime(frame['date'], errors='raise')
    if frame['date'].dt.tz is not None:
        raise ValueError('date must be timezone-naive daily dates')
    if (frame['date'].dropna() != frame['date'].dropna().dt.normalize()).any():
        raise ValueError('date must contain daily dates, without intraday times')
    frame['ticker_latest'] = frame['ticker_latest'].astype('string').str.strip().str.upper()
    if frame[KEY_COLUMNS].isna().any().any() or frame['ticker_latest'].eq('').any():
        raise ValueError('Null/empty date or ticker_latest key')
    if frame.duplicated(KEY_COLUMNS).any():
        raise ValueError('Duplicate (date, ticker_latest) keys; resolve source rows before calculation/load')
    return frame.sort_values(['ticker_latest', 'date']).reset_index(drop=True)

def add_technical_features(df, reset_boundaries=None):
    required = {*KEY_COLUMNS, 'adj_close', 'volume'}
    if required - set(df.columns):
        raise KeyError(f'Missing input columns: {sorted(required - set(df.columns))}')
    data = normalize_keys(df[list(KEY_COLUMNS) + ['adj_close', 'volume']])
    for col in ['adj_close', 'volume']:
        data[col] = pd.to_numeric(data[col], errors='raise').astype(float)
        if np.isinf(data[col]).any():
            raise ValueError(f'Infinite {col}')
    if (data['adj_close'] <= 0).any() or (data['volume'] < 0).any():
        raise ValueError('Prices must be positive and volume nonnegative (or missing)')

    def safe_div(num, den):
        return num / den.replace(0, np.nan)

    def drawdown(values):
        return values / np.maximum.accumulate(values) - 1.0

    def trend_r2(values):
        y = np.log(values)
        if np.ptp(y) == 0:
            return np.nan
        y = y - y.mean()
        x = np.arange(len(y), dtype=float)
        x -= x.mean()
        ss_y = np.dot(y, y)
        if ss_y <= np.finfo(float).eps ** 2:
            return np.nan
        return np.clip(np.dot(x, y) ** 2 / (np.dot(x, x) * ss_y), 0, 1)
    data['_identity_segment'] = 0
    for ticker, boundaries in (reset_boundaries or {}).items():
        mask = data.ticker_latest.eq(ticker)
        data.loc[mask, '_identity_segment'] = np.searchsorted(np.array(boundaries, dtype='datetime64[ns]'), data.loc[mask, 'date'].to_numpy(dtype='datetime64[ns]'), side='right')
    parts = []
    for ticker, g in data.groupby(['ticker_latest', '_identity_segment'], sort=False):
        p, v = (g['adj_close'], g['volume'])
        r = p.pct_change(fill_method=None)
        out = g[KEY_COLUMNS].copy()
        for w in [5, 21, 63, 126, 252]:
            out[f'return_{w}d'] = p / p.shift(w) - 1
        out['momentum_12_1'] = p.shift(21) / p.shift(252) - 1
        out['momentum_acceleration'] = out['return_21d'] - out['return_21d'].shift(21)
        out['reversal_5d'] = -out['return_5d']
        out['reversal_21d'] = -out['return_21d']
        for w in [21, 63]:
            out[f'realized_vol_{w}d'] = r.rolling(w, min_periods=w).std(ddof=1) * np.sqrt(252)
        out['downside_vol_63d'] = np.sqrt(252 * r.clip(upper=0).pow(2).rolling(63).mean())
        out['vol_ratio_21_63'] = safe_div(out['realized_vol_21d'], out['realized_vol_63d'])
        out['return_skew_63d'] = r.rolling(63).skew()
        out['return_kurtosis_63d'] = r.rolling(63).kurt()
        for w in [63, 252]:
            out[f'max_drawdown_{w}d'] = p.rolling(w).apply(lambda a: drawdown(a).min(), raw=True)
        out['ulcer_index_63d'] = p.rolling(63).apply(lambda a: np.sqrt(np.mean((100 * drawdown(a)) ** 2)), raw=True)
        smas = {w: p.rolling(w).mean() for w in [20, 50, 200]}
        for w, sma in smas.items():
            out[f'price_to_sma{w}'] = p / sma - 1
        out['sma50_to_sma200'] = smas[50] / smas[200] - 1
        out['trend_r2_63d'] = p.rolling(63).apply(trend_r2, raw=True)
        lo, hi = (p.rolling(252).min(), p.rolling(252).max())
        out['price_position_252d'] = safe_div(p - lo, hi - lo)
        out['relative_volume_20d'] = safe_div(v, v.rolling(20).mean())
        out['volume_trend_21_63'] = safe_div(v.rolling(21).mean(), v.rolling(63).mean()) - 1
        out['signed_volume_pressure_21d'] = safe_div((np.sign(r) * v).rolling(21).sum(), v.rolling(21).sum())
        out['return_volume_corr_63d'] = r.rolling(63).corr(v)
        dollar_volume = p * v
        out['log_dollar_volume_21d'] = np.log1p(dollar_volume.rolling(21).mean())
        out['amihud_illiquidity_21d'] = safe_div(r.abs(), dollar_volume).rolling(21).mean()
        parts.append(out[KEY_COLUMNS + FEATURE_COLUMNS])
    result = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=KEY_COLUMNS + FEATURE_COLUMNS)
    result[FEATURE_COLUMNS] = result[FEATURE_COLUMNS].replace([np.inf, -np.inf], np.nan)
    return result

def from_prices(prices):
    from .transforms import _unique
    _unique(prices,['security_id','date'])
    data=prices[['security_id','date','adj_close','volume']].copy()
    identities=list(data.security_id.unique())
    tokens={sid:str(i) for i,sid in enumerate(identities)}
    data['ticker_latest']=data.security_id.map(tokens)
    out=add_technical_features(data)
    out['security_id']=out.ticker_latest.map({v:k for k,v in tokens.items()})
    return out.drop(columns='ticker_latest')
