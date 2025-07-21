import os
import requests
from dotenv import load_dotenv

load_dotenv()

BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

import tweepy
from typing import List


def get_tweets(
    query: str,
    api_key: str,
    api_secret: str,
    access_token: str,
    access_token_secret: str,
) -> List[str]:
    """Fetch tweets matching a query."""
    try:
        auth = tweepy.OAuthHandler(
            api_key, api_secret, access_token, access_token_secret
        )
        api = tweepy.API(auth)
        tweets = api.search_tweets(q=query, lang="en", count=10)
        return [tweet.text for tweet in tweets]
    except Exception as e:
        return [f"Twitter API error: {e}"]


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

    except Exception as e:
        print("[TwitterAgent] Error:", e)
        return []
