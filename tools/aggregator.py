import os
from ..agents import reddit_agent

api_key = os.environ.get("GOOGLE_API_KEY")

def reddit_wrapper(wrap: bool, name: str, id: str, secret: str, user_agent: str):
    if wrap:
        return reddit_agent.get_reddit_posts(name, id, secret, user_agent)
