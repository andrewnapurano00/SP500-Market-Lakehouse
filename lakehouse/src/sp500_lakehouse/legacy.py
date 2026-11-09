"""Adapters to original formulas, without executing notebook SQL or API cells.

Only pure source functions are loaded; notebook SQL and API cells never execute.
"""
import ast
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd


def load_legacy_technical_builder(workspace):
    """Return original pure builder, feature names and immutable source evidence."""
    path = Path(workspace) / 'sp_technical_features.ipynb'
    if path.exists():
        notebook = json.loads(path.read_text(encoding='utf-8'))
    else:
        path=Path(workspace)/'tests/reference/stock_technicals.py'
        notebook={'cells':[{'cell_type':'code','source':[path.read_text(encoding='utf8')]}]}
    nodes = []
    functions = {'normalize_keys', 'add_technical_features'}
    constants = {'FEATURE_COLUMNS', 'KEY_COLUMNS'}
    for cell in notebook['cells']:
        if cell['cell_type'] != 'code':
            continue
        tree = ast.parse(''.join(cell['source']))
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name in functions:
                nodes.append(node)
            elif isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id in constants:
                ast.literal_eval(node.value)  # refuse executable constant expressions
                nodes.append(node)
    if {n.name for n in nodes if isinstance(n, ast.FunctionDef)} != functions:
        raise ValueError('Legacy technical source contract changed')
    namespace = {'pd': pd, 'np': np}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), namespace)
    return namespace['add_technical_features'], namespace['FEATURE_COLUMNS'], {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'source': str(path)}


def stock_technicals(prices, workspace):
    """Original observed-row formulas grouped by stable IDs, never reused tickers."""
    from .transforms import _unique
    _unique(prices, ['security_id', 'date'])
    builder, _, provenance = load_legacy_technical_builder(workspace)
    data = prices[['security_id', 'date', 'adj_close', 'volume']].copy()
    # Legacy normalize_keys uppercases routing keys; numeric surrogate prevents collisions.
    identities = list(data.security_id.unique())
    tokens = {sid: str(i) for i, sid in enumerate(identities)}
    data['ticker_latest'] = data.security_id.map(tokens)
    out = builder(data)
    out['security_id'] = out.ticker_latest.map({v: k for k, v in tokens.items()})
    out = out.drop(columns='ticker_latest')
    out.attrs['source_sha256'] = provenance['sha256']
    out.attrs['parity_status'] = 'original_formula_adapter_requires_output_reconciliation'
    return out
