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
        
        # Check Firestore first for cached news data
        try:
            from tools.firestore import get_unified_data_from_firestore
            log_event("Orchestrator", f"Checking Firestore for cached news data for: {city}")
            
            # Try to get cached news data from Firestore
            cached_data = get_unified_data_from_firestore(city, "news", 24, force_refresh=False)
            
            if cached_data and len(cached_data) > 0:
                # Use cached data
                log_event("Orchestrator", f"Using cached news data from Firestore for: {city}")
                news_data = cached_data[0].get("data", {})
                if "articles" in news_data:
                    articles = news_data["articles"]
                    if articles:
                        reply = f"Latest news for {city}:\n" + "\n".join(articles)
                        return True, reply
            
            # If no cached data, fetch from API and store in Firestore
            log_event("Orchestrator", f"No cached data found, fetching from API for: {city}")
            reply = fetch_city_news(city=city, limit=5)
            
            # Store the result in Firestore for future use
            try:
                from tools.firestore import store_unified_data
                articles_list = reply.split('\n')[1:] if '\n' in reply else [reply]  # Extract articles from reply
                store_unified_data(city, "news", {
                    "articles": articles_list,
                    "timestamp": datetime.utcnow().isoformat(),
                    "source": "news_api"
                })
                log_event("Orchestrator", f"Stored news data in Firestore for: {city}")
            except Exception as e:
                log_event("Orchestrator", f"Error storing news data in Firestore: {e}")
            
            log_event("Orchestrator", f"fetch_city_news reply: {reply!r}")
            return True, reply
            
        except Exception as e:
            log_event("Orchestrator", f"Error checking Firestore for news data: {e}")
            # Fallback to direct API call
            reply = fetch_city_news(city=city, limit=5)
            log_event("Orchestrator", f"fetch_city_news reply: {reply!r}")
            return True, reply
        
    elif intent == "get_firestore_reports" and location and topic:
        # Implement firestore reports tool call
        try:
            from tools.firestore import fetch_firestore_reports
            log_event("Orchestrator", f"Calling fetch_firestore_reports with location: {location!r}, topic: {topic!r}")
            reply = fetch_firestore_reports(location=location, topic=topic, limit=5)
            log_event("Orchestrator", f"fetch_firestore_reports reply: {reply!r}")
            return True, reply
        except Exception as e:
            log_event("Orchestrator", f"Error in fetch_firestore_reports: {e}")
            return False, f"Error fetching Firestore reports: {e}"
        
    elif intent == "get_similar_queries" and "user_id" in entities and "query" in entities:
        # Implement firestore similar tool call
        try:
            from tools.firestore import fetch_similar_user_queries
            user_id = entities.get("user_id")
            query = entities.get("query")
            log_event("Orchestrator", f"Calling fetch_similar_user_queries with user_id: {user_id!r}, query: {query!r}")
            reply = fetch_similar_user_queries(user_id=user_id, query=query, limit=5)
            log_event("Orchestrator", f"fetch_similar_user_queries reply: {reply!r}")
            return True, reply
        except Exception as e:
            log_event("Orchestrator", f"Error in fetch_similar_user_queries: {e}")
            return False, f"Error fetching similar queries: {e}"
        
    elif intent == "google_search" and "query" in entities:
        # Implement google search tool call
        try:
            from tools.google_search import google_search
            query = entities.get("query")
            log_event("Orchestrator", f"Calling google_search with query: {query!r}")
            results = google_search(query=query, num_results=5)
            if results:
                reply = f"Google search results for '{query}':\n" + "\n".join([f"- {r.get('title', 'No title')}: {r.get('snippet', 'No snippet')}" for r in results])
            else:
                reply = f"No results found for '{query}'"
            log_event("Orchestrator", f"google_search reply: {reply[:100]}...")
            return True, reply
        except Exception as e:
            log_event("Orchestrator", f"Error in google_search: {e}")
            return False, f"Error performing Google search: {e}"
        
    elif intent == "get_best_route" and "current_location" in entities and "destination" in entities:
        # Implement maps route tool call
        try:
            from tools.maps import get_best_route
            current_location = entities.get("current_location")
            destination = entities.get("destination")
            mode = entities.get("mode", "driving")
            log_event("Orchestrator", f"Calling get_best_route with current_location: {current_location!r}, destination: {destination!r}")
            reply = get_best_route(current_location=current_location, destination=destination, mode=mode)
            log_event("Orchestrator", f"get_best_route reply: {reply!r}")
            return True, reply
        except Exception as e:
            log_event("Orchestrator", f"Error in get_best_route: {e}")
            return False, f"Error getting route: {e}"
        
    elif intent in ["get_must_visit_places", "poi"] and location:
        # Check Firestore first for cached data
        try:
            from tools.firestore import get_unified_data_from_firestore
            log_event("Orchestrator", f"Checking Firestore for cached places data for: {location}")
            
            # Try to get cached maps data from Firestore
            cached_data = get_unified_data_from_firestore(location, "maps", 24, force_refresh=False)
            
            if cached_data and len(cached_data) > 0:
                # Check if cached data is actually useful (not empty)
                places_data = cached_data[0].get("data", {})
                if "places" in places_data and places_data["places"]:
                    places = places_data["places"]
                    # Check if places list is not empty and contains actual data
                    if places and len(places) > 0 and not all(place.strip() == "" for place in places):
                        # Additional check: make sure places don't contain error messages
                        error_indicators = [
                            "no must-visit places found",
                            "no places found",
                            "could not find",
                            "error",
                            "exception",
                            "not found"
                        ]
                        
                        places_text = " ".join(places).lower()
                        has_error = any(indicator in places_text for indicator in error_indicators)
                        
                        if not has_error:
                            log_event("Orchestrator", f"Using cached places data from Firestore for: {location}")
                            reply = "Must visit places in " + location + ":\n" + "\n".join(places)
                            return True, reply
                        else:
                            log_event("Orchestrator", f"Cached data contains error message, fetching fresh data for: {location}")
                            # Clear error-containing cached data
                            try:
                                from tools.firestore import clear_empty_cached_data
                                clear_empty_cached_data(location, "maps")
                            except Exception as e:
                                log_event("Orchestrator", f"Error clearing error-containing cached data: {e}")
                    else:
                        log_event("Orchestrator", f"Cached data is empty, fetching fresh data for: {location}")
                        # Clear empty cached data
                        try:
                            from tools.firestore import clear_empty_cached_data
                            clear_empty_cached_data(location, "maps")
                        except Exception as e:
                            log_event("Orchestrator", f"Error clearing empty cached data: {e}")
                else:
                    log_event("Orchestrator", f"No places data in cache, fetching fresh data for: {location}")
            else:
                log_event("Orchestrator", f"No cached data found, fetching from API for: {location}")
            
            # If no useful cached data, fetch from API and store in Firestore
            log_event("Orchestrator", f"Fetching fresh places data from API for: {location}")
            reply = get_must_visit_places_nearby(location, max_results=10)
            
            # Store the result in Firestore for future use
            try:
                from tools.firestore import store_unified_data
                places_list = reply.split('\n')[1:] if '\n' in reply else [reply]  # Extract places from reply
                store_unified_data(location, "maps", {
                    "places": places_list,
                    "timestamp": datetime.utcnow().isoformat(),
                    "source": "google_maps_api"
                })
                log_event("Orchestrator", f"Stored places data in Firestore for: {location}")
            except Exception as e:
                log_event("Orchestrator", f"Error storing places data in Firestore: {e}")
            
            return True, reply
            
        except Exception as e:
            log_event("Orchestrator", f"Error checking Firestore for places data: {e}")
            # Fallback to direct API call
            reply = get_must_visit_places_nearby(location, max_results=10)
            return True, reply
        
    elif intent == "history" or "query" in query.lower() and ("first" in query.lower() or "previous" in query.lower() or "last" in query.lower()):
        # Handle query history requests
        try:
            from tools.firestore import get_user_query_history
            # Extract user_id from entities or use a default for testing
            user_id = entities.get("user_id", "test")  # Default to "test" for now
            
            # Get query history
            history = get_user_query_history(user_id, limit=10)
            
            if not history:
                return True, "You haven't made any queries yet. This would be your first one!"
            
            # Format the response based on what was asked
            if "first" in query.lower():
                first_query = history[-1]  # Most recent is at the end
                return True, f"Your first query was: '{first_query['query']}' on {first_query['timestamp']}"
            elif "last" in query.lower():
                last_query = history[0]  # Most recent is at the beginning
                return True, f"Your last query was: '{last_query['query']}' on {last_query['timestamp']}"
            else:
                # Show recent queries
                recent_queries = history[:3]  # Show last 3 queries
                response = "Your recent queries:\n"
                for i, query_data in enumerate(recent_queries, 1):
                    response += f"{i}. '{query_data['query']}' on {query_data['timestamp']}\n"
                return True, response
                
        except Exception as e:
            log_event("Orchestrator", f"Error retrieving query history: {str(e)}")
            return True, "I'm having trouble accessing your query history right now."
        
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
    
    # Add user_id to entities for query history and other user-specific operations
    entities["user_id"] = query.user_id
    
    # 2. Dispatch to appropriate tool
    success, reply = dispatch_tool(intent, entities, query.message)
    
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
                        return
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
    unified_data = aggregate_api_results(
        reddit_data=[],
        twitter_data=[],
        news_data=[],
        maps_data=[],
        rag_data=[],
        google_search_data=[],
    )
    mood_result = aggregate_mood(unified_data)
    must_visit_places = get_must_visit_places_nearby(location, max_results=3)
    # Geocode location for lat/lng
    try:
        import googlemaps
        gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))
        geocode = gmaps.geocode(location)
        latlng = geocode[0]["geometry"]["location"] if geocode else {"lat": None, "lng": None}
    except Exception:
        latlng = {"lat": None, "lng": None}
    user_photos = []
    if latlng["lat"] is not None and latlng["lng"] is not None:
        user_photos = fetch_user_photos_nearby(latlng["lat"], latlng["lng"], radius_m=500)
    return {
        "location": location,
        "datetime": datetime_str,
        **mood_result,
        "must_visit_places": must_visit_places,
        "user_photos": user_photos
    }

if __name__ == "__main__":
    import uvicorn
    log_event("Orchestrator", "Starting FastAPI server...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
