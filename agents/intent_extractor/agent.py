# agents/intent_extractor/agent.py

from vertexai.generative_models import GenerativeModel
import re

gemini = GenerativeModel("gemini-1.5-pro")

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
            return eval(json_match.group(0))  # Quick dev shortcut

    except Exception as e:
        print("[IntentExtractor] Error:", e)

    return {
        "intent": "unknown",
        "entities": {}
    }
