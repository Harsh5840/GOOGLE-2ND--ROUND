# apps/api-gateway/server.py

from fastapi import FastAPI, Request
from pydantic import BaseModel
import httpx
import os
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response

ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "https://city-orchestrator-ixlmqkeuva-uc.a.run.app/")
NEWS_API_URL = os.getenv("NEWS_API_URL", "http://localhost:5001")

HTTPX_TIMEOUT = 30.0  # seconds

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "City Project API Gateway is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "orchestrator_url": ORCHESTRATOR_URL}

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

# Gemini Photo Classification Routes
@app.post("/api/v1/classify_photo")
async def proxy_classify_photo(request: Request):
    """Proxy photo classification requests to orchestrator"""
    form_data = await request.form()
    
    # Forward the multipart form data to orchestrator
    files = {}
    data = {}
    
    for key, value in form_data.items():
        if hasattr(value, 'read'):  # It's a file
            files[key] = (value.filename, await value.read(), value.content_type)
        else:  # It's regular form data
            data[key] = value
    
    async with httpx.AsyncClient(timeout=HTTPX_TIMEOUT) as client:
        response = await client.post(f"{ORCHESTRATOR_URL}/classify_photo", files=files, data=data)
    return response.json()

@app.post("/api/v1/submit_classified_report")
async def proxy_submit_classified_report(request: Request):
    """Proxy classified report submission to orchestrator"""
    form_data = await request.form()
    
    # Forward the multipart form data to orchestrator
    files = {}
    data = {}
    
    for key, value in form_data.items():
        if hasattr(value, 'read'):  # It's a file
            files[key] = (value.filename, await value.read(), value.content_type)
        else:  # It's regular form data
            data[key] = value
    
    async with httpx.AsyncClient(timeout=HTTPX_TIMEOUT) as client:
        response = await client.post(f"{ORCHESTRATOR_URL}/submit_classified_report", files=files, data=data)
    return response.json()

@app.get("/api/v1/user_reports")
async def proxy_user_reports(request: Request):
    """Proxy user reports requests to orchestrator"""
    params = dict(request.query_params)
    async with httpx.AsyncClient(timeout=HTTPX_TIMEOUT) as client:
        response = await client.get(f"{ORCHESTRATOR_URL}/user_reports", params=params)
    return response.json()

@app.get("/api/v1/report-image/{report_id}")
async def proxy_report_image(report_id: str):
    """Proxy report image requests to orchestrator"""
    async with httpx.AsyncClient(timeout=HTTPX_TIMEOUT) as client:
        response = await client.get(f"{ORCHESTRATOR_URL}/report-image/{report_id}")
        content = response.content
        return Response(content, media_type="image/jpeg")

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=5000, reload=True)
