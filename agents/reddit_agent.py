from typing import List
import praw

def get_reddit_posts(
    subreddit_name: str, client_id: str, client_secret: str, user_agent: str
) -> List[str]:
    """Fetch top posts from a subreddit."""
    try:
        reddit = praw.Reddit(
            client_id=client_id, client_secret=client_secret, user_agent=user_agent
        )
        subreddit = reddit.subreddit(subreddit_name)
        return [post.title for post in subreddit.hot(limit=10)]
    except Exception as e:
        return [f"Reddit API error: {e}"]
