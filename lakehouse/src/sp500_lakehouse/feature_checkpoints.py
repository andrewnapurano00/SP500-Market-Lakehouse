"""Hash-verified governed checkpoints after expensive original-formula builds."""
from pathlib import Path
import hashlib,json,re
import pandas as pd
from .spark_frames import parquet_bytes

def checkpoint_identity(inputs):
    return hashlib.sha256(json.dumps(inputs,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()

def load_checkpoint(cfg,identity):
    if not re.fullmatch('[a-f0-9]{64}',identity):raise ValueError('Invalid checkpoint identity')
    root=Path(cfg.volume('exports'))/'_feature_checkpoints'/identity
    path=root/'manifest.json'
    if not path.exists():return None
    manifest=json.loads(path.read_text())
    if manifest['inputs_sha256']!=identity:raise ValueError('Feature checkpoint identity mismatch')
    frames={}
    for name,item in manifest['files'].items():
        path=root/item['file']
        if path.name!=item['file'] or hashlib.sha256(path.read_bytes()).hexdigest()!=item['sha256']:raise ValueError('Feature checkpoint integrity failure')
        frames[name]=pd.read_parquet(path)
    canonical={family:frames.pop('canonical_'+family) for family in manifest['canonical_families']}
    frames['_canonical_financial']=canonical
    return frames,manifest['evidence']

def save_checkpoint(cfg,identity,frames,evidence):
    if not re.fullmatch('[a-f0-9]{64}',identity):raise ValueError('Invalid checkpoint identity')
    root=Path(cfg.volume('exports'))/'_feature_checkpoints'/identity
    root.mkdir(parents=True,exist_ok=True)
    flat={name:frame for name,frame in frames.items() if name!='_canonical_financial'}
    flat.update({'canonical_'+family:frame for family,frame in frames['_canonical_financial'].items()})
    files={}
    for name,frame in flat.items():
        if not name.replace('_','').isalnum():raise ValueError('Unsafe checkpoint family')
        order=[c for c in ['security_id','symbol','sector','date','month_end','week_end','source_row_id'] if c in frame]
        data=parquet_bytes(frame.sort_values(order).reset_index(drop=True) if order else frame)
        path=root/(name+'.parquet');digest=hashlib.sha256(data).hexdigest()
        if path.exists():
            if hashlib.sha256(path.read_bytes()).hexdigest()!=digest:raise ValueError('Immutable checkpoint conflict')
        else:
            with path.open('xb') as stream:stream.write(data)
        files[name]=dict(file=path.name,sha256=digest,rows=len(frame))
    manifest=dict(inputs_sha256=identity,files=files,canonical_families=sorted(frames['_canonical_financial']),evidence=evidence)
    data=json.dumps(manifest,sort_keys=True,indent=2,allow_nan=False).encode()
    path=root/'manifest.json'
    if path.exists():
        if path.read_bytes()!=data:raise ValueError('Immutable checkpoint commit conflict')
    else:
        with path.open('xb') as stream:stream.write(data)
    return str(path)
