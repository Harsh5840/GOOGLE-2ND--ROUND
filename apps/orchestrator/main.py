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

from agents.agent_router import agent_router
from tools.reddit import fetch_reddit_posts
from tools.twitter import fetch_twitter_posts
from agents.gemini_fallback_agent import run_gemini_fallback_agent
from shared.utils.mood import aggregate_mood
from agents.intent_extractor.agent import extract_intent
from agents.agglomerator import aggregate_api_results
from shared.utils.mood import aggregate_mood
from tools.maps import get_must_visit_places_nearby

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

@app.post("/chat", response_model=BotResponse)
async def chat_router(query: UserQuery):
    log_event("Orchestrator", f"Received: {query.message}")
    # 1. Extract intent/entities
    intent_data = extract_intent(query.message)
    intent = intent_data["intent"]
    entities = intent_data["entities"]
    location = entities.get("location", "")
    topic = entities.get("topic", "")
    # 2. Direct tool calls for each intent
    if intent == "get_twitter_posts" and location and topic:
        log_event("Orchestrator", f"Calling fetch_twitter_posts directly with location: {location!r}, topic: {topic!r}")
        reply = fetch_twitter_posts(location=location, topic=topic, limit=5)
        log_event("Orchestrator", f"fetch_twitter_posts reply: {reply!r}")
        if not reply.strip():
            log_event("Orchestrator", "No reply from Twitter tool, falling back to Gemini LLM.")
            reply = await run_gemini_fallback_agent(query.message, user_id=query.user_id)
        return BotResponse(intent=intent, entities=entities, reply=reply)
    elif intent == "get_reddit_posts" and "subreddit" in entities:
        log_event("Orchestrator", f"Calling fetch_reddit_posts directly with subreddit: {entities.get('subreddit')!r}, topic: {entities.get('topic')!r}")
        reply = await fetch_reddit_posts(subreddit=entities["subreddit"], limit=5)
        log_event("Orchestrator", f"fetch_reddit_posts reply: {reply!r}")
        if not reply.strip():
            log_event("Orchestrator", "No reply from Reddit tool, falling back to Gemini LLM.")
            reply = await run_gemini_fallback_agent(query.message, user_id=query.user_id)
        return BotResponse(intent=intent, entities=entities, reply=reply)
    elif intent == "social_media" and entities.get("source", "").lower() == "reddit" and "topic" in entities:
        log_event("Orchestrator", f"Calling fetch_reddit_posts (social_media intent) with subreddit: {entities.get('topic')!r}")
        reply = await fetch_reddit_posts(subreddit=entities["topic"].replace(' ', ''), limit=5)
        log_event("Orchestrator", f"fetch_reddit_posts (social_media intent) reply: {reply!r}")
        if not reply.strip():
            log_event("Orchestrator", "No reply from Reddit tool (social_media intent), falling back to Gemini LLM.")
            reply = await run_gemini_fallback_agent(query.message, user_id=query.user_id)
        return BotResponse(intent=intent, entities=entities, reply=reply)
    # --- FLEXIBLE ROUTING: News queries ---
    elif intent == "get_city_news" and ("city" in entities or location):
        city = entities.get("city", location)
        # ... (rest of your news logic) ...
        reply = "[News tool call here]"
        return BotResponse(intent=intent, entities=entities, reply=reply)
    # --- FLEXIBLE ROUTING: Firestore Reports queries ---
    elif intent == "get_firestore_reports" and location and topic:
        # ... (rest of your firestore reports logic) ...
        reply = "[Firestore reports tool call here]"
        return BotResponse(intent=intent, entities=entities, reply=reply)
    # --- FLEXIBLE ROUTING: Firestore Similar queries ---
    elif intent == "get_similar_queries" and "user_id" in entities and "query" in entities:
        # ... (rest of your firestore similar logic) ...
        reply = "[Firestore similar tool call here]"
        return BotResponse(intent=intent, entities=entities, reply=reply)
    # --- FLEXIBLE ROUTING: Google Search queries ---
    elif intent == "google_search" and "query" in entities:
        # ... (rest of your google search logic) ...
        reply = "[Google search tool call here]"
        return BotResponse(intent=intent, entities=entities, reply=reply)
    # --- FLEXIBLE ROUTING: Maps/Route queries ---
    elif intent == "get_best_route" and "current_location" in entities and "destination" in entities:
        # ... (rest of your maps/route logic) ...
        reply = "[Maps tool call here]"
        return BotResponse(intent=intent, entities=entities, reply=reply)
    elif intent in ["get_must_visit_places", "poi"] and location:
        reply = get_must_visit_places_nearby(location, max_results=10)
        if not reply.strip():
            log_event("Orchestrator", "No reply from Places tool, falling back to Gemini LLM.")
            reply = await run_gemini_fallback_agent(query.message, user_id=query.user_id)
        return BotResponse(intent=intent, entities=entities, reply=reply)
    # Fallback: use Gemini LLM or router
    tool_name = None
    args = {"query": query.message}
    log_event("Orchestrator", f"Intent: {intent}, Entities: {entities}, Tool: {tool_name}, Args: {args}")
    reply = await agent_router(tool_name, args, fallback="gemini")
    log_event("Orchestrator", f"Agent reply: {reply!r}")

    # GENERAL GEMINI FALLBACK
    if not reply.strip():
        log_event("Orchestrator", "No reply from any tool or agent, falling back to Gemini LLM.")
        reply = await run_gemini_fallback_agent(query.message, user_id=query.user_id)

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
