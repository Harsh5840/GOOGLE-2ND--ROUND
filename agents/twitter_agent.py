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
from tools.twitter import fetch_twitter_posts

def create_twitter_agent():
    return Agent(
        model="gemini-2.0-flash-001",
        name="twitter_agent",
        instruction="You are a Twitter Agent. Use the fetch_twitter_posts tool to answer questions about recent tweets for a location and topic.",
        tools=[FunctionTool(fetch_twitter_posts)]
    )

async def run_twitter_agent(location: str, topic: str, limit: int = 10, user_id: str = "testuser", session_id: str = None) -> str:
    agent = create_twitter_agent()
    runner = Runner(agent=agent, app_name=COMMON_APP_NAME, session_service=session_service)
    if not session_id:
        session_id = str(uuid.uuid4())
    await session_service.create_session(session_id=session_id, user_id=user_id, app_name=COMMON_APP_NAME)
    content = types.Content(role="user", parts=[types.Part(text=f"Get recent tweets for {location} about {topic} (limit {limit})")])
    result_parts = []
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if getattr(event, "text", None):
            s = str(event.text).strip()
            if s and s.lower() != 'none':
                result_parts.append(s)
        if getattr(event, "parts", None):
            for part in event.parts:
                part_text = getattr(part, "text", None)
                if part_text:
                    val = part_text() if callable(part_text) else part_text
                    s = str(val).strip()
                    if s and s.lower() != "none":
                        result_parts.append(s)
                func_resp = getattr(part, "function_response", None)
                if func_resp and hasattr(func_resp, "response"):
                    tool_resp = func_resp.response
                    if isinstance(tool_resp, dict) and "result" in tool_resp:
                        val = tool_resp["result"]
                        s = str(val).strip()
                        if s and s.lower() != "none":
                            result_parts.append(s)
                    elif isinstance(tool_resp, str):
                        s = str(tool_resp).strip()
                        if s and s.lower() != "none":
                            result_parts.append(s)
    final_result = "\n".join(result_parts).strip()
    print("DEBUG: Final result:", repr(final_result))
    return final_result 