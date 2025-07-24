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
import asyncio

def fetch_reddit_posts_sync(**kwargs):
    import asyncio
    subreddit = kwargs.get('subreddit') or kwargs.get('topic')
    if not subreddit:
        return "No subreddit or topic specified."
    kwargs['subreddit'] = subreddit
    print("DEBUG: fetch_reddit_posts_sync called with kwargs:", kwargs)
    return asyncio.run(fetch_reddit_posts(**kwargs))

def create_reddit_agent():
    return Agent(
        model="gemini-2.0-flash-001",
        name="reddit_agent",
        instruction="You are a Reddit Agent. Always use the fetch_reddit_posts tool to answer questions about Reddit posts. Do not answer directly.",
        tools=[FunctionTool(fetch_reddit_posts_sync)]
    )

async def run_reddit_agent(subreddit: str, limit: int = 5, user_id: str = "testuser", session_id: str = None) -> str:
    agent = create_reddit_agent()
    runner = Runner(agent=agent, app_name=COMMON_APP_NAME, session_service=session_service)
    if not session_id:
        session_id = str(uuid.uuid4())
    await session_service.create_session(session_id=session_id, user_id=user_id, app_name=COMMON_APP_NAME)
    content = types.Content(role="user", parts=[types.Part(text=f"Get top posts in r/{subreddit} (limit {limit})")])
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