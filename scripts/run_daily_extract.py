"""Explicitly budgeted API extraction; reruns verify immutable landing checkpoints."""
import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'ingestion/src'))
from sp500_ingest.fmp import FMPClient, HTTPClient, ENDPOINTS
from sp500_ingest.landing import Checkpoints, write_records


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--entity', choices=ENDPOINTS, required=True)
    parser.add_argument('--ticker', action='append', required=True)
    parser.add_argument('--start', required=True)
    parser.add_argument('--end', required=True)
    parser.add_argument('--landing', type=Path, required=True)
    parser.add_argument('--checkpoints', type=Path, required=True)
    parser.add_argument('--max-requests', type=int, required=True)
    parser.add_argument('--batch-id', required=True, help='New ID intentionally observes new source revisions')
    args=parser.parse_args()
    load_dotenv(Path(__file__).resolve().parents[1]/'.env')
    checkpoints=Checkpoints(args.checkpoints)
    client=FMPClient(os.getenv('FMP_API_KEY') or os.getenv('FMP_APIKEY'), HTTPClient(max_requests=args.max_requests))
    for ticker in args.ticker:
        request=dict(source='fmp',entity=args.entity,ticker=ticker,start=args.start,end=args.end,batch_id=args.batch_id)
        if checkpoints.completed(request):
            continue
        payload,params=client.fetch(args.entity,ticker,args.start,args.end)
        artifact=write_records(args.landing,'fmp',args.entity,[payload],request_parameters={**params,'ticker':ticker},
                               source_record_key=lambda _: dict(entity=args.entity,ticker=ticker,parameters=params))
        checkpoints.commit(request,artifact)
        print(str(artifact))

if __name__=='__main__':
    main()
