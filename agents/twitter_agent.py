import os
import requests
from dotenv import load_dotenv
from typing import List
import tweepy

load_dotenv()

BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")


def fetch_twitter_posts(location: str, topic: str, limit: int = 5) -> list:
    """
    Uses Twitter API v2 to search recent tweets based on location + topic.
    """
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}

    query = f"{location} {topic} -is:retweet lang:en"
    url = "https://api.twitter.com/2/tweets/search/recent"

    params = {
        "query": query,
        "max_results": min(limit, 100),
        "tweet.fields": "created_at,text,author_id",
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        tweets = response.json().get("data", [])

        return [
            {
                "text": tweet["text"],
                "id": tweet["id"],
                "created_at": tweet["created_at"],
            }
            for tweet in tweets
        ]

    except requests.exceptions.HTTPError as errh:
        print(f"[TwitterAgent] HTTP Error: {errh}")
        print(f"Response content: {response.text}")
        return []
    except requests.exceptions.ConnectionError as errc:
        print(f"[TwitterAgent] Error Connecting: {errc}")
        return []
    except requests.exceptions.Timeout as errt:
        print(f"[TwitterAgent] Timeout Error: {errt}")
        return []
    except requests.exceptions.RequestException as err:
        print(f"[TwitterAgent] Error: {err}")
        return []
    except Exception as e:
        print("[TwitterAgent] Error:", e)
        return []
