import os
from dotenv import load_dotenv
load_dotenv()
import vertexai
vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION")
)
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.genai import types
import uuid
from agents.session_service import session_service, COMMON_APP_NAME
from tools.rag import get_rag_fallback

def create_rag_agent():
    return Agent(
        model="gemini-2.0-flash-001",
        name="rag_agent",
        instruction="You are a RAG Agent. Use the get_rag_fallback tool to answer questions using background city knowledge.",
        tools=[FunctionTool(get_rag_fallback)]
    )

async def run_rag_agent(location: str, topic: str, user_id: str = "testuser", session_id: str = None) -> str:
    agent = create_rag_agent()
    runner = Runner(agent=agent, app_name=COMMON_APP_NAME, session_service=session_service)
    if not session_id:
        session_id = str(uuid.uuid4())
    await session_service.create_session(session_id=session_id, user_id=user_id, app_name=COMMON_APP_NAME)
    content = types.Content(role="user", parts=[types.Part(text=f"Get RAG fallback for {location} on {topic}")])
    result = ""
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if hasattr(event, 'text') and event.text:
            result += event.text
    return result 