"""Original factor recomputation from an explicit baseline and capture run.

No SQL, network calls or implicit latest revision selection. Baseline frames are
immutable inputs. Fresh observations supersede matching business dates only in
this new materialization, leaving prior snapshots unchanged.
"""
import json
import hashlib
import pandas as pd
from . import fundamental_features as fundamentals
from .stock_features import from_prices
from .sector_features import calculate, PROXIES
from .macro_features import build_features, normalized_observations

def overlay(baseline,fresh,keys):
    if baseline.duplicated(keys).any() or fresh.duplicated(keys).any():
        raise ValueError('Ambiguous baseline/capture business keys')
    if fresh.empty:return baseline.copy()
    return pd.concat([baseline,fresh],ignore_index=True).drop_duplicates(keys,keep='last').reset_index(drop=True)

def signal_macro_window(frame,signal_date):
    signal=pd.Timestamp(signal_date)
    return frame.loc[frame.date.between(signal-pd.Timedelta(days=7),signal)].copy()

def capture_rows(observations,run_id,entity,*,period=None):
    frame=observations.loc[observations.run_id.eq(run_id)&observations.entity.eq(entity)].copy()
    if period is not None:frame=frame.loc[frame.statement_period.eq(period)]
    if frame.empty:raise ValueError('Missing required capture entity: '+entity)
    if frame.source_business_key.duplicated().any():raise ValueError('Conflicting capture revisions')
    return frame

def financial_capture(observations,run_id):
    frames={}
    observed={}
    for family in fundamentals.SOURCES:
        source=capture_rows(observations,run_id,family,period='quarter')
        rows=[]
        for _,r in source.iterrows():
            value=json.loads(r['values']) if isinstance(r['values'],str) else dict(r['values'])
            value.update(symbol=r.api_lookup_ticker,source_symbol=r.api_lookup_ticker,
                source_family=family,source_row_id=r.observation_id,source_version=run_id,
                source_notebook='databricks_fmp_collector')
            rows.append(value)
            observed[r.observation_id]=r.retrieved_at
        frames[family]=pd.DataFrame(rows).sort_values(['symbol','date']).reset_index(drop=True)
    annual={}
    for _,r in capture_rows(observations,run_id,'cashflow',period='annual').iterrows():
        value=json.loads(r['values']) if isinstance(r['values'],str) else dict(r['values'])
        # Original annual-verification reader expects original FMP casing.
        for lower,original in {'operatingcashflow':'operatingCashFlow','netcashprovidedbyoperatingactivities':'netCashProvidedByOperatingActivities','accepteddate':'acceptedDate','fillingdate':'fillingDate'}.items():
            if lower in value:value[original]=value[lower]
        annual.setdefault(r.api_lookup_ticker,[]).append(value)
    result=fundamentals.canonical_sources(frames,annual_verification=annual)
    for family,frame in result.items():
        frame['ingested_at']=pd.to_datetime(frame.source_row_id.map(observed),utc=True,errors='raise')
    return result

def recompute(*,baseline_financial,baseline_stock,baseline_sector,baseline_macro,
              observations,run_id,monthly,identity,profiles,signal_date):
    """Recompute all four families; full monthly history fits past-only thresholds."""
    signal=pd.Timestamp(signal_date)
    monthly=monthly.copy();monthly['week_end']=pd.to_datetime(monthly.week_end)
    member=monthly.loc[monthly.week_end.eq(signal)].copy()
    if member.empty:raise ValueError('Reviewed monthly membership required for signal')
    if monthly.week_end.min()>pd.Timestamp('2018-01-31'):
        raise ValueError('Original calibration requires full 2018 membership anchor')
    fresh=financial_capture(observations,run_id)
    financial={}
    for family in fundamentals.SOURCES:
        base=baseline_financial[family].copy();base['date']=pd.to_datetime(base.date)
        financial[family]=overlay(base,fresh[family],['symbol','date'])
    funda=fundamentals.build(financial,monthly,identity,profiles)
    rows=[]
    prices=capture_rows(observations,run_id,'prices')
    for _,r in prices.iterrows():
        v=json.loads(r['values']) if isinstance(r['values'],str) else r['values']
        rows.append(dict(security_id=r.security_id,date=pd.Timestamp(r.observation_date),
            proxy_ticker=r.api_lookup_ticker,adj_close=v.get('adjclose'),volume=v.get('volume')))
    fresh_prices=pd.DataFrame(rows)
    stock=overlay(baseline_stock,fresh_prices.loc[fresh_prices.security_id.notna(),['security_id','date','adj_close','volume']],['security_id','date'])
    all_stock=stock
    stock=stock.loc[stock.security_id.isin(member.security_id)&stock.date.le(signal)]
    technical=from_prices(stock)
    sector=overlay(baseline_sector,fresh_prices.loc[fresh_prices.security_id.isna(),['date','proxy_ticker','adj_close','volume']],['proxy_ticker','date'])
    sector=calculate(sector.loc[sector.date.le(signal)])
    macro_fresh=normalized_observations(observations,run_id=run_id)
    macro=build_features(overlay(baseline_macro,macro_fresh,['series','date']))
    result=dict(population=member,technical=technical.loc[technical.date.eq(signal)],
        financial=funda['features'].loc[funda['features'].month_end.eq(signal)],
        sector=sector.loc[sector.date.eq(signal)],macro=signal_macro_window(macro,signal))
    result['_stock_prices']=all_stock
    result['_canonical_financial']=fresh
    for name in ['quality','lineage','thresholds']:
        audit=funda[name]
        result['_audit_'+name]=audit.loc[pd.to_datetime(audit.month_end).eq(signal)].copy()
    result['_audit_calibration']=pd.DataFrame([dict(calibration_json=json.dumps(funda['calibration'],sort_keys=True,allow_nan=False))])
    return result,dict(run_id=run_id,signal_date=str(signal.date()),
        factor_scope='original_formula_recomputed',fundamental_validation=funda['validation'],
        original_vintage_certified=False,revision_policy='explicit_capture_overlay_immutable_baseline')
