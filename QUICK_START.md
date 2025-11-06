# 🚀 QUICK SETUP CHECKLIST

Follow these steps to get CityScape running with fresh configuration:

## Step 1: Get Your API Keys (15-20 minutes)

### 🔑 Google Cloud Console
1. Visit: https://console.cloud.google.com/
2. Create a new project (or use existing)
3. **Enable these APIs:**
   - Vertex AI API
   - Maps JavaScript API
   - Geocoding API
   - Places API
   - Directions API
   - Cloud Firestore API

4. **Create API Key:**
   - Go to: Credentials → Create Credentials → API Key
   - Copy the key
   - Restrict it to localhost (optional but recommended)

5. **Create Service Account:**
   - Go to: IAM & Admin → Service Accounts → Create
   - Add roles: Vertex AI User, Firebase Admin
   - Create JSON key → Download it

### 🔥 Firebase Console
1. Visit: https://console.firebase.google.com/
2. Add your Google Cloud project to Firebase
3. **Enable Authentication:**
   - Authentication → Get Started
   - Sign-in method → Enable Google
   
4. **Create Firestore Database:**
   - Firestore Database → Create database
   - Start in test mode
   
5. **Get Config Values:**
   - Project Settings → Your apps → Web app
   - Copy all config values

6. **Download Service Account:**
   - Project Settings → Service Accounts
   - Generate new private key

### 🤖 Gemini API
1. Visit: https://makersuite.google.com/app/apikey
2. Create API Key
3. Copy the key

## Step 2: Place Service Account Files

Put these files in the project root (`GOOGLE-2ND--ROUND/`):
- `your-service-account.json` (from Google Cloud)
- `your-firebase-admin.json` (from Firebase)

## Step 3: Configure Environment Variables

### Frontend: `apps/frontend/.env.local`
```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=paste_your_key_here
GOOGLE_GENAI_API_KEY=paste_your_key_here
NEXT_PUBLIC_FIREBASE_API_KEY=paste_from_firebase_config
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123456789
NEXT_PUBLIC_FIREBASE_APP_ID=1:123:web:abc123
```

### Backend: `apps/api/.env`
```bash
GOOGLE_CLOUD_PROJECT=your-project-id
GCP_PROJECT_ID=your-project-id
GCP_REGION=us-central1
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=../../your-service-account.json
GOOGLE_MAPS_API_KEY=paste_your_key_here
GEMINI_API_KEY=paste_your_key_here
FIREBASE_SERVICE_ACCOUNT_PATH=../../your-firebase-admin.json
FIREBASE_COLLECTION_NAME=city_reports
```

## Step 4: Start the Application

### Option A: Use Start Script (Recommended)
```powershell
Set-Location 'D:\cityyyy\GOOGLE-2ND--ROUND'
.\start.ps1
```

### Option B: Manual Start

**Terminal 1 - API:**
```powershell
Set-Location 'D:\cityyyy\GOOGLE-2ND--ROUND'
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH = (Resolve-Path .).Path
Set-Location apps\api
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```powershell
Set-Location 'D:\cityyyy\GOOGLE-2ND--ROUND\apps\frontend'
npm run dev
```

## Step 5: Access the Application

- **Frontend:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs

## ✅ Verify Everything Works

1. Open http://localhost:3000
2. Click "Sign In with Google"
3. Complete authentication
4. Should redirect to dashboard
5. Map should load
6. Try sending a message in chat
7. Look for the blue camera button in bottom-right

## 🆘 If Something Doesn't Work

### AI Chat Not Responding
- Check: Service account has Vertex AI User role
- Check: `GOOGLE_APPLICATION_CREDENTIALS` path is correct
- Check: Vertex AI API is enabled

### Google Sign-In Fails
- Check: Firebase Auth (Google) is enabled
- Check: All Firebase config values are correct
- Check: `localhost` is in authorized domains

### Map Doesn't Load
- Check: Google Maps API key is valid
- Check: Maps JavaScript API is enabled
- Check: API key allows localhost

### Camera Button Missing
- Check: Dashboard loaded successfully
- Check: No JavaScript errors in console
- Look in bottom-right corner of the map

## 📚 Full Documentation

See `SETUP_GUIDE.md` for detailed instructions and troubleshooting.

## 🎯 Optional APIs (Add Later)

These are optional for enhanced features:
- Reddit API (social media trends)
- Twitter/X API (social monitoring)
- News API (news integration)

You can add these later without affecting core functionality.
