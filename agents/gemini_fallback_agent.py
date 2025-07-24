import os
from dotenv import load_dotenv
load_dotenv()
import vertexai
vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION")
)
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.genai import types
import uuid
from agents.session_service import session_service, COMMON_APP_NAME

def create_gemini_fallback_agent():
    return Agent(
        model="gemini-2.0-flash-001",
        name="gemini_fallback_agent",
        instruction="You are a helpful assistant. Answer the user's question as best as you can. Do not use any tools.",
        tools=[]
    )

async def run_gemini_fallback_agent(query: str, user_id: str = "testuser", session_id: str = None) -> str:
    agent = create_gemini_fallback_agent()
    runner = Runner(agent=agent, app_name=COMMON_APP_NAME, session_service=session_service)
    if not session_id:
        session_id = str(uuid.uuid4())
    await session_service.create_session(session_id=session_id, user_id=user_id, app_name=COMMON_APP_NAME)
    content = types.Content(role="user", parts=[types.Part(text=query)])
    result = ""
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        print("DEBUG: event:", event)
        if getattr(event, "text", None):
            print("DEBUG: event.text:", event.text)
            result += str(event.text) + "\n"
        if getattr(event, "parts", None):
            for part in event.parts:
                print("DEBUG: part:", part)
                part_text = getattr(part, "text", None)
                print("DEBUG: part.text:", part_text)
                if part_text is not None:
                    val = part_text() if callable(part_text) else part_text
                    s = str(val)
                    print("DEBUG: part.text value:", s)
                    if s.strip().lower() != "none":
                        print("DEBUG: Appending to result and returning immediately:", repr(s))
                        return s.strip()
                        result += s + "\n"
                        print("DEBUG: result so far:", repr(result))
                # Try other fields
                if hasattr(part, 'data'):
                    print("DEBUG: part.data:", getattr(part, 'data'))
                if hasattr(part, '_data'):
                    print("DEBUG: part._data:", getattr(part, '_data'))
                print("DEBUG: str(part):", str(part))
    print("DEBUG: Final result before return:", repr(result))
    return result.strip() 