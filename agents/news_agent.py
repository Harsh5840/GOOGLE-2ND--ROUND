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
from tools.news import fetch_city_news

def create_news_agent():
    return Agent(
        model="gemini-2.0-flash-001",
        name="news_agent",
        instruction="You are a News Agent. Use the fetch_city_news tool to answer questions about recent news for a city.",
        tools=[FunctionTool(fetch_city_news)]
    )

async def run_news_agent(city: str, limit: int = 5, user_id: str = "testuser", session_id: str = None) -> str:
    agent = create_news_agent()
    runner = Runner(agent=agent, app_name=COMMON_APP_NAME, session_service=session_service)
    if not session_id:
        session_id = str(uuid.uuid4())
    await session_service.create_session(session_id=session_id, user_id=user_id, app_name=COMMON_APP_NAME)
    content = types.Content(role="user", parts=[types.Part(text=f"Get recent news for {city} (limit {limit})")])
    result = ""
    function_result = None
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if hasattr(event, 'text') and event.text:
            result += event.text
        if hasattr(event, 'parts') and event.parts:
            for part in event.parts:
                if hasattr(part, 'text') and part.text:
                    result += part.text
                if hasattr(part, 'function_response') and part.function_response:
                    function_result = part.function_response.response.get('result')
    if not result.strip() and function_result:
        return function_result
    return result.strip() 