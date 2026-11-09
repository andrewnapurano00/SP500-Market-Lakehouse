"""Read-only Phase 0 baseline; explicit table allowlist and bounded export."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(Path(__file__).resolve().parents[1]/'ingestion/src')]
from sp500_ingest.baseline import inventory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--table', action='append', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--landing', type=Path)
    parser.add_argument('--export-limit', type=int, default=0)
    parser.add_argument('--date-column')
    parser.add_argument('--start')
    parser.add_argument('--end')
    parser.add_argument('--timeout-ms', type=int, default=60000)
    parser.add_argument('--business-key', action='append', default=[], metavar='TABLE:COL1,COL2',
                        help='Explicit key override, validated for catalog existence, nulls and duplicates')
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Output already exists; choose a new immutable baseline manifest path')
    business_keys = {}
    for specification in args.business_key:
        table, separator, columns = specification.partition(':')
        if not separator or not table or not columns or table in business_keys:
            parser.error('Business keys require unique TABLE:COL1,COL2 specifications')
        business_keys[table] = columns.split(',')
    # Existing project connection helper loads root .env; never serialize connection URL.
    from sp500_ingest.postgres import engine
    db = engine()
    try:
        report = inventory(db, args.table, output_root=args.landing, export_limit=args.export_limit,
                           date_column=args.date_column, start=args.start,end=args.end,timeout_ms=args.timeout_ms,
                           business_keys=business_keys)
    finally:
        db.dispose()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x',encoding='utf-8') as stream:
        json.dump(report,stream,indent=2,default=str)
    print(str(args.output))

if __name__ == '__main__':
    main()
