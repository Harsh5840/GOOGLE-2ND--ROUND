# agents/twitter_agent.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

def fetch_twitter_posts(location: str, topic: str, limit: int = 5) -> list:
    """
    Uses Twitter API v2 to search recent tweets based on location + topic.
    """
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}"
    }

    query = f"{location} {topic} -is:retweet lang:en"
    url = "https://api.twitter.com/2/tweets/search/recent"

    params = {
        "query": query,
        "max_results": min(limit, 100),
        "tweet.fields": "created_at,text,author_id"
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        tweets = response.json().get("data", [])

        return [
            {
                "text": tweet["text"],
                "id": tweet["id"],
                "created_at": tweet["created_at"]
            }
            for tweet in tweets
        ]

    except Exception as e:
        print("[TwitterAgent] Error:", e)
        return []
