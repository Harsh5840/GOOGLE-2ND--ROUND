# News Podcast Agent API

A FastAPI-based REST API for generating AI-powered news podcasts with Google Cloud Text-to-Speech.

## 🚀 Quick Start

### 1. Start the API Server
```bash
python run_api.py
```

The API will be available at:
- **API Base URL**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 2. Open the Frontend
Open `frontend_example.html` in your browser to use the web interface.

## 📡 API Endpoints

### Core Endpoints

#### `POST /api/v1/podcast/generate`
Generate a news podcast for a specific city.

**Request Body:**
```json
{
  "city": "New York",
  "duration_minutes": 5,
  "voice": "en-US-Studio-O",
  "speaking_rate": 0.95
}
```

**Response:**
```json
{
  "job_id": "uuid-string",
  "status": "pending",
  "message": "Podcast generation started"
}
```

#### `GET /api/v1/jobs/{job_id}`
Get the status of a podcast generation job.

**Response:**
```json
{
  "job_id": "uuid-string",
  "status": "completed",
  "progress": 100,
  "message": "Podcast generated successfully!",
  "created_at": "2024-01-01T12:00:00",
  "completed_at": "2024-01-01T12:02:30",
  "audio_file": "podcast_uuid.mp3",
  "script": "Welcome to your local news update...",
  "error": null
}
```

#### `GET /api/v1/files/{filename}`
Download generated audio files.

**Response:** Audio file (MP3)

### Additional Endpoints

#### `POST /api/v1/tts`
Convert text to speech directly.

**Request Body:**
```json
{
  "text": "Hello world",
  "voice": "en-US-Studio-O",
  "speaking_rate": 0.95
}
```

#### `GET /api/v1/news/{city}`
Get local news articles for a city.

**Response:**
```json
{
  "city": "New York",
  "articles": [...],
  "count": 10
}
```

#### `GET /api/v1/jobs`
List all jobs and their status.

#### `DELETE /api/v1/jobs/{job_id}`
Delete a job and its associated files.

#### `GET /api/v1/health`
Health check endpoint.

## 🎙️ Supported Voices

### Studio Voices (Recommended)
- `en-US-Studio-O` - Expressive, natural
- `en-US-Studio-Q` - Clear, professional

### Neural2 Voices
- `en-US-Neural2-A` - Standard quality
- `en-US-Neural2-C` - Standard quality

### Standard Voices
- `en-US-Standard-A` - Basic quality
- `en-US-Standard-B` - Basic quality

## 🔧 Configuration

Make sure your `.env` file contains:
```env
GOOGLE_API_KEY=your-google-api-key-here
```

## 📁 File Structure

```
news-podcast-agent/
├── app/
│   ├── api_server.py          # FastAPI server
│   ├── podcast_wrapper.py     # Podcast generation wrapper
│   ├── config.py             # Configuration
│   ├── tools.py              # TTS and news tools
│   └── agent.py              # Original agent logic
├── run_api.py                # Server startup script
├── frontend_example.html     # Web interface
├── outputs/                  # Generated audio files
└── .env                      # Environment variables
```

## 🌐 Frontend Integration

The API supports CORS and can be integrated with any frontend framework:

### JavaScript Example
```javascript
// Generate podcast
const response = await fetch('http://localhost:8000/api/v1/podcast/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    city: 'London',
    duration_minutes: 3,
    voice: 'en-US-Studio-O'
  })
});

const { job_id } = await response.json();

// Poll for status
const checkStatus = async () => {
  const statusResponse = await fetch(`http://localhost:8000/api/v1/jobs/${job_id}`);
  const status = await statusResponse.json();
  
  if (status.status === 'completed') {
    // Download audio
    window.open(`http://localhost:8000/api/v1/files/${status.audio_file}`);
  }
};
```

### React Example
```jsx
import { useState, useEffect } from 'react';

function PodcastGenerator() {
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState(null);

  const generatePodcast = async (city, duration) => {
    const response = await fetch('/api/v1/podcast/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ city, duration_minutes: duration })
    });
    
    const result = await response.json();
    setJobId(result.job_id);
  };

  useEffect(() => {
    if (!jobId) return;
    
    const interval = setInterval(async () => {
      const response = await fetch(`/api/v1/jobs/${jobId}`);
      const jobStatus = await response.json();
      setStatus(jobStatus);
      
      if (jobStatus.status === 'completed' || jobStatus.status === 'failed') {
        clearInterval(interval);
      }
    }, 2000);
    
    return () => clearInterval(interval);
  }, [jobId]);

  return (
    <div>
      <button onClick={() => generatePodcast('New York', 5)}>
        Generate Podcast
      </button>
      {status && <div>Status: {status.message}</div>}
    </div>
  );
}
```

## 🔒 Security Notes

- Configure CORS origins for production
- Use environment variables for API keys
- Implement rate limiting for production use
- Add authentication for sensitive endpoints

## 🐛 Troubleshooting

### Common Issues

1. **API not responding**: Make sure the server is running with `python run_api.py`
2. **SSML errors**: The API automatically handles SSML validation for different voice types
3. **Audio not playing**: Check that the audio file was generated successfully
4. **News not found**: Try a different city name or check your internet connection

### Logs
Check the server console for detailed error messages and request logs.

## 📈 Production Deployment

For production deployment:

1. Use a production WSGI server (e.g., Gunicorn)
2. Set up proper logging
3. Use a database for job storage instead of in-memory
4. Implement proper error handling and monitoring
5. Set up file storage (e.g., cloud storage)
6. Configure proper CORS origins
7. Add authentication and rate limiting
