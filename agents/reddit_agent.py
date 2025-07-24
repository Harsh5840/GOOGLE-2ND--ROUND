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
from tools.reddit import fetch_reddit_posts

def create_reddit_agent():
    return Agent(
        model="gemini-2.0-flash-001",
        name="reddit_agent",
        instruction="You are a Reddit Agent. Use the fetch_reddit_posts tool to answer questions about top posts in a subreddit.",
        tools=[FunctionTool(fetch_reddit_posts)]
    )

async def run_reddit_agent(subreddit: str, limit: int = 5, user_id: str = "testuser", session_id: str = None) -> str:
    agent = create_reddit_agent()
    runner = Runner(agent=agent, app_name=COMMON_APP_NAME, session_service=session_service)
    if not session_id:
        session_id = str(uuid.uuid4())
    await session_service.create_session(session_id=session_id, user_id=user_id, app_name=COMMON_APP_NAME)
    content = types.Content(role="user", parts=[types.Part(text=f"Get top posts in r/{subreddit} (limit {limit})")])
    result = ""
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if hasattr(event, 'text') and event.text:
            result += event.text
    return result 