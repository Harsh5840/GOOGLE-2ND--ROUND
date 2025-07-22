from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import FastAPI
from pydantic import BaseModel
from google.cloud import aiplatform
from shared.utils.logger import log_event
from fastapi import Query
from textblob import TextBlob
from typing import Optional, Dict, Any, Tuple, List
from fastapi import UploadFile, File, Form
from google.cloud import storage
from uuid import uuid4
from agents.firestore_agent import db
from datetime import datetime

from agents.reddit_agent import fetch_reddit_posts
from agents.twitter_agent import fetch_twitter_posts
from agents.firestore_agent import fetch_firestore_reports
from agents.rag_search import get_rag_fallback
from agents.response_agent import generate_final_response
from agents.intent_extractor.agent import extract_intent
from agents.news_agent import fetch_city_news
from agents.googlemaps_agent import get_best_route, get_must_visit_places_nearby
from agents.google_search_agent import google_search
from agents.agglomerator import aggregate_api_results
from shared.utils.mood import analyze_sentiment, aggregate_mood
from shared.utils.user_photos import save_user_photo, fetch_user_photos_nearby

# Initialize Google Cloud Vertex AI
aiplatform.init(
    project=os.getenv("GCP_PROJECT_ID"),
    location=os.getenv("GCP_REGION")
)

# FastAPI app setup
app = FastAPI()

# Request schema
class UserQuery(BaseModel):
    user_id: str
    message: str

# Response schema
class BotResponse(BaseModel):
    intent: str
    entities: dict
    reply: str

def city_chatbot_orchestrator(message: str) -> str:
    log_event("Orchestrator", "Running city_chatbot_orchestrator...")

    # Step 1: Extract intent and entities
    parsed = extract_intent(message)
    intent = parsed["intent"]
    entities = parsed["entities"]
    location = entities.get("location", "")
    topic = entities.get("topic", "")

    log_event("Orchestrator", f"Intent: {intent} | Location: {location} | Topic: {topic}")

    # Step 2: Fetch external data sources
    reddit_data = fetch_reddit_posts(location, topic)
    twitter_data = fetch_twitter_posts(location, topic)
    firestore_data = fetch_firestore_reports(location, topic)
    rag_data = get_rag_fallback(location, topic)
    news_data = fetch_city_news(location)
    maps_data = get_best_route(location, topic)  # If topic is a destination, else adjust as needed

    log_event("Orchestrator", "Data from tools fetched successfully.")

    # Step 3: Fallback to Google Search if all are empty
    google_results = []
    if not (reddit_data or twitter_data or firestore_data or rag_data or news_data):
        google_results = google_search(message)
        rag_data = [f"{item['title']}: {item['snippet']} ({item['link']})" for item in google_results]

    # Step 4: Aggregate all results
    unified_data = aggregate_api_results(
        reddit_data=reddit_data,
        twitter_data=twitter_data,
        news_data=news_data,
        maps_data=maps_data,
        firestore_data=firestore_data,
        rag_data=rag_data,
        google_search_data=google_results
    )

    # Step 5: Fuse all info via Gemini response agent
    final_response = generate_final_response(
        user_message=message,
        intent=intent,
        location=location,
        topic=topic,
        unified_data=unified_data
    )

    return final_response

@app.post("/chat", response_model=BotResponse)
async def chat_router(query: UserQuery):
    log_event("Orchestrator", f"Received: {query.message}")
    # Use the unified orchestrator logic
    reply = city_chatbot_orchestrator(query.message)
    # Extract intent/entities again for response (could be optimized)
    intent_data = extract_intent(query.message)
    intent = intent_data["intent"]
    entities = intent_data["entities"]
    return BotResponse(
        intent=intent,
        entities=entities,
        reply=reply
    )

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
    datetime_str: Optional[str] = Query(None, description="ISO datetime string (optional)")
):
    """
    Aggregate mood for a location at a given time using the unified aggregator response.
    Returns a mood label, score, detected events, must-visit places, user photos, and source breakdown for frontend use.
    """
    unified_data = aggregate_api_results(
        reddit_data=fetch_reddit_posts(location, ""),
        twitter_data=fetch_twitter_posts(location, ""),
        news_data=fetch_city_news(location),
        maps_data=get_best_route(location, location),
        firestore_data=[],
        rag_data=[],
        google_search_data=google_search(location)
    )
    mood_result = aggregate_mood(unified_data)
    must_visit_places = get_must_visit_places_nearby(location, max_results=3)
    # Geocode location for lat/lng
    try:
        gmaps = get_best_route.__globals__["googlemaps"].Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))
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
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
