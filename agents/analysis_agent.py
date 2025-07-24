from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import uuid

# Shared session service instance for all analysis agent runs
session_service = InMemorySessionService()

def create_analysis_agent():
    # TODO: Add FunctionTools for analysis (pattern recognition, synthesis)
    return Agent(
        model="gemini-2.0-flash-001",
        name="analysis_agent",
        instruction="You are the Analysis Agent. Synthesize and analyze findings from research and data agents.",
        tools=[]
    )

# Dynamic ADK-based run function
def run_analysis_agent(query: str, research_results: dict, data_results: dict, context: dict = None) -> dict:
    agent = create_analysis_agent()
    runner = Runner(agent=agent, app_name="analysis_agent", session_service=session_service)
    user_id = context.get("user_id", "testuser") if context else "testuser"
    session_id = context.get("session_id", str(uuid.uuid4())) if context else str(uuid.uuid4())
    # Create the session before running
    session_service.create_session(
        session_id=session_id,
        user_id=user_id,
        app_name=runner.app_name
    )
    prompt = f"Analyze the following research and data results for '{query}':\nResearch: {research_results}\nData: {data_results}"
    content = types.Content(role="user", parts=[types.Part(text=prompt)])
    events = runner.run(
        user_id=user_id,
        session_id=session_id,
        new_message=content
    )
    response_text = ""
    for event in events:
        if hasattr(event, "text") and event.text:
            response_text += event.text
    return {"analysis_agent_response": response_text} 