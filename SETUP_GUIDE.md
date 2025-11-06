# CityScape Setup Guide

Complete guide to configure all API keys and services for CityScape.

---

## 🎯 Required Services (Core Functionality)

### 1. Google Cloud Platform Setup

#### A. Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Create Project"
3. Name it (e.g., "cityscape-project")
4. Note your **Project ID** (e.g., `cityscape-project-123456`)

#### B. Enable Required APIs
In Google Cloud Console, enable these APIs:
- **Vertex AI API** (for AI chat)
- **Maps JavaScript API** (for map display)
- **Geocoding API** (for location services)
- **Places API** (for location search)
- **Directions API** (for routing)
- **Cloud Firestore API** (for database)

#### C. Create Service Account
1. Go to [IAM & Admin > Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Click "Create Service Account"
3. Name: `cityscape-backend`
4. Grant these roles:
   - Vertex AI User
   - Firebase Admin SDK Administrator Service Agent
   - Storage Object Admin
5. Click "Create Key" → JSON format
6. Download the JSON file
7. Rename it to something like `cityscape-service-account.json`
8. Place it in the project root: `GOOGLE-2ND--ROUND/`

#### D. Get Google Maps API Key
1. Go to [Credentials](https://console.cloud.google.com/apis/credentials)
2. Click "Create Credentials" → "API Key"
3. Copy the API key
4. Click "Restrict Key" (recommended):
   - **Application restrictions**: HTTP referrers
   - Add: `http://localhost:3000/*` and `http://localhost:8000/*`
   - **API restrictions**: Select APIs
   - Enable: Maps JavaScript API, Geocoding API, Places API, Directions API

---

### 2. Gemini API Setup

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Select your Google Cloud project
4. Copy the API key

---

### 3. Firebase Setup (Authentication & Database)

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add Project" → Select your Google Cloud project
3. Enable Google Analytics (optional)

#### A. Enable Authentication
1. Go to "Authentication" → "Get Started"
2. Click "Sign-in method"
3. Enable **Google** provider
4. Add authorized domain: `localhost`

#### B. Enable Firestore Database
1. Go to "Firestore Database" → "Create database"
2. Start in **test mode** (you can secure it later)
3. Choose a location (same as your GCP region, e.g., `us-central`)

#### C. Get Firebase Config
1. Go to Project Settings (gear icon)
2. Scroll to "Your apps"
3. Click the web icon `</>`
4. Register your app (name: "CityScape Web")
5. Copy the config values:
   ```javascript
   const firebaseConfig = {
     apiKey: "...",
     authDomain: "...",
     projectId: "...",
     storageBucket: "...",
     messagingSenderId: "...",
     appId: "..."
   };
   ```

#### D. Download Firebase Service Account
1. Go to Project Settings → Service Accounts
2. Click "Generate new private key"
3. Download the JSON file
4. Rename it to `cityscape-firebase-admin.json`
5. Place it in the project root

---

## 📝 Configure Environment Files

### Frontend Configuration

Edit `apps/frontend/.env.local`:

```bash
# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Google Maps API Key (from step 1.D)
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=YOUR_GOOGLE_MAPS_API_KEY

# Gemini API Key (from step 2)
GOOGLE_GENAI_API_KEY=YOUR_GEMINI_API_KEY

# Firebase Config (from step 3.C)
NEXT_PUBLIC_FIREBASE_API_KEY=YOUR_FIREBASE_API_KEY
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123456789
NEXT_PUBLIC_FIREBASE_APP_ID=1:123456789:web:abcdef123456
```

### Backend API Configuration

Edit `apps/api/.env`:

```bash
# Google Cloud Project (your Project ID from step 1.A)
GOOGLE_CLOUD_PROJECT=your-project-id
GCP_PROJECT_ID=your-project-id
GCP_REGION=us-central1
GOOGLE_CLOUD_LOCATION=us-central1

# Service Account (path to JSON from step 1.C)
GOOGLE_APPLICATION_CREDENTIALS=../../cityscape-service-account.json

# Google Maps API Key (from step 1.D)
GOOGLE_MAPS_API_KEY=YOUR_GOOGLE_MAPS_API_KEY

# Gemini API Key (from step 2)
GEMINI_API_KEY=YOUR_GEMINI_API_KEY

# Firebase Service Account (path to JSON from step 3.D)
FIREBASE_SERVICE_ACCOUNT_PATH=../../cityscape-firebase-admin.json
FIREBASE_COLLECTION_NAME=city_reports
```

---

## 🚀 Start the Application

### 1. Activate Python Environment
```powershell
Set-Location 'D:\cityyyy\GOOGLE-2ND--ROUND'
.\.venv\Scripts\Activate.ps1
```

### 2. Start Backend API
```powershell
$env:PYTHONPATH = (Resolve-Path .).Path
Set-Location apps\api
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Start Frontend (in new terminal)
```powershell
Set-Location 'D:\cityyyy\GOOGLE-2ND--ROUND\apps\frontend'
npm run dev
```

### 4. Access the Application
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

---

## 🔧 Optional Services (Enhanced Features)

### Reddit API (for social media trends)
1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Click "create another app"
3. Select "script"
4. Note: Client ID (under app name) and Client Secret

Add to `apps/api/.env`:
```bash
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=CityScape/1.0
```

### Twitter/X API (for social media integration)
1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Create a project and app
3. Generate keys and tokens

Add to `apps/api/.env`:
```bash
TWITTER_BEARER_TOKEN=your_bearer_token
TWITTER_CONSUMER_KEY=your_consumer_key
TWITTER_CONSUMER_SECRET=your_consumer_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
```

### News API (for news integration)
1. Go to [NewsAPI.org](https://newsapi.org/)
2. Sign up for free
3. Copy your API key

Add to `apps/api/.env`:
```bash
NEWS_API_KEY=your_news_api_key
```

---

## ✅ Verification Checklist

- [ ] Google Cloud project created
- [ ] All required APIs enabled
- [ ] Service account created and JSON downloaded
- [ ] Google Maps API key created and configured
- [ ] Gemini API key obtained
- [ ] Firebase project linked to Google Cloud
- [ ] Firebase Authentication (Google) enabled
- [ ] Firestore database created
- [ ] Firebase config values copied
- [ ] Frontend `.env.local` updated
- [ ] Backend `.env` updated
- [ ] Both service account JSON files in project root
- [ ] Backend API running on port 8000
- [ ] Frontend running on port 3000
- [ ] Can sign in with Google OAuth
- [ ] Dashboard loads with map
- [ ] AI chat responds to messages

---

## 🐛 Troubleshooting

### AI Not Responding
- Check service account has Vertex AI User role
- Verify `GOOGLE_APPLICATION_CREDENTIALS` path is correct
- Ensure Vertex AI API is enabled

### Google Sign-In Not Working
- Check Firebase Authentication is enabled
- Verify `localhost` is in authorized domains
- Ensure all Firebase config values are correct

### Map Not Loading
- Check Google Maps API key is valid
- Ensure Maps JavaScript API is enabled
- Verify API key restrictions allow localhost

### Network Errors
- Check backend API is running on port 8000
- Verify `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000`
- Ensure CORS is enabled in backend

---

## 📚 Additional Resources

- [Google Cloud Console](https://console.cloud.google.com/)
- [Firebase Console](https://console.firebase.google.com/)
- [Google AI Studio](https://makersuite.google.com/)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Firebase Documentation](https://firebase.google.com/docs)
