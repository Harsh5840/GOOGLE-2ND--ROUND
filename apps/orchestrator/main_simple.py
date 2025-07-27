from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class UserQuery(BaseModel):
    user_id: str
    message: str

class BotResponse(BaseModel):
    intent: str
    entities: dict
    reply: str
    location_data: Optional[dict] = None

@app.get("/")
def read_root():
    return {"message": "City Project Orchestrator is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/chat")
async def chat_endpoint(query: UserQuery):
    """Basic chat endpoint that works with the frontend"""
    try:
        # Simple response for now - can be enhanced later
        return BotResponse(
            intent="general",
            entities={},
            reply=f"I received your message: '{query.message}'. Backend services are being deployed. This is a temporary response.",
            location_data=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/location_mood")
async def location_mood_endpoint(location: str = "New York City"):
    """Temporary mood endpoint"""
    return {
        "location": location,
        "mood": "neutral",
        "sentiment_score": 0.0,
        "timestamp": "2024-01-01T00:00:00Z"
    } 