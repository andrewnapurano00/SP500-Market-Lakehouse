"""Strict semantic parity gate; never intersect away missing securities."""
import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype, is_bool_dtype


def reconcile_frames(expected, actual, keys, *, atol=1e-10, rtol=1e-8):
    from .transforms import _unique
    if atol < 0 or rtol < 0 or not np.isfinite([atol, rtol]).all():
        raise ValueError('Finite nonnegative tolerances required')
    _unique(expected, keys)
    _unique(actual, keys)
    if set(expected.columns) != set(actual.columns):
        raise AssertionError('Column contract mismatch')
    left = expected.set_index(keys).sort_index()
    right = actual.set_index(keys).sort_index()
    if not left.index.equals(right.index):
        raise AssertionError('Exact cohort mismatch')
    report = {}
    for col in left.columns:
        a, b = left[col], right[col]
        if not a.isna().equals(b.isna()):
            raise AssertionError(f'NULL mismatch: {col}')
        valid = a.notna()
        if is_numeric_dtype(a) and is_numeric_dtype(b) and not is_bool_dtype(a) and not is_bool_dtype(b):
            av, bv = a[valid].to_numpy(dtype=float), b[valid].to_numpy(dtype=float)
            if not np.isfinite(av).all() or not np.isfinite(bv).all():
                raise AssertionError(f'Nonfinite numeric: {col}')
            if not np.isclose(av, bv, atol=atol, rtol=rtol).all():
                raise AssertionError(f'Numeric mismatch: {col}')
            report[col] = {'max_absolute_difference': float(np.max(np.abs(av-bv))) if len(av) else 0.0}
        elif not a[valid].equals(b[valid]):
            raise AssertionError(f'Exact value/dtype mismatch: {col}')
    return {'passed': True, 'rows': len(left), 'atol': atol, 'rtol': rtol, 'numeric_columns': report}
