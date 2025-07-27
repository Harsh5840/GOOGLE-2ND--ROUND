#!/bin/bash

# Firebase Deployment Script for City Project
# This script deploys both frontend and backend components

set -e  # Exit on any error

echo "🚀 Starting deployment process..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Firebase CLI is installed
if ! command -v firebase &> /dev/null; then
    print_error "Firebase CLI is not installed. Please install it first:"
    echo "npm install -g firebase-tools"
    exit 1
fi

# Check if user is logged into Firebase
if ! firebase projects:list &> /dev/null; then
    print_warning "You are not logged into Firebase. Please login:"
    firebase login
fi

# Get project ID from Firebase config or use default
PROJECT_ID=${FIREBASE_PROJECT_ID:-"causal-galaxy-415009"}
print_status "Using Firebase project: $PROJECT_ID"

# Step 1: Deploy Firestore rules and indexes
print_status "Deploying Firestore rules and indexes..."
firebase deploy --only firestore:rules,firestore:indexes --project $PROJECT_ID

# Step 2: Deploy Storage rules
print_status "Deploying Storage rules..."
firebase deploy --only storage --project $PROJECT_ID

# Step 3: Build and deploy frontend
print_status "Building frontend application..."
cd apps/frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    print_status "Installing frontend dependencies..."
    npm install
fi

# Build the application
print_status "Building Next.js application..."
npm run build

# Deploy to Firebase Hosting
print_status "Deploying frontend to Firebase Hosting..."
firebase deploy --only hosting --project $PROJECT_ID

cd ../..

# Step 4: Deploy backend (if needed)
if [ "$DEPLOY_BACKEND" = "true" ]; then
    print_status "Deploying backend to Google Cloud..."
    
    # Check if we're in the right directory for backend deployment
    if [ -f "news-podcast-agent/app/agent_engine_app.py" ]; then
        cd news-podcast-agent
        
        # Check if Python environment is set up
        if [ ! -d ".venv" ]; then
            print_warning "Python virtual environment not found. Creating one..."
            python -m venv .venv
        fi
        
        # Activate virtual environment
        source .venv/bin/activate
        
        # Install dependencies
        print_status "Installing Python dependencies..."
        pip install -r requirements.txt
        
        # Deploy the agent engine
        print_status "Deploying agent engine to Vertex AI..."
        python -m app.agent_engine_app --project $PROJECT_ID --location us-central1 --agent-name news-podcast-agent
        
        cd ..
    else
        print_warning "Backend deployment skipped - agent_engine_app.py not found"
    fi
fi

print_success "🎉 Deployment completed successfully!"
print_status "Frontend URL: https://$PROJECT_ID.web.app"
print_status "Firebase Console: https://console.firebase.google.com/project/$PROJECT_ID"

# Optional: Open the deployed site
if [ "$OPEN_SITE" = "true" ]; then
    print_status "Opening deployed site..."
    open "https://$PROJECT_ID.web.app"
fi 