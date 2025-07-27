#!/usr/bin/env bash

# Deploy Backend Services to Cloud Run
set -e

echo "🚀 Deploying City Project Backend Services..."

# Set your project ID
PROJECT_ID="city-project-466410"
REGION="us-central1"

# Deploy Orchestrator
echo "📤 Deploying Orchestrator..."
cd apps/orchestrator
gcloud run deploy city-orchestrator \
  --source . \
  --platform managed \
  --region $REGION \
  --project $PROJECT_ID \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=$REGION"

ORCHESTRATOR_URL=$(gcloud run services describe city-orchestrator --region=$REGION --format="value(status.url)")

# Deploy API Gateway
echo "📤 Deploying API Gateway..."
cd ../api-gateway
gcloud run deploy city-api-gateway \
  --source . \
  --platform managed \
  --region $REGION \
  --project $PROJECT_ID \
  --allow-unauthenticated \
  --set-env-vars="ORCHESTRATOR_URL=$ORCHESTRATOR_URL"

API_GATEWAY_URL=$(gcloud run services describe city-api-gateway --region=$REGION --format="value(status.url)")

echo "✅ Backend deployment complete!"
echo "🌐 Orchestrator URL: $ORCHESTRATOR_URL"
echo "🌐 API Gateway URL: $API_GATEWAY_URL"
echo ""
echo "📝 Update your frontend environment variables:"
echo "NEXT_PUBLIC_API_BASE_URL=$API_GATEWAY_URL/api/v1" 
