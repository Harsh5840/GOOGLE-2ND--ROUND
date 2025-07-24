from google.adk.agents import Agent
from google.adk.tools import FunctionTool
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

# Real run function for data agent
def run_data_agent(query: str, context: dict = None) -> dict:
    """
    Calls each data tool with the query/context and returns a dict of results.
    """
    context = context or {}
    results = {}
    # Firestore reports
    results['firestore_reports'] = fetch_firestore_reports(location=context.get('location', ''), topic=query)
    # Store user query history (simulate user_id)
    results['store_history'] = store_user_query_history(user_id=context.get('user_id', 'demo'), query=query, response_data={})
    # Fetch similar user queries
    results['similar_queries'] = fetch_similar_user_queries(user_id=context.get('user_id', 'demo'), query=query)
    # RAG fallback
    results['rag'] = get_rag_fallback(location=context.get('location', ''), topic=query)
    return results 