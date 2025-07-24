import os
from dotenv import load_dotenv
from typing import Dict, Any
import tweepy
from shared.utils.logger import log_event

load_dotenv()

BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

def fetch_twitter_posts(location: str, topic: str, limit: int = 10) -> str:
    """
    Uses Twitter API v2 via Tweepy to search recent tweets based on location + topic.

    Args:
        location (str): The geographical location to search for tweets (e.g., "New Delhi").
        topic (str): The topic or keyword to search for (e.g., "cricket").
        limit (int): The maximum number of tweets to fetch (default is 2, max 100).

    Returns:
        dict: A dictionary containing a list of tweets with 'text', 'id', 'created_at', 'author_id'.
              Returns a dictionary with an 'error' key if an error occurs.
    """
    # Check all required credentials
    missing = []
    if not BEARER_TOKEN:
        missing.append("TWITTER_BEARER_TOKEN")
    if not CONSUMER_KEY:
        missing.append("TWITTER_CONSUMER_KEY")
    if not CONSUMER_SECRET:
        missing.append("TWITTER_CONSUMER_SECRET")
    if not ACCESS_TOKEN:
        missing.append("TWITTER_ACCESS_TOKEN")
    if not ACCESS_TOKEN_SECRET:
        missing.append("TWITTER_ACCESS_TOKEN_SECRET")
    if missing:
        log_event("TwitterTool", f"Error: Missing Twitter credentials: {', '.join(missing)}")
        return f"Twitter API credentials missing: {', '.join(missing)}"

    client = tweepy.Client(BEARER_TOKEN)

    actual_limit = min(limit, 100) # test carefully tho WARNING: tweepy only offers 100 searches

    query = f"{location} {topic} -is:retweet lang:en"  # Build the query string

    try:
        response = client.search_recent_tweets(
            query,
            max_results=actual_limit,
            tweet_fields=[
                "created_at",
                "author_id",
            ],
            expansions=["author_id"],  # To expand user data in the 'includes' field
        )

        tweets_data = response.data  # The actual list of Tweet objects FIX: check if none
        includes_data = response.includes  # Contains expanded data, e.g, user objects FIX: check if none

        processed_tweets = []
        if tweets_data:
            # Create a dictionary to quickly look up user info by author_id
            users_by_id = {}
            if includes_data and "users" in includes_data:
                users_by_id = {user["id"]: user["username"] for user in includes_data["users"]}

            for tweet in tweets_data:
                processed_tweets.append(
                    f"@{users_by_id.get(tweet.author_id, 'N/A')}: {tweet.text} (at {tweet.created_at})"
                )
        if not processed_tweets:
            return f"No recent tweets found for {location} about {topic}."
        return "Recent tweets: " + " | ".join(processed_tweets)

    except tweepy.TweepyException as e:
        if '429' in str(e) or 'Too Many Requests' in str(e):
            error_msg = "Twitter rate limit reached. Please try again in a few minutes."
        else:
            error_msg = f"Tweepy API Error: {e}"
        log_event("TwitterTool", error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        log_event("TwitterTool", error_msg)
        return error_msg 