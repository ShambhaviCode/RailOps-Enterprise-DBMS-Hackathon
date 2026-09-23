# RailOps x AWS SAM - 30 second demo
# Prereqs: Docker Desktop running, `pip install aws-sam-cli`, RailOps running (python run.py)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$env:SAM_CLI_TELEMETRY = "0"

Write-Host "`n[1/3] sam validate --lint" -ForegroundColor Cyan
sam validate --lint

Write-Host "`n[2/3] sam local invoke RailOpsStatsFunction (real RailOps data event)" -ForegroundColor Cyan
sam local invoke RailOpsStatsFunction --event events/stats-event.json

Write-Host "`n[3/3] sam local start-api  ->  open http://127.0.0.1:5000/insights" -ForegroundColor Cyan
sam local start-api --port 3000
