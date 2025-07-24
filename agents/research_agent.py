from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from tools.twitter import fetch_twitter_posts
from tools.reddit import fetch_reddit_posts
from tools.news import fetch_city_news
from tools.google_search import google_search

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

# Real run function for research agent
def run_research_agent(query: str, context: dict = None) -> dict:
    """
    Calls each research tool with the query/context and returns a dict of results.
    """
    context = context or {}
    results = {}
    # Twitter
    results['twitter'] = fetch_twitter_posts(location=context.get('location', ''), topic=query)
    # Reddit (using topic as subreddit for demo)
    results['reddit'] = fetch_reddit_posts(subreddit=query)
    # News
    results['news'] = fetch_city_news(city=context.get('location', query))
    # Google Search
    results['google_search'] = google_search(query)
    return results 