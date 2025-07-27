from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

app = FastAPI(title="City Project Orchestrator", version="1.0.0")

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

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "City Project Orchestrator is running!",
        "status": "healthy",
        "version": "minimal"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Chat endpoint
@app.post("/chat", response_model=BotResponse)
async def chat_router(query: UserQuery):
    try:
        # Simple response for now
        return BotResponse(
            intent="general",
            entities={},
            reply=f"I received your message: '{query.message}'. I'm here to help with city-related questions!",
            location_data=None
        )
    except Exception as e:
        print(f"Chat processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Location mood endpoint
@app.post("/location_mood")
async def location_mood(location: str = "New York City"):
    try:
        return {
            "location": location,
            "mood": "neutral",
            "sentiment_score": 0.0,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Location mood error: {e}")
        return {
            "location": location,
            "mood": "neutral",
            "sentiment_score": 0.0,
            "timestamp": datetime.now().isoformat()
        }

# Display locations endpoint
@app.post("/display_locations")
async def display_locations_endpoint(locations: list):
    try:
        return {
            "locations": locations,
            "status": "success",
            "message": f"Displaying {len(locations)} locations"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Best route endpoint
@app.post("/best_route")
async def best_route_endpoint(origin: str, destination: str, mode: str = "driving"):
    try:
        return {
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "route_info": f"Route from {origin} to {destination} via {mode}",
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Must visit places endpoint
@app.post("/must_visit_places")
async def must_visit_places_endpoint(location: str, max_results: int = 3):
    try:
        places = [
            {"name": f"Place 1 in {location}", "rating": 4.5},
            {"name": f"Place 2 in {location}", "rating": 4.2},
            {"name": f"Place 3 in {location}", "rating": 4.0}
        ]
        
        return {
            "location": location,
            "max_results": max_results,
            "places": places[:max_results],
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 