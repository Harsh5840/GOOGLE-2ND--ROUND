from agents.session_service import session_service, COMMON_APP_NAME
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.genai import types
import uuid
import asyncio
from tools.twitter import fetch_twitter_posts
from tools.reddit import fetch_reddit_posts
from tools.news import fetch_city_news
from tools.maps import get_best_route, get_must_visit_places_nearby

TOOL_FUNCTIONS = {
    "fetch_twitter_posts": fetch_twitter_posts,
    "fetch_reddit_posts": fetch_reddit_posts,
    "fetch_city_news": fetch_city_news,
    "get_best_route": get_best_route,
    "get_must_visit_places_nearby": get_must_visit_places_nearby,
}

def create_research_agent():
    tools = [
        FunctionTool(fetch_twitter_posts, description="Fetches recent Twitter posts for a location and topic."),
        FunctionTool(fetch_reddit_posts, description="Fetches top Reddit posts from a subreddit."),
        FunctionTool(fetch_city_news, description="Fetches news articles relevant to a specific city."),
        FunctionTool(get_best_route, description="Finds the best route between two locations using Google Maps."),
        FunctionTool(get_must_visit_places_nearby, description="Finds must-visit places near a location using Google Maps. Use for queries like 'best places to visit in <city>'."),
    ]
    return Agent(
        model="gemini-2.0-flash-001",
        name="research_agent",
        instruction="You are the Research Agent. Collect external data and artifacts for city investigations. Use the available tools for social media, news, and location-based queries.",
        tools=tools
    )

async def tool_dispatcher(tool_name, tool_args):
    func = TOOL_FUNCTIONS.get(tool_name)
    if not func:
        return f"Tool {tool_name} not found."
    try:
        result = func(**tool_args)
        if asyncio.iscoroutine(result):
            result = await result
        return str(result)
    except Exception as e:
        return f"Error running tool {tool_name}: {e}"

async def run_agent_with_tools(runner, user_id, session_id, initial_content, tool_dispatcher):
    content = initial_content
    response_text = ""
    while True:
        function_call_found = False
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ):
            if hasattr(event, "function_call") and event.function_call:
                tool_name = event.function_call.name
                tool_args = event.function_call.args
                tool_result = await tool_dispatcher(tool_name, tool_args)
                content = types.Content(role="function", parts=[types.Part(text=tool_result)])
                function_call_found = True
                break
            elif hasattr(event, "text") and event.text:
                response_text += event.text
        if not function_call_found:
            break
    return response_text

async def run_research_agent(query: str, context: dict = None) -> dict:
    agent = create_research_agent()
    runner = Runner(agent=agent, app_name=COMMON_APP_NAME, session_service=session_service)
    user_id = context.get("user_id", "testuser") if context else "testuser"
    session_id = context.get("session_id", str(uuid.uuid4())) if context else str(uuid.uuid4())
    content = types.Content(role="user", parts=[types.Part(text=query)])
    response_text = await run_agent_with_tools(runner, user_id, session_id, content, tool_dispatcher)
    return {"research_agent_response": response_text} 