from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import FastAPI
from pydantic import BaseModel
from google.cloud import aiplatform
from shared.utils.logger import log_event
from fastapi import Query
from textblob import TextBlob
from typing import Optional

from agents.reddit_agent import fetch_reddit_posts
from agents.twitter_agent import fetch_twitter_posts
from agents.firestore_agent import fetch_firestore_reports
from agents.rag_search import get_rag_fallback
from agents.response_agent import generate_final_response
from agents.intent_extractor.agent import extract_intent
from agents.news_agent import fetch_city_news
from agents.googlemaps_agent import get_best_route
from agents.google_search_agent import google_search
from agents.agglomerator import aggregate_api_results

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

@app.post("/location_mood")
async def location_mood(
    location: str = Query(..., description="Location name or address"),
    datetime_str: Optional[str] = Query(None, description="ISO datetime string (optional)")
):
    """
    Aggregate mood for a location at a given time using Reddit, Twitter, News, Google Search, and Maps.
    Returns a mood label, score, and source breakdown for frontend use.
    """
    # 1. Fetch data from all sources
    twitter_data = fetch_twitter_posts(location, "")
    reddit_data = fetch_reddit_posts(location, "")
    news_data = fetch_city_news(location)
    google_data = google_search(location)
    maps_data = get_best_route(location, location)  # Not sentiment, but can check for traffic

    # 2. Sentiment analysis helper
    def analyze_sentiment(texts):
        if not texts:
            return 0.0, []
        scores = []
        keywords = []
        for t in texts:
            if not t:
                continue
            if isinstance(t, dict):
                content = t.get("text") or t.get("title") or t.get("description") or ""
            else:
                content = str(t)
            if content:
                blob = TextBlob(content)
                scores.append(blob.sentiment.polarity)
                keywords.extend(blob.noun_phrases)
        avg_score = sum(scores) / len(scores) if scores else 0.0
        top_keywords = list(set(keywords))[:5]
        return avg_score, top_keywords

    # 3. Analyze each source
    twitter_score, twitter_keywords = analyze_sentiment(
        twitter_data.get("tweets", []) if isinstance(twitter_data, dict) else []
    )
    reddit_score, reddit_keywords = analyze_sentiment(
        reddit_data.get("posts", []) if isinstance(reddit_data, dict) else []
    )
    news_score, news_keywords = analyze_sentiment(
        news_data.get("articles", []) if isinstance(news_data, dict) else []
    )
    google_score, google_keywords = analyze_sentiment(google_data)
    # For maps, use traffic info as a negative/neutral signal
    maps_score = -0.5 if maps_data and isinstance(maps_data, dict) and "duration_in_traffic" in maps_data and maps_data["duration_in_traffic"] != maps_data.get("duration") else 0.0
    maps_keywords = ["traffic"] if maps_score < 0 else []

    # 4. Aggregate mood
    source_scores = [twitter_score, reddit_score, news_score, google_score, maps_score]
    mood_score = sum(source_scores) / len(source_scores)
    if mood_score > 0.3:
        mood_label = "happy"
    elif mood_score < -0.3:
        mood_label = "tense"
    elif maps_score < 0:
        mood_label = "busy"
    else:
        mood_label = "neutral"

    return {
        "location": location,
        "datetime": datetime_str,
        "mood_label": mood_label,
        "mood_score": round(mood_score, 2),
        "source_breakdown": {
            "twitter": {"score": round(twitter_score, 2), "top_keywords": twitter_keywords},
            "reddit": {"score": round(reddit_score, 2), "top_keywords": reddit_keywords},
            "news": {"score": round(news_score, 2), "top_keywords": news_keywords},
            "google_search": {"score": round(google_score, 2), "top_keywords": google_keywords},
            "maps": {"score": round(maps_score, 2), "top_keywords": maps_keywords},
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
