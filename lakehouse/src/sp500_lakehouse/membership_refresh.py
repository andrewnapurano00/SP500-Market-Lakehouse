"""Reconcile monthly membership with reviewed stable identities, never invent IDs."""
import json
import pandas as pd
SECTOR_ALIASES={'Technology':'Information Technology','Consumer Cyclical':'Consumer Discretionary',
    'Consumer Defensive':'Consumer Staples','Financial Services':'Financials',
    'Basic Materials':'Materials','Communication':'Communication Services'}

def reconcile_month(monthly,reviewed_routes,observations,*,run_id,signal_date):
    signal=pd.Timestamp(signal_date)
    capture=observations.loc[observations.run_id.eq(run_id)]
    def values(entity):
        rows=capture.loc[capture.entity.eq(entity)]
        if rows.empty:raise ValueError('Membership source missing: '+entity)
        return [json.loads(v) if isinstance(v,str) else v for v in rows['values']]
    members=values('membership_current');events=values('membership_history')
    bysymbol={v['symbol']:v for v in members}
    if len(bysymbol)!=len(members):raise ValueError('Duplicate current constituent')
    symbols=set(bysymbol)
    # Rewind changes after the signal. Current revisions remain retrospective
    # evidence; no claim is made that this was observed at historical close.
    for event in sorted(events,key=lambda x:str(x.get('date','')),reverse=True):
        day=pd.to_datetime(event.get('date'),errors='raise')
        if pd.isna(day):raise ValueError('Membership event date required')
        if day>signal:
            added=event.get('symbol');removed=event.get('removedticker')
            if added:symbols.discard(added)
            if removed:symbols.add(removed)
    routes=reviewed_routes[['security_id','api_lookup_ticker','ticker_latest','sector']].drop_duplicates()
    result=[]
    for ticker in sorted(symbols):
        route=routes.loc[routes.api_lookup_ticker.eq(ticker)]
        if ticker=='SKYD':
            from sp500_ingest.identity import price_identity
            route=route.loc[route.security_id.eq(price_identity(ticker,str(signal.date()),'SKYD'))]
        if route.security_id.nunique()!=1 or route.ticker_latest.nunique()!=1:
            raise ValueError('Review required for constituent identity: '+ticker)
        # Recent reviewed sector wins when resolving multiple historical rows.
        sector=SECTOR_ALIASES.get(bysymbol.get(ticker,{}).get('sector'))
        if sector is None:sector=bysymbol.get(ticker,{}).get('sector')
        if not sector:
            sectors=route.sector.dropna().unique()
            if len(sectors)!=1:raise ValueError('Review required for constituent sector: '+ticker)
            sector=sectors[0]
        row=route.iloc[-1].to_dict();row.update(week_end=signal,sector=sector,
            historical_ticker=ticker,mapping_status='reviewed_identity_fmp_membership_replay',
            price_status='not_used_for_membership_eligibility')
        result.append(row)
    frame=pd.DataFrame(result)
    if frame.security_id.duplicated().any():raise ValueError('Constituent routes collapse identities')
    existing=monthly.loc[pd.to_datetime(monthly.week_end).eq(signal)]
    if not existing.empty and set(existing.security_id)!=set(frame.security_id):
        raise ValueError('Reviewed baseline and reconstructed cohort disagree')
    if not existing.empty:return monthly.copy()
    return pd.concat([monthly,frame],ignore_index=True)
