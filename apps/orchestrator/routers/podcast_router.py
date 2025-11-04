#!/usr/bin/env python3
"""
Podcast and News Router for Orchestrator
Provides REST API endpoints for podcast generation, news, and TTS.
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any
import logging
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Add news-podcast-agent directory to Python path (due to hyphen in directory name)
news_agent_path = project_root / "news-podcast-agent"
sys.path.insert(0, str(news_agent_path))

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from app.news_tools import synthesize_speech, fetch_local_news
from app.podcast_wrapper import PodcastAgent
from app.utils.files import get_output_dir

# Create router
router = APIRouter(prefix="/podcast", tags=["podcast"])

# In-memory storage for job status (use Redis/database in production)
job_status: Dict[str, Dict[str, Any]] = {}

# Pydantic models for request/response
class PodcastRequest(BaseModel):
    city: str = Field(default="New York", description="City name for local news")
    duration_minutes: int = Field(default=5, ge=1, le=30, description="Podcast duration in minutes")
    voice: str = Field(default="en-US-Studio-Q", description="Gemini's modern TTS voice")
    speaking_rate: float = Field(default=1.0, ge=0.5, le=2.0, description="Speaking rate")

class PodcastResponse(BaseModel):
    job_id: str
    status: str
    message: str

class JobStatus(BaseModel):
    job_id: str
    status: str  # "pending", "processing", "completed", "failed"
    progress: int  # 0-100
    message: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    audio_file: Optional[str] = None
    script: Optional[str] = None
    error: Optional[str] = None

class TTSRequest(BaseModel):
    text: str = Field(..., description="Text to convert to speech")
    voice: str = Field(default="en-US-Studio-O", description="TTS voice to use")
    speaking_rate: float = Field(default=0.95, ge=0.5, le=2.0, description="Speaking rate")

# Utility functions
async def generate_podcast_async(job_id: str, city: str, duration_minutes: int, voice: str, speaking_rate: float):
    """Background task to generate podcast."""
    try:
        logging.info(f"[generate_podcast_async] Starting podcast generation for job_id={job_id}, city={city}, duration={duration_minutes}, voice={voice}, speaking_rate={speaking_rate}")
        # Update status to processing
        job_status[job_id].update({
            "status": "processing",
            "progress": 10,
            "message": "Fetching local news..."
        })
        # Initialize podcast agent
        agent = PodcastAgent()
        # Update progress
        job_status[job_id].update({
            "progress": 30,
            "message": "Generating podcast script..."
        })
        # Generate podcast script
        script = await agent.generate_podcast_script(city, duration_minutes)
        logging.info(f"[generate_podcast_async] Podcast script generated for job_id={job_id}")
        job_status[job_id].update({
            "progress": 70,
            "message": "Converting script to audio...",
            "script": script
        })
        # Generate audio file
        output_dir = get_output_dir()
        audio_filename = f"podcast_{job_id}.mp3"
        audio_path = output_dir / audio_filename
        logging.info(f"[generate_podcast_async] Saving podcast audio to {audio_path}")
        audio_file = synthesize_speech(
            text=script,
            output_path=str(audio_path),
            voice=voice,
            speaking_rate=speaking_rate
        )
        # Update status to completed
        job_status[job_id].update({
            "status": "completed",
            "progress": 100,
            "message": "Podcast generated successfully!",
            "completed_at": datetime.now(),
            "audio_file": audio_filename
        })
        logging.info(f"[generate_podcast_async] Podcast generation completed for job_id={job_id}, file={audio_filename}")
    except Exception as e:
        logging.error(f"[generate_podcast_async] Failed to generate podcast for job_id={job_id}: {e}")
        # Update status to failed
        job_status[job_id].update({
            "status": "failed",
            "progress": 0,
            "message": f"Failed to generate podcast: {str(e)}",
            "error": str(e),
            "completed_at": datetime.now()
        })

# API Endpoints

@router.get("/")
async def root():
    logging.info("[Podcast Router] Root endpoint called")
    """Root endpoint with API information."""
    return {
        "message": "News Podcast Agent API",
        "version": "1.0.0",
        "endpoints": {
            "generate_podcast": "/podcast/api/v1/podcast/generate",
            "job_status": "/podcast/api/v1/jobs/{job_id}",
            "download_audio": "/podcast/api/v1/files/{filename}",
            "text_to_speech": "/podcast/api/v1/tts"
        }
    }

@router.post("/api/v1/podcast/generate", response_model=PodcastResponse)
async def generate_podcast(request: PodcastRequest, background_tasks: BackgroundTasks):
    logging.info(f"[Podcast Router] /api/v1/podcast/generate called with city={request.city}, duration={request.duration_minutes}, voice={request.voice}, rate={request.speaking_rate}")
    """Generate a news podcast for the specified city."""
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    # Initialize job status
    job_status[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "progress": 0,
        "message": "Job queued for processing",
        "created_at": datetime.now(),
        "completed_at": None,
        "audio_file": None,
        "script": None,
        "error": None
    }
    
    # Start background task
    background_tasks.add_task(
        generate_podcast_async,
        job_id,
        request.city,
        request.duration_minutes,
        request.voice,
        request.speaking_rate
    )
    
    return PodcastResponse(
        job_id=job_id,
        status="pending",
        message="Podcast generation started"
    )

@router.get("/api/v1/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    logging.info(f"[Podcast Router] /api/v1/jobs/{{job_id}} called for job_id={job_id}")
    """Get the status of a podcast generation job."""
    
    if job_id not in job_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobStatus(**job_status[job_id])

@router.get("/api/v1/jobs")
async def list_jobs():
    logging.info("[Podcast Router] /api/v1/jobs called")
    """List all jobs with their current status."""
    return {
        "jobs": list(job_status.values()),
        "total": len(job_status)
    }

@router.get("/api/v1/files/{filename}")
async def download_file(filename: str):
    logging.info(f"[Podcast Router] /api/v1/files/{{filename}} called for filename={filename}")
    output_dir = get_output_dir()
    file_path = output_dir / filename
    if not file_path.exists():
        logging.error(f"[Podcast Router] File not found: {file_path}")
        raise HTTPException(status_code=404, detail="File not found")
    if file_path.stat().st_size == 0:
        logging.error(f"[Podcast Router] File is empty: {file_path}")
        raise HTTPException(status_code=500, detail="File is empty (TTS generation may have failed)")
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="audio/mpeg"
    )

@router.post("/api/v1/tts")
async def text_to_speech(request: TTSRequest):
    logging.info(f"[Podcast Router] /api/v1/tts called with voice={request.voice}, rate={request.speaking_rate}")
    """Convert text to speech using Google TTS."""
    
    try:
        # Generate unique filename
        filename = f"tts_{uuid.uuid4().hex[:8]}.mp3"
        output_dir = get_output_dir()
        audio_path = output_dir / filename
        
        # Generate audio
        audio_file = synthesize_speech(
            text=request.text,
            output_path=str(audio_path),
            voice=request.voice,
            speaking_rate=request.speaking_rate
        )
        
        return {
            "message": "Text converted to speech successfully",
            "filename": filename,
            "download_url": f"/podcast/api/v1/files/{filename}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")

@router.get("/api/v1/news/{city}")
async def get_local_news(city: str, limit: int = 10):
    logging.info(f"[Podcast Router] /api/v1/news/{{city}} called for city={city}, limit={limit}")
    """Get local news articles for a city."""
    
    try:
        news_articles = fetch_local_news(city, limit)
        return {
            "city": city,
            "articles": news_articles,
            "count": len(news_articles)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch news: {str(e)}")

@router.delete("/api/v1/jobs/{job_id}")
async def delete_job(job_id: str):
    logging.info(f"[Podcast Router] /api/v1/jobs/{{job_id}} DELETE called for job_id={job_id}")
    """Delete a job and its associated files."""
    
    if job_id not in job_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Delete associated audio file if it exists
    job_data = job_status[job_id]
    if job_data.get("audio_file"):
        output_dir = get_output_dir()
        audio_path = output_dir / job_data["audio_file"]
        if audio_path.exists():
            audio_path.unlink()
    
    # Remove job from status
    del job_status[job_id]
    
    return {"message": "Job deleted successfully"}

@router.get("/api/v1/health")
async def health_check():
    logging.info("[Podcast Router] /api/v1/health called")
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0"
    }