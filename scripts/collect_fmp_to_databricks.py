"""Local FMP collector. Identity and destination are Databricks; no PostgreSQL.

Run with an authenticated Databricks SDK profile and local FMP_API_KEY. Immutable
raw/normalized landing is uploaded before a cloud normalization job is invoked.
"""
import argparse, json, os, sys, hashlib
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
from datetime import datetime, timezone
PROJECT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(PROJECT/'ingestion/src'),str(PROJECT/'lakehouse/src')]
from sp500_ingest.fmp import FMPClient,HTTPClient
from sp500_ingest.refresh import plan_requests,refresh
from sp500_lakehouse.reader import StatementQuery
from sp500_lakehouse.config import identifier

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--profile',default='SP500');p.add_argument('--warehouse-id',required=True)
    p.add_argument('--catalog',default='workspace');p.add_argument('--prefix',default='sp500')
    p.add_argument('--start-date',required=True);p.add_argument('--end-date',required=True)
    p.add_argument('--run-id',required=True);p.add_argument('--max-requests',type=int,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--ca-bundle')
    p.add_argument('--cli-path')
    p.add_argument('--only-security-id',help='Bounded onboarding of one already reviewed identity')
    p.add_argument('--without-context',action='store_true',help='Reuse previously committed macro/sector context; still capture membership')
    p.add_argument('--execute',action='store_true',help='Fetch and upload after printing bounded plan; otherwise plan only')
    args=p.parse_args()
    args.output=args.output.resolve()
    from dotenv import load_dotenv
    load_dotenv(PROJECT/'.env')
    if args.ca_bundle:os.environ['REQUESTS_CA_BUNDLE']=args.ca_bundle
    from databricks.sdk import WorkspaceClient
    if args.cli_path:os.environ['DATABRICKS_CLI_PATH']=str(Path(args.cli_path).resolve())
    w=WorkspaceClient(profile=args.profile)
    catalog,prefix=identifier(args.catalog),identifier(args.prefix)
    table=f'{catalog}.{prefix}_bronze.pg_sp500_monthly_population'
    query=StatementQuery(w,args.warehouse_id,max_rows=5000)
    identities=query(f'SELECT DISTINCT security_id,api_lookup_ticker FROM {table} WHERE week_end=(SELECT max(week_end) FROM {table})')
    key=os.getenv('FMP_API_KEY') or os.getenv('FMP_APIKEY')
    client=FMPClient(key,HTTPClient(max_requests=args.max_requests,verify=args.ca_bundle or True)) if args.execute else None
    current_ids=set(identities.security_id)
    if args.execute:
        # Capture constituents first. A new ticker must resolve to a reviewed
        # identity before requesting its history; never freeze the old universe.
        preflight=[job for job in plan_requests([],args.start_date,args.end_date) if job['entity'].startswith('membership')]
        membership=refresh(client,preflight,args.output/'landing',args.output/'checkpoints',args.run_id)
        current_file=next(item['normalized_file'] for item in membership if '/membership_current/' in item['normalized_file'].replace('\\','/'))
        symbols={json.loads(line)['data']['values']['symbol'] for line in Path(current_file).read_text(encoding='utf-8').splitlines()}
        routes=query(f'SELECT security_id,api_lookup_ticker FROM {catalog}.{prefix}_silver.dim_security')
        from databricks.sdk.errors import NotFound
        review_table=f'{catalog}.{prefix}_ops.reviewed_security_routes'
        try:w.tables.get(review_table)
        except NotFound:pass
        else:
            additional=query('SELECT security_id,api_lookup_ticker,identity_valid_from FROM '+review_table)
            import pandas as pd
            routes=pd.concat([routes.loc[~routes.security_id.isin(additional.security_id)],additional],ignore_index=True)
        from sp500_ingest.identity import price_identity
        selected=[];unresolved=[]
        for ticker in sorted(symbols):
            choices=routes.loc[routes.api_lookup_ticker.eq(ticker)]
            if ticker=='SKYD':choices=choices.loc[choices.security_id.eq(price_identity(ticker,args.end_date,'SKYD'))]
            if len(choices)!=1:unresolved.append(ticker)
            else:
                row=choices.iloc[0].to_dict()
                if not isinstance(row.get('identity_valid_from'),str):row.pop('identity_valid_from',None)
                selected.append(row)
        if unresolved:
            args.output.mkdir(parents=True,exist_ok=True)
            (args.output/'review_required.json').write_text(json.dumps(dict(unresolved_constituents=unresolved,policy='NO_GENERATED_SECURITY_IDS'),indent=2))
            raise ValueError('Reviewed stable identity required for constituents: '+','.join(unresolved))
        import pandas as pd
        identities=pd.DataFrame(selected);current_ids=set(identities.security_id)
        # Keep the latest held cohort until its next-month exits are valued,
        # including securities that have left the index.
        registry=f'{catalog}.{prefix}_ops.active_dataset'
        from databricks.sdk.errors import NotFound
        try:w.tables.get(registry)
        except NotFound:holding=query(f'SELECT DISTINCT security_id FROM {table} WHERE week_end=(SELECT max(week_end) FROM {table})')
        else:
            from sp500_lakehouse.reader import _table,binding_sha256
            active=query('SELECT binding_json,binding_sha256 FROM '+registry+" WHERE dataset_id='sp500'")
            if len(active)!=1:raise ValueError('One active source binding required')
            binding=json.loads(active.iloc[0].binding_json)
            if binding_sha256(binding)!=active.iloc[0].binding_sha256:raise ValueError('Active binding digest mismatch')
            item=binding['cohort'];qualified=_table(item['table']);version=int(item['version'])
            sql=f'{qualified} VERSION AS OF {version}'
            holding=query(f'SELECT security_id FROM {sql} WHERE signal_month=(SELECT max(signal_month) FROM {sql})')
        missing_holds=holding.loc[~holding.security_id.isin(identities.security_id)].merge(routes,on='security_id',how='left',validate='one_to_one')
        if missing_holds.api_lookup_ticker.isna().any():raise ValueError('Held identity lacks reviewed price route')
        identities=pd.concat([identities,missing_holds],ignore_index=True).drop_duplicates('security_id')
        identities=identities.astype(object).where(identities.notna(),None)
    if args.only_security_id:
        identities=identities.loc[identities.security_id.eq(args.only_security_id)]
        if len(identities)!=1:raise ValueError('One reviewed identity required for bounded onboarding')
    jobs=plan_requests(identities.to_dict('records'),args.start_date,args.end_date,include_context=not args.without_context)
    if args.without_context:
        jobs.extend(job for job in plan_requests([],args.start_date,args.end_date) if job['entity'].startswith('membership'))
    for job in jobs:
        if job['entity'] in ['prices','profile'] and job.get('security_id') and job['security_id'] not in current_ids:job['allow_empty']=True
    print(json.dumps(dict(run_id=args.run_id,planned_requests=len(jobs),max_requests=args.max_requests,identities=len(identities),execute=args.execute)),flush=True)
    if len(jobs)>args.max_requests:raise ValueError('Plan exceeds explicit request budget')
    if not args.execute:return
    audit=refresh(client,jobs,args.output/'landing',args.output/'checkpoints',args.run_id)
    destination=f'/Volumes/{catalog}/{prefix}_files/landing'
    groups={}
    for event in audit:
        for family in ['raw_file','normalized_file']:
            path=Path(event[family]); relative=path.relative_to(args.output/'landing').as_posix()
            groups.setdefault(path.relative_to(args.output/'landing').parent,[]).append(path)
    # Pack unchanged envelopes by entity/date; thousands of one-request files
    # become a few dozen governed files without changing individual records.
    packed=[]
    for relative,paths in groups.items():
        path=args.output/'transfer'/relative/(identifier(args.run_id)+'.jsonl')
        path.parent.mkdir(parents=True,exist_ok=True)
        temporary=path.with_suffix('.tmp')
        with temporary.open('wb') as stream:
            for original in sorted(set(paths)):
                with original.open('rb') as source:
                    for block in iter(lambda:source.read(8*1024*1024),b''):stream.write(block)
        if path.exists():
            if hashlib.sha256(path.read_bytes()).digest()!=hashlib.sha256(temporary.read_bytes()).digest():raise ValueError('Immutable local transfer conflict')
            temporary.unlink()
        else:temporary.replace(path)
        packed.append(path)
    def upload(path):
            relative=path.relative_to(args.output/'transfer').as_posix();target=destination+'/'+relative
            w.files.create_directory(target.rsplit('/',1)[0])
            # Same-run retries must be byte-identical; existing objects are read-verified.
            try:
                existing=w.files.download(target).contents.read()
            except Exception as error:
                from databricks.sdk.errors import NotFound
                if not isinstance(error,NotFound):raise
                with path.open('rb') as stream:w.files.upload(target,stream,overwrite=False)
            else:
                if hashlib.sha256(existing).digest()!=hashlib.sha256(path.read_bytes()).digest():raise ValueError('Immutable remote landing conflict')
            return dict(path=target,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    files=[]
    with ThreadPoolExecutor(max_workers=4) as pool:
        pending=[pool.submit(upload,path) for path in packed]
        for done in as_completed(pending):
            files.append(done.result())
            print(json.dumps(dict(uploaded_files=len(files),total_files=len(packed))),flush=True)
    files.sort(key=lambda item:item['path'])
    report=dict(run_id=args.run_id,observed_at=datetime.now(timezone.utc).isoformat(),requests=len(audit),files=files,provider='fmp_local_to_databricks',postgres_required=False)
    manifest=args.output/'collector_manifest.json'
    if manifest.exists():
        previous=json.loads(manifest.read_text(encoding='utf-8'))
        if any(previous[k]!=report[k] for k in ['run_id','requests','files','provider','postgres_required']):raise ValueError('Immutable collector commit conflict')
        report=previous
    else:manifest.write_text(json.dumps(report,indent=2),encoding='utf-8')
    remote=f'{destination}/collector_manifests/{identifier(args.run_id)}.json'
    w.files.create_directory(remote.rsplit('/',1)[0])
    from databricks.sdk.errors import NotFound
    try:existing=w.files.download(remote).contents.read()
    except NotFound:
        with manifest.open('rb') as stream:w.files.upload(remote,stream,overwrite=False)
    else:
        if existing!=manifest.read_bytes():raise ValueError('Remote collector commit conflict')
    print(json.dumps(dict(completed_requests=len(audit),manifest=remote)),flush=True)

if __name__=='__main__':main()
