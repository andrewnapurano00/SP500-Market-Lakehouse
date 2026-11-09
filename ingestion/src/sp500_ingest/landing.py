"""Immutable JSONL landing; unchanged payloads with explicit vintage uncertainty."""
import hashlib
import json
import os
import re
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False, default=str)


def digest(value):
    return hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()


def safe_parameters(parameters):
    forbidden = ('key', 'token', 'secret', 'password', 'authorization', 'credential')
    if isinstance(parameters, list):
        return [safe_parameters(v) for v in parameters]
    if not isinstance(parameters, dict):
        return parameters
    return {str(k): safe_parameters(v) for k, v in parameters.items()
            if not any(word in str(k).lower() for word in forbidden)}


def component(value):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+', str(value)) or str(value) in ('.', '..'):
        raise ValueError('Unsafe path component')
    return str(value)


def write_records(root, source, entity, records, *, request_parameters=None, run_id=None,
                  source_kind='original_api_payload', retrieved_at=None, source_record_key=None,
                  source_key_strategy=None):
    run_id = component(run_id or uuid.uuid4().hex)
    if source_kind not in ('original_api_payload', 'postgres_reconstruction', 'reviewed_membership'):
        raise ValueError('Unknown source_kind')
    instant = datetime.fromisoformat(retrieved_at.replace('Z', '+00:00')) if retrieved_at else datetime.now(timezone.utc)
    if instant.tzinfo is None or instant.utcoffset() is None:
        raise ValueError('retrieved_at must have an explicit timezone')
    timestamp = instant.astimezone(timezone.utc).isoformat()
    folder = Path(root) / component(source) / component(entity) / ('dt=' + timestamp[:10])
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / (run_id + '.jsonl')
    fd, temporary = tempfile.mkstemp(dir=folder, prefix='.landing-')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as stream:
            for record in records:
                key = source_record_key(record) if source_record_key else None
                payload_hash = digest(record)
                strategy = source_key_strategy or ('provided_business_key' if key is not None else 'payload_hash_business_key_unresolved')
                if key is None or key == '' or key == [] or key == {}:
                    key = payload_hash
                    strategy = 'payload_hash_business_key_unresolved'
                elif not isinstance(key, str):
                    key = canonical(key)
                if not key.strip():
                    raise ValueError('source_record_key must be nonempty')
                meta = dict(source=source, entity=entity, dt=timestamp[:10], run_id=run_id,
                            retrieved_at=timestamp, ingested_at=timestamp,
                            request_parameters=safe_parameters(request_parameters or {}),
                            source_kind=source_kind, payload_hash=payload_hash,
                            source_record_key=key, source_key_strategy=strategy,
                            availability_quality='historical_vintage_unknown',
                            source_file=str(target))
                meta['event_id'] = digest([source, entity, key, payload_hash])
                stream.write(canonical(dict(meta=meta, data=record)) + '\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, target)  # atomic no-clobber publication
    finally:
        Path(temporary).unlink(missing_ok=True)
    return target


class Checkpoints:
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def path(self, request):
        return self.root / (digest(request) + '.json')

    def completed(self, request):
        path = self.path(request)
        if not path.exists():
            return None
        entry = json.loads(path.read_text(encoding='utf-8'))
        artifact = Path(entry['file'])
        if not artifact.exists() or hashlib.sha256(artifact.read_bytes()).hexdigest() != entry['sha256']:
            raise ValueError('Checkpoint landing artifact missing or modified')
        return artifact

    def commit(self, request, artifact):
        artifact = Path(artifact).resolve()
        entry = dict(file=str(artifact), sha256=hashlib.sha256(artifact.read_bytes()).hexdigest())
        fd, temporary = tempfile.mkstemp(dir=self.root)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as stream:
                json.dump(entry, stream)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.path(request))
        finally:
            Path(temporary).unlink(missing_ok=True)
