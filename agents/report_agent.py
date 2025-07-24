from google.adk.agents import Agent
from google.adk.runners import Runner
from agents.session_service import session_service, COMMON_APP_NAME
from google.genai import types
import uuid

def create_report_agent():
    # TODO: Add FunctionTools for report generation, validation, slides, etc.
    return Agent(
        model="gemini-2.0-flash-001",
        name="report_agent",
        instruction="You are the Report Agent. Validate findings and generate professional reports for city investigations.",
        tools=[]
    )

# Async ADK-based run function
async def run_report_agent(query: str, research_results: dict, data_results: dict, analysis_results: dict, context: dict = None) -> dict:
    agent = create_report_agent()
    runner = Runner(agent=agent, app_name=COMMON_APP_NAME, session_service=session_service)
    user_id = context.get("user_id", "testuser") if context else "testuser"
    session_id = context.get("session_id", str(uuid.uuid4())) if context else str(uuid.uuid4())
    prompt = f"Generate a final report for '{query}' using the following results:\nResearch: {research_results}\nData: {data_results}\nAnalysis: {analysis_results}"
    content = types.Content(role="user", parts=[types.Part(text=prompt)])
    response_text = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content
    ):
        if hasattr(event, "text") and event.text:
            response_text += event.text
    return {"final_report": response_text} 