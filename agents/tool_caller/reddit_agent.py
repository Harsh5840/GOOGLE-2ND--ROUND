# agents/tool_caller/reddit_agent.py

import requests
import os
from datetime import datetime, timedelta

REDDIT_BASE_URL = "https://www.reddit.com"
HEADERS = {
    "User-Agent": "CityChatbot/1.0",
}

def search_reddit_events(location: str, keywords=["events", "things to do"], limit=10):
    """
    Searches Reddit for recent posts related to events in the given location.
    Filters out posts older than 3 days.
    """
    search_query = f"{location} " + " OR ".join(keywords)
    url = f"{REDDIT_BASE_URL}/search.json"
    params = {
        "q": search_query,
        "sort": "new",
        "limit": limit,
        "restrict_sr": False,
    }

    try:
        res = requests.get(url, headers=HEADERS, params=params)
        res.raise_for_status()
        results = res.json().get("data", {}).get("children", [])
        cutoff_date = datetime.utcnow() - timedelta(days=3)

        events = []
        for post in results:
            data = post.get("data", {})
            created_utc = datetime.utcfromtimestamp(data.get("created_utc", 0))
            if created_utc > cutoff_date:
                events.append({
                    "title": data.get("title"),
                    "url": f"{REDDIT_BASE_URL}{data.get('permalink')}",
                    "upvotes": data.get("ups"),
                    "subreddit": data.get("subreddit"),
                    "created": created_utc.isoformat()
                })

        return events

    except Exception as e:
        print(f"[RedditAgent] Error fetching posts: {e}")
        return []
