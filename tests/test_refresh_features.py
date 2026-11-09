import unittest
from unittest.mock import patch
import pandas as pd
from sp500_lakehouse.refresh_features import financial_capture,overlay,signal_macro_window

class RefreshFeatureTests(unittest.TestCase):
    def test_macro_window_uses_calendar_days_not_eight_business_rows(self):
        macro=pd.DataFrame(dict(date=pd.bdate_range('2026-10-01','2026-11-04'),value=range(25)))
        result=signal_macro_window(macro,'2026-10-30')
        self.assertEqual(str(result.date.min().date()),'2026-10-23')
        self.assertEqual(str(result.date.max().date()),'2026-10-30')
    def test_annual_evidence_retains_original_field_contract(self):
        rows=[]
        for entity in ['income','cashflow','balance','market_cap','enterprise']:
            rows.append(dict(entity=entity,run_id='r',statement_period='quarter',source_business_key=entity,
                observation_id=entity,api_lookup_ticker='AAA',values={'date':'2025-12-31','operatingcashflow':10}))
        rows.append(dict(entity='cashflow',run_id='r',statement_period='annual',source_business_key='annual',observation_id='annual',api_lookup_ticker='AAA',
            values={'date':'2025-12-31','operatingcashflow':40,'accepteddate':'2026-02-01 12:00:00','fillingdate':'2026-02-01'}))
        with patch('sp500_lakehouse.refresh_features.fundamentals.canonical_sources',return_value={}) as canonical:
            financial_capture(pd.DataFrame(rows).assign(retrieved_at='2026-11-08T00:00:00Z'),'r')
        evidence=canonical.call_args.kwargs['annual_verification']['AAA'][0]
        self.assertEqual(evidence['operatingCashFlow'],40)
        self.assertEqual(evidence['acceptedDate'],'2026-02-01 12:00:00')
        self.assertEqual(len(canonical.call_args.args[0]['cashflow']),1)
    def test_overlay_is_explicit_and_does_not_mutate_old_snapshot(self):
        base=pd.DataFrame(dict(key=['a','b'],value=[1,2]));fresh=pd.DataFrame(dict(key=['a'],value=[3]))
        result=overlay(base,fresh,['key']).set_index('key')
        self.assertEqual(result.loc['a','value'],3)
        self.assertEqual(base.iloc[0].value,1)
        with self.assertRaises(ValueError):overlay(base,pd.concat([fresh,fresh]),['key'])

if __name__=='__main__':unittest.main()
