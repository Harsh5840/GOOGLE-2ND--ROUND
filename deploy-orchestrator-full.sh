#!/usr/bin/env bash

# Deploy Orchestrator with full main.py and proper error handling
set -e

echo "🚀 Deploying City Project Orchestrator (Full Version)..."

# Create a temporary deployment directory
TEMP_DIR=$(mktemp -d)
echo "📁 Created temp directory: $TEMP_DIR"

# Copy the entire project structure
echo "📋 Copying project files..."
cp -r shared "$TEMP_DIR/"
cp -r agents "$TEMP_DIR/"
cp -r tools "$TEMP_DIR/"

# Copy orchestrator files but use working main.py
cp -r apps/orchestrator/* "$TEMP_DIR/"
cp apps/orchestrator/main_working.py "$TEMP_DIR/main.py"

# Create uploads directory
mkdir -p "$TEMP_DIR/uploads"

# Create a robust Dockerfile that handles dependencies properly
cat > "$TEMP_DIR/Dockerfile" << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with error handling
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir fastapi==0.104.1 uvicorn==0.24.0 pydantic==2.5.0 python-dotenv==1.0.0 python-multipart==0.0.6 requests==2.31.0 && \
    pip install --no-cache-dir beautifulsoup4==4.12.2 googlemaps==4.10.0 textblob==0.17.1 || echo "Some optional dependencies failed to install"

# Try to install Google Cloud dependencies
RUN pip install --no-cache-dir google-cloud-firestore==2.13.1 google-cloud-storage==2.10.0 firebase-admin==6.2.0 || echo "Google Cloud dependencies failed"

# Try to install AI dependencies
RUN pip install --no-cache-dir google-cloud-aiplatform==1.38.1 || echo "AI Platform dependency failed"

# Try to install social media dependencies
RUN pip install --no-cache-dir tweepy==4.14.0 praw==7.7.1 newsapi-python==0.2.6 || echo "Social media dependencies failed"

# Copy all application files
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 8080

# Run the application with error handling
CMD ["python", "-c", "import uvicorn; uvicorn.run('main:app', host='0.0.0.0', port=8080)"]
EOF

# Deploy to Cloud Run with extended timeout
echo "📤 Deploying to Cloud Run..."
cd "$TEMP_DIR"
gcloud run deploy city-orchestrator \
  --source . \
  --platform managed \
  --region us-central1 \
  --project city-project-466410 \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=city-project-466410,GOOGLE_CLOUD_LOCATION=us-central1" \
  --timeout=1800 \
  --memory=2Gi \
  --cpu=2

# Get the URL
ORCHESTRATOR_URL=$(gcloud run services describe city-orchestrator --region=us-central1 --format="value(status.url)")

# Clean up
cd /home/cafo/git/city-proj
rm -rf "$TEMP_DIR"

echo "✅ Orchestrator deployed successfully!"
echo "🌐 URL: $ORCHESTRATOR_URL"
echo ""
echo "🧪 Test the deployment:"
echo "curl $ORCHESTRATOR_URL/"
echo "curl -X POST $ORCHESTRATOR_URL/chat -H 'Content-Type: application/json' -d '{\"user_id\": \"test\", \"message\": \"hello\"}'" 