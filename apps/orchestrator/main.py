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

from agents.reddit_agent import fetch_reddit_posts
from agents.twitter_agent import fetch_twitter_posts
from agents.firestore_agent import (
    fetch_firestore_reports, store_travel_time_record,
    store_user_query_history, fetch_similar_user_queries
)
from agents.rag_search import get_rag_fallback
from agents.response_agent import generate_final_response
from agents.intent_extractor.agent import extract_intent
from agents.news_agent import fetch_city_news
from agents.googlemaps_agent import get_best_route, get_must_visit_places_nearby
from agents.google_search_agent import google_search
from agents.agglomerator import aggregate_api_results
from shared.utils.mood import analyze_sentiment, aggregate_mood

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
    # 1. Check for similar past queries for this user
    similar = fetch_similar_user_queries(query.user_id, query.message, limit=1)
    # 2. Extract intent/entities
    intent_data = extract_intent(query.message)
    intent = intent_data["intent"]
    entities = intent_data["entities"]
    location = entities.get("location", "")
    topic = entities.get("topic", "")
    # 3. If a required parameter (like origin) is missing, try to fill from history
    if intent == "route" and not entities.get("origin") and similar:
        past_entities = similar[0]["response_data"].get("entities", {})
        if past_entities.get("origin"):
            entities["origin"] = past_entities["origin"]
    # 4. Run orchestrator
    reply = city_chatbot_orchestrator(query.message)
    # 5. Store this query and response in Firestore
    store_user_query_history(query.user_id, query.message, {
        "intent": intent,
        "entities": entities,
        "reply": reply
    })
    return BotResponse(
        intent=intent,
        entities=entities,
        reply=reply
    )

@app.post("/location_mood")
async def location_mood(
    location: str = Query(..., description="Location name or address"),
    datetime_str: Optional[str] = Query(None, description="ISO datetime string (optional)")
):
    """
    Aggregate mood for a location at a given time using the unified aggregator response.
    Returns a mood label, score, detected events, must-visit places, and source breakdown for frontend use.
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
    return {
        "location": location,
        "datetime": datetime_str,
        **mood_result,
        "must_visit_places": must_visit_places
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
