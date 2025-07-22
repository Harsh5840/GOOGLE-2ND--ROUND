import os
from dotenv import load_dotenv
from typing import Dict, Any
import tweepy
import vertexai
from vertexai.generative_models import (
    GenerativeModel,
    Tool,
    FunctionDeclaration,
    ToolConfig,
    Part,
)

load_dotenv()

BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")


def fetch_twitter_posts(location: str, topic: str, limit: int = 5) -> Dict[str, Any]:
    """
    Uses Twitter API v2 via Tweepy to search recent tweets based on location + topic.

    Args:
        location (str): The geographical location to search for tweets (e.g., "New Delhi").
        topic (str): The topic or keyword to search for (e.g., "cricket").
        limit (int): The maximum number of tweets to fetch (default is 5, max 100).

    Returns:
        dict: A dictionary containing a list of tweets with 'text', 'id', 'created_at', 'author_id'.
              Returns a dictionary with an 'error' key if an error occurs.
    """
    if not BEARER_TOKEN:
        print("[TwitterAgent] Error: TWITTER_BEARER_TOKEN not set.")
        return {"error": "Twitter API token not configured."}

    client = tweepy.Client(BEARER_TOKEN)

    actual_limit = min(limit, 100) # test carefully tho WARNING: tweepy only offers 100 searches

    query = f"{location} {topic} -is:retweet lang:en"  # Build the query string

    try:
        response = client.search_recent_tweets( #TODO: Maybe add user? -> gives includes.user()
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
                    {
                        "text": tweet.text,
                        "id": tweet.id,
                        "created_at": str(
                            tweet.created_at
                            ),  # WARNING: Convert datetime object to string
                        "author_id": tweet.author_id,
                        "author_username": users_by_id.get(
                            tweet.author_id, "N/A"
                        ),  # Get username
                    }
                )
        return {
            "tweets": processed_tweets
        }

    except tweepy.TweepyException as e:
        error_msg = f"Tweepy API Error: {e}"
        print(f"[TwitterAgent] {error_msg}")
        return {"error": error_msg}
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        print(f"[TwitterAgent] {error_msg}")
        return {"error": error_msg}


fetch_twitter_posts_tool_declaration = FunctionDeclaration(
    name="fetch_twitter_posts",
    description="Searches for recent posts on Twitter based on a location and a topic.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "location": {
                "type": "STRING",
                "description": "The geographical location to search for tweets (e.g., 'New Delhi', 'Gurugram').",
            },
            "topic": {
                "type": "STRING",
                "description": "The topic or keyword to search for (e.g., 'weather', 'traffic', 'sports').",
            },
            "limit": {
                "type": "INTEGER",
                "description": "The maximum number of tweets to fetch (optional, default is 5, max 100).",
            },
        },
        "required": ["location", "topic"],
    },
)

TWITTER_TOOLS = [
    Tool(function_declarations=[fetch_twitter_posts_tool_declaration]),
]

TOOL_FUNCTIONS = {
    "fetch_twitter_posts": fetch_twitter_posts,
}


# Wrapper class
class TwitterAgent:
    def __init__(self, project_id: str, region: str):
        vertexai.init(project=project_id, location=region)
        self.model = GenerativeModel(
            "gemini-1.5-flash",
            tools=TWITTER_TOOLS,
            tool_config=ToolConfig(
                function_calling_config=ToolConfig.FunctionCallingConfig(
                    mode=ToolConfig.FunctionCallingConfig.Mode.AUTO,
                ),
            ),
            system_instruction=[
                "You are a Twitter search assistant. Your primary goal is to find recent tweets.",
                "Always use the 'fetch_twitter_posts' tool when asked to find tweets.",
                "Summarize the retrieved tweets concisely, including the author's username if available.",
                "If the tool returns an error, inform the user about the error clearly.",
            ],
        )
        self.chat_session = self.model.start_chat()

    def process_query(self, query: str) -> str:
        """Processes a user query and returns a response, potentially using the Twitter tool."""
        print(f"DEBUG: TwitterAgent received query: {query}")
        response = self.chat_session.send_message(query)

        if response.candidates and response.candidates[0].function_calls:
            function_calls = response.candidates[0].function_calls
            tool_outputs = []
            for function_call in function_calls:
                function_name = function_call.name
                function_args = {k: v for k, v in function_call.args.items()}

                if function_name in TOOL_FUNCTIONS:
                    print(
                        f"DEBUG: TwitterAgent calling tool: {function_name} with args: {function_args}"
                    )
                    result = TOOL_FUNCTIONS[function_name](**function_args)
                    print(f"DEBUG: Tool output received: {result}")
                    tool_outputs.append(
                        Part.from_function_response(name=function_name, response=result)
                    )
                else:
                    error_msg = f"TwitterAgent: Unknown tool requested: {function_name}"
                    print(f"DEBUG: {error_msg}")
                    tool_outputs.append(
                        Part.from_function_response(
                            name=function_name, response={"error": error_msg}
                        )
                    )

            final_response = self.chat_session.send_message(tool_outputs)
            return final_response.text
        else:
            return response.text
