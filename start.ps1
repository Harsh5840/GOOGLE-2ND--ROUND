# CityScape Quick Start Script
# Run this after configuring your .env files

Write-Host "🚀 Starting CityScape..." -ForegroundColor Cyan

# Check if .env files exist
if (-not (Test-Path "apps\frontend\.env.local")) {
    Write-Host "❌ Missing apps/frontend/.env.local" -ForegroundColor Red
    Write-Host "   Please copy .env.local.example and configure your API keys" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path "apps\api\.env")) {
    Write-Host "❌ Missing apps/api/.env" -ForegroundColor Red
    Write-Host "   Please copy .env.example and configure your API keys" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Environment files found" -ForegroundColor Green

# Check if virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Host "❌ Python virtual environment not found" -ForegroundColor Red
    Write-Host "   Run: python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Python virtual environment found" -ForegroundColor Green

# Activate virtual environment
Write-Host "🔧 Activating Python environment..." -ForegroundColor Cyan
. .venv\Scripts\Activate.ps1

# Set Python path
$env:PYTHONPATH = (Resolve-Path .).Path

# Start API server in background
Write-Host "🔧 Starting API server on port 8000..." -ForegroundColor Cyan
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "Set-Location '$PWD\apps\api'; uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload" -WindowStyle Normal

# Wait for API to start
Write-Host "⏳ Waiting for API to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start Frontend
Write-Host "🔧 Starting Frontend on port 3000..." -ForegroundColor Cyan
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "Set-Location '$PWD\apps\frontend'; npm run dev" -WindowStyle Normal

Write-Host ""
Write-Host "✨ CityScape is starting!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "📍 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C in each window to stop the servers" -ForegroundColor Yellow
