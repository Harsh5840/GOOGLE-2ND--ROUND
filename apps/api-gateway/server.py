# apps/api-gateway/server.py

from fastapi import FastAPI, Request
from pydantic import BaseModel
import httpx
import os
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response

ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:8000")
NEWS_API_URL = os.getenv("NEWS_API_URL", "http://localhost:5001")

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

@app.post("/api/v1/podcast/generate")
async def proxy_podcast_generate(request: Request):
    data = await request.json()
    async with httpx.AsyncClient(timeout=HTTPX_TIMEOUT) as client:
        response = await client.post(f"{NEWS_API_URL}/api/v1/podcast/generate", json=data)
    return response.json()

@app.get("/api/v1/jobs/{job_id}")
async def proxy_podcast_job(job_id: str):
    async with httpx.AsyncClient(timeout=HTTPX_TIMEOUT) as client:
        response = await client.get(f"{NEWS_API_URL}/api/v1/jobs/{job_id}")
    return response.json()

@app.get("/api/v1/files/{filename}")
async def proxy_podcast_file(filename: str):
    async with httpx.AsyncClient(timeout=HTTPX_TIMEOUT) as client:
        response = await client.get(f"{NEWS_API_URL}/api/v1/files/{filename}")
        content = response.content
        return Response(content, media_type="audio/mpeg")

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=5000, reload=True)
