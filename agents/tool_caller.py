# agents/tool_caller.py

import requests

def fetch_reddit_posts(location: str, topic: str, limit: int = 5) -> list:
    """
    Fetches Reddit posts related to a city topic.
    You can replace this with PRAW or Pushshift later for richer data.
    """

    query = f"{location} {topic}".strip()
    headers = {"User-Agent": "CityBot/1.0"}
    url = f"https://www.reddit.com/search.json?q={query}&limit={limit}&sort=new"

    try:
        res = requests.get(url, headers=headers, timeout=5)
        data = res.json()
        posts = []

        for post in data.get("data", {}).get("children", []):
            post_data = post["data"]
            posts.append({
                "title": post_data.get("title"),
                "url": f"https://reddit.com{post_data.get('permalink')}"
            })

        return posts

    except Exception as e:
        print("[RedditAgent] Error fetching posts:", e)
        return []
