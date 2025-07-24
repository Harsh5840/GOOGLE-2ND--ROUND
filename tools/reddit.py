import os
from dotenv import load_dotenv
from typing import Dict, Any
import praw
from shared.utils.logger import log_event

load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

def fetch_reddit_posts(subreddit: str, limit: int = 5) -> Dict[str, Any]:
    """
    Fetches top posts from a subreddit using PRAW.

    Args:
        subreddit (str): The subreddit to fetch posts from (e.g., "news").
        limit (int): The maximum number of posts to fetch (default is 5, max 100).

    Returns:
        dict: A dictionary containing a list of posts with 'title', 'id', 'author', 'created_utc'.
              Returns a dictionary with an 'error' key if an error occurs.
    """
    if not (REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET and REDDIT_USER_AGENT):
        log_event("RedditTool", "Error: Reddit credentials not set.")
        return {"error": "Reddit API credentials not configured."}

    # Ensure limit is always an integer
    try:
        limit = int(limit)
    except Exception:
        limit = 5

    actual_limit = min(limit, 100)
    try:
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT,
        )
        subreddit_obj = reddit.subreddit(subreddit)
        posts = []
        for post in subreddit_obj.hot(limit=actual_limit):
            posts.append({
                "title": post.title,
                "id": post.id,
                "author": str(post.author) if post.author else "N/A",
                "created_utc": post.created_utc,
                "url": post.url,
            })
        return {"posts": posts}
    except Exception as e:
        error_msg = f"Reddit API error: {e}"
        log_event("RedditTool", error_msg)
        return {"error": error_msg} 