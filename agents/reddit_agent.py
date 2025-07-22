import os
from dotenv import load_dotenv
from typing import Dict, Any
import praw
import vertexai
from vertexai.generative_models import (
    GenerativeModel,
    Tool,
    FunctionDeclaration,
    ToolConfig,
    Part,
)

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
        print("[RedditAgent] Error: Reddit credentials not set.")
        return {"error": "Reddit API credentials not configured."}

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
        print(f"[RedditAgent] {error_msg}")
        return {"error": error_msg}

fetch_reddit_posts_tool_declaration = FunctionDeclaration(
    name="fetch_reddit_posts",
    description="Fetches top posts from a subreddit on Reddit.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "subreddit": {
                "type": "STRING",
                "description": "The subreddit to fetch posts from (e.g., 'news', 'technology').",
            },
            "limit": {
                "type": "INTEGER",
                "description": "The maximum number of posts to fetch (optional, default is 5, max 100).",
            },
        },
        "required": ["subreddit"],
    },
)

REDDIT_TOOLS = [
    Tool(function_declarations=[fetch_reddit_posts_tool_declaration]),
]

TOOL_FUNCTIONS = {
    "fetch_reddit_posts": fetch_reddit_posts,
}

class RedditAgent:
    def __init__(self, project_id: str, region: str):
        vertexai.init(project=project_id, location=region)
        self.model = GenerativeModel(
            "gemini-2.0-flash",
            tools=REDDIT_TOOLS,
            tool_config=ToolConfig(
                function_calling_config=ToolConfig.FunctionCallingConfig(
                    mode=ToolConfig.FunctionCallingConfig.Mode.AUTO,
                ),
            ),
            system_instruction=[
                "You are a Reddit search assistant. Your primary goal is to find top posts from subreddits.",
                "Always use the 'fetch_reddit_posts' tool when asked to find Reddit posts.",
                "Summarize the retrieved posts concisely, including the author's username if available.",
                "If the tool returns an error, inform the user about the error clearly.",
            ],
        )
        self.chat_session = self.model.start_chat()

    def process_query(self, query: str) -> str:
        """Processes a user query and returns a response, potentially using the Reddit tool."""
        print(f"DEBUG: RedditAgent received query: {query}")
        response = self.chat_session.send_message(query)

        if response.candidates and response.candidates[0].function_calls:
            function_calls = response.candidates[0].function_calls
            tool_outputs = []
            for function_call in function_calls:
                function_name = function_call.name
                function_args = {k: v for k, v in function_call.args.items()}

                if function_name in TOOL_FUNCTIONS:
                    print(
                        f"DEBUG: RedditAgent calling tool: {function_name} with args: {function_args}"
                    )
                    result = TOOL_FUNCTIONS[function_name](**function_args)
                    print(f"DEBUG: Tool output received: {result}")
                    tool_outputs.append(
                        Part.from_function_response(name=function_name, response=result)
                    )
                else:
                    error_msg = f"RedditAgent: Unknown tool requested: {function_name}"
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
