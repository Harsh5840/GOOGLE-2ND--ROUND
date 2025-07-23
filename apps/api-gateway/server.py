# apps/api-gateway/server.py

from fastapi import FastAPI, Request
from pydantic import BaseModel
import httpx
import os
import uvicorn

ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:8000")

app = FastAPI()

class ChatInput(BaseModel):
    user_id: str
    message: str

class ChatOutput(BaseModel):
    intent: str
    entities: dict
    reply: str

@app.post("/api/v1/chat", response_model=ChatOutput)
async def gateway_route(data: ChatInput):
    async with httpx.AsyncClient() as client:
        response = await client.post(ORCHESTRATOR_URL, json=data.dict())
    return response.json()

@app.post("/api/v1/location_mood")
async def proxy_location_mood(request: Request):
    params = dict(request.query_params)
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{ORCHESTRATOR_URL}/location_mood", params=params)
    return response.json()

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=3000, reload=True)
