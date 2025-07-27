from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "City Project API Gateway is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/v1/test")
def test_endpoint():
    return {"message": "API Gateway endpoint working!"} 