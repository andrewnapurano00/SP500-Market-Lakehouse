import unittest
import pandas as pd
from sp500_lakehouse.model_inputs import assemble_model_inputs


class ModelInputTests(unittest.TestCase):
    def setUp(self):
        self.population=pd.DataFrame({'security_id':['a','b'],'ticker_latest':['AAA','BBB'],'historical_ticker':['OLD','BBB'],'sector':['Technology','Energy'],'week_end':['2026-09-30']*2,'ret_week_fwd1':[1.,None]})
        self.technical=pd.DataFrame({'ticker_latest':['AAA'],'date':['2026-09-30'],'return_21d':[.2],'realized_vol_63d':[.4],'target':[999]})
        self.financial=pd.DataFrame({'security_id':['a'],'ticker_latest':['AAA'],'month_end':['2026-09-30'],'financial_strength':[.8]})
        self.sector=pd.DataFrame({'sector':['Information Technology','Energy'],'date':['2026-09-30']*2,'proxy_source_date':['2026-09-30']*2,'sector_return_21d':[.1,.05],'sector_realized_vol_63d':[.2,.3]})
        self.macro=pd.DataFrame({'date':['2026-09-25','2026-09-29'],'vix_level':[20.,21.]})
        self.features=['return_21d','financial_strength','vix_level','stock_excess_sector_return_21d','stock_to_sector_vol_ratio_63d']
        self.options=dict(signal_cutoff_at='2026-09-30T20:00Z',as_of_utc='2026-11-08T00:00Z',sector_aliases={'Technology':'Information Technology'})

    def run_assembly(self,**overrides):
        args=dict(population=self.population,technical=self.technical,financial=self.financial,sector=self.sector,macro=self.macro,signal_date='2026-09-30',feature_columns=self.features,**self.options)
        args.update(overrides)
        return assemble_model_inputs(**args)

    def test_preserve_population_exact_formulas_and_missingness(self):
        f,e=self.run_assembly()
        self.assertEqual(f.security_id.tolist(),['a','b'])
        self.assertEqual(f.loc[0,'stock_excess_sector_return_21d'],.1)
        self.assertEqual(f.loc[0,'stock_to_sector_vol_ratio_63d'],2.)
        self.assertTrue(pd.isna(f.loc[1,'financial_strength']))
        self.assertEqual(f.vix_level.tolist(),[21.,21.])
        self.assertEqual(e['missing_sources']['technical'],['b'])
        self.assertEqual(e['availability_quality'],'UNVERIFIED_VINTAGE')
        self.assertEqual(list(f),['security_id','signal_month']+self.features)

    def test_outcome_poisoning_cannot_change_features_or_lineage(self):
        a,e=self.run_assembly()
        self.population['ret_week_fwd1']=[-999,999]
        self.technical['target']=-1000
        b,g=self.run_assembly()
        pd.testing.assert_frame_equal(a,b)
        self.assertEqual(e['source_hashes'],g['source_hashes'])
        with self.assertRaises(ValueError):self.run_assembly(feature_columns=['target'])

    def test_nullable_string_hash_is_order_independent_and_unambiguous(self):
        self.population['note']=pd.Series([pd.NA,'a|b'],dtype='string')
        a,e=self.run_assembly()
        b,g=self.run_assembly(population=self.population.iloc[::-1])
        pd.testing.assert_frame_equal(a,b)
        self.assertEqual(e['source_hashes'],g['source_hashes'])

    def test_identity_mismatch_and_ambiguous_routes_fail(self):
        bad=self.financial.copy();bad['ticker_latest']='ACQUIRER'
        with self.assertRaises(ValueError):self.run_assembly(financial=bad)
        bad=self.population.copy();bad['ticker_latest']='AAA'
        with self.assertRaises(ValueError):self.run_assembly(population=bad)
        bad=self.technical.assign(security_id='b')
        with self.assertRaises(ValueError):self.run_assembly(technical=bad)
        with self.assertRaises(ValueError):self.run_assembly(technical=pd.concat([self.technical,self.technical]))

    def test_stale_and_future_source_clock_fail(self):
        with self.assertRaises(ValueError):self.run_assembly(macro=self.macro.assign(date=['2026-09-20','2026-09-29']))
        with self.assertRaises(ValueError):self.run_assembly(technical=self.technical.assign(date='2026-10-01'))
        with self.assertRaises(ValueError):self.run_assembly(financial=self.financial.assign(income_available_at='2026-10-01T00:00Z'))
        with self.assertRaises(ValueError):self.run_assembly(financial=self.financial.assign(first_seen_at='2026-10-01T00:00Z'))
        with self.assertRaises(ValueError):self.run_assembly(sector=self.sector.assign(proxy_source_date='2026-09-29'))

    def test_strict_rejects_legacy_and_accepts_complete_observed_clocks(self):
        with self.assertRaises(ValueError):self.run_assembly(mode='strict')
        sources={}
        for name in ('population','technical','financial','sector','macro'):
            f=getattr(self,name).copy()
            for clock in ('source_release_at','eligible_at','first_seen_at','ingested_at'):f[clock]='2026-09-30T19:00Z'
            f['availability_quality']='observed_vintage'
            sources[name]=f
        frame,e=self.run_assembly(mode='strict',**sources)
        self.assertEqual(len(frame),2)
        self.assertEqual(e['availability_quality'],'observed_vintage')

    def test_replay_ingestion_clock_is_bounded_by_asof_never_certified(self):
        frame,e=self.run_assembly(financial=self.financial.assign(ingested_at='2026-10-31T00:00Z'))
        self.assertEqual(e['availability_quality'],'UNVERIFIED_VINTAGE')
        self.assertFalse(e['original_vintage_certified'])
        with self.assertRaises(ValueError):self.run_assembly(financial=self.financial.assign(ingested_at='2026-11-09T00:00Z'))
        with self.assertRaises(ValueError):self.run_assembly(financial=self.financial.assign(ingested_at='2026-10-31T00:00Z'),mode='strict')


if __name__=='__main__':unittest.main()
