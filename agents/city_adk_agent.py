from vertexai.generative_models import GenerativeModel, Tool, FunctionDeclaration, ToolConfig, Part
from tools.twitter import fetch_twitter_posts
from tools.reddit import fetch_reddit_posts
from tools.maps import get_best_route, get_must_visit_places_nearby
from tools.news import fetch_city_news
from tools.google_search import google_search
from tools.rag import get_rag_fallback
from tools.firestore import fetch_firestore_reports, store_user_query_history, fetch_similar_user_queries

# Tool Declarations
fetch_twitter_posts_decl = FunctionDeclaration(
    name="fetch_twitter_posts",
    description="Searches for recent posts on Twitter based on a location and a topic.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "location": {"type": "STRING", "description": "The geographical location to search for tweets."},
            "topic": {"type": "STRING", "description": "The topic or keyword to search for."},
            "limit": {"type": "INTEGER", "description": "The maximum number of tweets to fetch (optional, default is 5, max 100)."},
        },
        "required": ["location", "topic"],
    },
)
fetch_reddit_posts_decl = FunctionDeclaration(
    name="fetch_reddit_posts",
    description="Fetches top posts from a subreddit on Reddit.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "subreddit": {"type": "STRING", "description": "The subreddit to fetch posts from."},
            "limit": {"type": "INTEGER", "description": "The maximum number of posts to fetch (optional, default is 5, max 100)."},
        },
        "required": ["subreddit"],
    },
)
get_best_route_decl = FunctionDeclaration(
    name="get_best_route",
    description="Finds the best route between two locations using Google Maps, considering current traffic.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "current_location": {"type": "STRING", "description": "The starting point (address or lat,lng)."},
            "destination": {"type": "STRING", "description": "The destination point (address or lat,lng)."},
            "mode": {"type": "STRING", "description": "Mode of transport (e.g., 'driving', 'walking', 'bicycling', 'transit'). Optional, default is 'driving'."},
        },
        "required": ["current_location", "destination"],
    },
)
get_must_visit_places_nearby_decl = FunctionDeclaration(
    name="get_must_visit_places_nearby",
    description="Finds must-visit places near a location using Google Maps.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "location": {"type": "STRING", "description": "The location to search around."},
            "max_results": {"type": "INTEGER", "description": "Maximum number of places to return (default 3)."},
        },
        "required": ["location"],
    },
)
fetch_city_news_decl = FunctionDeclaration(
    name="fetch_city_news",
    description="Fetches news articles relevant to a specific city using NewsAPI.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "city": {"type": "STRING", "description": "The city to search news for."},
            "limit": {"type": "INTEGER", "description": "The maximum number of articles to fetch (optional, default is 5, max 100)."},
        },
        "required": ["city"],
    },
)
google_search_decl = FunctionDeclaration(
    name="google_search",
    description="Performs a Google search and returns a list of results.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "query": {"type": "STRING", "description": "The search query."},
            "num_results": {"type": "INTEGER", "description": "Number of results to return (default 5)."},
        },
        "required": ["query"],
    },
)
get_rag_fallback_decl = FunctionDeclaration(
    name="get_rag_fallback",
    description="Fallback to a search-style Gemini query on background knowledge.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "location": {"type": "STRING", "description": "The location context."},
            "topic": {"type": "STRING", "description": "The topic context."},
        },
        "required": ["location", "topic"],
    },
)
fetch_firestore_reports_decl = FunctionDeclaration(
    name="fetch_firestore_reports",
    description="Fetch user-submitted incident reports from Firestore.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "location": {"type": "STRING", "description": "Location to filter reports."},
            "topic": {"type": "STRING", "description": "Topic to filter reports."},
            "limit": {"type": "INTEGER", "description": "Maximum number of reports to fetch (default 5)."},
        },
        "required": ["location", "topic"],
    },
)
store_user_query_history_decl = FunctionDeclaration(
    name="store_user_query_history",
    description="Store a user's query, timestamp, and response data in Firestore.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "user_id": {"type": "STRING", "description": "User ID."},
            "query": {"type": "STRING", "description": "User query."},
            "response_data": {"type": "OBJECT", "description": "Response data to store."},
        },
        "required": ["user_id", "query", "response_data"],
    },
)
fetch_similar_user_queries_decl = FunctionDeclaration(
    name="fetch_similar_user_queries",
    description="Fetch past queries for a user that are similar to the current query.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "user_id": {"type": "STRING", "description": "User ID."},
            "query": {"type": "STRING", "description": "Query to match."},
            "limit": {"type": "INTEGER", "description": "Maximum number of similar queries to fetch (default 5)."},
        },
        "required": ["user_id", "query"],
    },
)

CITY_TOOLS = [
    Tool(function_declarations=[
        fetch_twitter_posts_decl,
        fetch_reddit_posts_decl,
        get_best_route_decl,
        get_must_visit_places_nearby_decl,
        fetch_city_news_decl,
        google_search_decl,
        get_rag_fallback_decl,
        fetch_firestore_reports_decl,
        store_user_query_history_decl,
        fetch_similar_user_queries_decl,
    ])
]

TOOL_FUNCTIONS = {
    "fetch_twitter_posts": fetch_twitter_posts,
    "fetch_reddit_posts": fetch_reddit_posts,
    "get_best_route": get_best_route,
    "get_must_visit_places_nearby": get_must_visit_places_nearby,
    "fetch_city_news": fetch_city_news,
    "google_search": google_search,
    "get_rag_fallback": get_rag_fallback,
    "fetch_firestore_reports": fetch_firestore_reports,
    "store_user_query_history": store_user_query_history,
    "fetch_similar_user_queries": fetch_similar_user_queries,
}

SYSTEM_PROMPT = [
    "You are CityAgent, a smart city assistant. You have access to tools for Twitter, Reddit, Google Maps, News, Google Search, RAG, and Firestore.",
    "Use the tools to answer user queries, fetch data, and provide helpful, actionable responses.",
    "Always use the most relevant tool(s) for the user's request.",
    "If a tool returns an error, inform the user clearly.",
]

city_agent_model = GenerativeModel(
    "gemini-2.0-flash",
    tools=CITY_TOOLS,
    tool_config=ToolConfig(
        function_calling_config=ToolConfig.FunctionCallingConfig(
            mode=ToolConfig.FunctionCallingConfig.Mode.AUTO,
        ),
    ),
    system_instruction=SYSTEM_PROMPT,
)
city_agent_session = city_agent_model.start_chat()

def run_city_agent(query: str) -> str:
    response = city_agent_session.send_message(query)
    # If the agent called tools, handle tool calls and return the final response
    if response.candidates and response.candidates[0].function_calls:
        function_calls = response.candidates[0].function_calls
        tool_outputs = []
        for function_call in function_calls:
            function_name = function_call.name
            function_args = {k: v for k, v in function_call.args.items()}
            if function_name in TOOL_FUNCTIONS:
                result = TOOL_FUNCTIONS[function_name](**function_args)
                tool_outputs.append(Part.from_function_response(name=function_name, response=result))
            else:
                tool_outputs.append(Part.from_function_response(name=function_name, response={"error": f"Unknown tool: {function_name}"}))
        final_response = city_agent_session.send_message(tool_outputs)
        return final_response.text
    else:
        return response.text 