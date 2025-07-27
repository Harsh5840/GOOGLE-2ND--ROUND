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
    return {"message": "City Project Orchestrator is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/chat")
async def chat_test():
    return {"message": "Chat endpoint working!"} 