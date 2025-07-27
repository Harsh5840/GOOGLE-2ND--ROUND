import os
from dotenv import load_dotenv
load_dotenv()

from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.runners import Runner
from google.genai import types
import uuid
from agents.session_service import session_service, COMMON_APP_NAME
from agents.multilingual_wrapper import multilingual_wrapper

def create_gemini_fallback_agent():
    return Agent(
        model="gemini-2.0-flash-001",
        name="gemini_fallback_agent",
        instruction="You are a helpful assistant. Answer the user's question as best as you can. Only use google search tool if gemini doesn't give answer.",
        tools=[google_search]
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
        # Extract text from the event
        if hasattr(event, 'content') and event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, 'text'):
                    result += part.text
    print("DEBUG: Final result before return:", repr(result))
    
    # Translate response to user's language if needed
    user_lang = multilingual_wrapper.get_user_language(user_id)
    if user_lang != 'en':
        result = await multilingual_wrapper.translate_from_english(result.strip(), user_lang)
    
    from shared.utils.logger import log_event
    log_event("GeminiFallback", f"Generated response for user {user_id}: {len(result)} characters")
    
    return result.strip()

