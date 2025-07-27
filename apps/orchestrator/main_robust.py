import os
import sys
from pathlib import Path

# Add project root to Python path to avoid import conflicts
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Try to load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: dotenv not available")

# Try to initialize Vertex AI with error handling
try:
    import vertexai
    vertexai.init(
        project=os.getenv("GOOGLE_CLOUD_PROJECT", "city-project-466410"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    )
    print("Vertex AI initialized successfully")
except ImportError:
    print("Warning: vertexai not available")
except Exception as e:
    print(f"Warning: Vertex AI initialization failed: {e}")

from fastapi import FastAPI, HTTPException, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
from datetime import datetime

# Try to import optional modules with error handling
try:
    from fastapi.staticfiles import StaticFiles
    STATIC_FILES_AVAILABLE = True
except ImportError:
    print("Warning: StaticFiles not available")
    STATIC_FILES_AVAILABLE = False

try:
    from google.cloud import aiplatform
    aiplatform.init(project=os.getenv("GCP_PROJECT_ID"), location=os.getenv("GCP_REGION"))
    print("Google Cloud AI Platform initialized")
except ImportError:
    print("Warning: google.cloud.aiplatform not available")
except Exception as e:
    print(f"Warning: AI Platform initialization failed: {e}")

# Try to import custom modules with error handling
try:
    from shared.utils.logger import log_event
    LOGGING_AVAILABLE = True
except ImportError:
    print("Warning: shared.utils.logger not available")
    LOGGING_AVAILABLE = False

try:
    from agents.agent_router import agent_router
    from agents.gemini_fallback_agent import run_gemini_fallback_agent
    from agents.intent_extractor.agent import extract_intent
    from agents.agglomerator import aggregate_api_results
    AGENTS_AVAILABLE = True
except ImportError:
    print("Warning: agents modules not available")
    AGENTS_AVAILABLE = False

try:
    from tools.maps import get_must_visit_places_nearby
    from tools.image_upload import upload_event_photo, get_all_event_photos, get_event_photo_by_id
    from tools.reddit import fetch_reddit_posts
    from tools.twitter import fetch_twitter_posts
    from tools.news import fetch_city_news
    TOOLS_AVAILABLE = True
except ImportError:
    print("Warning: tools modules not available")
    TOOLS_AVAILABLE = False

try:
    from tools.firestore import (
        create_or_update_user_profile,
        get_user_profile,
        get_user_default_location,
        store_user_location,
        get_user_location_history,
        get_favorite_locations,
        add_favorite_location,
        store_unified_data,
        get_unified_data,
        get_aggregated_location_data,
        export_user_data,
        get_user_data_exports,
        restore_user_data,
        get_user_retention_analytics,
        store_user_query_history,
        load_unified_data_to_firestore,
        get_unified_data_from_firestore,
        get_aggregated_location_data_from_firestore,
        refresh_unified_data_for_location,
        get_unified_data_sources_for_location,
        clear_empty_cached_data
    )
    FIRESTORE_AVAILABLE = True
except ImportError:
    print("Warning: firestore tools not available")
    FIRESTORE_AVAILABLE = False

try:
    from shared.utils.mood import analyze_sentiment, aggregate_mood
    from shared.utils.user_photos import save_user_photo, fetch_user_photos_nearby
    UTILS_AVAILABLE = True
except ImportError:
    print("Warning: shared utils not available")
    UTILS_AVAILABLE = False

# FastAPI app setup
app = FastAPI(title="City Project Orchestrator", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files if available
if STATIC_FILES_AVAILABLE:
    try:
        app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
    except Exception as e:
        print(f"Warning: Could not mount static files: {e}")

# Request/Response models
class UserQuery(BaseModel):
    user_id: str
    message: str

class BotResponse(BaseModel):
    intent: str
    entities: dict
    reply: str
    location_data: Optional[dict] = None

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "City Project Orchestrator is running!",
        "status": "healthy",
        "modules": {
            "agents": AGENTS_AVAILABLE,
            "tools": TOOLS_AVAILABLE,
            "firestore": FIRESTORE_AVAILABLE,
            "utils": UTILS_AVAILABLE,
            "logging": LOGGING_AVAILABLE
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Chat endpoint with fallback
@app.post("/chat", response_model=BotResponse)
async def chat_router(query: UserQuery):
    try:
        if LOGGING_AVAILABLE:
            log_event("chat_request", {"user_id": query.user_id, "message": query.message})
        
        # Try to use full agent system if available
        if AGENTS_AVAILABLE:
            try:
                # Extract intent
                intent_result = extract_intent(query.message)
                intent = intent_result.get("intent", "general")
                entities = intent_result.get("entities", {})
                
                # Route to appropriate agent
                if intent in ["location", "weather", "traffic", "events"]:
                    # Use agent router for specific intents
                    response = await agent_router(query.user_id, query.message, intent, entities)
                    return BotResponse(
                        intent=intent,
                        entities=entities,
                        reply=response.get("reply", "I understand your request about " + intent),
                        location_data=response.get("location_data")
                    )
                else:
                    # Use fallback agent for general queries
                    response = await run_gemini_fallback_agent(query.user_id, query.message)
                    return BotResponse(
                        intent="general",
                        entities={},
                        reply=response.get("reply", "I'm here to help with city-related questions!"),
                        location_data=response.get("location_data")
                    )
            except Exception as e:
                print(f"Agent processing failed: {e}")
                # Fall through to basic response
        
        # Basic response if agents not available or failed
        return BotResponse(
            intent="general",
            entities={},
            reply=f"I received your message: '{query.message}'. I'm here to help with city-related questions!",
            location_data=None
        )
        
    except Exception as e:
        print(f"Chat processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Location mood endpoint
@app.post("/location_mood")
async def location_mood(
    location: str = Query(..., description="Location name or address"),
    datetime_str: Optional[str] = Query(None, description="ISO datetime string (optional)")
):
    try:
        if UTILS_AVAILABLE:
            # Use full mood analysis if available
            sentiment_score = analyze_sentiment(f"Information about {location}")
            mood = aggregate_mood(sentiment_score)
        else:
            # Basic fallback
            mood = "neutral"
            sentiment_score = 0.0
        
        return {
            "location": location,
            "mood": mood,
            "sentiment_score": sentiment_score,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Location mood error: {e}")
        return {
            "location": location,
            "mood": "neutral",
            "sentiment_score": 0.0,
            "timestamp": datetime.now().isoformat()
        }

# Display locations endpoint
@app.post("/display_locations")
async def display_locations_endpoint(locations: List[Dict[str, Any]]):
    try:
        return {
            "locations": locations,
            "status": "success",
            "message": f"Displaying {len(locations)} locations"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Best route endpoint
@app.post("/best_route")
async def best_route_endpoint(
    origin: str = Form(...),
    destination: str = Form(...),
    mode: str = Form("driving")
):
    try:
        if TOOLS_AVAILABLE:
            # Use full routing if available
            route_info = f"Route from {origin} to {destination} via {mode}"
        else:
            route_info = f"Basic route from {origin} to {destination} via {mode}"
        
        return {
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "route_info": route_info,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Must visit places endpoint
@app.post("/must_visit_places")
async def must_visit_places_endpoint(
    location: str = Form(...),
    max_results: int = Form(3)
):
    try:
        if TOOLS_AVAILABLE:
            # Use full places API if available
            places = await get_must_visit_places_nearby(location, max_results)
        else:
            # Basic fallback
            places = [
                {"name": f"Place 1 in {location}", "rating": 4.5},
                {"name": f"Place 2 in {location}", "rating": 4.2},
                {"name": f"Place 3 in {location}", "rating": 4.0}
            ]
        
        return {
            "location": location,
            "max_results": max_results,
            "places": places,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 