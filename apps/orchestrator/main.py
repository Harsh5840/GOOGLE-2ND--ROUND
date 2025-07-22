
from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import FastAPI
from pydantic import BaseModel
from google.cloud import aiplatform

from agents.intent_extractor.agent import extract_intent
from agents.reddit_agent import fetch_reddit_posts
from agents.twitter_agent import fetch_twitter_posts
from agents.firestore_agent import fetch_firestore_reports
from agents.rag_search import get_rag_fallback
from agents.response_agent import generate_final_response

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

@app.post("/chat", response_model=BotResponse)
async def chat_router(query: UserQuery):
    print(f"[Orchestrator] Received: {query.message}")

    # Step 1: Extract intent and entities
    intent_data = extract_intent(query.message)
    intent = intent_data["intent"]
    entities = intent_data["entities"]
    location = entities.get("location", os.getenv("DEFAULT_LOCATION", "Bengaluru"))
    topic = entities.get("topic", intent)

    # Step 2: Aggregate from agents
    reddit_data = fetch_reddit_posts(location, topic)
    twitter_data = fetch_twitter_posts(location, topic)
    firestore_data = fetch_firestore_reports(location, topic)
    rag_data = get_rag_fallback(location, topic)

    # Step 3: Generate fused AI response
    reply = generate_final_response(
        user_message=query.message,
        intent=intent,
        location=location,
        topic=topic,
        reddit_posts=reddit_data,
        twitter_posts=twitter_data,
        firestore_reports=firestore_data,
        rag_docs=rag_data
    )

    return BotResponse(
        intent=intent,
        entities=entities,
        reply=reply
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
