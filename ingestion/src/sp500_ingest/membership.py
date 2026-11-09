"""Normalize reviewed identities; no generated security identifiers."""
import csv
from datetime import date


def normalize_membership(records):
    output, seen = [], set()
    for record in records:
        row = dict(record)
        for field in ('security_id', 'date', 'ticker'):
            if row.get(field) is None or not str(row[field]).strip():
                raise ValueError(f'Reviewed membership requires {field}')
        day = date.fromisoformat(str(row['date'])[:10]).isoformat()
        key = (str(row['security_id']), day)
        if key in seen:
            raise ValueError('Duplicate security/date membership')
        seen.add(key)
        row.update(security_id=key[0], date=day)
        output.append(row)
    return output


def load_reviewed_csv(path):
    with open(path, encoding='utf-8-sig', newline='') as stream:
        return normalize_membership(csv.DictReader(stream))
