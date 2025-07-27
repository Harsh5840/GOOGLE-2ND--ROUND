#!/usr/bin/env bash

# City Project Complete Deployment Script
set -e

echo "🚀 Starting complete City Project deployment..."

# Configuration
PROJECT_ID="city-project-466410"
REGION="us-central1"

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

# Check if gcloud is available
if ! command -v gcloud &> /dev/null; then
    print_error "Google Cloud SDK not found. Please install it first:"
    echo "nix-shell -p google-cloud-sdk"
    exit 1
fi


# Check if user is logged in to gcloud
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    print_error "Not logged in to Google Cloud. Please run:"
    echo "gcloud auth login"
    exit 1
fi

# Check if user is logged in to Firebase
if ! $FIREBASE_CMD projects:list &> /dev/null; then
    print_error "Not logged in to Firebase. Please run:"
    echo "$FIREBASE_CMD login"
    exit 1
fi

print_status "Deploying backend services..."

# Deploy Orchestrator
print_status "Deploying Orchestrator to Cloud Run..."
cd apps/orchestrator
gcloud run deploy city-orchestrator \
  --source . \
  --platform managed \
  --region $REGION \
  --project $PROJECT_ID \
  --allow-unauthenticated \
  --quiet

ORCHESTRATOR_URL=$(gcloud run services describe city-orchestrator --region=$REGION --format="value(status.url)")
print_success "Orchestrator deployed: $ORCHESTRATOR_URL"

# Deploy API Gateway
print_status "Deploying API Gateway to Cloud Run..."
cd ../api-gateway
gcloud run deploy city-api-gateway \
  --source . \
  --platform managed \
  --region $REGION \
  --project $PROJECT_ID \
  --allow-unauthenticated \
  --quiet

API_GATEWAY_URL=$(gcloud run services describe city-api-gateway --region=$REGION --format="value(status.url)")
print_success "API Gateway deployed: $API_GATEWAY_URL"

# Return to project root
cd ../..

print_status "Building frontend..."
cd apps/frontend
npm install
npm run build
print_success "Frontend built successfully"

# Create environment file for the deployed API
print_status "Creating environment configuration..."
cat > .env.production << EOF
NEXT_PUBLIC_API_BASE_URL=$API_GATEWAY_URL/api/v1
EOF

print_success "Environment configured with API Gateway URL: $API_GATEWAY_URL/api/v1"

# Deploy to Firebase
print_status "Deploying frontend to Firebase..."
cd ../..
$FIREBASE_CMD deploy --only hosting --quiet

print_success "Frontend deployed to Firebase!"

# Get Firebase hosting URL
FIREBASE_URL=$($FIREBASE_CMD hosting:channel:list --json | jq -r '.result.channels[0].url // "https://city-project-466410.web.app"')

print_success "🎉 Complete deployment successful!"
echo ""
echo "📋 Deployment Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Frontend (Firebase):     $FIREBASE_URL"
echo "🔧 Orchestrator (Cloud Run): $ORCHESTRATOR_URL"
echo "🚪 API Gateway (Cloud Run):  $API_GATEWAY_URL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🧪 Test your deployment:"
echo "  Frontend:     curl $FIREBASE_URL"
echo "  Orchestrator: curl $ORCHESTRATOR_URL"
echo "  API Gateway:  curl $API_GATEWAY_URL"
echo ""
echo "📝 Environment variables for local development:"
echo "  NEXT_PUBLIC_API_BASE_URL=$API_GATEWAY_URL/api/v1"
echo ""
print_success "City Project is now live! 🎊" 
