from vertexai.generative_models import GenerativeModel
import re
import json
from shared.utils.logger import log_event

gemini = GenerativeModel("gemini-2.0-flash")

def extract_intent(message: str) -> dict:
    prompt = f"""
You are an intent extractor for a smart city assistant.
Given a user's message, extract:
- `intent`: One word, e.g., 'traffic', 'event', 'power', 'weather', etc.
- `entities`: Dict with keys like 'location', 'time', or 'topic' if mentioned.

Respond ONLY in JSON like:
{{
  "intent": "event",
  "entities": {{
    "location": "HSR Layout",
    "topic": "flash mob"
  }}
}}

User: "{message}"
"""

    try:
        response = gemini.generate_content(prompt)
        text = response.text.strip()

        # Naive safety net if Gemini wraps in markdown
        json_match = re.search(r'\{[\s\S]+\}', text)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except Exception as e:
                log_event("IntentExtractor", f"JSON parse error: {e} | text: {text}")

    except Exception as e:
        log_event("IntentExtractor", f"Error: {e}")

    return {
        "intent": "unknown",
        "entities": {}
    }
