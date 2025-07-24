from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
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

# Dynamic ADK-based run function
def run_research_agent(query: str, context: dict = None) -> dict:
    agent = create_research_agent()
    session_service = InMemorySessionService()
    runner = Runner(agent=agent, app_name="research_agent", session_service=session_service)
    # Optionally, context can be appended to the query or handled via session state
    response = runner.run(query)
    return {"research_agent_response": response.text if hasattr(response, 'text') else str(response)} 