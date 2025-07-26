import os
from dotenv import load_dotenv
load_dotenv()

import vertexai
vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION")
)

from fastapi import FastAPI, HTTPException, Form, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import asyncio
from google.cloud import aiplatform
from shared.utils.logger import log_event
from typing import Optional, List, Dict, Any, Tuple
import json
from fastapi import UploadFile, File
from google.cloud import storage
from uuid import uuid4
from datetime import datetime

from agents.agent_router import agent_router
from agents.gemini_fallback_agent import run_gemini_fallback_agent
from agents.intent_extractor.agent import extract_intent
from agents.agglomerator import aggregate_api_results
from tools.maps import get_must_visit_places_nearby
from tools.image_upload import upload_event_photo, get_all_event_photos, get_event_photo_by_id
from tools.reddit import fetch_reddit_posts
from tools.twitter import fetch_twitter_posts
from tools.news import fetch_city_news
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
from shared.utils.mood import analyze_sentiment, aggregate_mood
from shared.utils.user_photos import save_user_photo, fetch_user_photos_nearby

# Initialize Google Cloud Vertex AI
aiplatform.init(project=os.getenv("GCP_PROJECT_ID"), location=os.getenv("GCP_REGION"))

# FastAPI app setup
app = FastAPI()

# Static file serving for uploaded images
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
    location_data: Optional[dict] = None  # For location display data

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

def dispatch_tool(intent: str, entities: dict, query: str) -> tuple[bool, str, Optional[dict]]:
    """
    Dispatch to appropriate tool based on intent and entities.
    Returns (success, reply, response_data).
    """
    location = entities.get("location")
    
    if intent == "google_search" and "query" in entities:
        # Implement google search tool call
        try:
            from tools.google_search import google_search # Corrected from search_google
            query = entities.get("query")
            log_event("Orchestrator", f"Calling google_search with query: {query!r}")
            results = google_search(query=query, num_results=5) # Corrected function call
            if results:
                reply = f"Google search results for '{query}':\n" + "\n".join([f"- {r.get('title', 'No title')}: {r.get('snippet', 'No snippet')}" for r in results])
            else:
                reply = f"No results found for '{query}'"
            log_event("Orchestrator", f"google_search reply: {reply[:100]}...")
            return True, reply, None
        except Exception as e:
            log_event("Orchestrator", f"Error in google_search: {e}")
            return False, f"Error performing Google search: {e}", None
        
    elif intent == "best_route" and "origin" in entities and "destination" in entities:
        # Implement best route tool call
        try:
            from tools.maps import get_best_route, display_locations_on_map
            origin = entities.get("origin")
            destination = entities.get("destination")
            mode = entities.get("mode", "driving")
            
            log_event("Orchestrator", f"Calling get_best_route with origin: {origin}, destination: {destination}, mode: {mode}")
            
            result = get_best_route(origin, destination, mode)
            
            if result["success"]:
                # Format locations for frontend display
                display_result = display_locations_on_map(result["locations_to_display"])
                
                reply = result["route_info"]
                if result["mood_data"]:
                    origin_mood = result["mood_data"]["origin"]["mood_label"]
                    dest_mood = result["mood_data"]["destination"]["mood_label"]
                    reply += f"\n\nMood Analysis:\nOrigin ({origin}): {origin_mood}\nDestination ({destination}): {dest_mood}"
                
                # Add location display data to response
                response_data = {
                    "route_info": result["route_info"],
                    "mood_data": result["mood_data"],
                    "locations_to_display": display_result["locations"],
                    "route_details": result["route_details"]
                }
                
                log_event("Orchestrator", f"get_best_route reply: {reply[:100]}...")
                return True, reply, response_data
            else:
                reply = f"Error finding route: {result['error']}"
                log_event("Orchestrator", f"get_best_route error: {reply}")
                return False, reply, None
                
        except Exception as e:
            log_event("Orchestrator", f"Error in get_best_route: {e}")
            return False, f"Error finding route: {e}", None
        
    elif intent == "poi" and "location" in entities:
        # Implement must visit places tool call
        try:
            from tools.maps import get_must_visit_places_nearby, display_locations_on_map
            location = entities.get("location")
            max_results = entities.get("max_results", 3)
            
            log_event("Orchestrator", f"Calling get_must_visit_places_nearby with location: {location}, max_results: {max_results}")
            
            result = get_must_visit_places_nearby(location, max_results)
            
            if result["success"]:
                # Format locations for frontend display
                display_result = display_locations_on_map(result["locations_to_display"])
                
                reply = result["summary"]
                if result["mood_data"]:
                    mood_label = result["mood_data"]["mood_label"]
                    mood_score = result["mood_data"]["mood_score"]
                    reply += f"\n\nLocation Mood: {mood_label} (Score: {mood_score})"
                
                # Add location display data to response
                response_data = {
                    "places": result["places"],
                    "mood_data": result["mood_data"],
                    "locations_to_display": display_result["locations"],
                    "summary": result["summary"]
                }
                
                log_event("Orchestrator", f"get_must_visit_places_nearby reply: {reply[:100]}...")
                return True, reply, response_data
            else:
                reply = f"Error finding must-visit places: {result['error']}"
                log_event("Orchestrator", f"get_must_visit_places_nearby error: {reply}")
                return False, reply, None
                
        except Exception as e:
            log_event("Orchestrator", f"Error in get_must_visit_places_nearby: {e}")
            return False, f"Error finding must-visit places: {e}", None
        
    elif intent == "history" or "query" in query.lower() and ("first" in query.lower() or "previous" in query.lower() or "last" in query.lower()):
        # Handle user queries related to history
        try:
            from tools.firestore import get_user_query_history
            # Extract user_id from entities or use a default
            user_id = entities.get("user_id", "default_user")
            history = get_user_query_history(user_id, limit=5)
            
            if history:
                reply = "Your recent queries:\n" + "\n".join([
                    f"- {entry.get('query', 'Unknown query')} ({entry.get('timestamp', 'Unknown time')})"
                    for entry in history
                ])
            else:
                reply = "No query history found."
            
            return True, reply, None
        except Exception as e:
            log_event("Orchestrator", f"Error getting query history: {e}")
            return False, f"Error retrieving query history: {e}", None
    
    # Add more tool calls as needed
    elif intent == "fetch_firestore_reports":
        # Implement fetch_firestore_reports tool call
        try:
            from tools.firestore import fetch_firestore_reports
            location = entities.get("location", "")
            topic = entities.get("topic", "")
            reply = fetch_firestore_reports(location, topic)
            return True, reply, None
        except Exception as e:
            log_event("Orchestrator", f"Error in fetch_firestore_reports: {e}")
            return False, f"Error fetching reports: {e}", None
    
    elif intent == "fetch_similar_user_queries":
        # Implement fetch_similar_user_queries tool call
        try:
            from tools.firestore import fetch_similar_user_queries
            user_id = entities.get("user_id", "")
            query = entities.get("query", "")
            reply = fetch_similar_user_queries(user_id, query)
            return True, reply, None
        except Exception as e:
            log_event("Orchestrator", f"Error in fetch_similar_user_queries: {e}")
            return False, f"Error fetching similar queries: {e}", None
    
    return False, "", None

@app.post("/chat", response_model=BotResponse)
async def chat_router(query: UserQuery):
    log_event("Orchestrator", f"Received: {query.message}")
    
    # 1. Extract intent/entities
    intent_data = extract_intent(query.message)
    intent = intent_data["intent"]
    entities = intent_data["entities"]
    
    # Add user_id to entities for query history and other user-specific operations
    entities["user_id"] = query.user_id
    
    # 2. Dispatch to appropriate tool
    success, reply, response_data = dispatch_tool(intent, entities, query.message)
    
    # 3. Handle async tool calls
    if reply == "REDDIT_ASYNC_CALL":
        subreddit = entities.get("subreddit", entities.get("topic", "").replace(' ', ''))
        
        # Check Firestore first for cached Reddit data
        try:
            from tools.firestore import get_unified_data_from_firestore
            log_event("Orchestrator", f"Checking Firestore for cached Reddit data for: {subreddit}")
            
            # Try to get cached Reddit data from Firestore
            cached_data = get_unified_data_from_firestore(subreddit, "reddit", 24, force_refresh=False)
            
            if cached_data and len(cached_data) > 0:
                # Use cached data
                log_event("Orchestrator", f"Using cached Reddit data from Firestore for: {subreddit}")
                reddit_data = cached_data[0].get("data", {})
                if "posts" in reddit_data:
                    posts = reddit_data["posts"]
                    if posts:
                        reply = f"Latest posts from r/{subreddit}:\n" + "\n".join(posts)
                        success = True
                        log_event("Orchestrator", f"Using cached Reddit data: {reply!r}")
                        return BotResponse(intent=intent, entities=entities, reply=reply, location_data=response_data)
        except Exception as e:
            log_event("Orchestrator", f"Error checking Firestore for Reddit data: {e}")
        
        # If no cached data, fetch from API and store in Firestore
        log_event("Orchestrator", f"No cached data found, fetching from API for: {subreddit}")
        reply = await fetch_reddit_posts(subreddit=subreddit, limit=5)
        
        # Store the result in Firestore for future use
        try:
            from tools.firestore import store_unified_data
            posts_list = reply.split('\n')[1:] if '\n' in reply else [reply]  # Extract posts from reply
            store_unified_data(subreddit, "reddit", {
                "posts": posts_list,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "reddit_api"
            })
            log_event("Orchestrator", f"Stored Reddit data in Firestore for: {subreddit}")
        except Exception as e:
            log_event("Orchestrator", f"Error storing Reddit data in Firestore: {e}")
        
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

    return BotResponse(intent=intent, entities=entities, reply=reply, location_data=response_data)

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
    location_name: str = Form(...),
    data_type: str = Form(...),
    data: str = Form(...),  # JSON string
    user_id: Optional[str] = Form(None)
):
    """Store unified data"""
    try:
        data_dict = json.loads(data)
        result = store_unified_data(location_name, data_type, data_dict, user_id)
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        log_event("Orchestrator", f"Error storing unified data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/unified-data/{location_name}")
async def get_unified_data_endpoint(
    location_name: str,
    data_type: Optional[str] = None,
    hours: int = 24
):
    """Get unified data for a location"""
    try:
        data = get_unified_data(location_name, data_type, hours)
        return {"data": data}
    except Exception as e:
        log_event("Orchestrator", f"Error getting unified data for {location_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/unified-data/{location_name}/aggregated")
async def get_aggregated_data_endpoint(location_name: str, hours: int = 24):
    """Get aggregated data for a location"""
    try:
        aggregated = get_aggregated_location_data(location_name, hours)
        return aggregated
    except Exception as e:
        log_event("Orchestrator", f"Error getting aggregated data for {location_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced Unified Data Management Endpoints
@app.post("/unified-data/{location_name}/load")
async def load_unified_data_endpoint(
    location_name: str,
    data_sources: str = Form("reddit,twitter,news,maps,rag")  # Comma-separated list
):
    """Load unified data from various sources into Firestore for a specific location"""
    try:
        sources_list = [s.strip() for s in data_sources.split(",") if s.strip()]
        result = load_unified_data_to_firestore(location_name, sources_list)
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        log_event("Orchestrator", f"Error loading unified data for {location_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/unified-data/{location_name}/sources")
async def get_unified_data_sources_endpoint(location_name: str):
    """Get available data sources for a location from Firestore"""
    try:
        sources = get_unified_data_sources_for_location(location_name)
        return {"location": location_name, "sources": sources}
    except Exception as e:
        log_event("Orchestrator", f"Error getting data sources for {location_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/unified-data/{location_name}/refresh")
async def refresh_unified_data_endpoint(
    location_name: str,
    data_sources: str = Form("reddit,twitter,news,maps,rag")  # Comma-separated list
):
    """Force refresh unified data for a specific location"""
    try:
        sources_list = [s.strip() for s in data_sources.split(",") if s.strip()]
        result = refresh_unified_data_for_location(location_name, sources_list)
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        log_event("Orchestrator", f"Error refreshing unified data for {location_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/unified-data/{location_name}/firestore")
async def get_unified_data_firestore_endpoint(
    location_name: str,
    data_type: Optional[str] = None,
    hours: int = 24,
    force_refresh: bool = False
):
    """Get unified data directly from Firestore with optional refresh"""
    try:
        data = get_unified_data_from_firestore(location_name, data_type, hours, force_refresh)
        return {"location": location_name, "data": data, "count": len(data)}
    except Exception as e:
        log_event("Orchestrator", f"Error getting unified data from Firestore for {location_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/unified-data/{location_name}/aggregated/firestore")
async def get_aggregated_data_firestore_endpoint(location_name: str, hours: int = 24):
    """Get aggregated data directly from Firestore"""
    try:
        aggregated = get_aggregated_location_data_from_firestore(location_name, hours)
        return aggregated
    except Exception as e:
        log_event("Orchestrator", f"Error getting aggregated data from Firestore for {location_name}: {str(e)}")
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
    try:
        photos = get_all_event_photos()
        return [EventPhotoResponse(**photo) for photo in photos]
    except Exception as e:
        log_event("Orchestrator", f"Error getting event photos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/event_photos/{photo_id}", response_model=EventPhotoResponse)
async def get_event_photo(photo_id: str):
    """Get a specific event photo by ID."""
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

# User Data Retention Endpoints
@app.post("/user/export")
async def export_user_data_endpoint(user_id: str = Form(...)):
    """Export all user data for backup and retention"""
    try:
        result = export_user_data(user_id)
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        log_event("Orchestrator", f"Error exporting user data for {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/{user_id}/exports")
async def get_user_data_exports_endpoint(user_id: str):
    """Get user's data export history"""
    try:
        exports = get_user_data_exports(user_id)
        return {"exports": exports}
    except Exception as e:
        log_event("Orchestrator", f"Error getting user data exports for {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/user/{user_id}/restore")
async def restore_user_data_endpoint(
    user_id: str,
    backup_data: str = Form(...)  # JSON string
):
    """Restore user data from backup"""
    try:
        data = json.loads(backup_data)
        result = restore_user_data(user_id, data)
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    except Exception as e:
        log_event("Orchestrator", f"Error restoring user data for {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/{user_id}/retention-analytics")
async def get_user_retention_analytics_endpoint(user_id: str):
    """Get analytics about user data retention and usage"""
    try:
        result = get_user_retention_analytics(user_id)
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        log_event("Orchestrator", f"Error getting retention analytics for {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/{user_id}/query-history")
async def get_user_query_history_endpoint(user_id: str, limit: int = 20):
    """Get user's query history"""
    try:
        from tools.firestore import get_user_query_history
        history = get_user_query_history(user_id, limit)
        return {"user_id": user_id, "query_history": history, "count": len(history)}
    except Exception as e:
        log_event("Orchestrator", f"Error getting query history for {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/submit_photo")
async def submit_photo(
    file: UploadFile = File(...),
    lat: float = Form(...),
    lng: float = Form(...),
    description: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None)
):
    """
    Accepts a photo upload, geotags it, and stores metadata in Firestore.
    """
    photo_url = await save_user_photo(file, lat, lng, description, user_id)
    if photo_url:
        return {"success": True, "photo_url": photo_url}
    else:
        return {"success": False, "error": "Failed to save photo."}

@app.post("/location_mood")
async def location_mood(
    location: str = Query(..., description="Location name or address"),
    datetime_str: Optional[str] = Query(
        None, description="ISO datetime string (optional)"
    ),
):
    """
    Aggregate mood for a location at a given time using the unified aggregator response.
    Returns a mood label, score, detected events, must-visit places, user photos, and source breakdown for frontend use.
    """
    try:
        # Get mood data using the new maps functionality
        from tools.maps import get_location_mood_data, get_must_visit_places_nearby, display_locations_on_map
        
        # Get mood data for the location
        mood_result = get_location_mood_data(location)
        
        # Get must-visit places with mood integration
        places_result = get_must_visit_places_nearby(location, max_results=3)
        
        # Prepare response data
        response_data = {
            "location": location,
            "datetime": datetime_str,
            **mood_result
        }
        
        # Add must-visit places if available
        if places_result["success"]:
            response_data["must_visit_places"] = places_result["places"]
            response_data["locations_to_display"] = places_result["locations_to_display"]
        else:
            response_data["must_visit_places"] = []
            response_data["locations_to_display"] = []
        
        # Get user photos near the location
        try:
            from tools.firestore import get_location_event_photos
            # Geocode location for lat/lng
            import googlemaps
            gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))
            geocode = gmaps.geocode(location)
            latlng = geocode[0]["geometry"]["location"] if geocode else {"lat": None, "lng": None}
            
            user_photos = []
            if latlng["lat"] is not None and latlng["lng"] is not None:
                user_photos = get_location_event_photos(latlng["lat"], latlng["lng"], radius_km=5.0, limit=10)
            response_data["user_photos"] = user_photos
        except Exception as e:
            log_event("Orchestrator", f"Error getting user photos for {location}: {e}")
            response_data["user_photos"] = []
        
        return response_data
        
    except Exception as e:
        log_event("Orchestrator", f"Error in location_mood endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/display_locations")
async def display_locations_endpoint(locations: List[Dict[str, Any]]):
    """
    Display locations on the frontend map with mood data.
    """
    try:
        from tools.maps import display_locations_on_map
        result = display_locations_on_map(locations)
        return result
    except Exception as e:
        log_event("Orchestrator", f"Error in display_locations_endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/best_route")
async def best_route_endpoint(
    origin: str = Form(...),
    destination: str = Form(...),
    mode: str = Form("driving")
):
    """
    Get the best route between two locations with mood data.
    """
    try:
        from tools.maps import get_best_route, display_locations_on_map
        result = get_best_route(origin, destination, mode)
        
        if result["success"]:
            # Format locations for frontend display
            display_result = display_locations_on_map(result["locations_to_display"])
            result["locations_to_display"] = display_result["locations"]
        
        return result
    except Exception as e:
        log_event("Orchestrator", f"Error in best_route_endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/must_visit_places")
async def must_visit_places_endpoint(
    location: str = Form(...),
    max_results: int = Form(3)
):
    """
    Get must-visit places near a location with mood data.
    """
    try:
        from tools.maps import get_must_visit_places_nearby, display_locations_on_map
        result = get_must_visit_places_nearby(location, max_results)
        
        if result["success"]:
            # Format locations for frontend display
            display_result = display_locations_on_map(result["locations_to_display"])
            result["locations_to_display"] = display_result["locations"]
        
        return result
    except Exception as e:
        log_event("Orchestrator", f"Error in must_visit_places_endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    log_event("Orchestrator", "Starting FastAPI server...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
