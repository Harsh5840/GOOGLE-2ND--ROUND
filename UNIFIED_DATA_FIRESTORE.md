# Unified Data with Firestore Integration

## Overview

The unified data system now uses Firestore as the primary data source. Data is first loaded from various external APIs (Reddit, Twitter, News, Maps, RAG) into Firestore, and then all subsequent requests retrieve data from Firestore instead of making direct API calls. This approach provides better performance, data consistency, and reduces API rate limiting issues.

## Key Features

### 🔄 **Data Loading Process**
1. **Initial Load**: Data is fetched from external APIs and stored in Firestore
2. **Cached Retrieval**: Subsequent requests get data from Firestore cache
3. **Auto-Refresh**: Data is automatically refreshed when stale or missing
4. **Selective Loading**: Load data from specific sources as needed

### 📊 **Data Sources**
- **Reddit**: City events and discussions from relevant subreddits
- **Twitter**: Real-time tweets about city events and activities
- **News**: Local news articles and city updates
- **Maps**: Points of interest and must-visit places
- **RAG**: AI-generated insights from knowledge base

### 🗄️ **Firestore Collections**
- `unified_data`: Stores all unified data with location and timestamp
- `user_profiles`: User preferences and settings
- `location_history`: User location tracking
- `event_photos`: Photo metadata and analysis
- `user_query_history`: User interaction history

## Backend Implementation

### Core Functions

#### Data Loading
```python
def load_unified_data_to_firestore(location: str, data_sources: List[str] = None) -> Dict[str, Any]
```
Loads data from specified sources into Firestore for a location.

#### Data Retrieval
```python
def get_unified_data_from_firestore(location: str, data_type: Optional[str] = None, 
                                   hours: int = 24, force_refresh: bool = False) -> List[Dict[str, Any]]
```
Retrieves data from Firestore with optional refresh capability.

#### Aggregated Data
```python
def get_aggregated_location_data_from_firestore(location: str, hours: int = 24) -> Dict[str, Any]
```
Gets aggregated data combining all sources for a location.

#### Data Refresh
```python
def refresh_unified_data_for_location(location: str, data_sources: List[str] = None) -> Dict[str, Any]
```
Forces refresh of data for a specific location.

## API Endpoints

### Data Loading
- `POST /unified-data/{location_name}/load` - Load data from sources into Firestore
- `POST /unified-data/{location_name}/refresh` - Force refresh data for location

### Data Retrieval
- `GET /unified-data/{location_name}/firestore` - Get data directly from Firestore
- `GET /unified-data/{location_name}/aggregated/firestore` - Get aggregated data from Firestore
- `GET /unified-data/{location_name}/sources` - Get available data sources

### Legacy Endpoints (Now Use Firestore)
- `GET /unified-data/{location_name}` - Get unified data (uses Firestore)
- `GET /unified-data/{location_name}/aggregated` - Get aggregated data (uses Firestore)

### User Profile Management
- `POST /user/profile` - Create/update user profile with retention features
- `GET /user/profile/{user_id}` - Get user profile
- `GET /user/{user_id}/default-location` - Get user's default location

### Location History
- `POST /user/location` - Store user location
- `GET /user/{user_id}/location-history` - Get location history
- `GET /user/{user_id}/favorite-locations` - Get favorite locations
- `POST /user/favorite-location` - Add favorite location

### User Data Retention
- `POST /user/export` - Export all user data
- `GET /user/{user_id}/exports` - Get user's export history
- `POST /user/{user_id}/restore` - Restore user data from backup
- `GET /user/{user_id}/retention-analytics` - Get user retention analytics
- `GET /user/{user_id}/query-history` - Get user's query history

### Event Photos
- `POST /upload_event_photo` - Upload geotagged photo
- `GET /event_photos` - Get all event photos
- `GET /event_photos/{photo_id}` - Get specific event photo
- `GET /user/{user_id}/event-photos` - Get user's event photos
- `GET /location/{latitude}/{longitude}/event-photos` - Get photos by location

## Frontend API Functions

### Data Loading
```typescript
export async function loadUnifiedDataToFirestore(location: string, dataSources: string[]): Promise<any>
export async function refreshUnifiedData(location: string, dataSources: string[]): Promise<any>
```

### Data Retrieval
```typescript
export async function getUnifiedDataFromFirestore(location: string, dataType?: string, hours?: number, forceRefresh?: boolean): Promise<any>
export async function getAggregatedDataFromFirestore(location: string, hours?: number): Promise<any>
```

### Enhanced Wrapper Functions
```typescript
export async function getUnifiedDataWithFirestore(location: string, dataType?: string, hours?: number, autoLoad?: boolean): Promise<any>
export async function getAggregatedDataWithFirestore(location: string, hours?: number, autoLoad?: boolean): Promise<any>
```

### Utility Functions
```typescript
export async function getUnifiedDataSources(location: string): Promise<any>
```

## Usage Examples

### Loading Data into Firestore
```typescript
// Load all data sources for a location
const loadResult = await loadUnifiedDataToFirestore('New York', ['reddit', 'twitter', 'news', 'maps']);

// Load specific sources only
const loadResult = await loadUnifiedDataToFirestore('San Francisco', ['reddit', 'news']);

console.log('Data loaded:', loadResult.sources_loaded);
console.log('Timestamp:', loadResult.timestamp);
```

### Retrieving Data from Firestore
```typescript
// Get all data for a location
const data = await getUnifiedDataFromFirestore('New York', undefined, 24, false);

// Get specific data type
const redditData = await getUnifiedDataFromFirestore('New York', 'reddit', 24, false);

// Force refresh data
const freshData = await getUnifiedDataFromFirestore('New York', undefined, 24, true);
```

### Using Enhanced Wrapper Functions
```typescript
// Automatically loads data if not available
const data = await getUnifiedDataWithFirestore('New York', undefined, 24, true);

// Get aggregated data with auto-load
const aggregated = await getAggregatedDataWithFirestore('New York', 24, true);
```

### Refreshing Data
```typescript
// Refresh all data sources
const refreshResult = await refreshUnifiedData('New York', ['reddit', 'twitter', 'news', 'maps']);

// Refresh specific sources
const refreshResult = await refreshUnifiedData('New York', ['reddit', 'news']);
```

### Getting Available Sources
```typescript
// Check what data sources are available for a location
const sources = await getUnifiedDataSources('New York');
console.log('Available sources:', sources.sources);
```

### User Profile Management
```typescript
// Create or update user profile
const profileData = {
  preferences: {
    default_location: { latitude: 40.7128, longitude: -74.0060 },
    notification_settings: { email: true, push: true }
  }
};
const profile = await createOrUpdateUserProfile('user123', profileData);

// Get user profile
const userProfile = await getUserProfile('user123');

// Get user's default location
const defaultLocation = await getUserDefaultLocation('user123');
```

### Location History
```typescript
// Store user location
const locationResult = await storeUserLocation('user123', 40.7128, -74.0060, 'Times Square', 'visit');

// Get location history
const history = await getUserLocationHistory('user123', 7); // Last 7 days

// Get favorite locations
const favorites = await getFavoriteLocations('user123');

// Add favorite location
const addFavorite = await addFavoriteLocation('user123', 40.7128, -74.0060, 'Times Square');
```

### User Data Retention
```typescript
// Export user data
const exportResult = await exportUserData('user123');
console.log('Export ID:', exportResult.export_id);

// Get export history
const exports = await getUserDataExports('user123');

// Restore user data
const restoreResult = await restoreUserData('user123', backupData);

// Get retention analytics
const analytics = await getUserRetentionAnalytics('user123');
console.log('Retention Score:', analytics.analytics.retention_score);

// Get query history
const queryHistory = await getUserQueryHistory('user123', 20);
console.log('Query count:', queryHistory.count);
console.log('Recent queries:', queryHistory.query_history);
```

### Event Photos
```typescript
// Upload event photo
const formData = new FormData();
formData.append('file', imageFile);
formData.append('latitude', '40.7128');
formData.append('longitude', '-74.0060');
formData.append('user_id', 'user123');
formData.append('description', 'Times Square event');

const uploadResult = await uploadEventPhoto(formData);

// Get all event photos
const photos = await getEventPhotos();

// Get specific photo
const photo = await getEventPhotoById('photo123');

// Get user's photos
const userPhotos = await getUserEventPhotos('user123', 50);

// Get photos by location
const locationPhotos = await getLocationEventPhotos(40.7128, -74.0060, 5.0, 50);
```

## Data Flow

### 1. Initial Data Load
```
User Request → Load Data from APIs → Store in Firestore → Return Data
```

### 2. Subsequent Requests
```
User Request → Check Firestore → Return Cached Data
```

### 3. Auto-Refresh Flow
```
User Request → Check Firestore → No Data Found → Load from APIs → Store in Firestore → Return Data
```

### 4. Manual Refresh Flow
```
User Request → Force Refresh → Load from APIs → Update Firestore → Return Fresh Data
```

## Data Structure

### Firestore Document Structure
```json
{
  "location": "New York",
  "data_type": "reddit",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "posts": [...],
    "subreddit": "r/nyc",
    "topic": "city events"
  },
  "source": "reddit",
  "processed": false
}
```

### Aggregated Data Structure
```json
{
  "location": "New York",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "reddit": [...],
    "twitter": [...],
    "news": [...],
    "maps": [...]
  },
  "sources": ["reddit", "twitter", "news", "maps"],
  "total_sources": 4
}
```

## Performance Benefits

### 1. **Reduced API Calls**
- Data is cached in Firestore after first load
- Subsequent requests don't hit external APIs
- Reduces rate limiting issues

### 2. **Faster Response Times**
- Firestore queries are faster than external API calls
- No network latency for external services
- Consistent response times

### 3. **Better Reliability**
- Firestore provides high availability
- No dependency on external API uptime
- Automatic retry and error handling

### 4. **Data Consistency**
- All data is stored with consistent structure
- Timestamps ensure data freshness
- Version control for data changes

## Error Handling

### API Failures
- Individual API failures don't affect other sources
- Graceful degradation when sources are unavailable
- Error logging for debugging

### Firestore Issues
- Automatic retry mechanisms
- Fallback to direct API calls if needed
- Comprehensive error reporting

### Data Validation
- Input validation for location and parameters
- Data structure validation before storage
- Timestamp validation for data freshness

## Best Practices

### For Developers
1. **Use wrapper functions** for automatic data loading
2. **Set appropriate cache times** based on data freshness needs
3. **Monitor API rate limits** and implement backoff strategies
4. **Handle errors gracefully** with fallback mechanisms
5. **Log data operations** for debugging and monitoring

### For Users
1. **Load data once** and reuse cached data
2. **Refresh data periodically** for fresh information
3. **Use specific data types** when you only need certain sources
4. **Monitor data freshness** with timestamps
5. **Handle missing data** gracefully in UI

## Configuration

### Data Sources
```typescript
const DEFAULT_DATA_SOURCES = ['reddit', 'twitter', 'news', 'maps', 'rag'];
const REDDIT_SOURCES = ['reddit'];
const NEWS_SOURCES = ['news'];
const ALL_SOURCES = ['reddit', 'twitter', 'news', 'maps', 'rag'];
```

### Cache Settings
```typescript
const CACHE_DURATIONS = {
  REDDIT: 3600,    // 1 hour
  TWITTER: 1800,   // 30 minutes
  NEWS: 7200,      // 2 hours
  MAPS: 86400,     // 24 hours
  RAG: 3600        // 1 hour
};
```

### Refresh Strategies
```typescript
const REFRESH_STRATEGIES = {
  AUTO: 'auto',           // Automatically refresh when stale
  MANUAL: 'manual',       // Only refresh on explicit request
  SCHEDULED: 'scheduled'  // Refresh on schedule
};
```