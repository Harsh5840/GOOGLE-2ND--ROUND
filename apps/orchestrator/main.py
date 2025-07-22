from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import FastAPI
from pydantic import BaseModel
from google.cloud import aiplatform
from shared.utils.logger import log_event

from agents.reddit_agent import fetch_reddit_posts
from agents.twitter_agent import fetch_twitter_posts
from agents.firestore_agent import fetch_firestore_reports, store_travel_time_record
from agents.rag_search import get_rag_fallback
from agents.response_agent import generate_final_response
from agents.intent_extractor.agent import extract_intent
from agents.news_agent import fetch_city_news
from agents.googlemaps_agent import get_best_route
from agents.google_search_agent import google_search
from agents.agglomerator import aggregate_api_results

from datetime import datetime

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

class TravelDataRequest(BaseModel):
    route: str
    datetime: str  # ISO format
    weather: str = ""
    # Optionally, allow user to specify origin/destination, but route string is enough for now

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

@app.post("/collect_travel_data")
async def collect_travel_data(request: TravelDataRequest):
    """
    Collect and store travel time and event data for a given route and datetime.
    Gathers Google Maps travel time, Twitter, Reddit, News, and Google Search events.
    """
    # Parse datetime
    try:
        dt = datetime.fromisoformat(request.datetime)
    except Exception as e:
        return {"success": False, "error": f"Invalid datetime format: {e}"}

    # Fetch travel time from Google Maps
    # For demo, use get_best_route with route as both origin and destination (should be split in real use)
    maps_data = get_best_route(request.route, request.route)
    travel_time_minutes = None
    if isinstance(maps_data, dict) and "duration" in maps_data:
        # Try to extract minutes from string like '45 mins'
        try:
            travel_time_minutes = int(maps_data["duration"].split()[0])
        except Exception:
            travel_time_minutes = None

    # Fetch event data
    twitter_events = fetch_twitter_posts(request.route, "traffic")
    reddit_events = fetch_reddit_posts(request.route, "traffic")
    news_events = fetch_city_news(request.route)
    google_search_events = google_search(f"traffic {request.route}")

    # Store in Firestore
    success = store_travel_time_record(
        route=request.route,
        datetime_str=request.datetime,
        travel_time_minutes=travel_time_minutes or -1,
        twitter_events=twitter_events.get("tweets") if isinstance(twitter_events, dict) else [],
        reddit_events=reddit_events.get("posts") if isinstance(reddit_events, dict) else [],
        news_events=news_events.get("articles") if isinstance(news_events, dict) else [],
        google_search_events=google_search_events,
        weather=request.weather
    )
    return {"success": success}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
