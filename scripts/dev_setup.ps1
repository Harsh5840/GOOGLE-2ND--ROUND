<#
Dev setup script (PowerShell)
Creates and activates a virtual environment and installs API requirements.
#>

Param()

Write-Host "Setting up development environment for GOOGLE-2ND--ROUND (apps/api)"

$repoRoot = (Resolve-Path ".").Path
Set-Location $repoRoot

if (-Not (Test-Path -Path ".venv")) {
    Write-Host "Creating virtual environment .venv..."
    python -m venv .venv
}

Write-Host "Activating virtual environment..."
. .venv\Scripts\Activate.ps1

Write-Host "Installing Python requirements (this may take several minutes)..."
pip install -r apps\api\requirements.txt

Write-Host "If you hit google-cloud circular import errors, try pinning google-cloud-storage:"
Write-Host "    pip install google-cloud-storage==2.18.2"

Write-Host "Setup complete. To start the API see scripts/dev_run_api.ps1 or run:"
Write-Host "    python -m apps.api.src.main"
