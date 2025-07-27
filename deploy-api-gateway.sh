#!/usr/bin/env bash

# Deploy API Gateway
set -e

echo "🚀 Deploying City Project API Gateway..."

# Create a temporary deployment directory
TEMP_DIR=$(mktemp -d)
echo "📁 Created temp directory: $TEMP_DIR"

# Copy API gateway files
echo "📋 Copying API gateway files..."
cp -r apps/api-gateway/* "$TEMP_DIR/"

# Create a proper Dockerfile
cat > "$TEMP_DIR/Dockerfile" << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Copy all files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8080

# Run the application
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
EOF

# Deploy to Cloud Run
echo "📤 Deploying to Cloud Run..."
cd "$TEMP_DIR"
gcloud run deploy city-api-gateway \
  --source . \
  --platform managed \
  --region us-central1 \
  --project city-project-466410 \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=city-project-466410,GOOGLE_CLOUD_LOCATION=us-central1,ORCHESTRATOR_URL=https://city-orchestrator-ixlmqkeuva-uc.a.run.app"

# Get the URL
API_GATEWAY_URL=$(gcloud run services describe city-api-gateway --region=us-central1 --format="value(status.url)")

# Clean up
cd /home/cafo/git/city-proj
rm -rf "$TEMP_DIR"

echo "✅ API Gateway deployed successfully!"
echo "🌐 URL: $API_GATEWAY_URL"
echo ""
echo "🧪 Test the deployment:"
echo "curl $API_GATEWAY_URL/"
echo "curl $API_GATEWAY_URL/api/v1/test" 
