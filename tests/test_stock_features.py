import unittest
from pathlib import Path
import numpy as np
import pandas as pd
from sp500_lakehouse.stock_features import from_prices,FEATURE_COLUMNS
from sp500_lakehouse.legacy import load_legacy_technical_builder

class StockFormulaTests(unittest.TestCase):
    def test_original_formula_parity_and_stable_identity_isolation(self):
        days=pd.bdate_range('2024-01-01',periods=400)
        prices=pd.DataFrame(dict(security_id=['a']*400+['b']*400,
            date=list(days)*2,adj_close=np.r_[100+np.arange(400)*.1+np.sin(np.arange(400)),60+np.arange(400)*.05],
            volume=100000+np.arange(800)*17))
        actual=from_prices(prices)
        legacy,cols,_=load_legacy_technical_builder(Path(__file__).resolve().parents[1])
        expected=legacy(prices.assign(ticker_latest=prices.security_id.map({'a':'0','b':'1'})))
        expected['security_id']=expected.ticker_latest.map({'0':'a','1':'b'})
        pd.testing.assert_frame_equal(actual.set_index(['security_id','date'])[cols].sort_index(),expected.set_index(['security_id','date'])[cols].sort_index(),check_exact=True)
        self.assertTrue(actual.groupby('security_id').head(1)[FEATURE_COLUMNS].isna().all().all())

if __name__=='__main__':unittest.main()
