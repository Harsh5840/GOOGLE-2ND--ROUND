import os
import sys
from pathlib import Path

# Add project root to Python path to avoid import conflicts
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
from datetime import datetime

# Try to import optional dependencies
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import vertexai
    vertexai.init(
        project=os.getenv("GOOGLE_CLOUD_PROJECT", "city-project-466410"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    )
except ImportError:
    print("Warning: vertexai not available")

# FastAPI app setup
app = FastAPI()

# Static file serving for uploaded images
try:
    from fastapi.staticfiles import StaticFiles
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
except:
    print("Warning: StaticFiles not available")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request schema
class UserQuery(BaseModel):
    user_id: str
    message: str

# Response schema
class BotResponse(BaseModel):
    intent: str
    entities: dict
    reply: str
    location_data: Optional[dict] = None

@app.get("/")
def read_root():
    return {"message": "City Project Orchestrator is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/chat", response_model=BotResponse)
async def chat_router(query: UserQuery):
    """Main chat endpoint"""
    try:
        # Simple response for now
        return BotResponse(
            intent="general",
            entities={},
            reply=f"I received your message: '{query.message}'. Backend services are being deployed. This is a temporary response.",
            location_data=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/location_mood")
async def location_mood(
    location: str = Query(..., description="Location name or address"),
    datetime_str: Optional[str] = Query(None, description="ISO datetime string (optional)")
):
    """Location mood endpoint"""
    try:
        return {
            "location": location,
            "mood": "neutral",
            "sentiment_score": 0.0,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/display_locations")
async def display_locations_endpoint(locations: List[Dict[str, Any]]):
    """Display locations endpoint"""
    try:
        return {"locations": locations, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/best_route")
async def best_route_endpoint(
    origin: str = Form(...),
    destination: str = Form(...),
    mode: str = Form("driving")
):
    """Best route endpoint"""
    try:
        return {
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "route_info": f"Route from {origin} to {destination} via {mode}",
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/must_visit_places")
async def must_visit_places_endpoint(
    location: str = Form(...),
    max_results: int = Form(3)
):
    """Must visit places endpoint"""
    try:
        return {
            "location": location,
            "max_results": max_results,
            "places": [
                {"name": f"Place 1 in {location}", "rating": 4.5},
                {"name": f"Place 2 in {location}", "rating": 4.2},
                {"name": f"Place 3 in {location}", "rating": 4.0}
            ],
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 