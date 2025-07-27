# Firebase Deployment Script for City Project (Windows PowerShell)
# This script deploys both frontend and backend components

param(
    [string]$ProjectId = "causal-galaxy-415009",
    [switch]$DeployBackend,
    [switch]$OpenSite
)

# Set error action preference
$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting deployment process..." -ForegroundColor Blue

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check if Firebase CLI is installed
try {
    $null = Get-Command firebase -ErrorAction Stop
} catch {
    Write-Error "Firebase CLI is not installed. Please install it first:"
    Write-Host "npm install -g firebase-tools" -ForegroundColor Yellow
    exit 1
}

# Check if user is logged into Firebase
try {
    firebase projects:list | Out-Null
} catch {
    Write-Warning "You are not logged into Firebase. Please login:"
    firebase login
}

Write-Status "Using Firebase project: $ProjectId"

# Step 1: Deploy Firestore rules and indexes
Write-Status "Deploying Firestore rules and indexes..."
firebase deploy --only firestore:rules,firestore:indexes --project $ProjectId

# Step 2: Deploy Storage rules
Write-Status "Deploying Storage rules..."
firebase deploy --only storage --project $ProjectId

# Step 3: Build and deploy frontend
Write-Status "Building frontend application..."
Set-Location "apps/frontend"

# Install dependencies if needed
if (-not (Test-Path "node_modules")) {
    Write-Status "Installing frontend dependencies..."
    npm install
}

# Build the application
Write-Status "Building Next.js application..."
npm run build

# Deploy to Firebase Hosting
Write-Status "Deploying frontend to Firebase Hosting..."
firebase deploy --only hosting --project $ProjectId

Set-Location "../.."

# Step 4: Deploy backend (if requested)
if ($DeployBackend) {
    Write-Status "Deploying backend to Google Cloud..."
    
    # Check if we're in the right directory for backend deployment
    if (Test-Path "news-podcast-agent/app/agent_engine_app.py") {
        Set-Location "news-podcast-agent"
        
        # Check if Python environment is set up
        if (-not (Test-Path ".venv")) {
            Write-Warning "Python virtual environment not found. Creating one..."
            python -m venv .venv
        }
        
        # Activate virtual environment
        Write-Status "Activating Python virtual environment..."
        & ".venv\Scripts\Activate.ps1"
        
        # Install dependencies
        Write-Status "Installing Python dependencies..."
        pip install -r requirements.txt
        
        # Deploy the agent engine
        Write-Status "Deploying agent engine to Vertex AI..."
        python -m app.agent_engine_app --project $ProjectId --location us-central1 --agent-name news-podcast-agent
        
        Set-Location ".."
    } else {
        Write-Warning "Backend deployment skipped - agent_engine_app.py not found"
    }
}

Write-Success "🎉 Deployment completed successfully!"
Write-Status "Frontend URL: https://$ProjectId.web.app"
Write-Status "Firebase Console: https://console.firebase.google.com/project/$ProjectId"

# Optional: Open the deployed site
if ($OpenSite) {
    Write-Status "Opening deployed site..."
    Start-Process "https://$ProjectId.web.app"
} 