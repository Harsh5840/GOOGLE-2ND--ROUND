import os
from dotenv import load_dotenv
load_dotenv()
import vertexai
vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION")
)
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.genai import types
import uuid
from agents.session_service import session_service, COMMON_APP_NAME
from tools.maps import get_must_visit_places_nearby

def create_places_agent():
    return Agent(
        model="gemini-2.0-flash-001",
        name="places_agent",
        instruction="You are a Places Agent. Use the get_must_visit_places_nearby tool to answer questions about must-visit places near a location.",
        tools=[FunctionTool(get_must_visit_places_nearby)]
    )

async def run_places_agent(location: str, max_results: int = 3, user_id: str = "testuser", session_id: str = None) -> str:
    from shared.utils.logger import log_event
    agent = create_places_agent()
    runner = Runner(agent=agent, app_name=COMMON_APP_NAME, session_service=session_service)
    if not session_id:
        session_id = str(uuid.uuid4())
    await session_service.create_session(session_id=session_id, user_id=user_id, app_name=COMMON_APP_NAME)
    content = types.Content(role="user", parts=[types.Part(text=f"Get must-visit places near {location} (max {max_results})")])
    log_event("PlacesAgent", f"Input: location={location}, max_results={max_results}")
    result = ""
    function_result = None
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        log_event("PlacesAgent", f"Event: {event}")
        if hasattr(event, 'text') and event.text:
            result += event.text
        if hasattr(event, 'parts') and event.parts:
            for part in event.parts:
                if hasattr(part, 'function_response') and part.function_response:
                    function_result = part.function_response.response.get('result')
    log_event("PlacesAgent", f"Result: {result!r}")
    if not result.strip() and function_result:
        log_event("PlacesAgent", f"Returning function_result: {function_result}")
        return function_result
    return result.strip() 