import os
from dotenv import load_dotenv
load_dotenv()

import vertexai
vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION")
)

from fastapi import FastAPI, Query, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from google.cloud import aiplatform
from shared.utils.logger import log_event
from typing import Optional, List
import json
import io

from agents.agent_router import agent_router
from tools.reddit import fetch_reddit_posts
from tools.twitter import fetch_twitter_posts
from tools.news import fetch_city_news
from agents.gemini_fallback_agent import run_gemini_fallback_agent
from shared.utils.mood import aggregate_mood
from agents.intent_extractor.agent import extract_intent
from agents.agglomerator import aggregate_api_results
from tools.maps import get_must_visit_places_nearby
from tools.image_upload import upload_event_photo, get_all_event_photos, get_event_photo_by_id
from tools.firestore import (
    create_or_update_user_profile, 
    get_user_profile, 
    get_user_default_location,
    store_user_location,
    get_recent_user_location,
    get_user_location_history,
    get_favorite_locations,
    add_favorite_location,
    store_unified_data,
    get_unified_data,
    get_aggregated_location_data,
    store_user_query_history,
    get_user_query_history
)

# Initialize Google Cloud Vertex AI
aiplatform.init(project=os.getenv("GCP_PROJECT_ID"), location=os.getenv("GCP_REGION"))

# FastAPI app setup
app = FastAPI()

# Static file serving for uploaded images
# Mount static files for uploaded images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Request schema
class UserQuery(BaseModel):
    user_id: str
    message: str

# Response schema
class BotResponse(BaseModel):
    intent: str
    entities: dict
    reply: str

# Event Photo schemas
class EventPhotoResponse(BaseModel):
    id: str
    filename: str
    file_url: str
    latitude: float
    longitude: float
    user_id: str
    description: Optional[str] = None
    gemini_summary: str
    upload_timestamp: str
    status: str

class UploadResponse(BaseModel):
    success: bool
    photo_id: Optional[str] = None
    message: str
    error: Optional[str] = None

# User Profile schemas
class UserProfileResponse(BaseModel):
    user_id: str
    preferences: dict
    created_at: str
    last_updated: str

class LocationHistoryResponse(BaseModel):
    user_id: str
    latitude: float
    longitude: float
    location_name: Optional[str] = None
    activity_type: Optional[str] = None
    timestamp: str

class UnifiedDataResponse(BaseModel):
    location: str
    data_type: str
    data: dict
    timestamp: str
    processed: bool

def dispatch_tool(intent: str, entities: dict, query: str) -> tuple[bool, str]:
    """
    Dispatch to the appropriate tool based on intent and entities.
    Returns (success: bool, reply: str)
    """
    location = entities.get("location", "")
    topic = entities.get("topic", "")
    
    if intent == "get_twitter_posts" and location and topic:
        log_event("Orchestrator", f"Calling fetch_twitter_posts with location: {location!r}, topic: {topic!r}")
        reply = fetch_twitter_posts(location=location, topic=topic, limit=10)
        log_event("Orchestrator", f"fetch_twitter_posts reply: {reply!r}")
        return True, reply
        
    elif intent == "get_reddit_posts" and "subreddit" in entities:
        log_event("Orchestrator", f"Calling fetch_reddit_posts with subreddit: {entities.get('subreddit')!r}, topic: {entities.get('topic')!r}")
        # Note: This will be awaited in the calling function
        return True, "REDDIT_ASYNC_CALL"
        
    elif intent == "social_media" and entities.get("source", "").lower() == "reddit" and "topic" in entities:
        log_event("Orchestrator", f"Calling fetch_reddit_posts (social_media intent) with subreddit: {entities.get('topic')!r}")
        # Note: This will be awaited in the calling function
        return True, "REDDIT_ASYNC_CALL"
        
    elif intent == "get_city_news" and ("city" in entities or location):
        city = entities.get("city", location)
        log_event("Orchestrator", f"Calling fetch_city_news with city: {city!r}")
        reply = fetch_city_news(city=city, limit=5)
        log_event("Orchestrator", f"fetch_city_news reply: {reply!r}")
        return True, reply
        
    elif intent == "get_firestore_reports" and location and topic:
        # TODO: Implement firestore reports tool call
        return False, "Firestore reports tool not yet implemented"
        
    elif intent == "get_similar_queries" and "user_id" in entities and "query" in entities:
        # TODO: Implement firestore similar tool call
        return False, "Firestore similar tool not yet implemented"
        
    elif intent == "google_search" and "query" in entities:
        # TODO: Implement google search tool call
        return False, "Google search tool not yet implemented"
        
    elif intent == "get_best_route" and "current_location" in entities and "destination" in entities:
        # TODO: Implement maps route tool call
        return False, "Maps route tool not yet implemented"
        
    elif intent in ["get_must_visit_places", "poi"] and location:
        reply = get_must_visit_places_nearby(location, max_results=10)
        return True, reply
        
    else:
        log_event("Orchestrator", f"No direct tool match for intent: {intent}, entities: {entities}")
        return False, ""

@app.post("/chat", response_model=BotResponse)
async def chat_router(query: UserQuery):
    log_event("Orchestrator", f"Received: {query.message}")
    
    # 1. Extract intent/entities
    intent_data = extract_intent(query.message)
    intent = intent_data["intent"]
    entities = intent_data["entities"]
    
    # 2. Dispatch to appropriate tool
    success, reply = dispatch_tool(intent, entities, query.message)
    
    # 3. Handle async tool calls
    if reply == "REDDIT_ASYNC_CALL":
        subreddit = entities.get("subreddit", entities.get("topic", "").replace(' ', ''))
        reply = await fetch_reddit_posts(subreddit=subreddit, limit=5)
        log_event("Orchestrator", f"fetch_reddit_posts reply: {reply!r}")
        success = True
    
    # 4. Fallback to agent_router if no direct tool match
    if not success:
        tool_name = None
        args = {"query": query.message, "user_id": query.user_id}
        log_event("Orchestrator", f"Falling back to agent_router for intent: {intent}")
        reply = await agent_router(tool_name, args, fallback="gemini")
        log_event("Orchestrator", f"Agent reply: {reply!r}")

    # 5. General Gemini fallback for empty/error responses
    if (
        not reply.strip() or
        reply.lower().startswith("error fetching") or
        reply.lower().startswith("no posts found") or
        "rate limit" in reply.lower() or
        "not yet implemented" in reply.lower()
    ):
        log_event("Orchestrator", "No valid reply from tool, falling back to Gemini LLM.")
        reply = await run_gemini_fallback_agent(query.message, user_id=query.user_id)

    # 6. Store query history in Firestore
    try:
        store_user_query_history(
            user_id=query.user_id,
            query=query.message,
            response_data={"intent": intent, "entities": entities, "reply": reply},
            location=entities.get("location")
        )
    except Exception as e:
        log_event("Orchestrator", f"Error storing query history: {str(e)}")

    return BotResponse(intent=intent, entities=entities, reply=reply)

# User Profile Management Endpoints
@app.post("/user/profile", response_model=UserProfileResponse)
async def create_update_user_profile(
    user_id: str = Form(...),
    profile_data: str = Form(...)  # JSON string
):
    """Create or update user profile"""
    try:
        data = json.loads(profile_data)
        result = create_or_update_user_profile(user_id, data)
        if result["success"]:
            return UserProfileResponse(**result["profile"])
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        log_event("Orchestrator", f"Error in create_update_user_profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/profile/{user_id}", response_model=UserProfileResponse)
async def get_user_profile_endpoint(user_id: str):
    """Get user profile by ID"""
    try:
        profile = get_user_profile(user_id)
        if profile:
            return UserProfileResponse(**profile)
        else:
            raise HTTPException(status_code=404, detail="User profile not found")
    except Exception as e:
        log_event("Orchestrator", f"Error getting user profile {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/{user_id}/default-location")
async def get_user_default_location_endpoint(user_id: str):
    """Get user's default location"""
    try:
        location = get_user_default_location(user_id)
        return {"location": location}
    except Exception as e:
        log_event("Orchestrator", f"Error getting default location for {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Location History Endpoints
@app.post("/user/location")
async def store_user_location_endpoint(
    user_id: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    location_name: Optional[str] = Form(None),
    activity_type: Optional[str] = Form(None)
):
    """Store user location"""
    try:
        result = store_user_location(user_id, latitude, longitude, location_name, activity_type)
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        log_event("Orchestrator", f"Error storing user location: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/{user_id}/location-history")
async def get_user_location_history_endpoint(user_id: str, days: int = 7):
    """Get user's location history"""
    try:
        history = get_user_location_history(user_id, days)
        return {"history": history}
    except Exception as e:
        log_event("Orchestrator", f"Error getting location history for {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/{user_id}/favorite-locations")
async def get_favorite_locations_endpoint(user_id: str):
    """Get user's favorite locations"""
    try:
        favorites = get_favorite_locations(user_id)
        return {"favorites": favorites}
    except Exception as e:
        log_event("Orchestrator", f"Error getting favorite locations for {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/user/favorite-location")
async def add_favorite_location_endpoint(
    user_id: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    location_name: str = Form(...)
):
    """Add location to user's favorites"""
    try:
        result = add_favorite_location(user_id, latitude, longitude, location_name)
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    except Exception as e:
        log_event("Orchestrator", f"Error adding favorite location: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Unified Data Endpoints
@app.post("/unified-data")
async def store_unified_data_endpoint(
    location: str = Form(...),
    data_type: str = Form(...),
    data: str = Form(...),  # JSON string
    user_id: Optional[str] = Form(None)
):
    """Store unified data"""
    try:
        data_dict = json.loads(data)
        result = store_unified_data(location, data_type, data_dict, user_id)
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        log_event("Orchestrator", f"Error storing unified data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/unified-data/{location}")
async def get_unified_data_endpoint(
    location: str,
    data_type: Optional[str] = None,
    hours: int = 24
):
    """Get unified data for a location"""
    try:
        data = get_unified_data(location, data_type, hours)
        return {"data": data}
    except Exception as e:
        log_event("Orchestrator", f"Error getting unified data for {location}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/unified-data/{location}/aggregated")
async def get_aggregated_data_endpoint(location: str, hours: int = 24):
    """Get aggregated data for a location"""
    try:
        aggregated = get_aggregated_location_data(location, hours)
        return aggregated
    except Exception as e:
        log_event("Orchestrator", f"Error getting aggregated data for {location}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Event Photos Endpoints
@app.post("/upload_event_photo", response_model=UploadResponse)
async def upload_event_photo_endpoint(
    file: UploadFile = File(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    user_id: str = Form(...),
    description: Optional[str] = Form(None)
):
    """Upload a geotagged image for city event reporting."""
    """
    Upload a geotagged image for city event reporting.
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image data
        image_data = await file.read()
        
        # Upload the photo
        result = upload_event_photo(
            image_data=image_data,
            latitude=latitude,
            longitude=longitude,
            user_id=user_id,
            description=description
        )
        
        if result["success"]:
            return UploadResponse(
                success=True,
                photo_id=result["photo_id"],
                message=result["message"]
            )
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except Exception as e:
        log_event("Orchestrator", f"Error in upload_event_photo_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/event_photos", response_model=List[EventPhotoResponse])
async def get_event_photos():
    """Get all uploaded event photos with their metadata and Gemini summaries."""
    """
    Get all uploaded event photos with their metadata and Gemini summaries.
    """
    try:
        photos = get_all_event_photos()
        return [EventPhotoResponse(**photo) for photo in photos]
    except Exception as e:
        log_event("Orchestrator", f"Error getting event photos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/event_photos/{photo_id}", response_model=EventPhotoResponse)
async def get_event_photo(photo_id: str):
    """Get a specific event photo by ID."""
    """
    Get a specific event photo by ID.
    """
    try:
        photo = get_event_photo_by_id(photo_id)
        if photo:
            return EventPhotoResponse(**photo)
        else:
            raise HTTPException(status_code=404, detail="Photo not found")
    except Exception as e:
        log_event("Orchestrator", f"Error getting event photo {photo_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/{user_id}/event-photos")
async def get_user_event_photos_endpoint(user_id: str, limit: int = 50):
    """Get all event photos uploaded by a specific user"""
    try:
        from tools.firestore import get_user_event_photos
        photos = get_user_event_photos(user_id, limit)
        return {"photos": photos}
    except Exception as e:
        log_event("Orchestrator", f"Error getting user event photos for {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/location/{latitude}/{longitude}/event-photos")
async def get_location_event_photos_endpoint(
    latitude: float,
    longitude: float,
    radius_km: float = 5.0,
    limit: int = 50
):
    """Get event photos within a radius of specified coordinates"""
    try:
        from tools.firestore import get_location_event_photos
        photos = get_location_event_photos(latitude, longitude, radius_km, limit)
        return {"photos": photos}
    except Exception as e:
        log_event("Orchestrator", f"Error getting location event photos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/location_mood")
async def location_mood(
    location: str = Query(..., description="Location name or address"),
    datetime_str: Optional[str] = Query(
        None, description="ISO datetime string (optional)"
    ),
):
    """
    Aggregate mood for a location at a given time using the unified aggregator response.
    Returns a mood label, score, detected events, must-visit places, and source breakdown for frontend use.
    """
    unified_data = aggregate_api_results(
        reddit_data=[],
        twitter_data=[],
        news_data=[],
        maps_data=[],
        rag_data=[],
        google_search_data=[],
    )
    mood_result = aggregate_mood(unified_data)
    must_visit_places = []
    return {
        "location": location,
        "datetime": datetime_str,
        **mood_result,
        "must_visit_places": must_visit_places,
    }

if __name__ == "__main__":
    import uvicorn
    print("GOOGLE_MAPS_API_KEY (startup):", repr(os.getenv("GOOGLE_MAPS_API_KEY")))
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
