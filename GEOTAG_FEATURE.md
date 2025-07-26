# Geotag Feature Implementation

This document describes the geotag feature implementation that allows users to upload geotagged photos and view them in a dedicated dashboard.

## Features

### 1. Photo Upload with Geotagging
- **Location Capture**: Automatically captures GPS coordinates when uploading photos
- **Manual Location**: Users can manually enter latitude/longitude coordinates
- **Image Analysis**: Uses Gemini Vision API to analyze and summarize photo content
- **Metadata Storage**: Stores photo metadata including location, timestamp, user info, and AI analysis

### 2. Photo Dashboard
- **Grid View**: Display photos in a responsive grid layout
- **Map View**: View photos on an interactive Google Map
- **Search & Filter**: Search photos by description, content, or user
- **Photo Details**: Click on photos to view detailed information
- **Responsive Design**: Works on desktop and mobile devices

### 3. Integration with Main Dashboard
- **Quick Upload**: Photo upload button available in main dashboard
- **Navigation**: Direct link to photo dashboard from sidebar
- **Map Integration**: Photos appear as markers on the main map

## API Endpoints

### Upload Photo
```
POST /upload_event_photo
Content-Type: multipart/form-data

Parameters:
- file: Image file
- latitude: GPS latitude (float)
- longitude: GPS longitude (float)
- user_id: User identifier (string)
- description: Optional description (string)

Response:
{
  "success": true,
  "photo_id": "uuid",
  "message": "Event photo uploaded successfully"
}
```

### Get All Photos
```
GET /event_photos

Response:
[
  {
    "id": "uuid",
    "filename": "photo.jpg",
    "file_url": "/uploads/event_photos/photo.jpg",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "user_id": "user123",
    "description": "Optional description",
    "gemini_summary": "AI analysis of the photo",
    "upload_timestamp": "2024-01-01T12:00:00Z",
    "status": "uploaded"
  }
]
```

### Get Photo by ID
```
GET /event_photos/{photo_id}

Response: Same as individual photo object above
```

## Frontend Components

### EventPhotosDashboard
Main dashboard component for viewing and managing geotagged photos.

**Features:**
- Grid and map view modes
- Search and filtering
- Photo detail modal
- Upload functionality
- Responsive design

### PhotoUpload
Reusable component for uploading geotagged photos.

**Features:**
- File selection and preview
- Location capture
- Form validation
- Success/error handling

## File Structure

```
apps/
├── frontend/
│   ├── components/
│   │   ├── EventPhotosDashboard.tsx    # Main photo dashboard
│   │   ├── PhotoUpload.tsx             # Upload component
│   │   └── Sidebar.tsx                 # Updated with photo dashboard link
│   ├── lib/
│   │   └── api.ts                      # Updated with photo API functions
│   └── app/
│       └── event-dashboard/
│           └── page.tsx                # Photo dashboard route
├── orchestrator/
│   └── main.py                         # Updated with photo endpoints
└── tools/
    └── image_upload.py                 # Photo upload and analysis logic
```

## Usage

### 1. Upload a Photo
1. Click the "Upload Photo" button in the main dashboard or photo dashboard
2. Select an image file or take a photo
3. Enable location access or manually enter coordinates
4. Add an optional description
5. Click "Upload Photo"

### 2. View Photos
1. Navigate to the Photo Dashboard via the sidebar link
2. Browse photos in grid view or switch to map view
3. Use search to find specific photos
4. Click on photos to view detailed information

### 3. View on Map
1. Switch to map view in the photo dashboard
2. Photos appear as markers on the map
3. Click markers to view photo details
4. Photos also appear on the main dashboard map

## Technical Implementation

### Backend
- **FastAPI**: RESTful API endpoints
- **PIL**: Image processing and validation
- **Gemini Vision API**: AI-powered image analysis
- **File Storage**: Local file system with metadata JSON
- **Static File Serving**: Serves uploaded images

### Frontend
- **React/Next.js**: Modern UI framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **Google Maps**: Interactive mapping
- **Axios**: HTTP client for API calls

### Data Flow
1. User selects image and location
2. Frontend sends multipart form data to backend
3. Backend validates image and saves to file system
4. Gemini Vision API analyzes image content
5. Metadata stored in JSON file
6. Frontend displays uploaded photo in dashboard

## Security Considerations

- **File Validation**: Only image files accepted
- **File Size Limits**: Consider implementing size restrictions
- **User Authentication**: Currently uses placeholder user ID
- **Location Privacy**: Users control location sharing
- **Content Moderation**: Consider implementing content filtering

## Future Enhancements

- **User Authentication**: Integrate with Firebase Auth
- **Cloud Storage**: Move to Google Cloud Storage
- **Real-time Updates**: WebSocket integration
- **Advanced Filtering**: Date range, location radius, tags
- **Photo Albums**: Group photos by events or locations
- **Social Features**: Like, comment, share photos
- **Mobile App**: Native mobile application
- **Offline Support**: Cache photos for offline viewing

## Environment Variables

Ensure these environment variables are set:

```bash
# Google Cloud
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=your-location
GCP_PROJECT_ID=your-project-id
GCP_REGION=your-region

# Google Maps
GOOGLE_MAPS_API_KEY=your-maps-api-key

# Frontend
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Testing

1. Start the backend server: `cd apps/orchestrator && python main.py`
2. Start the frontend: `cd apps/frontend && npm run dev`
3. Navigate to the photo dashboard
4. Test photo upload with location
5. Verify photos appear in grid and map views
6. Test search and filtering functionality 