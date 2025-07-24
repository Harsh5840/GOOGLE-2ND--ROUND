from agents.session_service import session_service, COMMON_APP_NAME
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.genai import types
import uuid
import asyncio

# No tools yet, but set up for future expansion
TOOL_FUNCTIONS = {}

def create_analysis_agent():
    # TODO: Add FunctionTools for analysis (pattern recognition, synthesis)
    return Agent(
        model="gemini-2.0-flash-001",
        name="analysis_agent",
        instruction="You are the Analysis Agent. Synthesize and analyze findings from research and data agents.",
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
    return response_text

async def run_analysis_agent(query: str, research_results: dict, data_results: dict, context: dict = None) -> dict:
    agent = create_analysis_agent()
    runner = Runner(agent=agent, app_name=COMMON_APP_NAME, session_service=session_service)
    user_id = context.get("user_id", "testuser") if context else "testuser"
    session_id = context.get("session_id", str(uuid.uuid4())) if context else str(uuid.uuid4())
    prompt = f"Analyze the following research and data results for '{query}':\nResearch: {research_results}\nData: {data_results}"
    content = types.Content(role="user", parts=[types.Part(text=prompt)])
    response_text = await run_agent_with_tools(runner, user_id, session_id, content, tool_dispatcher)
    return {"analysis_agent_response": response_text} 