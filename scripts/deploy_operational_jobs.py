"""Deploy the operational jobs from the verified local pipeline configuration."""
import argparse,json,os
from pathlib import Path
def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);a=p.parse_args()
    cfg=json.loads(a.config.read_text())
    if cfg.get('cli_path'):os.environ['DATABRICKS_CLI_PATH']=cfg['cli_path']
    if cfg.get('ca_bundle'):os.environ['REQUESTS_CA_BUNDLE']=cfg['ca_bundle']
    from databricks.sdk import WorkspaceClient
    w=WorkspaceClient(profile=cfg['profile'])
    common=dict(catalog=cfg['catalog'],prefix=cfg['prefix'])
    jobs={'ingest':(cfg.get('cloud_job_ids',{}).get('ingest'),'sp500-daily_refresh','09_ingest_landed_fmp',dict(common,collector_manifest='')),
        'features':(cfg.get('cloud_job_ids',{}).get('features'),'sp500-monthly_snapshot','07_refresh_features',dict(common,run_id='',signal_date='',snapshot_id='',as_of='',
            baseline_manifest_sha256=cfg['baseline_manifest_sha256'],profiles_path=cfg['profiles_path'],profiles_sha256=cfg['profiles_sha256'],
            previous_binding_path=cfg['parent_binding_path'],feature_columns_json=json.dumps(cfg['feature_columns']))),
        'activate':(cfg.get('cloud_job_ids',{}).get('activate'),'sp500-activate-verified-gold','13_activate_release',dict(common,binding_path='',validation_path='',expected_parent_sha256='',rollback='false'))}
    ids={}
    for stage,(job_id,name,notebook,params) in jobs.items():
        settings=dict(name=name,max_concurrent_runs=1,timeout_seconds=7200,
            parameters=[dict(name=k,default=v) for k,v in params.items()],
            tasks=[dict(task_key=stage,notebook_task=dict(notebook_path=cfg['notebook_root']+'/'+notebook,base_parameters={k:'{{job.parameters.'+k+'}}' for k in params}),environment_key='sp500',max_retries=0,timeout_seconds=7200)],
            environments=[dict(environment_key='sp500',spec=dict(environment_version='4',dependencies=[cfg['wheel_path']]))])
        if job_id:w.api_client.do('POST','/api/2.1/jobs/reset',body=dict(job_id=job_id,new_settings=settings))
        else:job_id=w.api_client.do('POST','/api/2.1/jobs/create',body=settings)['job_id']
        ids[stage]=job_id
    # The bootstrap job is a recovery/import operation, always the complete
    # immutable baseline, never the old three-stock proof.
    settings=dict(name='sp500-backfill',max_concurrent_runs=1,timeout_seconds=7200,
        tasks=[dict(task_key='historical_import',notebook_task=dict(notebook_path=cfg['notebook_root']+'/05_import_history',base_parameters=dict(catalog=cfg['catalog'],schema=cfg['prefix']+'_bronze',manifest_path=cfg['baseline_manifest_path'])),environment_key='sp500',max_retries=0)],
        environments=[dict(environment_key='sp500',spec=dict(environment_version='4',dependencies=[cfg['wheel_path']]))])
    backfill_id=cfg.get('backfill_job_id')
    if backfill_id:w.api_client.do('POST','/api/2.1/jobs/reset',body=dict(job_id=backfill_id,new_settings=settings))
    else:backfill_id=w.api_client.do('POST','/api/2.1/jobs/create',body=settings)['job_id']
    cfg['backfill_job_id']=backfill_id
    cfg['cloud_job_ids']=ids
    temp=a.config.with_suffix('.tmp');temp.write_text(json.dumps(cfg,indent=2));temp.replace(a.config)
    print(json.dumps(dict(jobs=ids,backfill=backfill_id,schedules='local_collector_only')))
if __name__=='__main__':main()
