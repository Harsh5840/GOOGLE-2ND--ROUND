from agents.session_service import session_service, COMMON_APP_NAME
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.genai import types
import uuid
import asyncio
from tools.firestore import fetch_firestore_reports, store_user_query_history, fetch_similar_user_queries
from tools.rag import get_rag_fallback

TOOL_FUNCTIONS = {
    "fetch_firestore_reports": fetch_firestore_reports,
    "store_user_query_history": store_user_query_history,
    "fetch_similar_user_queries": fetch_similar_user_queries,
    "get_rag_fallback": get_rag_fallback,
}

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

def create_fallback_llm_agent():
    return Agent(
        model="gemini-2.0-flash-001",
        name="llm_fallback_agent",
        instruction="You are a helpful assistant. Answer the user's question as best as you can.",
        tools=[]
    )

async def run_llm_fallback(query: str, context: dict = None) -> str:
    agent = create_fallback_llm_agent()
    runner = Runner(agent=agent, app_name=COMMON_APP_NAME, session_service=session_service)
    user_id = context.get("user_id", "testuser") if context else "testuser"
    session_id = context.get("session_id", str(uuid.uuid4())) if context else str(uuid.uuid4())
    content = types.Content(role="user", parts=[types.Part(text=query)])
    response_text = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content
    ):
        if hasattr(event, "text") and event.text:
            response_text += event.text
    return response_text

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
    print(f"[DEBUG] run_agent_with_tools final response_text: {response_text}")
    return response_text

async def run_data_agent(query: str, context: dict = None) -> dict:
    agent = create_data_agent()
    runner = Runner(agent=agent, app_name=COMMON_APP_NAME, session_service=session_service)
    user_id = context.get("user_id", "testuser") if context else "testuser"
    session_id = context.get("session_id", str(uuid.uuid4())) if context else str(uuid.uuid4())
    content = types.Content(role="user", parts=[types.Part(text=query)])
    response_text = await run_agent_with_tools(runner, user_id, session_id, content, tool_dispatcher)
    if not response_text:
        print("[DEBUG] Falling back to plain LLM agent.")
        response_text = await run_llm_fallback(query, context)
    print(f"[DEBUG] run_data_agent returning: {response_text}")
    return {"data_agent_response": response_text} 