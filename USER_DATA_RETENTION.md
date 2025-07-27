# User Data Retention System

## Overview

The user data retention system ensures that users retain all their data across sessions, providing comprehensive data persistence, backup capabilities, and analytics. This system is built on top of Firestore and provides both backend and frontend APIs for managing user data retention.

## Key Features

### 🔄 **Data Persistence**
- **Profile Management**: Enhanced user profiles with version tracking and data retention preferences
- **Location History**: Persistent location tracking with activity types and timestamps
- **Query History**: All user interactions stored with context and responses
- **Photo Metadata**: Event photos with AI analysis and location data
- **Favorite Locations**: User-defined favorite places with coordinates

### 📊 **Data Analytics**
- **Retention Score**: Calculated based on user activity, query frequency, and engagement
- **Usage Analytics**: Comprehensive metrics about user behavior and data usage
- **Location Analytics**: Analysis of user movement patterns and location preferences
- **Photo Analytics**: Tracking of user photo uploads and engagement

### 💾 **Data Export/Import**
- **Complete Data Export**: Export all user data in JSON format for backup
- **Export History**: Track all data exports with timestamps and metadata
- **Data Restoration**: Restore user data from backup files
- **Version Control**: Track data versions and changes over time

### 🛡️ **Data Protection**
- **Automatic Backups**: Configurable automatic backup schedules
- **Data Validation**: Validate backup data before restoration
- **Error Handling**: Comprehensive error handling and logging
- **Privacy Controls**: User-configurable data retention preferences

## Backend Implementation

### Firestore Collections

```python
USER_PROFILES_COLLECTION = "user_profiles"
USER_HISTORY_COLLECTION = "user_query_history"
LOCATION_HISTORY_COLLECTION = "location_history"
UNIFIED_DATA_COLLECTION = "unified_data"
EVENT_PHOTOS_COLLECTION = "event_photos"
USER_DATA_EXPORTS_COLLECTION = "user_data_exports"
```

### Core Functions

#### User Profile Management
```python
def create_or_update_user_profile(user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]
def get_user_profile(user_id: str) -> Optional[Dict[str, Any]]
def get_user_default_location(user_id: str) -> Optional[Dict[str, float]]
```

#### Data Export/Import
```python
def export_user_data(user_id: str) -> Dict[str, Any]
def get_user_data_exports(user_id: str) -> List[Dict[str, Any]]
def restore_user_data(user_id: str, backup_data: Dict[str, Any]) -> Dict[str, Any]
```

#### Analytics
```python
def get_user_retention_analytics(user_id: str) -> Dict[str, Any]
def calculate_retention_score(user_id: str, profile: Optional[Dict], queries: List[Dict]) -> float
```

## API Endpoints

### Data Export/Import
- `POST /user/export` - Export all user data
- `GET /user/{user_id}/exports` - Get user's export history
- `POST /user/{user_id}/restore` - Restore user data from backup

### Analytics
- `GET /user/{user_id}/retention-analytics` - Get user retention analytics

### Enhanced Profile Management
- `POST /user/profile` - Create/update user profile with retention features
- `GET /user/profile/{user_id}` - Get user profile
- `GET /user/{user_id}/default-location` - Get user's default location

### Location History
- `POST /user/location` - Store user location
- `GET /user/{user_id}/location-history` - Get location history
- `GET /user/{user_id}/favorite-locations` - Get favorite locations
- `POST /user/favorite-location` - Add favorite location

## Frontend API Functions

### Data Export/Import
```typescript
export async function exportUserData(userId: string): Promise<any>
export async function getUserDataExports(userId: string): Promise<any>
export async function restoreUserData(userId: string, backupData: any): Promise<any>
```

### Analytics
```typescript
export async function getUserRetentionAnalytics(userId: string): Promise<any>
```

## Data Structure

### User Profile
```json
{
  "user_id": "string",
  "created_at": "ISO timestamp",
  "first_login": "ISO timestamp",
  "last_updated": "ISO timestamp",
  "data_version": 1,
  "preferences": {
    "default_location": {"latitude": 0.0, "longitude": 0.0},
    "favorite_locations": [],
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
    },
    "data_retention": {
      "keep_history_days": 365,
      "auto_backup": true,
      "export_frequency": "monthly"
    }
  }
}
```

### Retention Analytics
```json
{
  "user_id": "string",
  "profile_created": "ISO timestamp",
  "total_queries": 0,
  "unique_locations_visited": 0,
  "total_photos_uploaded": 0,
  "favorite_locations_count": 0,
  "last_activity": "ISO timestamp",
  "data_version": 1,
  "retention_score": 0.0
}
```

## Usage Examples

### Exporting User Data
```typescript
const exportResult = await exportUserData('user123');
console.log('Export ID:', exportResult.export_id);
console.log('Data size:', exportResult.data_size);

// Download the data
const dataStr = JSON.stringify(exportResult.data, null, 2);
const dataBlob = new Blob([dataStr], {type: 'application/json'});
const url = URL.createObjectURL(dataBlob);
const link = document.createElement('a');
link.href = url;
link.download = `user_data_${Date.now()}.json`;
link.click();
```

### Getting Retention Analytics
```typescript
const analytics = await getUserRetentionAnalytics('user123');
console.log('Retention Score:', analytics.analytics.retention_score);
console.log('Total Queries:', analytics.analytics.total_queries);
console.log('Unique Locations:', analytics.analytics.unique_locations_visited);
console.log('Photos Uploaded:', analytics.analytics.total_photos_uploaded);
```

### Restoring User Data
```typescript
const backupData = JSON.parse(backupFileContent);
const restoreResult = await restoreUserData('user123', backupData);
console.log('Restore successful:', restoreResult.success);
```

## Retention Score Calculation

The retention score (0-100) is calculated based on:

1. **Query Activity** (30 points max)
   - Based on total number of queries made
   - More queries = higher score

2. **Location Diversity** (25 points max)
   - Based on unique locations visited
   - More diverse locations = higher score

3. **Photo Uploads** (20 points max)
   - Based on number of photos uploaded
   - More photos = higher score

4. **Recent Activity** (25 points max)
   - Active in last week: 25 points
   - Active in last month: 15 points
   - Active in last quarter: 5 points

## Best Practices

### For Developers
1. **Use user IDs consistently** for all data storage and retrieval
2. **Implement automatic data export** for critical user data
3. **Use the retention analytics** to understand user engagement
4. **Validate backup data** before restoration
5. **Handle errors gracefully** with proper logging

### For Users
1. **Export data regularly** for personal backup
2. **Review retention analytics** to understand usage patterns
3. **Configure retention preferences** in user settings
4. **Keep backup files safe** for data restoration

## Security Considerations

1. **Data Validation**: All input data is validated before storage
2. **User Authentication**: Ensure proper user authentication before data access
3. **Data Encryption**: Sensitive data should be encrypted at rest
4. **Access Control**: Implement proper access controls for user data
5. **Audit Logging**: All data operations are logged for security auditing

## Future Enhancements

1. **Real-time Sync**: Implement real-time data synchronization across devices
2. **Advanced Analytics**: Add machine learning-based user behavior analysis
3. **Data Compression**: Implement data compression for large exports
4. **Incremental Backups**: Support for incremental backup strategies
5. **Cross-platform Sync**: Enable data synchronization across different platforms 