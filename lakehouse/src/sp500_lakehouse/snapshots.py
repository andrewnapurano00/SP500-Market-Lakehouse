"""Immutable local Gold exports; conflicting IDs always fail closed."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile


def write_snapshot(frame, root, feature_version, run_id, data_snapshot_id, source_hashes, feature_columns=None):
    from .transforms import _unique, is_outcome_column, project_features
    if any(is_outcome_column(c) for c in frame.columns):
        raise ValueError('Outcomes prohibited in feature snapshots')
    if feature_columns is not None:
        frame = project_features(frame, feature_columns)
    _unique(frame, ['security_id', 'signal_month'])
    for name in (feature_version, run_id, data_snapshot_id):
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', name):
            raise ValueError('Invalid manifest identifier')
    if not source_hashes or any(not re.fullmatch('[0-9a-f]{64}', value) for value in source_hashes.values()):
        raise ValueError('SHA256 source lineage is required')
    data = frame.copy()
    for key, value in dict(feature_version=feature_version, run_id=run_id, data_snapshot_id=data_snapshot_id).items():
        if key in data and not data[key].eq(value).all():
            raise ValueError(f'Conflicting {key}')
        data[key] = value
    data = data.sort_values(['signal_month', 'security_id']).reset_index(drop=True)
    payload = data.to_json(orient='table', index=False, date_format='iso', double_precision=15).encode()
    manifest = dict(feature_version=feature_version, run_id=run_id, data_snapshot_id=data_snapshot_id,
                    rows=len(data), columns=list(data.columns), source_hashes=dict(sorted(source_hashes.items())),
                    data_sha256=hashlib.sha256(payload).hexdigest(), format='pandas-table-json-v1')
    manifest_bytes = json.dumps(manifest, sort_keys=True, indent=2).encode()
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    destination = root / data_snapshot_id
    if destination.exists():
        if (destination / 'manifest.json').read_bytes() != manifest_bytes or (destination / 'data.json').read_bytes() != payload:
            raise FileExistsError('Immutable snapshot ID conflict')
        return manifest
    stage = Path(tempfile.mkdtemp(prefix='.snapshot-', dir=root))
    try:
        (stage / 'data.json').write_bytes(payload)
        (stage / 'manifest.json').write_bytes(manifest_bytes)
        os.rename(stage, destination)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return manifest
