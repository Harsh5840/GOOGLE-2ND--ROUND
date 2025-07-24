import asyncpraw #TODO: Fix async issue
import os
from shared.utils.logger import log_event

def normalize_subreddit(subreddit: str) -> str:
    s = subreddit.lower().replace(' ', '')
    if s in ("bengaluru", "bengalurucity", "bangalore", "bangalorecity"):
        return "bangalore"
    return subreddit

async def fetch_reddit_posts(subreddit: str, limit: int = 5) -> str:
    subreddit = normalize_subreddit(subreddit)
    log_event("RedditTool", f"Requested subreddit after normalization: {subreddit!r}")
    reddit = asyncpraw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT", "city-proj/1.0"),
    )
    posts = []
    try:
        subreddit_obj = await reddit.subreddit(subreddit)
        async for submission in subreddit_obj.hot(limit=limit):
            posts.append(submission.title)
        log_event("RedditTool", f"Fetched posts: {posts}")
    except Exception as e:
        log_event("RedditTool", f"Error: {e}")
        return f"Error fetching Reddit posts: {e}"
    if not posts:
        return f"No posts found for r/{subreddit}."
    return f"Top posts in r/{subreddit}:\n" + "\n".join(posts)

if __name__ == "__main__":
    import asyncio
    print("Testing fetch_reddit_posts('bengaluru'):")
    print(asyncio.run(fetch_reddit_posts("bengaluru")))
    print("Testing fetch_reddit_posts('bangalore'):")
    print(asyncio.run(fetch_reddit_posts("bangalore")))
    print("Testing fetch_reddit_posts('Bengaluru City'):")
    print(asyncio.run(fetch_reddit_posts("Bengaluru City"))) 
