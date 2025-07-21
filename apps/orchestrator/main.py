# apps/orchestrator/main.py

from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn
import os
from google.cloud import aiplatform
from agents.intent_extractor.agent import extract_intent

# Initialize Vertex AI (make sure GOOGLE_APPLICATION_CREDENTIALS is set)
aiplatform.init(project=os.getenv("GCP_PROJECT_ID"), location=os.getenv("GCP_REGION"))

app = FastAPI()

# Input/Output schema
class UserQuery(BaseModel):
    user_id: str
    message: str

class BotResponse(BaseModel):
    intent: str
    entities: dict
    reply: str

@app.post("/chat", response_model=BotResponse)
async def chat_router(query: UserQuery):
    print(f"[Orchestrator] Received: {query.message}")

    # Step 1: Extract intent and entities
    intent_data = extract_intent(query.message)

    # Step 2: Placeholder for context/tool/RAG/response agents
    final_reply = f"Intent: {intent_data['intent']} with location: {intent_data['entities'].get('location', 'unknown')}"

    return BotResponse(
        intent=intent_data["intent"],
        entities=intent_data["entities"],
        reply=final_reply
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
