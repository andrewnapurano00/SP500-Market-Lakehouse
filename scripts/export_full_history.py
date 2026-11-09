"""Export every reviewed public PostgreSQL table using one read-only snapshot."""
import argparse
import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(PROJECT/'ingestion/src')]
from sp500_ingest.bulk import export_history


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True,help='New immutable export directory')
    parser.add_argument('--batch-rows',type=int,default=50000)
    args=parser.parse_args()
    from sp500_ingest.postgres import engine
    db=engine()
    try:
        report=export_history(db,args.output,json.loads((PROJECT/'config/table_contracts.json').read_text()),args.batch_rows)
    finally:
        db.dispose()
    print(json.dumps(dict(manifest=str(args.output/'manifest.json'),tables=len(report['tables']),rows=report['total_rows'],bytes=report['total_bytes'])))


if __name__=='__main__': main()
