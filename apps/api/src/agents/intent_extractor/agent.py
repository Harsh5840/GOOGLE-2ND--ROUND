from vertexai.generative_models import GenerativeModel
import re
import json
from shared.utils.logger import log_event

gemini = GenerativeModel("gemini-2.0-flash")

def extract_intent(message: str) -> dict:
    # --- PATCH: Regex-based pre-processing for Twitter queries ---
    twitter_patterns = [
        r"what is twitter saying about (?P<location>[\w\s]+)",
        r"twitter.*about (?P<location>[\w\s]+)",
        r"tweets? (about|in|for) (?P<location>[\w\s]+)",
        r"(?P<location>[\w\s]+) twitter feed",
        r"(?P<location>[\w\s]+) tweets"
    ]
    for pat in twitter_patterns:
        m = re.search(pat, message, re.IGNORECASE)
        if m:
            location = m.groupdict().get("location", "").strip()
            if location:
                return {
                    "intent": "get_twitter_posts",
                    "entities": {"location": location, "topic": "general"}
                }
    # --- PATCH: Regex-based pre-processing for Reddit queries ---
    reddit_patterns = [
        r"what is reddit saying about (?P<topic>[\w\s]+)",
        r"reddit.*about (?P<topic>[\w\s]+)",
        r"(?P<topic>[\w\s]+) reddit feed",
        r"(?P<topic>[\w\s]+) reddit"
    ]
    for pat in reddit_patterns:
        m = re.search(pat, message, re.IGNORECASE)
        if m:
            topic = m.groupdict().get("topic", "").strip()
            if topic:
                return {
                    "intent": "get_reddit_posts",
                    "entities": {"subreddit": topic.replace(' ', ''), "topic": topic}
                }
    # --- PATCH: News queries ---
    news_patterns = [
        r"news (in|about|for) (?P<city>[\w\s]+)",
        r"(?P<city>[\w\s]+) news"
    ]
    for pat in news_patterns:
        m = re.search(pat, message, re.IGNORECASE)
        if m:
            city = m.groupdict().get("city", "").strip()
            if city:
                return {
                    "intent": "get_city_news",
                    "entities": {"city": city, "location": city}
                }
    # --- PATCH: Firestore Reports queries ---
    firestore_reports_patterns = [
        r"reports? (in|about|for) (?P<location>[\w\s]+) (on|about) (?P<topic>[\w\s]+)",
        r"(?P<location>[\w\s]+) reports? (on|about) (?P<topic>[\w\s]+)"
    ]
    for pat in firestore_reports_patterns:
        m = re.search(pat, message, re.IGNORECASE)
        if m:
            location = m.groupdict().get("location", "").strip()
            topic = m.groupdict().get("topic", "").strip()
            if location and topic:
                return {
                    "intent": "get_firestore_reports",
                    "entities": {"location": location, "topic": topic}
                }
    # --- PATCH: Firestore Similar queries ---
    firestore_similar_patterns = [
        r"similar queries for user (?P<user_id>[\w\d]+) (about|for) (?P<query>[\w\s]+)"
    ]
    for pat in firestore_similar_patterns:
        m = re.search(pat, message, re.IGNORECASE)
        if m:
            user_id = m.groupdict().get("user_id", "").strip()
            query_val = m.groupdict().get("query", "").strip()
            if user_id and query_val:
                return {
                    "intent": "get_similar_queries",
                    "entities": {"user_id": user_id, "query": query_val}
                }
    # --- PATCH: Google Search queries ---
    google_search_patterns = [
        r"google search for (?P<query>[\w\s]+)",
        r"search google for (?P<query>[\w\s]+)",
        r"search for (?P<query>[\w\s]+) on google"
    ]
    for pat in google_search_patterns:
        m = re.search(pat, message, re.IGNORECASE)
        if m:
            query_val = m.groupdict().get("query", "").strip()
            if query_val:
                return {
                    "intent": "google_search",
                    "entities": {"query": query_val}
                }
    # --- PATCH: Maps/Route queries ---
    maps_patterns = [
        r"route from (?P<current_location>[\w\s]+) to (?P<destination>[\w\s]+)",
        r"best route (from|between) (?P<current_location>[\w\s]+) (to|and) (?P<destination>[\w\s]+)"
    ]
    for pat in maps_patterns:
        m = re.search(pat, message, re.IGNORECASE)
        if m:
            current_location = m.groupdict().get("current_location", "").strip()
            destination = m.groupdict().get("destination", "").strip()
            if current_location and destination:
                return {
                    "intent": "get_best_route",
                    "entities": {"current_location": current_location, "destination": destination}
                }
    # --- END PATCHES ---
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
