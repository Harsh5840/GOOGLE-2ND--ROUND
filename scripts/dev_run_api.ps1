<#
Dev run script (PowerShell)
Activates venv, sets PYTHONPATH, and starts the API in module mode.
#>

Param()

Write-Host "Starting API (module mode)"

Set-Location (Resolve-Path ".").Path

if (-Not (Test-Path -Path ".venv")) {
    Write-Host "Virtual environment not found. Run scripts/dev_setup.ps1 first."
    exit 1
}

Write-Host "Activating .venv..."
. .venv\Scripts\Activate.ps1

Write-Host "Setting PYTHONPATH to repo root"
$env:PYTHONPATH = (Resolve-Path .).Path

Write-Host "Running: python -m apps.api.src.main"
python -m apps.api.src.main
