# Firestore Integration for City Project

This document describes the comprehensive Firestore integration that provides user records, location history, and unified data storage for the city project.

## 🏗️ **Architecture Overview**

### **Collections Structure**
```
firestore/
├── user_profiles/           # User preferences and settings
├── location_history/        # User location tracking
├── user_query_history/      # Chat and search history
├── event_photos/           # Geotagged photo metadata
├── unified_data/           # Aggregated data from various sources
└── city_reports/           # Legacy city reports (existing)
```

## 📊 **Data Models**

### **User Profile**
```json
{
  "user_id": "string",
  "created_at": "2024-01-01T12:00:00Z",
  "last_updated": "2024-01-01T12:00:00Z",
  "last_activity": "2024-01-01T12:00:00Z",
  "last_query": "What's happening in NYC?",
  "preferences": {
    "default_location": {
      "latitude": 40.7128,
      "longitude": -74.0060
    },
    "favorite_locations": [
      {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "location_name": "Times Square",
        "added_at": "2024-01-01T12:00:00Z"
      }
    ],
    "notification_settings": {
      "email": true,
      "push": true,
      "frequency": "daily"
    },
    "map_settings": {
      "default_zoom": 12,
      "default_center": null,
      "show_traffic": true,
      "show_events": true
    }
  }
}
```

### **Location History**
```json
{
  "user_id": "string",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "location_name": "Times Square",
  "activity_type": "photo_upload",
  "timestamp": "2024-01-01T12:00:00Z",
  "coordinates": "GeoPoint(40.7128, -74.0060)"
}
```

### **Event Photo**
```json
{
  "id": "uuid",
  "filename": "photo.jpg",
  "file_path": "/uploads/event_photos/photo.jpg",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "user_id": "string",
  "description": "Busy street scene",
  "gemini_summary": "AI analysis of the photo content",
  "upload_timestamp": "2024-01-01T12:00:00Z",
  "status": "uploaded",
  "stored_at": "2024-01-01T12:00:00Z",
  "firestore_id": "uuid"
}
```

### **Unified Data**
```json
{
  "location": "New York City",
  "data_type": "twitter",
  "data": {
    "posts": [...],
    "sentiment": "positive",
    "topics": ["traffic", "events"]
  },
  "user_id": "string",
  "timestamp": "2024-01-01T12:00:00Z",
  "processed": true
}
```

## 🔧 **Backend Implementation**

### **Enhanced Firestore Tools** (`tools/firestore.py`)

#### **User Profile Management**
- `create_or_update_user_profile()` - Create or update user profiles
- `get_user_profile()` - Retrieve user profile by ID
- `get_user_default_location()` - Get user's default location with fallback

#### **Location History Management**
- `store_user_location()` - Store user location with activity tracking
- `get_recent_user_location()` - Get most recent location within time window
- `get_user_location_history()` - Get location history for specified days
- `get_favorite_locations()` - Get user's favorite locations
- `add_favorite_location()` - Add location to favorites

#### **Unified Data Storage**
- `store_unified_data()` - Store data from various sources (Twitter, Reddit, News)
- `get_unified_data()` - Retrieve data by location and type
- `get_aggregated_location_data()` - Get aggregated data from all sources

#### **Enhanced Event Photos**
- `store_event_photo_firestore()` - Store photo metadata in Firestore
- `get_user_event_photos()` - Get photos by user
- `get_location_event_photos()` - Get photos within geographic radius

### **API Endpoints** (`apps/orchestrator/main.py`)

#### **User Profile Endpoints**
```
POST   /user/profile                    # Create/update user profile
GET    /user/profile/{user_id}          # Get user profile
GET    /user/{user_id}/default-location # Get user's default location
```

#### **Location Management Endpoints**
```
POST   /user/location                   # Store user location
GET    /user/{user_id}/location-history # Get location history
GET    /user/{user_id}/favorite-locations # Get favorite locations
POST   /user/favorite-location          # Add favorite location
```

#### **Unified Data Endpoints**
```
POST   /unified-data                    # Store unified data
GET    /unified-data/{location}         # Get data by location
GET    /unified-data/{location}/aggregated # Get aggregated data
```

#### **Enhanced Photo Endpoints**
```
POST   /upload_event_photo              # Upload geotagged photo
GET    /event_photos                    # Get all photos
GET    /event_photos/{photo_id}         # Get specific photo
GET    /user/{user_id}/event-photos     # Get user's photos
GET    /location/{lat}/{lng}/event-photos # Get photos by location
```

## 🎨 **Frontend Integration**

### **API Functions** (`apps/frontend/lib/api.ts`)

#### **User Profile Management**
```typescript
createOrUpdateUserProfile(userId: string, profileData: any)
getUserProfile(userId: string)
getUserDefaultLocation(userId: string)
```

#### **Location Management**
```typescript
storeUserLocation(userId, latitude, longitude, locationName?, activityType?)
getUserLocationHistory(userId, days = 7)
getFavoriteLocations(userId)
addFavoriteLocation(userId, latitude, longitude, locationName)
```

#### **Unified Data Management**
```typescript
storeUnifiedData(location, dataType, data, userId?)
getUnifiedData(location, dataType?, hours = 24)
getAggregatedData(location, hours = 24)
```

#### **Enhanced Photo Management**
```typescript
uploadEventPhoto(formData)
getEventPhotos()
getEventPhotoById(photoId)
getUserEventPhotos(userId, limit = 50)
getLocationEventPhotos(latitude, longitude, radiusKm = 5.0, limit = 50)
```

## 🚀 **Key Features**

### **1. User Records & Preferences**
- **Profile Management**: Store user preferences, settings, and metadata
- **Default Locations**: Automatic fallback to recent locations
- **Favorite Locations**: User-curated list of important places
- **Activity Tracking**: Monitor user engagement and last activity

### **2. Location History**
- **GPS Tracking**: Store user locations with timestamps
- **Activity Context**: Track what users were doing (photo upload, search, etc.)
- **Geographic Queries**: Find photos and data within radius
- **Location Analytics**: Analyze user movement patterns

### **3. Unified Data Storage**
- **Multi-Source Integration**: Store data from Twitter, Reddit, News, Maps
- **Temporal Queries**: Get data within time windows
- **Location-Based Retrieval**: Find data for specific locations
- **Aggregated Analytics**: Combine data from multiple sources

### **4. Enhanced Photo Management**
- **Firestore Metadata**: Store photo metadata with location data
- **User Association**: Link photos to specific users
- **Geographic Search**: Find photos by location and radius
- **AI Integration**: Store Gemini analysis results

## 🔄 **Data Flow**

### **Photo Upload Flow**
1. User uploads photo with location
2. Image saved to local storage
3. Gemini AI analyzes image content
4. Metadata stored in Firestore
5. User location tracked in history
6. Photo appears in user's collection

### **Location Default Flow**
1. User requests location-based data
2. Check user profile for default location
3. If not found, get most recent location from history
4. Update user profile with this location
5. Use location for maps and data queries

### **Unified Data Flow**
1. External APIs return data (Twitter, Reddit, News)
2. Data processed and categorized
3. Stored in Firestore with location and timestamp
4. Available for aggregation and analysis
5. Served to frontend for display

## 🛠️ **Usage Examples**

### **Setting User Default Location**
```typescript
// Frontend
const profile = await createOrUpdateUserProfile(userId, {
  preferences: {
    default_location: { latitude: 40.7128, longitude: -74.0060 }
  }
});

// Backend automatically uses this for maps and queries
const defaultLocation = await getUserDefaultLocation(userId);
```

### **Storing Location History**
```typescript
// When user uploads photo
await storeUserLocation(userId, latitude, longitude, "Photo upload", "photo_upload");

// When user searches for location
await storeUserLocation(userId, latitude, longitude, "Search query", "search");
```

### **Storing Unified Data**
```typescript
// Store Twitter data
await storeUnifiedData("New York City", "twitter", {
  posts: twitterPosts,
  sentiment: "positive",
  topics: ["traffic", "events"]
}, userId);

// Store aggregated data
const aggregated = await getAggregatedData("New York City", 24);
```

### **Finding Photos by Location**
```typescript
// Get photos within 5km of Times Square
const photos = await getLocationEventPhotos(40.7580, -73.9855, 5.0);

// Get user's photos
const userPhotos = await getUserEventPhotos(userId, 50);
```

## 🔒 **Security Considerations**

### **Data Privacy**
- User location data is stored with user consent
- Location history can be limited by time windows
- Users can control what data is stored

### **Access Control**
- All data is associated with user IDs
- Location queries require user authentication
- Photo access is controlled by user ownership

### **Data Retention**
- Location history can be automatically aged out
- Old unified data can be archived
- User profiles persist until deletion

## 🚀 **Future Enhancements**

### **Real-time Features**
- WebSocket integration for live location updates
- Real-time photo sharing between users
- Live data streaming from external sources

### **Advanced Analytics**
- User behavior analysis
- Location pattern recognition
- Predictive location suggestions

### **Enhanced Search**
- Semantic search across all data types
- Image similarity search
- Location-based recommendations

### **Mobile Integration**
- Native mobile app with location services
- Offline data caching
- Push notifications for location events

## 📋 **Environment Setup**

### **Required Environment Variables**
```bash
# Google Cloud
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=your-location
GCP_PROJECT_ID=your-project-id
GCP_REGION=your-region

# Firebase/Firestore
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
FIREBASE_COLLECTION_NAME=city_reports

# Frontend
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### **Firestore Security Rules**
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // User profiles - users can only access their own
    match /user_profiles/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Location history - users can only access their own
    match /location_history/{docId} {
      allow read, write: if request.auth != null && 
        resource.data.user_id == request.auth.uid;
    }
    
    // Event photos - users can read all, write their own
    match /event_photos/{photoId} {
      allow read: if request.auth != null;
      allow write: if request.auth != null && 
        resource.data.user_id == request.auth.uid;
    }
  }
}
```

## 🧪 **Testing**

### **Backend Testing**
```bash
# Test user profile creation
curl -X POST "http://localhost:8000/user/profile" \
  -F "user_id=test-user" \
  -F "profile_data={\"preferences\":{\"default_location\":{\"latitude\":40.7128,\"longitude\":-74.0060}}}"

# Test location storage
curl -X POST "http://localhost:8000/user/location" \
  -F "user_id=test-user" \
  -F "latitude=40.7128" \
  -F "longitude=-74.0060" \
  -F "location_name=Times Square" \
  -F "activity_type=test"

# Test photo upload
curl -X POST "http://localhost:8000/upload_event_photo" \
  -F "file=@test-image.jpg" \
  -F "latitude=40.7128" \
  -F "longitude=-74.0060" \
  -F "user_id=test-user" \
  -F "description=Test photo"
```

### **Frontend Testing**
```typescript
// Test user profile
const profile = await createOrUpdateUserProfile("test-user", {
  preferences: { default_location: { latitude: 40.7128, longitude: -74.0060 } }
});

// Test location storage
await storeUserLocation("test-user", 40.7128, -74.0060, "Test location", "test");

// Test photo upload
const formData = new FormData();
formData.append('file', imageFile);
formData.append('latitude', '40.7128');
formData.append('longitude', '-74.0060');
formData.append('user_id', 'test-user');
await uploadEventPhoto(formData);
```

This Firestore integration provides a robust foundation for user data management, location tracking, and unified data storage in the city project! 🎉 