# apps/api-gateway/server.py

from fastapi import FastAPI, Request
from pydantic import BaseModel
import httpx
import os
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:8000")

HTTPX_TIMEOUT = 30.0  # seconds

app = FastAPI()

# Enable CORS for all origins and all routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or restrict: ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatInput(BaseModel):
    user_id: str
    message: str

class ChatOutput(BaseModel):
    intent: str
    entities: dict
    reply: str

@app.post("/api/v1/chat", response_model=ChatOutput)
async def gateway_route(data: ChatInput):
    async with httpx.AsyncClient(timeout=HTTPX_TIMEOUT) as client:
        response = await client.post(f"{ORCHESTRATOR_URL}/chat", json=data.model_dump())
    return response.json()

@app.post("/api/v1/location_mood")
async def proxy_location_mood(request: Request):
    params = dict(request.query_params)
    async with httpx.AsyncClient(timeout=HTTPX_TIMEOUT) as client:
        response = await client.post(f"{ORCHESTRATOR_URL}/location_mood", params=params)
    return response.json()

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=5000, reload=True)
