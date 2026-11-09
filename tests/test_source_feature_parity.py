import ast
import json
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
import pandas_market_calendars as mcal
from sp500_lakehouse import macro_features as macro, sector_features as sector

ROOT=Path(__file__).resolve().parents[1]

def original(path,names):
    mapping={'sp_macro_cross_asset_features.ipynb':'macro_features.py','src/sector_technical_features.py':'sector_features.py'}
    path=ROOT/'tests/reference'/mapping[path]
    texts=[''.join(c['source']) for c in json.loads(path.read_text(encoding='utf8'))['cells'] if c['cell_type']=='code'] if path.suffix=='.ipynb' else [path.read_text()]
    nodes=[]
    for text in texts:
        for node in ast.parse(text).body:
            if isinstance(node,ast.FunctionDef) and node.name in names:nodes.append(node)
    scope={'np':np,'pd':pd,'mcal':mcal,**{k:getattr(sector,k) for k in ('PROXIES','CONTEXT_FEATURES','SECTOR_FEATURES')},'RATE_FIELDS':macro.RATE_FIELDS}
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),scope)
    return scope

class SourceFormulaParity(unittest.TestCase):
    def macro_rows(self):
        output=[]
        for i,day in enumerate(pd.bdate_range('2019-01-01',periods=400)):
            def add(entity,ticker,values):
                output.append(dict(entity=entity,api_lookup_ticker=ticker,observation_date=day,run_id='r',values=json.dumps(values)))
            for j,ticker in enumerate(macro.SYMBOLS.values()):add('macro_prices',ticker,{'adjclose':100+j+i*.1+np.sin(i/9)})
            add('vix','^VIX',{'close':20+np.sin(i/13)})
            add('treasury','',{'month3':2+i*.001,'year2':3+i*.001,'year10':4+i*.001,'year30':5+i*.001})
        return pd.DataFrame(output)
    def test_macro_exact_original_and_parsing(self):
        frame=self.macro_rows();obs=macro.normalized_observations(frame,run_id='r')
        expected=original('sp_macro_cross_asset_features.ipynb',{'build_features'})['build_features'](obs)
        pd.testing.assert_frame_equal(macro.from_observations(frame,run_id='r'),expected,check_exact=True)
        self.assertTrue((obs.date>obs.observation_date).all())
    def test_sector_exact_original_and_parsing(self):
        rows=[];normalized=[]
        for j,ticker in enumerate(set(sector.PROXIES.values())|{'SPY'}):
            for i,day in enumerate(pd.bdate_range('2019-01-01',periods=400)):
                value=100+j+i*.1+np.sin(i/9)
                rows.append(dict(date=day,proxy_ticker=ticker,adj_close=value,volume=1000+i))
                normalized.append(dict(entity='prices',security_id=None,run_id='r',observation_date=day,api_lookup_ticker=ticker,values=json.dumps({'adjclose':value,'volume':1000+i})))
        expected=original('src/sector_technical_features.py',{'calculate'})['calculate'](pd.DataFrame(rows))
        pd.testing.assert_frame_equal(sector.from_observations(pd.DataFrame(normalized),run_id='r'),expected,check_exact=True)
    def test_macro_missing_and_conflicting_series_fail(self):
        frame=self.macro_rows()
        with self.assertRaises(ValueError):macro.from_observations(frame.loc[frame.entity.ne('vix')],run_id='r')
        other=frame.iloc[[0]].copy();other['values']='{"adjclose":999}'
        with self.assertRaises(ValueError):macro.from_observations(pd.concat([frame,other]),run_id='r')
        with self.assertRaises(ValueError):macro.from_observations(frame,run_id='r',row_cap=300)
