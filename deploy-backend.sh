#!/usr/bin/env bash

# Deploy Both Backend Services
set -e

echo "🚀 Deploying City Project Backend Services..."

# Configuration
PROJECT_ID="city-project-466410"
REGION="us-central1"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Deploy Orchestrator (Simplified version for testing)
print_status "Deploying Orchestrator (Simplified)..."
chmod +x deploy-orchestrator-simple.sh
./deploy-orchestrator-simple.sh

# Get orchestrator URL
ORCHESTRATOR_URL=$(gcloud run services describe city-orchestrator --region=$REGION --format="value(status.url)")
print_success "Orchestrator URL: $ORCHESTRATOR_URL"

cd /home/cafo/git/city-proj/

# Deploy API Gateway
print_status "Deploying API Gateway..."
chmod +x deploy-api-gateway.sh
./deploy-api-gateway.sh

# Get API gateway URL
API_GATEWAY_URL=$(gcloud run services describe city-api-gateway --region=$REGION --format="value(status.url)")
print_success "API Gateway URL: $API_GATEWAY_URL"

print_success "🎉 Backend deployment complete!"
echo ""
echo "📋 Deployment Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 Orchestrator (Cloud Run): $ORCHESTRATOR_URL"
echo "🚪 API Gateway (Cloud Run):  $API_GATEWAY_URL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🧪 Test your deployment:"
echo "  Orchestrator: curl $ORCHESTRATOR_URL/"
echo "  API Gateway:  curl $API_GATEWAY_URL/"
echo ""
echo "📝 Next steps:"
echo "  1. Update frontend environment variable:"
echo "     NEXT_PUBLIC_API_BASE_URL=$API_GATEWAY_URL/api/v1"
echo "  2. Rebuild and redeploy frontend"
echo ""
print_success "Backend services are now live! 🎊" 
