from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.genai import types
import uuid
from agents.session_service import session_service, COMMON_APP_NAME
from tools.google_search import google_search

def create_google_search_agent():
    return Agent(
        model="gemini-2.0-flash-001",
        name="google_search_agent",
        instruction="You are a Google Search Agent. Use the google_search tool to answer questions using Google Custom Search.",
        tools=[FunctionTool(google_search)]
    )

async def run_google_search_agent(query: str, num_results: int = 5, user_id: str = "testuser", session_id: str = None) -> str:
    agent = create_google_search_agent()
    runner = Runner(agent=agent, app_name=COMMON_APP_NAME, session_service=session_service)
    if not session_id:
        session_id = str(uuid.uuid4())
    await session_service.create_session(session_id=session_id, user_id=user_id, app_name=COMMON_APP_NAME)
    content = types.Content(role="user", parts=[types.Part(text=f"Google search for: {query} (num_results {num_results})")])
    result = ""
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if hasattr(event, 'text') and event.text:
            result += event.text
    return result 