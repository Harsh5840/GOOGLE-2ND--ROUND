import os
from dotenv import load_dotenv
from typing import Dict, Any
import requests
from shared.utils.logger import log_event

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def fetch_city_news(city: str, limit: int = 5) -> Dict[str, Any]:
    """
    Fetches news articles relevant to a specific city using NewsAPI.

    Args:
        city (str): The city to search news for.
        limit (int): The maximum number of articles to fetch (default 5, max 100).

    Returns:
        dict: A dictionary containing a list of articles with 'title', 'description', 'url', 'publishedAt'.
              Returns a dictionary with an 'error' key if an error occurs.
    """
    if not NEWS_API_KEY:
        log_event("NewsTool", "NEWS_API_KEY not set.")
        return {"error": "News API key not configured."}

    actual_limit = min(limit, 100)
    url = (
        f"https://newsapi.org/v2/everything?q={requests.utils.quote(city)}"
        f"&pageSize={actual_limit}&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    )
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        if data.get("status") != "ok":
            return {"error": data.get("message", "Failed to fetch news.")}
        articles = [
            {
                "title": a.get("title"),
                "description": a.get("description"),
                "url": a.get("url"),
                "publishedAt": a.get("publishedAt"),
                "source": a.get("source", {}).get("name", "")
            }
            for a in data.get("articles", [])
        ]
        return {"articles": articles}
    except Exception as e:
        error_msg = f"News API error: {e}"
        log_event("NewsTool", error_msg)
        return {"error": error_msg} 