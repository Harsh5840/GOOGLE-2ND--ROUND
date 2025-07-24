from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from tools.firestore import fetch_firestore_reports, store_user_query_history, fetch_similar_user_queries
from tools.rag import get_rag_fallback

def create_data_agent():
    tools = [
        FunctionTool(fetch_firestore_reports),
        FunctionTool(store_user_query_history),
        FunctionTool(fetch_similar_user_queries),
        FunctionTool(get_rag_fallback),
    ]
    return Agent(
        model="gemini-2.0-flash-001",
        name="data_agent",
        instruction="You are the Data Agent. Retrieve and analyze internal city data (Firestore, RAG, user history).",
        tools=tools
    )

# Dynamic ADK-based run function
def run_data_agent(query: str, context: dict = None) -> dict:
    agent = create_data_agent()
    session_service = InMemorySessionService()
    runner = Runner(agent=agent, app_name="data_agent", session_service=session_service)
    response = runner.run(query)
    return {"data_agent_response": response.text if hasattr(response, 'text') else str(response)} 