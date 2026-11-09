$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$sourceConfig = Join-Path $projectRoot 'config\data_source.json'
if (-not (Test-Path -LiteralPath $sourceConfig)) { throw 'Databricks source activation must pass before scheduling refreshes.' }
$config = Join-Path $projectRoot 'config\operator.json'
$python = Join-Path $projectRoot '.venv\Scripts\python.exe'
$coordinator = Join-Path $PSScriptRoot 'run_local_pipeline.py'
$localDay = [TimeZoneInfo]::ConvertTimeBySystemTimeZoneId([DateTimeOffset]::UtcNow, 'Eastern Standard Time').ToString('yyyyMMdd')
$logRoot = Join-Path $projectRoot 'outputs\lakehouse_operations\logs'
New-Item -ItemType Directory -Path $logRoot -Force | Out-Null
$logPath = Join-Path $logRoot ('daily_' + $localDay + '.log')
Set-Location -LiteralPath $projectRoot
& $python $coordinator --config $config --run-id ('daily_' + $localDay) --activate *> $logPath
exit $LASTEXITCODE
