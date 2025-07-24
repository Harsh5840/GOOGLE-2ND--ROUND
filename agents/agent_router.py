from agents.twitter_agent import run_twitter_agent
from agents.reddit_agent import run_reddit_agent
from agents.maps_agent import run_maps_agent
from agents.places_agent import run_places_agent
from agents.news_agent import run_news_agent
from agents.rag_agent import run_rag_agent
from agents.firestore_reports_agent import run_firestore_reports_agent
from agents.firestore_history_agent import run_firestore_history_agent
from agents.firestore_similar_agent import run_firestore_similar_agent
from agents.google_search_agent import run_google_search_agent
from agents.gemini_fallback_agent import run_gemini_fallback_agent

async def agent_router(tool_name: str, args: dict, fallback: str = "gemini") -> str:
    """
    Routes the tool call to the correct single-tool agent. Falls back to Gemini LLM or Google Search if tool is not found or fails.
    Args:
        tool_name (str): The name of the tool/agent to use.
        args (dict): Arguments for the tool.
        fallback (str): 'gemini' or 'google_search'.
    Returns:
        str: The agent's response.
    """
    try:
        if tool_name == "fetch_twitter_posts":
            return await run_twitter_agent(**args)
        elif tool_name == "fetch_reddit_posts":
            return await run_reddit_agent(**args)
        elif tool_name == "get_best_route":
            return await run_maps_agent(**args)
        elif tool_name == "get_must_visit_places_nearby":
            return await run_places_agent(**args)
        elif tool_name == "fetch_city_news":
            return await run_news_agent(**args)
        elif tool_name == "get_rag_fallback":
            return await run_rag_agent(**args)
        elif tool_name == "fetch_firestore_reports":
            return await run_firestore_reports_agent(**args)
        elif tool_name == "store_user_query_history":
            return await run_firestore_history_agent(**args)
        elif tool_name == "fetch_similar_user_queries":
            return await run_firestore_similar_agent(**args)
        elif tool_name == "google_search":
            return await run_google_search_agent(**args)
        else:
            if fallback == "google_search":
                return await run_google_search_agent(query=args.get("query", ""))
            else:
                return await run_gemini_fallback_agent(args.get("query", ""))
    except Exception as e:
        if fallback == "google_search":
            return f"[Fallback: Google Search] {await run_google_search_agent(query=args.get('query', ''))}"
        else:
            return f"[Fallback: Gemini] {await run_gemini_fallback_agent(args.get('query', ''))}" 