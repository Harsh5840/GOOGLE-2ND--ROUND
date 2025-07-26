import os
from dotenv import load_dotenv
load_dotenv()

import vertexai
vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION")
)

from fastapi import FastAPI, Query
from pydantic import BaseModel
from google.cloud import aiplatform
from shared.utils.logger import log_event
from typing import Optional

from agents.agent_router import agent_router
from tools.reddit import fetch_reddit_posts
from tools.twitter import fetch_twitter_posts
from tools.news import fetch_city_news
from agents.gemini_fallback_agent import run_gemini_fallback_agent
from shared.utils.mood import aggregate_mood
from agents.intent_extractor.agent import extract_intent
from agents.agglomerator import aggregate_api_results
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
