import os
import requests
from urllib.parse import quote
from dotenv import load_dotenv


load_dotenv()

REDDIT_SUBREDDITS = os.getenv("REDDIT_SUBREDDITS", "bangalore,bengaluru").split(",")

def fetch_reddit_posts(location: str, topic: str, limit: int = 5) -> list:
    """
    Fetches Reddit posts related to a location/topic combination across configured subreddits.
    Uses Reddit's public search API.
    """
    headers = {"User-Agent": "CityPulseAI/1.0"}
    posts = []

    for subreddit in REDDIT_SUBREDDITS:
        query = quote(f"{location} {topic}")
        url = f"https://www.reddit.com/r/{subreddit}/search.json?q={query}&limit={limit}&sort=new&restrict_sr=1"

        try:
            res = requests.get(url, headers=headers, timeout=5)
            data = res.json()

            for post in data.get("data", {}).get("children", []):
                post_data = post["data"]
                posts.append({
                    "subreddit": subreddit,
                    "title": post_data.get("title"),
                    "url": f"https://reddit.com{post_data.get('permalink')}"
                })

        except Exception as e:
            print(f"[RedditAgent] Error fetching from r/{subreddit}:", e)

    return posts
