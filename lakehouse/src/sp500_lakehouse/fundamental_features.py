"""Portable, availability-aware original fundamental factor implementation.
Vendored formulas/calibration/scoring from src/fundamental_features.py.
No PostgreSQL, root-module imports, filesystem writes or vendor API calls.
Revision uncertainty and retrospective sector/profile limitations are preserved.
"""
ORIGINAL_SOURCE_SHA256 = '81d06cbc94f841c62edd9477b43e80b87aad617317e21ef57f54bcb3b1793d0a'
SOURCES={
 'income':dict(notebook='sp_income_statement_DATE_END_FIXED (1).ipynb',table='income_statements_q',endpoint='income-statement',cadence='quarter'),
 'cashflow':dict(notebook='sp_cash_flow_DATE_END_FIXED.ipynb',table='cashflow_statements_q',endpoint='cash-flow-statement',cadence='quarter'),
 'balance':dict(notebook='sp_balance_sheet_v2.ipynb',table='balance_sheets_q',endpoint='balance-sheet-statement',cadence='quarter'),
 'market_cap':dict(notebook='sp_alt_metrics.ipynb',table='market_caps_d',endpoint='historical-market-capitalization',cadence='daily'),
 'enterprise':dict(notebook='sp_alt_metrics.ipynb',table='enterprise_values_q',endpoint='enterprise-values',cadence='quarter'),
}

def calendar_maps(schedule=None):
    if schedule is None:
        schedule=mcal.get_calendar('NYSE').schedule(start_date='2012-01-01',end_date='2035-12-31')
    return schedule.market_close.to_dict(),schedule.index.to_numpy(dtype='datetime64[ns]')

import json
import math
import numpy as np
import pandas as pd
import pandas_market_calendars as mcal
VERSION = 'fundamentals_v1_2026-10-31'
FACTORS = {'growth': ['revenue_growth_yoy', 'revenue_cagr_3y', 'eps_growth_yoy', 'net_income_growth_3y', 'ebitda_growth_yoy', 'ocf_growth_yoy', 'fcf_growth_3y'], 'profitability': ['gross_margin', 'ebitda_margin', 'operating_margin', 'net_margin', 'roe', 'roic', 'fcf_margin'], 'valuation': ['earnings_yield', 'sales_yield', 'ebitda_ev_yield', 'fcf_yield', 'book_to_market', 'ocf_yield', 'net_shareholder_yield'], 'balance_sheet': ['debt_to_equity', 'debt_to_assets', 'net_debt_to_ebitda', 'interest_coverage', 'cash_to_assets', 'current_ratio', 'ocf_to_debt']}
BASE_FACTORS = sum(FACTORS.values(), [])
EXTRAS = ['roa', 'equity_to_assets']
ALL_FACTORS = BASE_FACTORS + EXTRAS
LOWER = {'debt_to_equity', 'debt_to_assets', 'net_debt_to_ebitda'}
FAMILY = {f: g for g, fs in FACTORS.items() for f in fs} | {'roa': 'profitability', 'equity_to_assets': 'balance_sheet'}
FIELDS = {'revenue_growth_yoy': ('income.revenue', 'income.revenue', 'TTM / lag4Q TTM - 1'), 'revenue_cagr_3y': ('income.revenue', 'income.revenue', '(TTM / lag12Q TTM) ** (1/3) - 1'), 'eps_growth_yoy': ('income.netincome;income.weightedaverageshsoutdil;income.epsdiluted', 'income.netincome;income.weightedaverageshsoutdil;income.epsdiluted', 'TTM EPS / lag4Q TTM EPS - 1'), 'net_income_growth_3y': ('income.netincome', 'income.netincome', '(TTM / lag12Q TTM) ** (1/3) - 1'), 'ebitda_growth_yoy': ('income.ebitda', 'income.ebitda', 'TTM / lag4Q TTM - 1'), 'ocf_growth_yoy': ('cashflow.operatingcashflow;cashflow.netcashprovidedbyoperatingactivities', 'cashflow.operatingcashflow', 'TTM / lag4Q TTM - 1'), 'fcf_growth_3y': ('cashflow.freecashflow;cashflow.capitalexpenditure', 'cashflow.freecashflow', '(TTM / lag12Q TTM) ** (1/3) - 1'), 'gross_margin': ('income.grossprofit', 'income.revenue', 'TTM / TTM'), 'ebitda_margin': ('income.ebitda', 'income.revenue', 'TTM / TTM'), 'operating_margin': ('income.operatingincome', 'income.revenue', 'TTM / TTM'), 'net_margin': ('income.netincome', 'income.revenue', 'TTM / TTM'), 'roe': ('income.netincome', 'balance.totalstockholdersequity;balance.preferredstock', 'TTM / average(common equity now and 4Q earlier)'), 'roic': ('income.operatingincome;income.incometaxexpense;income.incomebeforetax', 'balance.totaldebt;balance.totalequity;balance.cashandcashequivalents', 'EBIT TTM * (1 - prior-history sector tax proxy) / average invested capital'), 'fcf_margin': ('cashflow.freecashflow', 'income.revenue', 'TTM / TTM'), 'earnings_yield': ('income.netincome', 'market_cap.marketcap', 'TTM / market cap'), 'sales_yield': ('income.revenue', 'market_cap.marketcap', 'TTM / market cap'), 'ebitda_ev_yield': ('income.ebitda', 'market_cap.marketcap;balance.totaldebt;balance.cashandcashequivalents;balance.preferredstock;balance.minorityinterest', 'EBITDA TTM / (historical market cap + released debt + preferred + minority - cash)'), 'fcf_yield': ('cashflow.freecashflow', 'market_cap.marketcap', 'TTM / market cap'), 'book_to_market': ('balance.totalstockholdersequity;balance.preferredstock', 'market_cap.marketcap', 'common equity / market cap'), 'ocf_yield': ('cashflow.operatingcashflow', 'market_cap.marketcap', 'TTM / market cap'), 'net_shareholder_yield': ('cashflow.dividendspaid;cashflow.commonstockrepurchased;cashflow.commonstockissued', 'market_cap.marketcap', 'TTM(abs(dividends) + abs(buybacks) - nonnegative issuance) / market cap'), 'debt_to_equity': ('balance.totaldebt;balance.shorttermdebt;balance.longtermdebt', 'balance.totalstockholdersequity;balance.preferredstock', 'debt / common equity'), 'debt_to_assets': ('balance.totaldebt', 'balance.totalassets', 'debt / assets'), 'net_debt_to_ebitda': ('balance.netdebt;balance.totaldebt;balance.cashandcashequivalents', 'income.ebitda', 'reconciled net debt / EBITDA TTM'), 'interest_coverage': ('income.operatingincome', 'income.interestexpense', 'EBIT TTM / abs(interest expense) TTM'), 'cash_to_assets': ('balance.cashandcashequivalents', 'balance.totalassets', 'cash / assets'), 'current_ratio': ('balance.totalcurrentassets', 'balance.totalcurrentliabilities', 'current assets / current liabilities'), 'ocf_to_debt': ('cashflow.operatingcashflow', 'balance.totaldebt', 'OCF TTM / debt'), 'roa': ('income.netincome', 'balance.totalassets', 'TTM / average(assets now and 4Q earlier)'), 'equity_to_assets': ('balance.totalequity', 'balance.totalassets', 'equity / assets')}
FLOW_FIELDS = {'income': ['revenue', 'grossprofit', 'ebitda', 'operatingincome', 'netincome', 'interestexpense', 'incomebeforetax', 'incometaxexpense', 'epsdiluted'], 'cashflow': ['operatingcashflow', 'freecashflow', 'dividendspaid', 'commonstockrepurchased', 'commonstockissued']}
TEXT_FIELDS = {'symbol', 'cik', 'reportedcurrency', 'accepteddate', 'fillingdate', 'calendaryear', 'period', 'link', 'finallink', 'source_symbol', 'source_notebook', 'source_family', 'source_version', 'source_row_id'}

def trading_age(observed, snapshot, sessions):
    return int(np.searchsorted(sessions, np.datetime64(snapshot), 'right') - np.searchsorted(sessions, np.datetime64(observed), 'right'))

def norm_cik(value):
    if pd.isna(value):
        return None
    digits = ''.join((x for x in str(value).split('.')[0] if x.isdigit()))
    return str(int(digits)) if digits else None

def publication_time(accepted, filing):
    """FMP naive acceptance timestamps interpreted as NY; date-only fallback +2 BDays.
    The fallback is an explicit conservative proxy, never described as actual release.
    """
    value = pd.to_datetime(accepted, errors='coerce')
    fallback = False
    if pd.isna(value):
        value = pd.to_datetime(filing, errors='coerce')
        fallback = True
        if pd.isna(value):
            return (pd.NaT, True)
        value = value.normalize() + pd.offsets.BDay(2)
    value = pd.Timestamp(value)
    if value.tzinfo is None:
        value = value.tz_localize('America/New_York', ambiguous='NaT', nonexistent='shift_forward')
    return (value.tz_convert('UTC'), fallback)

def cashflow_semantics(f, annual_verification=None, semantics_overrides=None, audit=None):
    annual_verification = annual_verification or {}
    semantics_overrides = semantics_overrides or {}
    audits = [] if audit is None else audit
    pieces = []
    for symbol, g in f.groupby('symbol', sort=False):
        g = g.sort_values('date').copy()
        annual = annual_verification.get(symbol, [])
        annual_by_date = {str(r.get('date')): r for r in annual}
        verified_times = []
        modes = {}
        for i, row in enumerate(g.itertuples()):
            if row.period != 'Q4':
                continue
            key = str(pd.Timestamp(row.date).date())
            a = annual_by_date.get(key)
            block = g.iloc[max(0, i - 3):i + 1]
            if a is None or len(block) != 4:
                continue
            if block.period.tolist() != ['Q1', 'Q2', 'Q3', 'Q4']:
                continue
            actual = pd.to_numeric(block.operatingcashflow, errors='coerce')
            total = a.get('operatingCashFlow', a.get('netCashProvidedByOperatingActivities'))
            if total is None or actual.isna().any():
                continue
            tol = max(1000000.0, abs(float(total)) * 0.02)
            mode = 'standalone' if abs(actual.sum() - float(total)) <= tol else 'ytd_pattern_unverified' if abs(actual.iloc[-1] - float(total)) <= tol else 'unreconciled'
            if semantics_overrides:
                evidence = semantics_overrides.get(symbol, {}).get(key, {})
                if evidence.get('mode') == 'ytd' and evidence.get('filing_evidence_url'):
                    mode = 'ytd'
            fiscal_key = row.calendaryear
            modes[str(fiscal_key)] = mode
            available, _ = publication_time(a.get('acceptedDate'), a.get('fillingDate'))
            if mode in ['standalone', 'ytd'] and pd.notna(available):
                verified_times.append(available)
            audits.append(dict(symbol=symbol, fiscal_end=key, quarter_sum=actual.sum(), annual=total, mode=mode, source_notebook=SOURCES['cashflow']['notebook']))
        known = set(modes.values()) - {'unreconciled', 'ytd_pattern_unverified'}
        default = next(iter(known)) if len(known) == 1 else None
        g['cf_semantics_verified'] = False
        g['cf_mode'] = 'unverified'
        g['cf_semantics_available_at'] = pd.Series(pd.NaT, index=g.index, dtype='datetime64[ns, UTC]')
        for year, ix in g.groupby('calendaryear').groups.items():
            mode = modes.get(str(year), default)
            if mode not in ['standalone', 'ytd'] or not verified_times:
                continue
            g.loc[ix, 'cf_semantics_verified'] = True
            g.loc[ix, 'cf_mode'] = mode
            g.loc[ix, 'cf_semantics_available_at'] = min(verified_times)
            if mode == 'ytd':
                block = g.loc[ix].sort_values('date')
                original_available = block.data_available_at.copy()
                for position, index in enumerate(block.index):
                    if block.loc[index, 'period'] == 'Q1':
                        continue
                    if position == 0 or block.iloc[position - 1].reportedcurrency != block.loc[index, 'reportedcurrency']:
                        g.loc[index, 'data_available_at'] = pd.NaT
                        continue
                    times = [original_available.iloc[position], original_available.iloc[position - 1]]
                    g.loc[index, 'data_available_at'] = max(times) if all((pd.notna(t) for t in times)) else pd.NaT
                for field in FLOW_FIELDS['cashflow'] + ['capitalexpenditure', 'netcashprovidedbyoperatingactivities']:
                    if field not in g:
                        continue
                    vals = pd.to_numeric(block[field], errors='coerce')
                    derived = vals.diff()
                    derived.loc[block.period.eq('Q1')] = vals.loc[block.period.eq('Q1')]
                    expected = block.period.map({'Q1': 1, 'Q2': 2, 'Q3': 3, 'Q4': 4}).diff().eq(1) | block.period.eq('Q1')
                    g.loc[block.index, field] = derived.where(expected)
        pieces.append(g)
    result = pd.concat(pieces, ignore_index=True)
    return result

def canonical_sources(frames, *, annual_verification=None, semantics_overrides=None, calendar_schedule=None):
    CLOSES, _ = calendar_maps(calendar_schedule)
    result = {}
    for family in frames:
        f = frames[family].copy()
        f['date'] = pd.to_datetime(f.date)
        for field in list(f.columns):
            if field not in TEXT_FIELDS and field != 'date':
                f[field] = pd.to_numeric(f[field], errors='coerce')
        f['cik_normalized'] = f.get('cik', pd.Series(index=f.index, dtype=object)).map(norm_cik)
        if family in FLOW_FIELDS or family == 'balance':
            times = [publication_time(a, b) for a, b in zip(f.get('accepteddate', [None] * len(f)), f.get('fillingdate', [None] * len(f)))]
            f['data_available_at'] = pd.to_datetime([x[0] for x in times], utc=True)
            f['availability_proxy'] = np.array([x[1] for x in times], dtype=bool)
            fiscal_midnight = f.date.dt.tz_localize('America/New_York').dt.tz_convert('UTC')
            f.loc[f.data_available_at.lt(fiscal_midnight), 'data_available_at'] = pd.NaT
            f['date_start'] = f.date
            next_date = f.groupby('symbol').date.shift(-1)
            f['date_end'] = (next_date - pd.Timedelta(days=1)).fillna(pd.Timestamp('2100-12-31'))
        else:
            f['data_available_at'] = pd.to_datetime(f.date.map(CLOSES), utc=True)
            if family == 'enterprise':
                f['observation_close_at'] = f.data_available_at
                f['data_available_at'] = pd.Series(pd.NaT, index=f.index, dtype='datetime64[ns, UTC]')
                f['availability_unknown'] = True
        if family == 'cashflow':
            for field in FLOW_FIELDS['cashflow'] + ['capitalexpenditure', 'netcashprovidedbyoperatingactivities']:
                if field not in f:
                    f[field] = np.nan
            alias = f.operatingcashflow.fillna(f.netcashprovidedbyoperatingactivities)
            mismatch = (f.operatingcashflow - f.netcashprovidedbyoperatingactivities).abs() > np.maximum(1000.0, alias.abs() * 0.001)
            f['ocf_alias_mismatch'] = mismatch.fillna(False)
            f['operatingcashflow'] = alias.mask(f.ocf_alias_mismatch)
            f = cashflow_semantics(f, annual_verification, semantics_overrides)
            calculated = f.operatingcashflow - f.capitalexpenditure.abs()
            f['fcf_derived'] = f.freecashflow.isna() & calculated.notna()
            f['fcf_reconciliation_failed'] = ((f.freecashflow - calculated).abs() > np.maximum(1000000.0, calculated.abs() * 0.02)).fillna(False)
            f['freecashflow'] = f.freecashflow.fillna(calculated).mask(f.fcf_reconciliation_failed)
            for field in FLOW_FIELDS['cashflow']:
                f[field] = f[field].where(f.cf_semantics_verified)
        f['ingested_at'] = pd.Timestamp.now(tz='UTC')
        f['pit_revision_uncertain'] = True
        if family == 'income':
            error = (f.grossprofit - (f.revenue - f.costofrevenue)).abs()
            f['accounting_reconciliation_failed'] = error.gt(np.maximum(1000000.0, f.revenue.abs() * 0.02))
        elif family == 'balance':
            error = (f.totalassets - f.totalliabilities - f.totalequity).abs()
            f['accounting_reconciliation_failed'] = error.gt(np.maximum(1000000.0, f.totalassets.abs() * 0.02))
        elif family == 'cashflow':
            f['accounting_reconciliation_failed'] = f.fcf_reconciliation_failed | f.ocf_alias_mismatch
        else:
            f['accounting_reconciliation_failed'] = False
        f = f.sort_values(['symbol', 'date']).reset_index(drop=True)
        result[family] = f
    return result

def prepare_history(f, family):
    """Materialize contiguous 4Q sums and provenance; availability stays explicit."""
    if family == 'market_cap':
        f = f.loc[f.data_available_at.notna()].copy()
        f['_observation_month'] = f.date.dt.to_period('M')
        f = f.sort_values('date').groupby(['symbol', '_observation_month'], sort=False).tail(1).drop(columns='_observation_month')
    output = {}
    for symbol, group in f.groupby('symbol', sort=False):
        g = group.sort_values('date').copy().reset_index(drop=True)
        q = g.get('period', pd.Series(index=g.index, dtype=object)).map({'Q1': 1, 'Q2': 2, 'Q3': 3, 'Q4': 4})
        gaps = g.date.diff().dt.days
        continuation = gaps.between(50, 120) & q.eq(q.shift() % 4 + 1)
        segment = (~continuation).cumsum()
        recs = g.to_dict('records')
        for i, row in enumerate(recs):
            row['_segment'] = int(segment.iloc[i])
            row['_position'] = i
            if family in FLOW_FIELDS:
                valid = i >= 3 and segment.iloc[i] == segment.iloc[i - 3]
                block = recs[i - 3:i + 1] if valid else []
                currency = {r.get('reportedcurrency') for r in block}
                dates = [r.get('data_available_at', pd.NaT) for r in block]
                if family == 'cashflow':
                    dates += [r.get('cf_semantics_available_at', pd.NaT) for r in block]
                row['ttm_available_at'] = max(dates) if dates and all((pd.notna(d) for d in dates)) else pd.NaT
                row['ttm_valid'] = valid and len(currency) == 1 and all((pd.notna(x) and bool(str(x)) for x in currency))
                row['ttm_source_ids'] = ';'.join((r['source_row_id'] for r in block))
                row['ttm_accounting_reconciliation_failed'] = any((r.get('accounting_reconciliation_failed', False) for r in block))
                for field in FLOW_FIELDS[family]:
                    vals = [r.get(field, np.nan) for r in block]
                    if field == 'interestexpense':
                        vals = [abs(x) for x in vals]
                    row[field + '_ttm'] = float(sum(vals)) if row['ttm_valid'] and len(vals) == 4 and np.isfinite(vals).all() else np.nan
                if family == 'income':
                    shares = [r.get('weightedaverageshsoutdil', np.nan) for r in block]
                    row['eps_approximation'] = False
                    if len(shares) == 4 and np.isfinite(shares).all() and (min(shares) > 0):
                        row['eps_ttm'] = row['netincome_ttm'] / np.mean(shares)
                        row['eps_approximation'] = True
                    else:
                        row['eps_ttm'] = row.get('epsdiluted_ttm', np.nan)
                        row['eps_approximation'] = True
            for lag in [4, 12]:
                row[f'_lag{lag}'] = recs[i - lag] if i >= lag and segment.iloc[i] == segment.iloc[i - lag] else None
        output[symbol] = recs
    return output

def latest_eligible(history, cutoff, cik=None, statements=True):
    eligible = [r for r in history if pd.notna(r.get('data_available_at')) and r['data_available_at'] <= cutoff and (not statements or (cik is not None and r.get('cik_normalized') == cik))]
    return eligible[-1] if eligible else None

def valid_ttm(row, cutoff):
    return row is not None and row.get('ttm_valid', False) and pd.notna(row.get('ttm_available_at')) and (row['ttm_available_at'] <= cutoff)

def classify(sector, industry):
    s = str(industry).lower()
    if sector == 'Financials':
        if any((x in s for x in ['bank', 'savings', 'thrift'])):
            return 'bank'
        if 'broker' in s:
            return 'financial_other'
        if any((x in s for x in ['insurance', 'insurer', 'reinsurance'])):
            return 'insurer'
        return 'financial_other'
    if sector == 'Real Estate':
        return 'reit' if 'reit' in s else 'real_estate_other'
    return 'industrial'

def applicable(factor, sector, subtype):
    finance = sector == 'Financials'
    if factor in EXTRAS:
        return finance
    if finance and factor in {'ebitda_growth_yoy', 'ocf_growth_yoy', 'fcf_growth_3y', 'gross_margin', 'ebitda_margin', 'operating_margin', 'roic', 'fcf_margin', 'ebitda_ev_yield', 'fcf_yield', 'ocf_yield', 'debt_to_equity', 'debt_to_assets', 'net_debt_to_ebitda', 'interest_coverage', 'cash_to_assets', 'current_ratio', 'ocf_to_debt'}:
        return False
    if subtype == 'reit' and factor in {'eps_growth_yoy', 'net_income_growth_3y', 'fcf_growth_3y', 'net_margin', 'roe', 'roic', 'fcf_margin', 'earnings_yield', 'fcf_yield', 'book_to_market', 'current_ratio'}:
        return False
    if sector == 'Utilities' and factor == 'current_ratio':
        return False
    return True

def compute_factors(inputs, sector, subtype, floors, tax_rate):
    """Pure economic guards: returns finite values plus explicit reason taxonomy."""
    v = inputs
    result = {}
    reasons = {}

    def ratio(name, num, den, reason='near_zero_denominator', floor=0.0, positive=True):
        if not applicable(name, sector, subtype):
            result[name] = np.nan
            reasons[name] = 'not_applicable'
            return
        if not np.isfinite(num) or not np.isfinite(den):
            result[name] = np.nan
            reasons[name] = 'source_missing'
            return
        if den <= floor if positive else abs(den) <= floor:
            result[name] = np.nan
            reasons[name] = reason
            return
        result[name] = num / den
        reasons[name] = None

    def growth(name, key, lag, years=1):
        a = v.get(key, np.nan)
        b = v.get(key + f'_lag{lag}', np.nan)
        if not applicable(name, sector, subtype):
            result[name] = np.nan
            reasons[name] = 'not_applicable'
            return
        if not np.isfinite(a) or not np.isfinite(b):
            result[name] = np.nan
            reasons[name] = 'history_insufficient'
            return
        floor = floors.get(key, 0.01 if key == 'eps_ttm' else 1000000.0)
        if b <= 0:
            result[name] = np.nan
            reasons[name] = 'negative_base' if b < 0 else 'near_zero_denominator'
            return
        if b <= floor:
            result[name] = np.nan
            reasons[name] = 'near_zero_denominator'
            return
        if years > 1 and a <= 0:
            result[name] = np.nan
            reasons[name] = 'negative_base'
            return
        result[name] = (a / b) ** (1 / years) - 1
        reasons[name] = None
    for name, key, lag, years in [('revenue_growth_yoy', 'revenue_ttm', 4, 1), ('revenue_cagr_3y', 'revenue_ttm', 12, 3), ('eps_growth_yoy', 'eps_ttm', 4, 1), ('net_income_growth_3y', 'netincome_ttm', 12, 3), ('ebitda_growth_yoy', 'ebitda_ttm', 4, 1), ('ocf_growth_yoy', 'operatingcashflow_ttm', 4, 1), ('fcf_growth_3y', 'freecashflow_ttm', 12, 3)]:
        growth(name, key, lag, years)
    pairs = {'gross_margin': ('grossprofit_ttm', 'revenue_ttm'), 'ebitda_margin': ('ebitda_ttm', 'revenue_ttm'), 'operating_margin': ('operatingincome_ttm', 'revenue_ttm'), 'net_margin': ('netincome_ttm', 'revenue_ttm'), 'roe': ('netincome_ttm', 'average_common_equity'), 'fcf_margin': ('freecashflow_ttm', 'revenue_ttm'), 'earnings_yield': ('netincome_ttm', 'market_cap'), 'sales_yield': ('revenue_ttm', 'market_cap'), 'ebitda_ev_yield': ('ebitda_ttm', 'enterprise_value'), 'fcf_yield': ('freecashflow_ttm', 'market_cap'), 'book_to_market': ('common_equity', 'market_cap'), 'ocf_yield': ('operatingcashflow_ttm', 'market_cap'), 'net_shareholder_yield': ('net_shareholder_cash_ttm', 'market_cap'), 'debt_to_equity': ('debt', 'common_equity'), 'debt_to_assets': ('debt', 'assets'), 'net_debt_to_ebitda': ('net_debt', 'ebitda_ttm'), 'interest_coverage': ('operatingincome_ttm', 'interestexpense_ttm'), 'cash_to_assets': ('cash', 'assets'), 'current_ratio': ('current_assets', 'current_liabilities'), 'ocf_to_debt': ('operatingcashflow_ttm', 'debt'), 'roa': ('netincome_ttm', 'average_assets'), 'equity_to_assets': ('equity', 'assets')}
    for name, (num, den) in pairs.items():
        numerator = v.get(num, np.nan)
        denominator = v.get(den, np.nan)
        reason = {'average_common_equity': 'nonpositive_equity', 'common_equity': 'nonpositive_equity', 'ebitda_ttm': 'nonpositive_ebitda', 'interestexpense_ttm': 'no_interest_expense', 'debt': 'zero_debt'}.get(den, 'near_zero_denominator')
        if applicable(name, sector, subtype) and (name == 'book_to_market' and np.isfinite(numerator) and (numerator <= 0) or (name == 'roe' and np.isfinite(v.get('common_equity', np.nan)) and (v['common_equity'] <= 0))):
            result[name] = np.nan
            reasons[name] = 'nonpositive_equity'
            continue
        ratio(name, numerator, denominator, reason, floor=floors.get(den, 1000000.0) if den in ['revenue_ttm', 'ebitda_ttm', 'common_equity', 'average_common_equity', 'debt'] else 0.0)
    ratio('roic', v.get('operatingincome_ttm', np.nan) * (1 - tax_rate), v.get('average_invested_capital', np.nan), floor=1000000.0)
    if np.isfinite(result.get('cash_to_assets', np.nan)) and (not 0 <= result['cash_to_assets'] <= 1):
        result['cash_to_assets'] = np.nan
        reasons['cash_to_assets'] = 'invalid_accounting'
    for name, value in result.items():
        if not np.isfinite(value):
            result[name] = np.nan
    return (result, reasons)

def score_values(values, higher=True, min_peers=15):
    valid = values.notna()
    out = pd.Series(np.nan, index=values.index, dtype=float)
    if valid.sum() < min_peers:
        return out
    rank = values.loc[valid].rank(method='average')
    score = 100 * (rank - 1) / (valid.sum() - 1)
    out.loc[valid] = score if higher else 100 - score
    return out

def composite_score(scores, eligible):
    count = scores.notna().sum(axis=1)
    required = np.maximum(2, np.ceil(eligible * 0.5))
    return (scores.mean(axis=1).where(count.ge(required) & eligible.gt(0)), count)

def score_factors_fast(f):
    """Same prior-month percentile policy, with array writes instead of row lookups."""
    from scipy.stats import rankdata
    f = f.reset_index(drop=True)
    size = len(f)
    groups = {}
    for (peer, date), indices in f.groupby(['peer_group_used', 'month_end'], sort=True).groups.items():
        groups.setdefault(peer, []).append((pd.Timestamp(date), np.asarray(indices, dtype=int)))
    columns = {}
    qualities = []
    thresholds = []
    for factor in ALL_FACTORS:
        raw = f[factor + '_raw'].to_numpy(dtype=float)
        applicable_values = f[factor + '_applicable'].to_numpy(dtype=bool)
        clean = raw.copy()
        scores = np.full(size, np.nan)
        outlier = np.zeros(size, dtype=bool)
        n_valid = np.zeros(size, dtype=int)
        n_applicable = np.zeros(size, dtype=int)
        coverage = np.full(size, np.nan)
        for peer, months in groups.items():
            history = []
            for date, indices in months:
                values = raw[indices]
                low = high = np.nan
                if len(history) >= 100:
                    low, high = np.quantile(history, [0.01, 0.99])
                adjusted = np.clip(values, low, high) if np.isfinite(low) else values.copy()
                valid = np.isfinite(adjusted)
                count = int(valid.sum())
                eligible = int(applicable_values[indices].sum())
                clean[indices] = adjusted
                outlier[indices] = np.isfinite(values) & (values != adjusted)
                n_valid[indices] = count
                n_applicable[indices] = eligible
                if eligible:
                    coverage[indices] = count / eligible
                if count >= 15:
                    ranked = 100 * (rankdata(adjusted[valid], method='average') - 1) / (count - 1)
                    scores[indices[valid]] = 100 - ranked if factor in LOWER else ranked
                thresholds.append(dict(peer_group=peer, factor_id=factor, month_end=date, fit_observations=len(history), fit_end=(date.to_period('M') - 1).to_timestamp('M'), low=low, high=high))
                history.extend(values[np.isfinite(values)].tolist())
        columns[factor + '_clean'] = clean
        columns[factor + '_outlier_flag'] = outlier
        columns[factor + '_sector_score'] = scores
        reasons = f[factor + '_missing_reason'].to_numpy(dtype=object, copy=True)
        score_reason = reasons.copy()
        score_reason[(n_valid < 15) & np.isfinite(clean)] = 'insufficient_peers'
        qualities.append(pd.DataFrame(dict(security_id=f.security_id.to_numpy(), month_end=f.month_end.to_numpy(), factor_id=factor, missing_reason=reasons, n_valid=n_valid, n_eligible_applicable=n_applicable, sector_coverage=coverage, score_missing_reason=score_reason, outlier_flag=outlier, peer_group_used=f.peer_group_used.to_numpy(), version=VERSION)))
    f = pd.concat([f.drop(columns=list(columns), errors='ignore'), pd.DataFrame(columns)], axis=1)
    return (f, pd.concat(qualities, ignore_index=True), pd.DataFrame(thresholds))

def _number(row, key):
    if row is None:
        return np.nan
    x = row.get(key, np.nan)
    return float(x) if x is not None and pd.notna(x) and np.isfinite(x) else np.nan

def build(sources, monthly, identity, profiles, *, calendar_schedule=None):
    """Recompute from explicit canonical frames; no I/O or API dependencies.

    Identity grain security_id/latest_ticker; monthly grain security_id/week_end.
    Sources must include all five families, release timestamps and source_row_id.
    Profiles are a ticker -> profile mapping; current sectors remain retrospective.
    """
    CLOSES, sessions = calendar_maps(calendar_schedule)
    if set(sources) != set(SOURCES):
        raise ValueError('All five source families required')
    if monthly.duplicated(['security_id', 'week_end']).any():
        raise ValueError('Duplicate monthly membership')
    sources = {family: frame.copy() for family, frame in sources.items()}
    monthly = monthly.copy()
    monthly['week_end'] = pd.to_datetime(monthly.week_end)
    identity = identity[['security_id', 'latest_ticker', 'cik', 'currency']].drop_duplicates().copy()
    for family, f in sources.items():
        f['date'] = pd.to_datetime(f.date)
        f['data_available_at'] = pd.to_datetime(f.data_available_at, utc=True)
        if 'cf_semantics_available_at' in f:
            f['cf_semantics_available_at'] = pd.to_datetime(f.cf_semantics_available_at, utc=True)
    histories = {family: prepare_history(f, family) for family, f in sources.items()}
    identities = {}
    for (sid, ticker), g in identity.groupby(['security_id', 'latest_ticker']):
        ciks = set(g.cik.map(norm_cik).dropna())
        curr = set(g.currency.dropna())
        identities[sid, ticker] = (next(iter(ciks)) if len(ciks) == 1 else None, next(iter(curr)) if len(curr) == 1 else None)
    calibration = []
    anchor = monthly.loc[monthly.week_end.eq(monthly.week_end.min())]
    anchor_symbols = set(anchor.ticker_latest)
    for family in FLOW_FIELDS:
        for symbol, recs in histories[family].items():
            if symbol not in anchor_symbols:
                continue
            sector = monthly.loc[monthly.ticker_latest.eq(symbol), 'sector']
            sector = sector.iloc[-1] if len(sector) else None
            allowed = {identities.get((m.security_id, m.ticker_latest), (None, None))[0] for m in anchor.loc[anchor.ticker_latest.eq(symbol)].itertuples()} - {None}
            for row in recs:
                if valid_ttm(row, pd.Timestamp('2018-01-01', tz='UTC')) and row.get('cik_normalized') in allowed:
                    calibration.append(dict(sector=sector, reported_currency=row.get('reportedcurrency'), **{k: row.get(k, np.nan) for k in ['revenue_ttm', 'eps_ttm', 'netincome_ttm', 'ebitda_ttm', 'operatingcashflow_ttm', 'freecashflow_ttm', 'incometaxexpense_ttm', 'incomebeforetax_ttm']}))
    calibration = pd.DataFrame(calibration, columns=['sector', 'reported_currency', 'revenue_ttm', 'eps_ttm', 'netincome_ttm', 'ebitda_ttm', 'operatingcashflow_ttm', 'freecashflow_ttm', 'incometaxexpense_ttm', 'incomebeforetax_ttm'])
    floor_map = {}
    tax_map = {}
    for (sector, currency), g in calibration.groupby(['sector', 'reported_currency']):
        floor_map[sector + '|' + currency] = {key: max(0.01 if key == 'eps_ttm' else 1000000.0, 0.005 * g[key].abs().median()) for key in ['revenue_ttm', 'eps_ttm', 'netincome_ttm', 'ebitda_ttm', 'operatingcashflow_ttm', 'freecashflow_ttm'] if g[key].notna().any()}
    for sector, g in calibration.groupby('sector'):
        tax = (g.incometaxexpense_ttm / g.incomebeforetax_ttm).where(g.incomebeforetax_ttm.gt(1000000.0)).dropna().clip(0, 0.4)
        tax_map[sector] = float(tax.median()) if len(tax) else 0.21
    output = []
    lineage = []
    for count, member in enumerate(monthly.itertuples(), 1):
        date = pd.Timestamp(member.week_end)
        cutoff = CLOSES[date]
        sid, ticker, sector = (member.security_id, member.ticker_latest, member.sector)
        expected, currency = identities.get((sid, ticker), (None, None))
        profile = profiles.get(ticker, {})
        industry = profile.get('industry')
        subtype = classify(sector, industry)
        selected = {family: latest_eligible(histories[family].get(ticker, []), cutoff, expected, statements=family in ['income', 'cashflow', 'balance']) for family in SOURCES}
        i, c, b, cap, ev = [selected[x] for x in SOURCES]
        ev_observations = [r for r in histories['enterprise'].get(ticker, []) if r['date'] <= date]
        vendor_ev = ev_observations[-1] if ev_observations else None
        inputs = {}
        metadata = {}
        periods = {}
        for family, row in selected.items():
            short = {'income': 'income', 'cashflow': 'cf', 'balance': 'bs', 'market_cap': 'market_cap', 'enterprise': 'ev'}[family]
            if row is not None:
                age = (date - row['date']).days
                metadata[f'{short}_source_row_id'] = row['source_row_id']
                metadata[f'{short}_available_at'] = row['data_available_at']
                metadata[f'{short}_fiscal_period_end'] = row['date']
                metadata[f'{short}_fiscal_age_days'] = age
                metadata[f'{short}_available_age_days'] = (cutoff - row['data_available_at']).days
                metadata[f'{short}_availability_proxy'] = bool(row.get('availability_proxy', False))
                periods[family] = row['date']
                lineage.append(dict(security_id=sid, month_end=date, family=family, source_row_id=row['source_row_id'], ttm_source_ids=row.get('ttm_source_ids'), available_at=row['data_available_at'], ttm_available_at=row.get('ttm_available_at'), ttm_used=valid_ttm(row, cutoff) and age <= 180, lag4_source_ids=(row.get('_lag4') or {}).get('ttm_source_ids'), lag12_source_ids=(row.get('_lag12') or {}).get('ttm_source_ids'), feature_cutoff_at=cutoff, source_notebook=SOURCES[family]['notebook']))
            else:
                age = 99999
            stale = age > 180 if family in ['income', 'cashflow', 'balance'] else row is None or trading_age(row['date'], date, sessions) > 5
            metadata[f'{short}_stale'] = bool(stale)
            if family in FLOW_FIELDS:
                okay = not stale and valid_ttm(row, cutoff)
                for field in FLOW_FIELDS[family]:
                    inputs[field + '_ttm'] = _number(row, field + '_ttm') if okay else np.nan
                if family == 'income':
                    inputs['eps_ttm'] = _number(row, 'eps_ttm') if okay else np.nan
                for lag in [4, 12]:
                    previous = row.get(f'_lag{lag}') if row else None
                    lag_ok = okay and valid_ttm(previous, cutoff) and (previous.get('reportedcurrency') == row.get('reportedcurrency'))
                    for field in FLOW_FIELDS[family] + (['eps'] if family == 'income' else []):
                        key = field + '_ttm'
                        inputs[key + f'_lag{lag}'] = _number(previous, key) if lag_ok else np.nan
                metadata[f'{short}_ttm_complete'] = bool(okay)
        currencies = {r.get('reportedcurrency') for r in [i, c, b] if r is not None}
        currencies.discard(None)
        cross_currency_ok = len(currencies) == 1
        stale_bs = metadata['bs_stale']
        bs_ok = b is not None and (not stale_bs)
        get = lambda key: _number(b, key) if bs_ok else np.nan
        inputs.update(assets=get('totalassets'), equity=get('totalequity'), cash=get('cashandcashequivalents'), current_assets=get('totalcurrentassets'), current_liabilities=get('totalcurrentliabilities'))
        debt = get('totaldebt')
        derived_debt = get('shorttermdebt') + get('longtermdebt')
        if not np.isfinite(debt):
            debt = derived_debt
        common = get('totalstockholdersequity') - get('preferredstock')
        inputs['debt'] = debt
        inputs['common_equity'] = common
        canonical_net = debt - inputs['cash']
        vendor_net = get('netdebt')
        net_coherent = np.isfinite(vendor_net) and abs(vendor_net - canonical_net) <= max(1000000.0, abs(canonical_net) * 0.02)
        inputs['net_debt'] = vendor_net if net_coherent else canonical_net
        previous = b.get('_lag4') if b else None
        prev_ok = bs_ok and previous is not None and pd.notna(previous.get('data_available_at')) and (previous['data_available_at'] <= cutoff) and (previous.get('reportedcurrency') == b.get('reportedcurrency'))
        metadata['bs_opening_source_row_id'] = previous.get('source_row_id') if prev_ok else None
        metadata['bs_opening_available_at'] = previous.get('data_available_at') if prev_ok else pd.NaT
        for name, current, old in [('common_equity', common, _number(previous, 'totalstockholdersequity') - _number(previous, 'preferredstock')), ('assets', inputs['assets'], _number(previous, 'totalassets')), ('invested_capital', debt + inputs['equity'] - inputs['cash'], _number(previous, 'totaldebt') + _number(previous, 'totalequity') - _number(previous, 'cashandcashequivalents'))]:
            inputs['average_' + name] = (current + old) / 2 if prev_ok else np.nan
        bs_matches_income = bs_ok and i is not None and (b['date'] == i['date']) and cross_currency_ok
        if not bs_matches_income:
            for key in ['average_common_equity', 'average_assets', 'average_invested_capital']:
                inputs[key] = np.nan
        if c is not None and i is not None and (c['date'] != i['date']):
            inputs['fcf_ttm_for_margin'] = np.nan
        valuation_currency = next(iter(currencies)) if len(currencies) == 1 else None
        route_verified = pd.notna(member.api_lookup_ticker) and member.api_lookup_ticker == ticker
        market_ok = cap is not None and (not metadata['market_cap_stale']) and (currency is not None) and (valuation_currency == currency) and route_verified
        inputs['market_cap'] = _number(cap, 'marketcap') if market_ok else np.nan
        inputs['enterprise_value'] = inputs['market_cap'] + debt + get('preferredstock') + get('minorityinterest') - inputs['cash'] if bs_ok and market_ok else np.nan
        inputs['net_shareholder_cash_ttm'] = abs(inputs.get('dividendspaid_ttm', np.nan)) + abs(inputs.get('commonstockrepurchased_ttm', np.nan)) - inputs.get('commonstockissued_ttm', np.nan)
        if inputs.get('commonstockissued_ttm', 0) < 0:
            inputs['net_shareholder_cash_ttm'] = np.nan
        inputs['interestexpense_ttm'] = abs(inputs.get('interestexpense_ttm', np.nan))
        floors = dict(floor_map.get(sector + '|' + str((i or {}).get('reportedcurrency')), {}))
        cf_floors = floor_map.get(sector + '|' + str((c or {}).get('reportedcurrency')), {})
        for key in ['operatingcashflow_ttm', 'freecashflow_ttm']:
            if key in cf_floors:
                floors[key] = cf_floors[key]
        factors, reasons = compute_factors(inputs, sector, subtype, floors, tax_map.get(sector, 0.21))
        income_qc = bool(i and i.get('ttm_accounting_reconciliation_failed', False))
        bs_qc = bool(b and b.get('accounting_reconciliation_failed', False))
        cf_qc = bool(c and (c.get('ttm_accounting_reconciliation_failed', False) or not c.get('cf_semantics_verified', False)))
        bad_factors = {'gross_margin'} if income_qc else set()
        if bs_qc:
            bad_factors |= {'roe', 'roic', 'book_to_market', 'debt_to_equity', 'debt_to_assets', 'net_debt_to_ebitda', 'cash_to_assets', 'current_ratio', 'ocf_to_debt', 'roa', 'equity_to_assets', 'ebitda_ev_yield'}
        for factor in bad_factors:
            if reasons[factor] != 'not_applicable':
                factors[factor] = np.nan
                reasons[factor] = 'invalid_accounting'
        if cf_qc:
            for factor in ALL_FACTORS:
                if 'cashflow.' in FIELDS[factor][0] and (not np.isfinite(factors[factor])) and (reasons[factor] != 'not_applicable'):
                    reasons[factor] = 'invalid_accounting'
        cross = {'roe', 'roic', 'fcf_margin', 'net_debt_to_ebitda', 'ocf_to_debt', 'roa'}
        for factor in cross:
            if reasons[factor] != 'not_applicable' and (not cross_currency_ok):
                factors[factor] = np.nan
                reasons[factor] = 'invalid_currency'
        if c is not None and i is not None and (c['date'] != i['date']) and (reasons['fcf_margin'] != 'not_applicable'):
            factors['fcf_margin'] = np.nan
            reasons['fcf_margin'] = 'history_insufficient'
        for factor in FACTORS['valuation']:
            if reasons[factor] != 'not_applicable' and (not market_ok):
                reasons[factor] = 'invalid_currency' if currency != valuation_currency else 'stale_market_data'
        income_stale = metadata['income_stale']
        cf_stale = metadata['cf_stale']
        for factor in ALL_FACTORS:
            if np.isfinite(factors[factor]) or reasons[factor] == 'not_applicable':
                continue
            families = {x.split('.')[0] for x in (FIELDS[factor][0] + ';' + FIELDS[factor][1]).split(';')}
            if any((selected[x] is None for x in families if x != 'enterprise')):
                reasons[factor] = 'not_yet_public'
            elif any((metadata[{'income': 'income', 'cashflow': 'cf', 'balance': 'bs'}[x] + '_stale'] for x in families if x in ['income', 'cashflow', 'balance'])):
                reasons[factor] = 'stale_statement'
        row = dict(security_id=sid, ticker_latest=ticker, cik=expected, month_end=date, feature_cutoff_at=cutoff, sector_clean=sector, industry=industry, financial_subtype=subtype, is_sp500_member=True, peer_group_used=sector + '::' + subtype if sector == 'Financials' else sector, score_fallback_used=False, sector_classification_retrospective=True, industry_classification_retrospective=True, pit_revision_uncertain=True, sector_score_version=VERSION, reported_currency=valuation_currency, market_currency=currency, market_currency_inferred_from_profile=True, enterprise_value_method='market_cap_plus_released_bs_components', market_route_verified=bool(route_verified), enterprise_value_vendor_unverified=_number(vendor_ev, 'enterprisevalue'), enterprise_value_vendor_usable=False, ev_vendor_observation_date=vendor_ev.get('date') if vendor_ev else pd.NaT, ev_vendor_source_row_id=vendor_ev.get('source_row_id') if vendor_ev else None, eps_approximation=True, common_income_attribution_proxy=True, excess_cash_proxy=True, tax_rate_proxy=tax_map.get(sector, 0.21), tax_proxy_fit_end=pd.Timestamp('2017-12-31'), identity_cik_verified=expected is not None, debt_free=bool(np.isfinite(debt) and debt == 0), nonpositive_equity=bool(np.isfinite(common) and common <= 0), no_interest_expense=bool(inputs.get('interestexpense_ttm') == 0), income_accounting_reconciliation_failed=income_qc, bs_accounting_reconciliation_failed=bs_qc, cf_accounting_or_semantics_failed=cf_qc, net_debt_definition_discrepancy=bool(np.isfinite(vendor_net) and (not net_coherent)), **metadata, **{k: v for k, v in inputs.items() if '_lag' not in k})
        row.update(latest_income_fiscal_end=periods.get('income'), latest_cf_fiscal_end=periods.get('cashflow'), latest_bs_fiscal_end=periods.get('balance'), market_cap_asof_date=periods.get('market_cap'), enterprise_value_asof_date=periods.get('market_cap') if np.isfinite(inputs['enterprise_value']) else pd.NaT, fundamental_age_days=max([metadata.get(x + '_fiscal_age_days', 0) for x in ['income', 'cf', 'bs']]), net_income_ttm=inputs.get('netincome_ttm'), ocf_ttm=inputs.get('operatingcashflow_ttm'), fcf_ttm=inputs.get('freecashflow_ttm'), accepted_timestamp_timezone_assumed='America/New_York')
        accepted = [publication_time(r.get('accepteddate'), None)[0] for r in [i, c, b] if r is not None]
        accepted = [t for t in accepted if pd.notna(t)]
        row['latest_filing_accepted_at'] = max(accepted) if accepted else pd.NaT
        for factor in ALL_FACTORS:
            row[factor + '_raw'] = factors[factor]
            row[factor + '_missing_reason'] = reasons[factor]
            row[factor + '_applicable'] = applicable(factor, sector, subtype)
        output.append(row)
    f = pd.DataFrame(output).sort_values(['month_end', 'security_id']).reset_index(drop=True)
    result = finalize(f, monthly, pd.DataFrame(lineage))
    result['calibration'] = dict(fit_cutoff='2017-12-31', floor_currency_groups=True, floors=floor_map, tax_proxies=tax_map)
    return result

def finalize(f, monthly, lineage):
    f = f.copy()
    f['financial_subtype'] = [classify(s, i) for s, i in zip(f.sector_clean, f.industry)]
    f['peer_group_used'] = np.where(f.sector_clean.eq('Financials'), f.sector_clean + '::' + f.financial_subtype, f.sector_clean)
    f['fundamental_age_days'] = f[['income_fiscal_age_days', 'cf_fiscal_age_days', 'bs_fiscal_age_days']].max(axis=1)
    applicability = []
    for (sector, subtype), group in f.groupby(['sector_clean', 'financial_subtype']):
        for factor in ALL_FACTORS:
            substitute = 'equity_to_assets' if sector == 'Financials' and factor == 'debt_to_assets' else 'roa' if sector == 'Financials' and factor == 'roic' else None
            applicability.append(dict(sector=sector, financial_subtype=subtype, factor_id=factor, applicable=applicable(factor, sector, subtype), substitute_factor_id=substitute, preferred_peer_group=group.peer_group_used.iloc[0], direction='lower' if factor in LOWER else 'higher', scoring_method='within-month percentile', null_policy='structural NULL; no sector-median imputation', min_peer_count=15, version=VERSION))
    f, quality, thresholds = score_factors_fast(f)
    for family, fs in FACTORS.items():
        members = fs + (['roa'] if family == 'profitability' else ['equity_to_assets'] if family == 'balance_sheet' else [])
        scores = f[[x + '_sector_score' for x in members]]
        eligible = f[[x + '_applicable' for x in members]].sum(axis=1)
        composite, count = composite_score(scores, eligible)
        f[family + '_factor_count'] = count
        f[family + '_composite'] = composite
    applicable_count = f[[x + '_applicable' for x in ALL_FACTORS]].sum(axis=1)
    f['quality_coverage_pct'] = f[[x + '_clean' for x in ALL_FACTORS]].notna().sum(axis=1) / applicable_count.replace(0, np.nan)
    f['growth_unavailable_negative_base'] = f[[x + '_missing_reason' for x in FACTORS['growth']]].eq('negative_base').any(axis=1)
    f['growth_unavailable_small_base'] = f[[x + '_missing_reason' for x in FACTORS['growth']]].eq('near_zero_denominator').any(axis=1)
    lineage = pd.DataFrame(lineage)
    assert not f.duplicated(['security_id', 'month_end']).any() and len(f) == len(monthly)
    assert (lineage.available_at <= lineage.feature_cutoff_at).all()
    assert (thresholds.fit_end < thresholds.month_end).all()
    values = f[[x + '_sector_score' for x in ALL_FACTORS]].stack().dropna()
    assert values.between(0, 100).all()
    assert not np.isinf(f.select_dtypes(include='number').to_numpy()).any()
    coverage = f.groupby('month_end')[[x + '_clean' for x in ALL_FACTORS]].count()
    report = dict(status='passed', rows=len(f), securities=f.security_id.nunique(), months=f.month_end.nunique(), baseline_factors=len(BASE_FACTORS), additional_substitutes=len(EXTRAS), latest_snapshot=str(f.month_end.max().date()), mean_valid_applicable_coverage=float(f.quality_coverage_pct.mean()), pit_revision_uncertain_fraction=1.0, source_notebooks=SOURCES, quarterly_balance_only=True, annual_cashflow_use='reconciliation only', sector_classification='retrospectively standardized; true historical GICS unavailable', enterprise_value='explicit source-backed monthly reconstruction; quarterly vendor EV retained only for audit', no_labels_in_feature_table=True, trading_cost_bps=0, model_primary_target='top20; outperform target separate', unavailable_extensions=['CET1', 'NIM', 'NPL', 'insurance_combined_ratio', 'FFO', 'AFFO'], version=VERSION)
    return dict(features=f, quality=quality, lineage=lineage, thresholds=thresholds, validation=report)
