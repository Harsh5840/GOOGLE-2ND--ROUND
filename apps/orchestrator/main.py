import os
from dotenv import load_dotenv
load_dotenv()

import vertexai
vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION")
)

import sys
from fastapi import FastAPI
from pydantic import BaseModel
from google.cloud import aiplatform
from shared.utils.logger import log_event
from fastapi import Query
from textblob import TextBlob
from typing import Optional

from agents.city_adk_agent import run_city_agent
from agents.response_agent import generate_final_response
from agents.intent_extractor.agent import extract_intent
from agents.agglomerator import aggregate_api_results
from shared.utils.mood import aggregate_mood
from agents.agent_router import agent_router
from agents.places_agent import run_places_agent

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
    # Use the new Google ADK agent for all queries
    return run_city_agent(message)


@app.post("/chat", response_model=BotResponse)
async def chat_router(query: UserQuery):
    log_event("Orchestrator", f"Received: {query.message}")
    # 1. Extract intent/entities
    intent_data = extract_intent(query.message)
    intent = intent_data["intent"]
    entities = intent_data["entities"]
    location = entities.get("location", "")
    topic = entities.get("topic", "")
    # 2. Decide tool and args based on intent/entities (simple mapping, can be improved)
    tool_name = None
    args = {}
    if intent == "get_twitter_posts" and location and topic:
        tool_name = "fetch_twitter_posts"
        args = {"location": location, "topic": topic, "limit": 5}
    elif intent == "get_reddit_posts" and "subreddit" in entities:
        tool_name = "fetch_reddit_posts"
        args = {"subreddit": entities["subreddit"], "limit": 5}
    elif intent == "get_best_route" and "current_location" in entities and "destination" in entities:
        tool_name = "get_best_route"
        args = {"current_location": entities["current_location"], "destination": entities["destination"], "mode": entities.get("mode", "driving")}
    elif intent in ["get_must_visit_places", "poi"] and location:
        # --- DIRECTLY CALL run_places_agent for must-visit places ---
        log_event("Orchestrator", f"Calling run_places_agent for location={location}, max_results=3")
        reply = await run_places_agent(location, max_results=3, user_id=query.user_id)
        log_event("Orchestrator", f"run_places_agent reply: {reply!r}")
        return BotResponse(intent=intent, entities=entities, reply=reply)
    elif intent == "get_city_news" and location:
        tool_name = "fetch_city_news"
        args = {"city": location, "limit": 5}
    elif intent == "get_firestore_reports" and location and topic:
        tool_name = "fetch_firestore_reports"
        args = {"location": location, "topic": topic, "limit": 5}
    elif intent == "get_similar_queries" and "user_id" in entities and "query" in entities:
        tool_name = "fetch_similar_user_queries"
        args = {"user_id": entities["user_id"], "query": entities["query"], "limit": 5}
    elif intent == "google_search" and "query" in entities:
        tool_name = "google_search"
        args = {"query": entities["query"], "num_results": 5}
    else:
        # Fallback: use Gemini LLM
        tool_name = None
        args = {"query": query.message}
    log_event("Orchestrator", f"Intent: {intent}, Entities: {entities}, Tool: {tool_name}, Args: {args}")
    # 3. Call agent_router
    reply = await agent_router(tool_name, args, fallback="gemini")
    log_event("Orchestrator", f"Agent reply: {reply!r}")
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
