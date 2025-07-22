import os
from dotenv import load_dotenv
from typing import Dict, Any
import requests
import vertexai
from vertexai.generative_models import (
    GenerativeModel,
    Tool,
    FunctionDeclaration,
    ToolConfig,
    Part,
)
from shared.utils.logger import log_event

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")


def fetch_city_news(city: str, limit: int = 5) -> Dict[str, Any]:
    """
    Fetches news articles relevant to a specific city using NewsAPI.

    Args:
        city (str): The city to search news for.
        limit (int): The maximum number of articles to fetch (default 5, max 100).

    Returns:
        dict: A dictionary containing a list of articles with 'title', 'description', 'url', 'publishedAt'.
              Returns a dictionary with an 'error' key if an error occurs.
    """
    if not NEWS_API_KEY:
        log_event("NewsAgent", "NEWS_API_KEY not set.")
        return {"error": "News API key not configured."}

    actual_limit = min(limit, 100)
    url = (
        f"https://newsapi.org/v2/everything?q={requests.utils.quote(city)}"
        f"&pageSize={actual_limit}&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    )
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        if data.get("status") != "ok":
            return {"error": data.get("message", "Failed to fetch news.")}
        articles = [
            {
                "title": a.get("title"),
                "description": a.get("description"),
                "url": a.get("url"),
                "publishedAt": a.get("publishedAt"),
                "source": a.get("source", {}).get("name", "")
            }
            for a in data.get("articles", [])
        ]
        return {"articles": articles}
    except Exception as e:
        error_msg = f"News API error: {e}"
        log_event("NewsAgent", error_msg)
        return {"error": error_msg}

fetch_city_news_tool_declaration = FunctionDeclaration(
    name="fetch_city_news",
    description="Fetches news articles relevant to a specific city using NewsAPI.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "city": {
                "type": "STRING",
                "description": "The city to search news for (e.g., 'Bangalore', 'New York').",
            },
            "limit": {
                "type": "INTEGER",
                "description": "The maximum number of articles to fetch (optional, default is 5, max 100).",
            },
        },
        "required": ["city"],
    },
)

NEWS_TOOLS = [
    Tool(function_declarations=[fetch_city_news_tool_declaration]),
]

TOOL_FUNCTIONS = {
    "fetch_city_news": fetch_city_news,
}

class NewsAgent:
    def __init__(self, project_id: str, region: str):
        vertexai.init(project=project_id, location=region)
        self.model = GenerativeModel(
            "gemini-2.0-flash",
            tools=NEWS_TOOLS,
            tool_config=ToolConfig(
                function_calling_config=ToolConfig.FunctionCallingConfig(
                    mode=ToolConfig.FunctionCallingConfig.Mode.AUTO,
                ),
            ),
            system_instruction=[
                "You are a news assistant. Your primary goal is to find recent news articles relevant to a specific city.",
                "Always use the 'fetch_city_news' tool when asked for city news.",
                "Summarize the retrieved articles concisely, including the source and publication date if available.",
                "If the tool returns an error, inform the user about the error clearly.",
            ],
        )
        self.chat_session = self.model.start_chat()

    def process_query(self, query: str) -> str:
        log_event("NewsAgent", f"Received query: {query}")
        response = self.chat_session.send_message(query)

        if response.candidates and response.candidates[0].function_calls:
            function_calls = response.candidates[0].function_calls
            tool_outputs = []
            for function_call in function_calls:
                function_name = function_call.name
                function_args = {k: v for k, v in function_call.args.items()}

                if function_name in TOOL_FUNCTIONS:
                    log_event(
                        "NewsAgent",
                        f"Calling tool: {function_name} with args: {function_args}"
                    )
                    result = TOOL_FUNCTIONS[function_name](**function_args)
                    log_event("NewsAgent", f"Tool output received: {result}")
                    tool_outputs.append(
                        Part.from_function_response(name=function_name, response=result)
                    )
                else:
                    error_msg = f"NewsAgent: Unknown tool requested: {function_name}"
                    log_event("NewsAgent", error_msg)
                    tool_outputs.append(
                        Part.from_function_response(
                            name=function_name, response={"error": error_msg}
                        )
                    )

            final_response = self.chat_session.send_message(tool_outputs)
            return final_response.text
        else:
            return response.text
