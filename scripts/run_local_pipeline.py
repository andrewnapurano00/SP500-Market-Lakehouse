"""Run the local collector, cloud transformations and guarded Gold activation.

No PostgreSQL, model fitting, allocation publication or broker actions. The
Windows task invokes this coordinator using the signed-in user's SDK profile.
"""
import argparse,hashlib,json,os,subprocess,sys,time
from pathlib import Path
from datetime import datetime,timezone,timedelta
from zoneinfo import ZoneInfo
PROJECT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(PROJECT/'lakehouse/src'),str(PROJECT/'ingestion/src')]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,required=True);parser.add_argument('--run-id',required=True)
    parser.add_argument('--signal-date');parser.add_argument('--phase',choices=['all','ingest','features','activate'],default='all')
    parser.add_argument('--activate',action='store_true')
    args=parser.parse_args();config=json.loads(args.config.read_text(encoding='utf-8'))
    from sp500_lakehouse.config import identifier
    identifier(args.run_id)
    identifier(config['catalog']);identifier(config['prefix'])
    if config.get('cli_path'):os.environ['DATABRICKS_CLI_PATH']=config['cli_path']
    if config.get('ca_bundle'):os.environ['REQUESTS_CA_BUNDLE']=config['ca_bundle']
    from databricks.sdk import WorkspaceClient
    from databricks.sdk.errors import NotFound
    from sp500_lakehouse.reader import GoldReader,StatementQuery,binding_sha256
    import pandas as pd
    import pandas_market_calendars as mcal
    w=WorkspaceClient(profile=config['profile'])
    root=Path(config['runs_root'])/args.run_id;root.mkdir(parents=True,exist_ok=True)
    state_path=root/'pipeline_state.json'
    state=json.loads(state_path.read_text()) if state_path.exists() else {}
    def save():
        tmp=state_path.with_suffix('.tmp');tmp.write_text(json.dumps(state,indent=2));tmp.replace(state_path)
    now=datetime.now(timezone.utc)
    asof=max(pd.Timestamp(now),pd.Timestamp(config.get('minimum_as_of',now.isoformat())))
    if args.signal_date:signal=args.signal_date
    else:
        schedule=mcal.get_calendar('NYSE').schedule(start_date=(asof-pd.DateOffset(months=3)).date(),end_date=asof.date())
        completed=schedule.loc[schedule.market_close<=asof]
        monthly=completed.groupby(completed.index.to_period('M')).tail(1)
        candidate=monthly.index[-1];period=candidate.to_period('M')
        last=mcal.get_calendar('NYSE').schedule(start_date=period.start_time,end_date=period.end_time).index[-1]
        signal=str((candidate if candidate==last else monthly.index[-2]).date())
    state.setdefault('as_of',asof.isoformat());state.setdefault('signal_date',signal);save()
    def upload(path,target):
        w.files.create_directory(target.rsplit('/',1)[0])
        try:existing=w.files.download(target).contents.read()
        except NotFound:
            with Path(path).open('rb') as stream:w.files.upload(target,stream,overwrite=False)
        else:
            if existing!=Path(path).read_bytes():raise ValueError('Immutable deployment file conflict')
    def cloud(stage,notebook,params):
        if stage not in state:
            body=dict(run_name='sp500-'+stage+'-'+args.run_id,timeout_seconds=7200,
                tasks=[dict(task_key=stage,notebook_task=dict(notebook_path=config['notebook_root']+'/'+notebook,base_parameters=params),environment_key='sp500',max_retries=0,timeout_seconds=7200)],
                environments=[dict(environment_key='sp500',spec=dict(environment_version='4',dependencies=[config['wheel_path']]))])
            if stage in config.get('cloud_job_ids',{}):
                state[stage]=w.api_client.do('POST','/api/2.2/jobs/run-now',body=dict(job_id=config['cloud_job_ids'][stage],job_parameters=params))
            else:state[stage]=w.api_client.do('POST','/api/2.2/jobs/runs/submit',body=body)
            save()
        run_id=state[stage]['run_id']
        while True:
            run=w.api_client.do('GET','/api/2.2/jobs/runs/get',query={'run_id':run_id})
            if any(t.get('state',{}).get('result_state') in ['FAILED','TIMEDOUT'] for t in run.get('tasks',[])):
                w.api_client.do('POST','/api/2.2/jobs/runs/cancel',body={'run_id':run_id})
                raise RuntimeError('Cloud '+stage+' failed; inspect run '+str(run_id))
            lifecycle=run['state']['life_cycle_state']
            print(json.dumps(dict(stage=stage,run_id=run_id,state=lifecycle)),flush=True)
            if lifecycle in ['TERMINATED','SKIPPED','INTERNAL_ERROR']:break
            time.sleep(20)
        if run['state'].get('result_state')!='SUCCESS':raise RuntimeError('Cloud '+stage+' did not succeed')
        output=w.api_client.do('GET','/api/2.2/jobs/runs/get-output',query={'run_id':run['tasks'][-1]['run_id']})
        result=json.loads(output['notebook_output']['result']);(root/(stage+'_result.json')).write_text(json.dumps(result,indent=2));return result
    collector_root=root/'collector'
    if args.phase=='all':
        local_day=now.astimezone(ZoneInfo('America/New_York')).date()
        end=local_day.isoformat();start=(local_day-timedelta(days=600)).isoformat()
        command=[sys.executable,str(PROJECT/'scripts/collect_fmp_to_databricks.py'),'--profile',config['profile'],'--warehouse-id',config['warehouse_id'],
            '--catalog',config['catalog'],'--prefix',config['prefix'],'--start-date',start,'--end-date',end,'--run-id',args.run_id,
            '--max-requests',str(config.get('max_requests',4000)),'--output',str(collector_root),'--execute']
        for flag,key in [('--cli-path','cli_path'),('--ca-bundle','ca_bundle')]:
            if config.get(key):command.extend([flag,config[key]])
        subprocess.run(command,check=True)
    remote_root=f"/Volumes/{config['catalog']}/{config['prefix']}_files"
    common=dict(catalog=config['catalog'],prefix=config['prefix'])
    if args.phase in ['all','ingest']:
        cloud('ingest','09_ingest_landed_fmp',dict(common,collector_manifest=remote_root+'/landing/collector_manifests/'+args.run_id+'.json'))
    if args.phase in ['all','ingest','features']:
        if 'features' not in state:
            registry=f"{config['catalog']}.{config['prefix']}_ops.active_dataset"
            try:w.tables.get(registry)
            except NotFound:pass
            else:
                active=StatementQuery(w,config['warehouse_id'])('SELECT binding_path,binding_json,binding_sha256 FROM '+registry+" WHERE dataset_id='sp500'")
                if len(active)!=1 or binding_sha256(json.loads(active.iloc[0].binding_json))!=active.iloc[0].binding_sha256:raise ValueError('Invalid active source registry')
                config['parent_binding_path']=active.iloc[0].binding_path;config['active_parent_sha256']=active.iloc[0].binding_sha256
            state['as_of']=max(pd.Timestamp(state['as_of']),pd.Timestamp(datetime.now(timezone.utc))).isoformat();save()
        params=dict(common,run_id=args.run_id,signal_date=state['signal_date'],snapshot_id='refresh_'+args.run_id,
            baseline_manifest_sha256=config['baseline_manifest_sha256'],profiles_path=config['profiles_path'],profiles_sha256=config['profiles_sha256'],
            previous_binding_path=config['parent_binding_path'],feature_columns_json=json.dumps(config['feature_columns']),as_of=state['as_of'])
        result=cloud('features','07_refresh_features',params)
    else:result=json.loads((root/'features_result.json').read_text())
    binding=result['binding'];query=StatementQuery(w,config['warehouse_id'])
    reader=GoldReader(query,binding);frame=reader.read([state['signal_date'][:7]])
    if len(frame)!=result['assembly']['population_count']:raise ValueError('Release population transport mismatch')
    required=config.get('required_non_null_features',[])
    if not required or set(required)-set(binding['feature_columns']):raise ValueError('Declare outcome-free required_non_null_features in operator configuration')
    complete=int(frame[required].notna().all(axis=1).sum())
    if complete/len(frame)<config.get('minimum_complete_fraction',.9):raise ValueError('Required-feature coverage below activation floor')
    proof=dict(passed=True,source_binding_sha256=reader.sha256,rows=len(frame),complete_required_feature_rows=complete,
        scope='data_contract_only_no_model_execution',collector_run_id=args.run_id,signal_date=state['signal_date'],
        historical_baseline_validation=config['historical_validation_sha256'])
    binding_file=root/'binding.json';validation_file=root/'release_validation.json'
    binding_file.write_text(json.dumps(binding,indent=2));validation_file.write_text(json.dumps(proof,indent=2))
    remote_binding=remote_root+'/exports/releases/'+binding['snapshot_id']+'/binding.json'
    remote_validation=remote_root+'/exports/releases/'+binding['snapshot_id']+'/release_validation.json'
    upload(binding_file,remote_binding);upload(validation_file,remote_validation)
    if args.activate:
        activation=cloud('activate','13_activate_release',dict(common,binding_path=remote_binding,validation_path=remote_validation,expected_parent_sha256=config.get('active_parent_sha256','')))
        source=dict(provider='databricks_gold',profile=config['profile'],warehouse_id=config['warehouse_id'],binding_path=str(binding_file.resolve()),
            active_registry=f"{config['catalog']}.{config['prefix']}_ops.active_dataset",cli_path=config.get('cli_path'),ca_bundle=config.get('ca_bundle'))
        destination=PROJECT/'config/data_source.json';temporary=destination.with_suffix('.tmp');temporary.write_text(json.dumps(source,indent=2));temporary.replace(destination)
        config['parent_binding_path']=remote_binding;config['active_parent_sha256']=reader.sha256
        temporary=args.config.with_suffix('.tmp');temporary.write_text(json.dumps(config,indent=2));temporary.replace(args.config)
        print(json.dumps(activation),flush=True)
    else:print(json.dumps(dict(verified=True,activated=False,binding=remote_binding)),flush=True)

if __name__=='__main__':main()
