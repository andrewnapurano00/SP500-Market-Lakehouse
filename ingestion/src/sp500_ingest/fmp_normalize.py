"""Source-specific observation projection; raw payload remains authoritative evidence."""
from datetime import date
import math
from .landing import digest

WRAPPERS = ('enterpriseValues', 'historical', 'financials', 'items', 'data', 'results', 'financialStatements')
NORMALIZATION_VERSION='fmp_observation_v2'

def rows(payload):
    if isinstance(payload, list):
        result = payload
    elif isinstance(payload, dict):
        result = next((payload[k] for k in WRAPPERS if isinstance(payload.get(k), list)), None)
        if result is None:
            result = [payload] if 'date' in payload else None
    else:
        result = None
    if result is None or any(not isinstance(r, dict) for r in result):
        raise ValueError('Unrecognized FMP response shape')
    return result


def normalize(payload, request, run_id, retrieved_at):
    entity = request['entity']
    result, seen = [], set()
    for ordinal,original in enumerate(rows(payload)):
        data = {str(k).lower(): v for k, v in original.items()}
        day = data.get('date')
        if entity=='profile':day=request['to_date']
        if not entity.startswith('membership'):
            if not day:
                raise ValueError('Source row missing date')
            day = date.fromisoformat(str(day)[:10]).isoformat()
            if not request['from_date'] <= day <= request['to_date']:
                continue
        ticker = request.get('ticker', '')
        security = request.get('security_id')
        if entity=='prices':
            from .identity import price_identity
            security=price_identity(ticker,day,security)
            if request.get('identity_valid_from') and day<request['identity_valid_from']:continue
        # Request routes are lookup evidence, never identity inferred from symbol.
        key = [entity, security, ticker, day, data.get('symbol'), request.get('period', 'quarter')]
        if entity.startswith('membership'):
            key = [entity, data.get('symbol'), data.get('date'), data.get('addedsecurity'), data.get('removedsecurity')]
        business_key = digest(key)
        if business_key in seen and entity not in {'income','cashflow','balance','enterprise','market_cap'}:
            raise ValueError('Duplicate source business key in one response')
        seen.add(business_key)
        if entity in ('prices', 'macro_prices','benchmark_prices'):
            value = data.get('adjclose')
            if value is None or not math.isfinite(float(value)) or float(value) <= 0:
                raise ValueError('Adjusted prices required; no raw close fallback')
        if entity == 'vix' and (data.get('close') is None or float(data['close']) <= 0):
            raise ValueError('Invalid spot VIX index level')
        if entity == 'treasury' and any(data.get(k) is None for k in ('month3','year2','year10','year30')):
            raise ValueError('Missing Treasury tenor')
        revision = digest(original)
        result.append(dict(entity=entity, security_id=security, api_lookup_ticker=ticker,
            observation_date=day, source_business_key=business_key,
            observation_id=digest([NORMALIZATION_VERSION,run_id,business_key,revision,ordinal]), payload_revision=revision,
            normalization_version=NORMALIZATION_VERSION,
            source_ordinal=ordinal,
            retrieved_at=retrieved_at, run_id=run_id,
            availability_quality='current_vendor_history_revision_uncertain',
            statement_period=request.get('period', 'quarter'), values=data))
    if not result and entity not in {'income','cashflow','balance','market_cap','enterprise','macro_prices','vix','treasury'} and not (entity in {'prices','profile'} and request.get('allow_empty') is True):
        raise ValueError('Empty source response in requested coverage')
    return result
