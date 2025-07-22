import os
from dotenv import load_dotenv
from typing import Dict, Any
import googlemaps
import vertexai
from vertexai.generative_models import (
    GenerativeModel,
    Tool,
    FunctionDeclaration,
    ToolConfig,
    Part,
)
from shared.utils.logger import log_event
import requests

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
GOOGLE_SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

def get_best_route(current_location: str, destination: str, mode: str = "driving") -> Dict[str, Any]:
    """
    Uses Google Maps Directions API to find the best route between two locations, considering current traffic.

    Args:
        current_location (str): The starting point (address or lat,lng).
        destination (str): The destination point (address or lat,lng).
        mode (str): Mode of transport (default: 'driving').

    Returns:
        dict: Route summary, duration (with and without traffic), distance, and step-by-step directions.
              Returns a dictionary with an 'error' key if an error occurs.
    """
    if not GOOGLE_MAPS_API_KEY:
        log_event("GoogleMapsAgent", "GOOGLE_MAPS_API_KEY not set.")
        return {"error": "Google Maps API key not configured."}

    try:
        gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
        directions_result = gmaps.directions(
            origin=current_location,
            destination=destination,
            mode=mode,
            departure_time="now",
            traffic_model="best_guess",
        )
        if not directions_result:
            return {"error": "No route found."}
        route = directions_result[0]
        leg = route["legs"][0]
        steps = [
            {
                "instruction": step["html_instructions"],
                "distance": step["distance"]["text"],
                "duration": step["duration"]["text"],
            }
            for step in leg["steps"]
        ]
        return {
            "summary": route.get("summary", "N/A"),
            "distance": leg["distance"]["text"],
            "duration": leg["duration"]["text"],
            "duration_in_traffic": leg.get("duration_in_traffic", {}).get("text", "N/A"),
            "start_address": leg["start_address"],
            "end_address": leg["end_address"],
            "steps": steps,
        }
    except Exception as e:
        error_msg = f"Google Maps API error: {e}"
        log_event("GoogleMapsAgent", error_msg)
        return {"error": error_msg}

get_best_route_tool_declaration = FunctionDeclaration(
    name="get_best_route",
    description="Finds the best route between two locations using Google Maps, considering current traffic.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "current_location": {
                "type": "STRING",
                "description": "The starting point (address or lat,lng).",
            },
            "destination": {
                "type": "STRING",
                "description": "The destination point (address or lat,lng).",
            },
            "mode": {
                "type": "STRING",
                "description": "Mode of transport (e.g., 'driving', 'walking', 'bicycling', 'transit'). Optional, default is 'driving'.",
            },
        },
        "required": ["current_location", "destination"],
    },
)

GOOGLEMAPS_TOOLS = [
    Tool(function_declarations=[get_best_route_tool_declaration]),
]

TOOL_FUNCTIONS = {
    "get_best_route": get_best_route,
}

class GoogleMapsAgent:
    def __init__(self, project_id: str, region: str):
        vertexai.init(project=project_id, location=region)
        self.model = GenerativeModel(
            "gemini-2.0-flash",
            tools=GOOGLEMAPS_TOOLS,
            tool_config=ToolConfig(
                function_calling_config=ToolConfig.FunctionCallingConfig(
                    mode=ToolConfig.FunctionCallingConfig.Mode.AUTO,
                ),
            ),
            system_instruction=[
                "You are a navigation assistant. Your primary goal is to find the best route between two locations, considering current traffic.",
                "Always use the 'get_best_route' tool when asked for directions or routes.",
                "Summarize the route, including estimated time, distance, and key steps.",
                "If the tool returns an error, inform the user about the error clearly.",
            ],
        )
        self.chat_session = self.model.start_chat()

    def process_query(self, query: str) -> str:
        """Processes a user query and returns a response, potentially using the Google Maps tool."""
        log_event("GoogleMapsAgent", f"Received query: {query}")
        response = self.chat_session.send_message(query)

        if response.candidates and response.candidates[0].function_calls:
            function_calls = response.candidates[0].function_calls
            tool_outputs = []
            for function_call in function_calls:
                function_name = function_call.name
                function_args = {k: v for k, v in function_call.args.items()}

                if function_name in TOOL_FUNCTIONS:
                    log_event(
                        "GoogleMapsAgent",
                        f"Calling tool: {function_name} with args: {function_args}"
                    )
                    result = TOOL_FUNCTIONS[function_name](**function_args)
                    log_event("GoogleMapsAgent", f"Tool output received: {result}")
                    tool_outputs.append(
                        Part.from_function_response(name=function_name, response=result)
                    )
                else:
                    error_msg = f"GoogleMapsAgent: Unknown tool requested: {function_name}"
                    log_event("GoogleMapsAgent", error_msg)
                    tool_outputs.append(
                        Part.from_function_response(
                            name=function_name, response={"error": error_msg}
                        )
                    )

            final_response = self.chat_session.send_message(tool_outputs)
            return final_response.text
        else:
            return response.text 
