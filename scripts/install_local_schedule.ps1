$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$sourceConfig = Join-Path $projectRoot 'config\data_source.json'
if (-not (Test-Path -LiteralPath $sourceConfig)) { throw 'Activate and verify the Databricks source before installing the schedule.' }
if ((Get-TimeZone).Id -ne 'Eastern Standard Time') { throw 'This schedule requires the configured America/New_York Windows time zone.' }
$script = Join-Path $PSScriptRoot 'run_scheduled_refresh.ps1'
$arguments = '-NoProfile -NonInteractive -WindowStyle Hidden -File "' + $script + '"'
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $arguments -WorkingDirectory $projectRoot
$trigger = New-ScheduledTaskTrigger -Weekly -WeeksInterval 1 -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At '19:30'
$principal = New-ScheduledTaskPrincipal -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Hours 4)
Register-ScheduledTask -TaskName 'SP500 Databricks Refresh' -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description 'FMP collector -> Databricks observations -> reconciled immutable Gold -> atomic active registry. No PostgreSQL or model fitting.' -Force | Select-Object TaskName,State
