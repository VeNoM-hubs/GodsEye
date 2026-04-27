$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$npmCmd = Join-Path $env:ProgramFiles "nodejs\npm.cmd"

Write-Host "Starting backend (uvicorn) in a new window..." -ForegroundColor Cyan
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "Set-Location -Path '$root'; uvicorn backend.api_server:app --reload --host 0.0.0.0 --port 8000"

Write-Host "Starting frontend (npm run dev) in a new window..." -ForegroundColor Cyan
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "Set-Location -Path '$root'; & '$npmCmd' run dev"

Write-Host "Both processes started." -ForegroundColor Green
