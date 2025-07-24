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
from tools.maps import get_must_visit_places_nearby # Assuming this imports correctly
import json

def create_places_agent():
  return Agent(
    model="gemini-2.0-flash-001",
    name="places_agent",
    instruction="You are a Places Agent. Use the get_must_visit_places_nearby tool to answer questions about must-visit places near a location. If the tool returns a result, present it clearly. If there's no result, say so.",
    tools=[FunctionTool(get_must_visit_places_nearby)]
  )

async def run_places_agent(location: str, max_results: int = 3, user_id: str = "testuser", session_id: str = None) -> str:
  from shared.utils.logger import log_event
  agent = create_places_agent()
  runner = Runner(agent=agent, app_name=COMMON_APP_NAME, session_service=session_service)

  if not session_id:
    session_id = str(uuid.uuid4())

  await session_service.create_session(
    session_id=session_id,
    user_id=user_id,
    app_name=COMMON_APP_NAME
  )

  user_prompt = f"Get must-visit places near {location} (max {max_results})"
  content = types.Content(
    role="user",
    parts=[types.Part(text=user_prompt)]
  )

  log_event("PlacesAgent", f"Input: {user_prompt}")

  # This list will hold the *final* consolidated output parts from the agent
  final_output_parts = []

  # Iterate through the events yielded by the runner. The last one usually contains the final model response.
  async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
    log_event("PlacesAgent", f"Event: {event}")

    # Process the final output of the agent. The 'content' attribute of the event
    # typically holds the model's response parts after all tool calls.
    if event.content and event.content.parts:
      for part in event.content.parts:
        # Extract text from text parts
        part_text_attr = getattr(part, "text", None)
        if part_text_attr:
          val = part_text_attr() if callable(part_text_attr) else part_text_attr
          s = str(val).strip()
          if s and s.lower() != "none":
            final_output_parts.append(s)

        # Extract text from function responses if they were directly converted to text
        # (though usually function responses are handled by the runner internally)
        func_resp = getattr(part, "function_response", None)
        if func_resp and hasattr(func_resp, "response"):
          tool_resp = func_resp.response
          if isinstance(tool_resp, dict) and "result" in tool_resp:
            val = tool_resp["result"]
            s = str(val).strip()
            if s and s.lower() != "none":
              final_output_parts.append(s)
          elif isinstance(tool_resp, str): # Handle direct string responses
              s = str(tool_resp).strip()
              if s and s.lower() != "none":
                  final_output_parts.append(s)

  # Join the collected parts to form the final string output
  final_result = "\n".join(final_output_parts).strip()

  print("DEBUG: Final result:", repr(final_result))
  log_event("PlacesAgent", f"Final result: {final_result!r}")
  return final_result

if __name__ == "__main__":
  import asyncio
  async def test():
    result = await run_places_agent("Bengaluru", max_results=3, user_id="testuser")
    print("[TEST OUTPUT]", result)
  asyncio.run(test())
