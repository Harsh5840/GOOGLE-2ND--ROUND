from google.adk import Agent
from google.adk.tools import google_search
from tools.twitter import fetch_twitter_posts
from tools.reddit import fetch_reddit_posts
from tools.maps import get_best_route, get_must_visit_places_nearby
from tools.news import fetch_city_news
from tools.rag import get_rag_fallback
from tools.firestore import fetch_firestore_reports, store_user_query_history, fetch_similar_user_queries

agent = Agent(
    tools=[
        google_search,
        fetch_twitter_posts,
        fetch_reddit_posts,
        get_best_route,
        get_must_visit_places_nearby,
        fetch_city_news,
        get_rag_fallback,
        fetch_firestore_reports,
        store_user_query_history,
        fetch_similar_user_queries,
    ],
    system_instruction="""
You are CityAgent, a smart city assistant. You have access to tools for Twitter, Reddit, Google Maps, News, Google Search, RAG, and Firestore.
Use the tools to answer user queries, fetch data, and provide helpful, actionable responses.
Always use the most relevant tool(s) for the user's request.
If a tool returns an error, inform the user clearly.
"""
)

def run_city_agent(query: str) -> str:
    response = agent.run(query)
    return response.text if hasattr(response, 'text') else str(response) 