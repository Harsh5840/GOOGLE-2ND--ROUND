#!/usr/bin/env bash

# Deploy Orchestrator with proper project structure
set -e

echo "🚀 Deploying City Project Orchestrator..."

# Create a temporary deployment directory
TEMP_DIR=$(mktemp -d)
echo "📁 Created temp directory: $TEMP_DIR"

# Copy the entire project structure
echo "📋 Copying project files..."
cp -r shared "$TEMP_DIR/"
cp -r agents "$TEMP_DIR/"
cp -r tools "$TEMP_DIR/"

# Copy orchestrator files
cp -r apps/orchestrator/* "$TEMP_DIR/"

# Create uploads directory
mkdir -p "$TEMP_DIR/uploads"

# Create a proper Dockerfile
cat > "$TEMP_DIR/Dockerfile" << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Copy all files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 8080

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
EOF

# Deploy to Cloud Run
echo "📤 Deploying to Cloud Run..."
cd "$TEMP_DIR"
gcloud run deploy city-orchestrator \
  --source . \
  --platform managed \
  --region us-central1 \
  --project city-project-466410 \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=city-project-466410,GOOGLE_CLOUD_LOCATION=us-central1"

# Get the URL
ORCHESTRATOR_URL=$(gcloud run services describe city-orchestrator --region=us-central1 --format="value(status.url)")

# Clean up
cd /home/cafo/git/city-proj
rm -rf "$TEMP_DIR"

echo "✅ Orchestrator deployed successfully!"
echo "🌐 URL: $ORCHESTRATOR_URL" 
