# Firebase Deployment Guide

This guide will help you deploy your City Project application to Firebase Hosting, Firestore, and Google Cloud Platform.

## 🚀 Quick Start

### Prerequisites

1. **Node.js and npm** (v16 or higher)
2. **Firebase CLI** - Install globally:
   ```bash
   npm install -g firebase-tools
   ```
3. **Google Cloud CLI** (for backend deployment)
4. **Python 3.8+** (for backend deployment)

### Step 1: Firebase Setup

1. **Login to Firebase**:
   ```bash
   firebase login
   ```

2. **Initialize Firebase** (if not already done):
   ```bash
   firebase init
   ```
   - Select your project: `causal-galaxy-415009`
   - Enable Hosting, Firestore, and Storage

### Step 2: Deploy Frontend Only

**For Windows (PowerShell)**:
```powershell
.\deploy.ps1
```

**For Linux/Mac**:
```bash
chmod +x deploy.sh
./deploy.sh
```

**Manual deployment**:
```bash
cd apps/frontend
npm install
npm run build
firebase deploy --only hosting
```

### Step 3: Deploy Backend (Optional)

**With backend deployment**:
```powershell
# Windows
.\deploy.ps1 -DeployBackend

# Linux/Mac
DEPLOY_BACKEND=true ./deploy.sh
```

## 📁 Project Structure

```
GOOGLE-2ND--ROUND/
├── firebase.json              # Firebase configuration
├── firestore.rules            # Firestore security rules
├── firestore.indexes.json     # Firestore indexes
├── storage.rules              # Storage security rules
├── deploy.sh                  # Linux/Mac deployment script
├── deploy.ps1                 # Windows deployment script
├── apps/
│   └── frontend/              # Next.js frontend
│       ├── package.json
│       ├── next.config.mjs
│       └── lib/
│           └── firebase.ts    # Firebase client config
└── news-podcast-agent/        # Python backend
    └── app/
        └── agent_engine_app.py
```

## 🔧 Configuration Files

### Firebase Configuration (`firebase.json`)

```json
{
  "hosting": {
    "public": "apps/frontend/out",
    "ignore": ["firebase.json", "**/.*", "**/node_modules/**"],
    "rewrites": [{"source": "**", "destination": "/index.html"}]
  },
  "firestore": {
    "rules": "firestore.rules",
    "indexes": "firestore.indexes.json"
  },
  "storage": {
    "rules": "storage.rules"
  }
}
```

### Next.js Configuration (`apps/frontend/next.config.mjs`)

```javascript
const nextConfig = {
  output: 'export',           // Static export for Firebase Hosting
  trailingSlash: true,        // Required for Firebase Hosting
  images: {
    unoptimized: true,        // Required for static export
  }
}
```

## 🔐 Security Rules

### Firestore Rules (`firestore.rules`)

- **User Profiles**: Users can only access their own profile data
- **Query History**: Users can only access their own query history
- **Events & Photos**: Public read, authenticated write
- **Unified Data**: Public read, authenticated write

### Storage Rules (`storage.rules`)

- **Event Photos**: Public read, user-specific write
- **Profile Pictures**: Public read, user-specific write
- **Uploads**: Public read, user-specific write
- **Public Content**: Public read/write for authenticated users

## 🌐 Environment Variables

Create a `.env.local` file in `apps/frontend/`:

```bash
# Firebase Configuration (already in firebase.ts)
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=causal-galaxy-415009
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id

# Google Cloud Configuration (for backend)
GOOGLE_CLOUD_PROJECT=causal-galaxy-415009
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
```

## 🚀 Deployment Options

### Option 1: Frontend Only (Recommended for testing)

```bash
# Quick frontend deployment
cd apps/frontend
npm run deploy
```

### Option 2: Full Stack Deployment

```bash
# Deploy everything
./deploy.sh  # Linux/Mac
.\deploy.ps1  # Windows
```

### Option 3: Manual Step-by-Step

1. **Deploy Firestore Rules**:
   ```bash
   firebase deploy --only firestore:rules,firestore:indexes
   ```

2. **Deploy Storage Rules**:
   ```bash
   firebase deploy --only storage
   ```

3. **Build and Deploy Frontend**:
   ```bash
   cd apps/frontend
   npm install
   npm run build
   firebase deploy --only hosting
   ```

4. **Deploy Backend** (optional):
   ```bash
   cd news-podcast-agent
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\Activate.ps1  # Windows
   pip install -r requirements.txt
   python -m app.agent_engine_app --project causal-galaxy-415009
   ```

## 🔍 Troubleshooting

### Common Issues

1. **Firebase CLI not found**:
   ```bash
   npm install -g firebase-tools
   ```

2. **Build errors**:
   ```bash
   cd apps/frontend
   rm -rf node_modules package-lock.json
   npm install
   npm run build
   ```

3. **Authentication issues**:
   ```bash
   firebase logout
   firebase login
   ```

4. **Permission denied**:
   - Check Firebase project permissions
   - Verify service account credentials

### Debug Commands

```bash
# Check Firebase project
firebase projects:list

# Check deployment status
firebase hosting:channel:list

# View logs
firebase functions:log

# Test locally
firebase serve
```

## 📊 Monitoring

### Firebase Console
- **Hosting**: https://console.firebase.google.com/project/causal-galaxy-415009/hosting
- **Firestore**: https://console.firebase.google.com/project/causal-galaxy-415009/firestore
- **Storage**: https://console.firebase.google.com/project/causal-galaxy-415009/storage

### Google Cloud Console
- **Vertex AI**: https://console.cloud.google.com/vertex-ai
- **Logging**: https://console.cloud.google.com/logs

## 🔄 Continuous Deployment

### GitHub Actions (Optional)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Firebase
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - run: npm install -g firebase-tools
      - run: cd apps/frontend && npm install
      - run: cd apps/frontend && npm run build
      - run: firebase deploy --token ${{ secrets.FIREBASE_TOKEN }}
```

## 📞 Support

If you encounter issues:

1. Check the Firebase Console for error messages
2. Verify your project ID and credentials
3. Test with a simple deployment first
4. Check the application logs

## 🎯 Next Steps

After successful deployment:

1. **Set up custom domain** (optional)
2. **Configure CDN** for better performance
3. **Set up monitoring and alerts**
4. **Implement CI/CD pipeline**
5. **Add analytics and tracking**

Your application will be available at: `https://causal-galaxy-415009.web.app` 