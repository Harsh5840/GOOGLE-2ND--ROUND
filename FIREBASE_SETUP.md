# Firebase/Firestore Authentication Setup Guide

## 🔑 **Step 1: Get Your Firebase Service Account Key**

1. **Go to Firebase Console**: https://console.firebase.google.com/
2. **Select your project**: `city-project-466410`
3. **Go to Project Settings**: Click the gear icon ⚙️ next to "Project Overview"
4. **Service Accounts Tab**: Click on "Service accounts" tab
5. **Generate New Private Key**: Click "Generate new private key"
6. **Download JSON File**: Save the `city-project-466410-firebase-adminsdk-xxxxx-xxxxxxxxxx.json` file

## 📁 **Step 2: Set Up Environment Variables**

### **Option A: Environment Variable (Recommended)**

Create a `.env` file in your project root:

```bash
# Firebase/Firestore Configuration
FIREBASE_SERVICE_ACCOUNT_PATH=/path/to/your/city-project-466410-firebase-adminsdk-xxxxx-xxxxxxxxxx.json

# Google Cloud Configuration
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/city-project-466410-firebase-adminsdk-xxxxx-xxxxxxxxxx.json

# Other Configuration
GEMINI_API_KEY=your_gemini_api_key_here
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
NEWS_API_KEY=your_news_api_key
```

### **Option B: Direct JSON Content**

Alternatively, you can put the entire JSON content in an environment variable:

```bash
FIREBASE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"city-project-466410",...}
```

### **Option C: System Environment Variable**

Set the environment variable in your shell:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/city-project-466410-firebase-adminsdk-xxxxx-xxxxxxxxxx.json"
```

## 🔧 **Step 3: Update Firestore Configuration**

The current `tools/firestore.py` file should automatically detect the credentials. If you need to modify the initialization, update the `initialize_firestore()` function:

```python
def initialize_firestore():
    """Initialize Firestore with proper authentication"""
    try:
        # Option 1: Use environment variable for JSON file path
        service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')
        if service_account_path and os.path.exists(service_account_path):
            credentials = service_account.Credentials.from_service_account_file(service_account_path)
            return firestore.Client(credentials=credentials)
        
        # Option 2: Use direct JSON content
        service_account_json = os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON')
        if service_account_json:
            credentials = service_account.Credentials.from_service_account_info(json.loads(service_account_json))
            return firestore.Client(credentials=credentials)
        
        # Option 3: Use default credentials (GOOGLE_APPLICATION_CREDENTIALS)
        return firestore.Client()
        
    except Exception as e:
        log_event("FirestoreTool", f"Error initializing Firestore: {e}")
        return None
```

## 🛡️ **Step 4: Security Best Practices**

### **File Permissions**
```bash
# Set restrictive permissions on your service account key
chmod 600 /path/to/your/city-project-466410-firebase-adminsdk-xxxxx-xxxxxxxxxx.json
```

### **Git Ignore**
Make sure your `.gitignore` includes:
```
# Firebase credentials
*.json
.env
.env.local
.env.production
```

### **Environment-Specific Files**
- `.env.local` - Local development
- `.env.production` - Production environment
- `.env.staging` - Staging environment

## 🧪 **Step 5: Test Your Setup**

### **Test Firestore Connection**
```bash
# Test the connection
nix-shell --run "python -c \"from tools.firestore import db; print('Firestore connected:', db is not None)\""
```

### **Test Query History**
```bash
# Test query history functionality
nix-shell --run "python -c \"from tools.firestore import get_user_query_history; result = get_user_query_history('test', 5); print(f'Found {len(result)} queries')\""
```

## 📋 **Step 6: Verify Your Setup**

### **Check Environment Variables**
```bash
# Check if environment variables are set
echo $GOOGLE_APPLICATION_CREDENTIALS
echo $FIREBASE_SERVICE_ACCOUNT_PATH
```

### **Check File Exists**
```bash
# Verify your service account file exists
ls -la /path/to/your/city-project-466410-firebase-adminsdk-xxxxx-xxxxxxxxxx.json
```

## 🚨 **Common Issues & Solutions**

### **Issue: "No module named 'firebase_admin'"**
```bash
# Install Firebase Admin SDK
pip install firebase-admin
```

### **Issue: "Permission denied"**
```bash
# Fix file permissions
chmod 600 /path/to/your/service-account-key.json
```

### **Issue: "Invalid credentials"**
- Verify the JSON file is complete and valid
- Check that the project ID matches your Firebase project
- Ensure the service account has the necessary permissions

### **Issue: "Project not found"**
- Verify you're using the correct project ID
- Check that the service account belongs to the right project

## 🔐 **Firebase Security Rules**

Make sure your Firestore security rules allow the operations you need:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Allow authenticated users to read/write their own data
    match /user_profiles/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    match /user_query_history/{docId} {
      allow read, write: if request.auth != null && resource.data.user_id == request.auth.uid;
    }
    
    // Allow public read access to unified data
    match /unified_data/{docId} {
      allow read: if true;
      allow write: if request.auth != null;
    }
  }
}
```

## 📞 **Support**

If you encounter issues:
1. Check the Firebase Console for any error messages
2. Verify your service account has the necessary permissions
3. Test with a simple Firestore operation first
4. Check the application logs for detailed error messages 