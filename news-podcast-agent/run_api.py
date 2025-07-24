#!/usr/bin/env python3
"""
FastAPI Server Startup Script
Run this to start the News Podcast Agent API server.
"""

import uvicorn
from app.api_server import app

if __name__ == "__main__":
    print("🚀 Starting News Podcast Agent API Server...")
    print("📡 API will be available at: http://localhost:5001")
    print("📖 API Documentation: http://localhost:5001/docs")
    print("🔧 Interactive API: http://localhost:5001/redoc")
    print("\n" + "="*50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5001,
        reload=True,
        log_level="info"
    )
