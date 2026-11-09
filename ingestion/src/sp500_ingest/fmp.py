"""Verified legacy v3 routes from fundamental_ingestion/sector_technical_features."""
import time
from datetime import date
from urllib.parse import quote
import requests

ENDPOINTS = {'prices': 'historical-price-full', 'income': 'income-statement',
             'cashflow': 'cash-flow-statement', 'balance': 'balance-sheet-statement',
             'market_cap': 'historical-market-capitalization', 'enterprise': 'enterprise-values'}
ENDPOINTS['benchmark_prices']='historical-price-full'


class HTTPClient:
    def __init__(self, *, session=None, max_requests=1, attempts=4, interval=0.3, verify=True):
        if max_requests < 1 or not 1 <= attempts <= 8 or interval < 0:
            raise ValueError('Invalid HTTP budget')
        self.session = session or requests.Session()
        self.remaining, self.attempts, self.interval, self.verify = max_requests, attempts, interval, verify
        self.last_request = 0.0

    def get_json(self, url, params):
        for attempt in range(self.attempts):
            if self.remaining <= 0:
                raise RuntimeError('Explicit HTTP request budget exhausted')
            time.sleep(max(0, self.last_request + self.interval - time.monotonic()))
            self.remaining -= 1
            self.last_request = time.monotonic()
            try:
                response = self.session.get(url, params=params, timeout=(10, 60), verify=self.verify)
            except requests.RequestException:
                if attempt + 1 == self.attempts:
                    raise RuntimeError('Source network request failed') from None
                time.sleep(min(16, 2 ** attempt))
                continue
            if response.status_code in (429, 500, 502, 503, 504):
                if attempt + 1 < self.attempts:
                    time.sleep(min(16, 2 ** attempt))
                    continue
                raise RuntimeError('Source retries exhausted')
            if response.status_code != 200:
                raise RuntimeError(f'Source HTTP status {response.status_code}')
            try:
                payload = response.json()
            except ValueError:
                raise RuntimeError('Source returned invalid JSON') from None
            if isinstance(payload, dict) and any(k in payload for k in ('Error Message', 'error', 'Error')):
                raise RuntimeError('Source returned error payload')
            return payload
        raise RuntimeError('Source retries exhausted')


class FMPClient:
    def __init__(self, api_key, http=None):
        if not api_key:
            raise ValueError('FMP API key is required')
        self.api_key, self.http = api_key, http or HTTPClient()

    def fetch(self, entity, ticker, from_date, to_date):
        if entity not in ENDPOINTS or not ticker or len(ticker) > 30:
            raise ValueError('Unsupported source entity or ticker')
        start, end = date.fromisoformat(from_date), date.fromisoformat(to_date)
        if start > end:
            raise ValueError('Invalid source date range')
        if entity == 'market_cap' and (end-start).days > 1826:
            raise ValueError('Market-cap requests require windows no longer than five years')
        params = {'from': from_date, 'to': to_date} if entity in ('prices', 'benchmark_prices', 'market_cap') else {'period': 'quarter', 'limit': 1000}
        if entity == 'market_cap':
            params['limit'] = 200000
        payload = self.http.get_json('https://financialmodelingprep.com/api/v3/' + ENDPOINTS[entity] + '/' + quote(ticker, safe=''), {**params, 'apikey': self.api_key})
        return payload, params  # keep wrapper and every revision unchanged


    def fetch_request(self, request):
        """Execute only a planner-approved route; credentials never enter metadata."""
        entity = request['entity']
        if entity=='profile':
            params={}
            return self.http.get_json('https://financialmodelingprep.com/api/v3/profile/'+quote(request['ticker'],safe=''),{'apikey':self.api_key}),params
        if entity in ENDPOINTS:
            if entity == 'cashflow_annual':
                raise ValueError('Invalid entity')
            if request.get('period') == 'annual':
                if entity != 'cashflow':
                    raise ValueError('Annual verification only supported for cashflow')
                params = {'period': 'annual', 'limit': 1000}
                return self.http.get_json('https://financialmodelingprep.com/api/v3/cash-flow-statement/' + quote(request['ticker'], safe=''), {**params, 'apikey': self.api_key}), params
            return self.fetch(entity, request['ticker'], request['from_date'], request['to_date'])
        routes = {'macro_prices': 'historical-price-eod/dividend-adjusted',
                  'vix': 'historical-price-eod/full', 'treasury': 'treasury-rates'}
        if entity in routes:
            params = {'from': request['from_date'], 'to': request['to_date']}
            if entity != 'treasury':
                params['symbol'] = request['ticker']
            url = 'https://financialmodelingprep.com/stable/' + routes[entity]
        elif entity in ('membership_current', 'membership_history'):
            params = {}
            url = 'https://financialmodelingprep.com/api/v3/' + ('sp500_constituent' if entity == 'membership_current' else 'historical/sp500_constituent')
        else:
            raise ValueError('Unsupported planned source entity')
        return self.http.get_json(url, {**params, 'apikey': self.api_key}), params
