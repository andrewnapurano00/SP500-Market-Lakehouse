"""Explicit research and frozen-scoring consumer boundaries for Gold."""
import hashlib
import json
from pathlib import Path
import pandas as pd
from .reader import GoldReader


def export_consumer_panel(reader, destination, *, months=None, include_targets=False):
    """Write an immutable Parquet + binding sidecar for existing notebook workbenches."""
    destination = Path(destination)
    sidecar = destination.with_suffix(destination.suffix+'.source.json')
    if destination.exists() or sidecar.exists(): raise FileExistsError('Consumer export already exists')
    frame = reader.read(months,include_targets=include_targets)
    destination.parent.mkdir(parents=True,exist_ok=True)
    frame.to_parquet(destination,index=False)
    evidence = dict(provider='databricks_gold',source_binding=reader.binding,
        source_as_of=getattr(reader,'source_as_of',reader.binding.get('as_of')),
        source_binding_sha256=reader.sha256,rows=len(frame),columns=list(frame),
        include_targets=include_targets,months=sorted(frame.signal_month.unique()),
        data_sha256=hashlib.sha256(destination.read_bytes()).hexdigest())
    sidecar.write_text(json.dumps(evidence,sort_keys=True,indent=2),encoding='utf-8')
    return evidence


def read_consumer_export(path, *, expected_binding_sha256):
    """Read only a hash-pinned export; never silently fall back to local PostgreSQL."""
    path = Path(path)
    evidence = json.loads(path.with_suffix(path.suffix+'.source.json').read_text(encoding='utf-8'))
    from .reader import binding_sha256
    if evidence.get('provider') != 'databricks_gold' or evidence.get('source_binding_sha256') != expected_binding_sha256:
        raise ValueError('Consumer export source binding mismatch')
    if binding_sha256(evidence['source_binding']) != expected_binding_sha256:
        raise ValueError('Consumer source binding digest mismatch')
    if hashlib.sha256(path.read_bytes()).hexdigest() != evidence['data_sha256']:
        raise ValueError('Consumer export data digest mismatch')
    frame = pd.read_parquet(path)
    if len(frame)!=evidence['rows'] or list(frame)!=evidence['columns']:
        raise ValueError('Consumer export schema/row count mismatch')
    frame.attrs['source_binding_sha256'] = expected_binding_sha256
    frame.attrs['source_as_of'] = evidence.get('source_as_of')
    frame.attrs['source_provider']='databricks_gold'
    return frame


def frozen_score_transport_parity(reference, transported, predictor_columns, scorer, *, keys=('security_id','signal_date')):
    """Replay the same frozen scorer on identical matched rows; never fit a model.

    Full-history cohort changes must be assessed separately: stock ranks depend
    on the contemporaneous cohort. This comparison proves transport equivalence.
    """
    from .transforms import _unique
    from .reconcile import reconcile_frames
    keys=list(keys)
    _unique(reference,keys); _unique(transported,keys)
    projection=keys+list(predictor_columns)
    proof=reconcile_frames(reference[projection],transported[projection],keys)
    if not proof['passed']: raise ValueError('Input transport differs before frozen replay')
    a=reference.sort_values(keys).reset_index(drop=True)
    b=transported.sort_values(keys).reset_index(drop=True)
    import numpy as np
    first,second=np.asarray(scorer(a)),np.asarray(scorer(b))
    np.testing.assert_allclose(first,second,atol=1e-12,rtol=1e-10)
    np.testing.assert_array_equal(np.argsort(first,axis=0,kind='stable'),np.argsort(second,axis=0,kind='stable'))
    np.testing.assert_array_equal(first>=.5,second>=.5)
    return dict(passed=True,rows=len(a),max_absolute_score_difference=float(np.max(np.abs(first-second))) if first.size else 0.0,refit=False,
        ranks_identical=True,classification_threshold_identical=True,atol=1e-12,rtol=1e-10,
        scope='MATCHED_COHORT_FROZEN_TRANSPORT_PARITY',input_comparison=proof)
