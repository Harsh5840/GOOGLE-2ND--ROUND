# agents/intent_extractor/agent.py

from vertexai.language_models import ChatModel
import os
import re

# Load Gemini model (Vertex AI must be initialized by caller)
chat_model = ChatModel.from_pretrained("chat-bison")

def extract_intent(message: str) -> dict:
    """
    Uses Gemini to extract structured intent and entities from the user's query.
    Example:
        Input: "Any events in Indiranagar tonight?"
        Output: {
            "intent": "GET_EVENTS",
            "entities": { "location": "Indiranagar", "date": "tonight" }
        }
    """
    prompt = f"""
You are an intent extraction agent for a city chatbot.

Extract:
1. The INTENT (e.g., GET_EVENTS, CHECK_TRAFFIC, FIND_PLACES, etc.)
2. The ENTITIES in JSON (e.g., location, date, category, etc.)

Respond in this JSON format only:
{{
  "intent": "INTENT_NAME",
  "entities": {{
    "location": "string",
    "date": "string",
    "category": "string"
  }}
}}

User Query:
"{message}"
"""

    chat = chat_model.start_chat()
    response = chat.send_message(prompt)

    # Extract JSON using regex (safe fallback)
    match = re.search(r'\{.*\}', response.text, re.DOTALL)
    if match:
        try:
            import json
            return json.loads(match.group())
        except Exception as e:
            print("Error parsing JSON:", e)

    # Fallback
    return {
        "intent": "UNKNOWN",
        "entities": {}
    }
