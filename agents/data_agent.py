from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import uuid
from tools.firestore import fetch_firestore_reports, store_user_query_history, fetch_similar_user_queries
from tools.rag import get_rag_fallback

# Shared session service instance for all data agent runs
session_service = InMemorySessionService()

def create_data_agent():
    tools = [
        FunctionTool(fetch_firestore_reports),
        FunctionTool(store_user_query_history),
        FunctionTool(fetch_similar_user_queries),
        FunctionTool(get_rag_fallback),
    ]
    return Agent(
        model="gemini-2.0-flash-001",
        name="data_agent",
        instruction="You are the Data Agent. Retrieve and analyze internal city data (Firestore, RAG, user history).",
        tools=tools
    )

# Async ADK-based run function
async def run_data_agent(query: str, context: dict = None) -> dict:
    agent = create_data_agent()
    runner = Runner(agent=agent, app_name="data_agent", session_service=session_service)
    user_id = context.get("user_id", "testuser") if context else "testuser"
    session_id = context.get("session_id", str(uuid.uuid4())) if context else str(uuid.uuid4())
    content = types.Content(role="user", parts=[types.Part(text=query)])
    response_text = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content
    ):
        if hasattr(event, "text") and event.text:
            response_text += event.text
    return {"data_agent_response": response_text} 