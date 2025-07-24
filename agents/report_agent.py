from agents.session_service import session_service, COMMON_APP_NAME
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.genai import types
import uuid
import asyncio

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

# No tools yet, but set up for future expansion
TOOL_FUNCTIONS = {}

def create_report_agent():
    # TODO: Add FunctionTools for report generation, validation, slides, etc.
    return Agent(
        model="gemini-2.0-flash-001",
        name="report_agent",
        instruction="You are the Report Agent. Use the available tools to gather information, but once you have enough, answer the user's question in plain text. Do not keep calling tools if you can answer.",
        tools=[]
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
            print(f"[DEBUG] LLM event: {event}")
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

async def run_report_agent(query: str, research_results: dict = None, data_results: dict = None, analysis_results: dict = None, context: dict = None) -> dict:
    agent = create_report_agent()
    runner = Runner(agent=agent, app_name=COMMON_APP_NAME, session_service=session_service)
    user_id = context.get("user_id", "testuser") if context else "testuser"
    session_id = context.get("session_id", str(uuid.uuid4())) if context else str(uuid.uuid4())
    content = types.Content(role="user", parts=[types.Part(text=query)])
    response_text = await run_agent_with_tools(runner, user_id, session_id, content, tool_dispatcher)
    if not response_text:
        print("[DEBUG] Falling back to plain LLM agent.")
        response_text = await run_llm_fallback(query, context)
    print(f"[DEBUG] run_report_agent returning: {response_text}")
    return {"report_agent_response": response_text} 