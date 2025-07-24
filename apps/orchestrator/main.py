import os

import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from fastapi import FastAPI
from pydantic import BaseModel
from google.cloud import aiplatform
from shared.utils.logger import log_event
from fastapi import Query
from textblob import TextBlob
from typing import Optional

from agents.reddit_agent import fetch_reddit_posts
from agents.twitter_agent import fetch_twitter_posts
from agents.rag_search import get_rag_fallback
from agents.response_agent import generate_final_response
from agents.intent_extractor.agent import extract_intent
from agents.news_agent import fetch_city_news
from agents.googlemaps_agent import get_best_route, get_must_visit_places_nearby
from agents.google_search_agent import google_search
from agents.agglomerator import aggregate_api_results
from shared.utils.mood import aggregate_mood

# Initialize Google Cloud Vertex AI
aiplatform.init(project=os.getenv("GCP_PROJECT_ID"), location=os.getenv("GCP_REGION"))

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

    log_event(
        "Orchestrator", f"Intent: {intent} | Location: {location} | Topic: {topic}"
    )

    # Step 1.5: If intent is 'poi' (places of interest) and location is missing, prompt user
    if intent == "poi" and not location.strip():
        log_event("Orchestrator", "No location provided for POI intent. Prompting user.")
        return "Please specify a location (city or area) to find the best places to visit."

    # Step 2: Fetch external data sources based on intent
    maps_data = {}
    must_visit_places = []
    if intent == "poi":
        # Only call must_visit for POI intent
        must_visit_places = get_must_visit_places_nearby(location, max_results=3) if location.strip() else []
    elif intent == "route" and location.strip() and topic.strip():
        # Only call best_route if both location and topic are present for route intent
        maps_data = get_best_route(location, topic)
    # For other intents, skip both Google Maps calls unless both params are present (optional)

    if isinstance(maps_data, dict) and "error" in maps_data:
        log_event("Orchestrator", f"Google Maps error: {maps_data['error']}")
        maps_data = {}
    if must_visit_places and not isinstance(must_visit_places, list):
        log_event(
            "Orchestrator",
            f"get_must_visit_places_nearby returned non-list: {must_visit_places}",
        )
        must_visit_places = []

    try:
        news_data = fetch_city_news(location)
        rag_data = get_rag_fallback(location, topic)
        reddit_data = fetch_reddit_posts(location, topic)
        twitter_data = fetch_twitter_posts(location, topic)
    except Exception as e:
        log_event("Orchestrator", f"Error fetching external data: {e}")
        news_data = rag_data = reddit_data = twitter_data = []

    log_event("Orchestrator", "Data from tools fetched successfully.")

    # Step 3: Improved fallback to Google Search if all are empty or error
    def is_empty_or_error(data):
        if not data:
            return True
        if isinstance(data, dict) and "error" in data:
            return True
        if isinstance(data, dict) and not data:  # empty dict
            return True
        if isinstance(data, list) and not data:  # empty list
            return True
        return False

    if all(is_empty_or_error(x) for x in [reddit_data, twitter_data, rag_data, news_data]):
        google_results = google_search(message)
        rag_data = [
            f"{item['title']}: {item['snippet']} ({item['link']})"
            for item in google_results
        ]
    else:
        google_results = []

    # Step 4: Aggregate all results
    unified_data = aggregate_api_results(
        reddit_data=reddit_data,
        twitter_data=twitter_data,
        news_data=news_data,
        maps_data=maps_data,
        rag_data=rag_data,
        google_search_data=google_results,
    )
    unified_data["must_visit_places"] = must_visit_places

    # Step 5: Fuse all info via Gemini response agent
    final_response = generate_final_response(
        user_message=message,
        intent=intent,
        location=location,
        topic=topic,
        unified_data=unified_data,
    )

    return final_response


@app.post("/chat", response_model=BotResponse)
async def chat_router(query: UserQuery):
    log_event("Orchestrator", f"Received: {query.message}")
    # Use the unified orchestrator logic
    # 1. Extract intent/entities
    intent_data = extract_intent(query.message)
    intent = intent_data["intent"]
    entities = intent_data["entities"]
    location = entities.get("location", "")
    topic = entities.get("topic", "")
    # 2. If a required parameter (like origin) is missing, try to fill from history (feature removed)
    # 3. Run orchestrator
    reply = city_chatbot_orchestrator(query.message)
    # 4. Store this query and response in Firestore (feature removed)
    return BotResponse(intent=intent, entities=entities, reply=reply)


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
        reddit_data=fetch_reddit_posts(location, ""),
        twitter_data=fetch_twitter_posts(location, ""),
        news_data=fetch_city_news(location),
        maps_data=get_best_route(location, location),
        rag_data=[],
        google_search_data=google_search(location),
    )
    mood_result = aggregate_mood(unified_data)
    must_visit_places = get_must_visit_places_nearby(location, max_results=3)
    return {
        "location": location,
        "datetime": datetime_str,
        **mood_result,
        "must_visit_places": must_visit_places,
    }


if __name__ == "__main__":
    import uvicorn
    load_dotenv()
    print("GOOGLE_MAPS_API_KEY (startup):", repr(os.getenv("GOOGLE_MAPS_API_KEY")))

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
