import os
import requests
from dotenv import load_dotenv
from shared.utils.logger import log_event

load_dotenv()
GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
GOOGLE_SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

def google_search(query: str, num_results: int = 5) -> list:
    if not (GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_ENGINE_ID):
        log_event("GoogleSearchAgent", "API key or engine ID not set.")
        return []
    url = (
        f"https://www.googleapis.com/customsearch/v1"
        f"?key={GOOGLE_SEARCH_API_KEY}&cx={GOOGLE_SEARCH_ENGINE_ID}"
        f"&q={requests.utils.quote(query)}&num={num_results}"
    )
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        results = []
        for item in data.get("items", []):
            results.append({
                "title": item.get("title"),
                "snippet": item.get("snippet"),
                "link": item.get("link"),
            })
        return results
    except Exception as e:
        log_event("GoogleSearchAgent", f"Error: {e}")
        return []