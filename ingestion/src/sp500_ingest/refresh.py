"""Bounded, restartable FMP landing. No PostgreSQL dependency or implicit publication."""
import calendar
import json
from pathlib import Path
from datetime import date, timedelta, datetime, timezone
from .landing import Checkpoints, write_records, digest, component
from .fmp_normalize import normalize,NORMALIZATION_VERSION

SECTOR_ETFS = ('VOX','XLY','XLP','XLE','XLF','XLV','XLI','XLK','XLB','XLRE','XLU','SPY')
MACRO_ETFS = ('SPY','USO','GLD','UUP','IEF','TLT','HYG','LQD','VIXY')


def windows(start, end, cadence):
    cursor, finish = date.fromisoformat(start), date.fromisoformat(end)
    if cursor > finish:
        raise ValueError('Invalid request interval')
    while cursor <= finish:
        if cadence == 'month':
            stop = date(cursor.year, cursor.month, calendar.monthrange(cursor.year, cursor.month)[1])
        elif cadence == 'year':
            stop = date(cursor.year, 12, 31)
        elif cadence == 'five_year':
            stop = cursor + timedelta(days=1825)
        else:
            stop = finish
        stop = min(stop, finish)
        yield cursor.isoformat(), stop.isoformat()
        cursor = stop + timedelta(days=1)


def plan_requests(identities, start, end, *, include_context=True,include_profiles=True):
    """Reviewed security_id/api_lookup_ticker mapping mandatory; no ticker substitution."""
    jobs, seen = [], set()
    def add(entity, ticker='', security_id=None, cadence='full', period='quarter'):
        for begin, finish in windows(start, end, cadence):
            job = dict(entity=entity,ticker=ticker,security_id=security_id,from_date=begin,to_date=finish,period=period)
            fingerprint = digest(job)
            if fingerprint not in seen:
                seen.add(fingerprint); jobs.append(job)
    ids = set()
    for identity in identities:
        sid, ticker = identity.get('security_id'), identity.get('api_lookup_ticker')
        if not sid or not ticker or sid in ids:
            raise ValueError('Unique reviewed security identity and API lookup route required')
        ids.add(sid)
        for entity in ('prices','income','cashflow','balance','market_cap','enterprise'):
            add(entity,ticker,sid,'five_year' if entity=='market_cap' else 'full')
        add('cashflow',ticker,sid,period='annual')
        if include_profiles:add('profile',ticker,sid)
        if identity.get('identity_valid_from'):
            for job in jobs:
                if job['security_id']==sid and job['entity']=='prices':job['identity_valid_from']=identity['identity_valid_from']
    if include_context:
        add('benchmark_prices','VOO')
        for ticker in SECTOR_ETFS: add('prices',ticker)
        for ticker in MACRO_ETFS: add('macro_prices',ticker,cadence='year')
        add('vix','^VIX',cadence='year')
        add('treasury',cadence='month')
        add('membership_current'); add('membership_history')
    return jobs


def refresh(client, jobs, landing_root, checkpoint_root, run_id):
    """Checkpoints are run-scoped: later independent observations never disappear."""
    component(run_id)
    checkpoints = Checkpoints(checkpoint_root)
    audit = []
    for request in jobs:
        checkpoint = dict(run_id=run_id, request=request)
        normalized_checkpoint=dict(checkpoint,normalization_version=NORMALIZATION_VERSION)
        cached = checkpoints.completed(normalized_checkpoint)
        if cached:
            raw_cached = checkpoints.completed(dict(checkpoint, artifact='raw'))
            if not raw_cached:
                raise ValueError('Normalized checkpoint lacks raw evidence checkpoint')
            audit.append(dict(request_id=digest(request), raw_file=str(raw_cached), normalized_file=str(cached), resumed=True))
            continue
        token = run_id + '_' + digest(request)[:24]
        existing = list((Path(landing_root)/'fmp'/('raw_'+request['entity'])).glob('dt=*/'+token+'.jsonl'))
        if existing:
            envelope = json.loads(existing[0].read_text(encoding='utf-8'))
            payload = envelope['data']['payload']
            params = envelope['meta']['request_parameters']
            instant = envelope['meta']['retrieved_at']
        else:
            payload, params = client.fetch_request(request)
            instant = datetime.now(timezone.utc).isoformat()
        token = run_id + '_' + digest(request)[:24]
        # Both raw wrapper and normalized projection retain original payload revision.
        raw = existing[0] if existing else write_records(landing_root,'fmp','raw_'+request['entity'],[dict(request=request,payload=payload)],
            request_parameters=params,run_id=token,retrieved_at=instant,
            source_record_key=lambda r: [run_id,digest(request)])
        observations = normalize(payload,request,run_id,instant)
        token=token+'_'+NORMALIZATION_VERSION
        normalized_existing = list((Path(landing_root)/'fmp'/request['entity']).glob('dt=*/'+token+'.jsonl'))
        normalized = normalized_existing[0] if normalized_existing else write_records(landing_root,'fmp',request['entity'],observations,
            request_parameters=params,run_id=token,retrieved_at=instant,
            source_record_key=lambda r:r['observation_id'])
        checkpoints.commit(dict(checkpoint, artifact='raw'),raw)
        checkpoints.commit(normalized_checkpoint,normalized)
        audit.append(dict(request_id=digest(request),raw_file=str(raw),normalized_file=str(normalized),rows=len(observations),resumed=False))
    return audit
