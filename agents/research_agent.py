from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import uuid
from tools.twitter import fetch_twitter_posts
from tools.reddit import fetch_reddit_posts
from tools.news import fetch_city_news
from tools.google_search import google_search

# Shared session service instance for all research agent runs
session_service = InMemorySessionService()

def create_research_agent():
    tools = [
        FunctionTool(fetch_twitter_posts),
        FunctionTool(fetch_reddit_posts),
        FunctionTool(fetch_city_news),
        FunctionTool(google_search),
    ]
    return Agent(
        model="gemini-2.0-flash-001",
        name="research_agent",
        instruction="You are the Research Agent. Collect external data and artifacts for city investigations.",
        tools=tools
    )

# Dynamic ADK-based run function
def run_research_agent(query: str, context: dict = None) -> dict:
    agent = create_research_agent()
    runner = Runner(agent=agent, app_name="research_agent", session_service=session_service)
    user_id = context.get("user_id", "testuser") if context else "testuser"
    session_id = context.get("session_id", str(uuid.uuid4())) if context else str(uuid.uuid4())
    content = types.Content(role="user", parts=[types.Part(text=query)])
    events = runner.run(
        user_id=user_id,
        session_id=session_id,
        new_message=content
    )
    response_text = ""
    for event in events:
        if hasattr(event, "text") and event.text:
            response_text += event.text
    return {"research_agent_response": response_text} 