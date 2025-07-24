from google.adk import Agent
from google.adk.tools import google_search
from tools.twitter import fetch_twitter_posts
from tools.reddit import fetch_reddit_posts
from tools.maps import get_best_route, get_must_visit_places_nearby
from tools.news import fetch_city_news
from tools.rag import get_rag_fallback
from tools.firestore import fetch_firestore_reports, store_user_query_history, fetch_similar_user_queries
from google.adk.runners import Runner
from google.genai import types
import uuid
from agents.session_service import session_service, COMMON_APP_NAME
from google.adk.tools import FunctionTool

def city_tool_dispatcher(tool_name: str, **kwargs) -> str:
    """
    Dispatches tool calls to the correct function.

    Args:
        tool_name (str): The name of the tool to call. One of:
            - fetch_twitter_posts(location: str, topic: str, limit: int = 10)
            - fetch_reddit_posts(subreddit: str, limit: int = 5)
            - get_best_route(current_location: str, destination: str, mode: str = "driving")
            - get_must_visit_places_nearby(location: str, max_results: int = 3)
            - fetch_city_news(city: str, limit: int = 5)
            - get_rag_fallback(location: str, topic: str)
            - fetch_firestore_reports(location: str, topic: str, limit: int = 5)
            - store_user_query_history(user_id: str, query: str, response_data: dict)
            - fetch_similar_user_queries(user_id: str, query: str, limit: int = 5)
        kwargs: The arguments for the tool, as described above. You must always provide all required arguments for the tool_name you specify.

    Returns:
        str: The result of the tool call.
    """
    if tool_name == "fetch_twitter_posts":
        return fetch_twitter_posts(**kwargs)
    elif tool_name == "fetch_reddit_posts":
        return fetch_reddit_posts(**kwargs)
    elif tool_name == "get_best_route":
        return get_best_route(**kwargs)
    elif tool_name == "get_must_visit_places_nearby":
        return get_must_visit_places_nearby(**kwargs)
    elif tool_name == "fetch_city_news":
        return fetch_city_news(**kwargs)
    elif tool_name == "get_rag_fallback":
        return get_rag_fallback(**kwargs)
    elif tool_name == "fetch_firestore_reports":
        return fetch_firestore_reports(**kwargs)
    elif tool_name == "store_user_query_history":
        return store_user_query_history(**kwargs)
    elif tool_name == "fetch_similar_user_queries":
        return fetch_similar_user_queries(**kwargs)
    else:
        return f"Unknown tool: {tool_name}"

agent = Agent(
    name="CityAgent",
    model="gemini-2.0-flash-001",
    instruction="""
You are CityAgent, a smart city assistant. You have access to a single tool called 'city_tool_dispatcher'.
To use a capability, call city_tool_dispatcher with the tool_name (e.g., 'fetch_twitter_posts', 'get_best_route', etc.) and the required arguments as keyword arguments.
You must always provide all required arguments for the tool_name you specify. For example, for get_must_visit_places_nearby, always provide location (and optionally max_results).
After using the tool, answer the user's question in plain text if you have enough information.
If a tool returns an error, inform the user clearly.
Available tool_names: fetch_twitter_posts, fetch_reddit_posts, get_best_route, get_must_visit_places_nearby, fetch_city_news, get_rag_fallback, fetch_firestore_reports, store_user_query_history, fetch_similar_user_queries.
""",
    tools=[FunctionTool(city_tool_dispatcher)]
)

async def run_city_agent(query: str) -> str:
    runner = Runner(agent=agent, app_name=COMMON_APP_NAME, session_service=session_service)
    user_id = "testuser"
    session_id = str(uuid.uuid4())
    content = types.Content(role="user", parts=[types.Part(text=query)])
    # Create the session before running the agent
    await session_service.create_session(
        session_id=session_id,
        user_id=user_id,
        app_name=COMMON_APP_NAME
    )
    result = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content
    ):
        if hasattr(event, 'text') and event.text:
            result += event.text
    return result 