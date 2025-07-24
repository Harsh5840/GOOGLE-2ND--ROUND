import os
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
import traceback

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

# Log googlemaps version
try:
    import pkg_resources
    log_event("GoogleMapsAgent", f"googlemaps version: {pkg_resources.get_distribution('googlemaps').version}")
except Exception as e:
    log_event("GoogleMapsAgent", f"Could not determine googlemaps version: {e}")

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

    # Input validation
    if not current_location or not str(current_location).strip():
        log_event("GoogleMapsAgent", "get_best_route called with empty current_location.")
        return {"error": "Current location is required to find a route."}
    if not destination or not str(destination).strip():
        log_event("GoogleMapsAgent", "get_best_route called with empty destination.")
        return {"error": "Destination is required to find a route."}

    try:
        params = {
            "origin": current_location,
            "destination": destination,
            "mode": mode,
        }

        if mode == "driving":
            params["departure_time"] = "now"
            params["traffic_model"] = "best_guess"

        directions_result = gmaps.directions(**params)

        if not directions_result or not isinstance(directions_result, list) or not directions_result[0].get("legs"):
            return {"error": "No route found."}
        route = directions_result[0]
        leg = route["legs"][0]
        steps = [
            {
                "instruction": step.get("html_instructions", ""),
                "distance": step.get("distance", {}).get("text", "N/A"),
                "duration": step.get("duration", {}).get("text", "N/A"),
            }
            for step in leg.get("steps", [])
        ]
        return {
            "summary": route.get("summary", "N/A"),
            "distance": leg.get("distance", {}).get("text", "N/A"),
            "duration": leg.get("duration", {}).get("text", "N/A"),
            "duration_in_traffic": leg.get("duration_in_traffic", {}).get("text", "N/A"),
            "start_address": leg.get("start_address", "N/A"),
            "end_address": leg.get("end_address", "N/A"),
            "steps": steps,
        }
    except Exception as e:
        error_msg = f"Google Maps API error: {e}"
        log_event("GoogleMapsAgent", error_msg)
        return {"error": error_msg}

def get_must_visit_places_nearby(location: str, max_results: int = 3) -> list:
    """
    Uses Google Maps Places API to find top-rated places (any type) near a location.
    Returns a list of dicts with name, type, rating, address, place_id, photo_url, open_now.
    If location is empty, returns a dict with an 'error' key.
    """

    if not GOOGLE_MAPS_API_KEY:
        log_event("GoogleMapsAgent", "GOOGLE_MAPS_API_KEY not set.")
        return {"error": "Google Maps API key not set."}
    if not location or not location.strip():
        log_event("GoogleMapsAgent", f"get_must_visit_places_nearby called with empty location: '{location}'")
        return {"error": "Location is required to find must-visit places."}
    try:
        log_event("GoogleMapsAgent", f"Geocoding location: '{location}'")
        geocode = gmaps.geocode(location)
        log_event("GoogleMapsAgent", f"Geocode result: {geocode}")
        if not geocode or not geocode[0].get("geometry"):
            log_event("GoogleMapsAgent", f"Geocoding failed for location: '{location}'")
            return []
        lat = float(geocode[0]["geometry"]["location"]["lat"])
        lng = float(geocode[0]["geometry"]["location"]["lng"])
        log_event("GoogleMapsAgent", f"places_nearby params: location=({lat}, {lng}), radius=1000")
        # Only include required parameters, remove open_now for testing
        try:
            places = gmaps.places_nearby(
                location=(lat, lng),
                radius=1000,
                keyword='point of interest'  # <-- ADD THIS
            )
        except Exception as e:
            log_event("GoogleMapsAgent", f"places_nearby failed for '{location}': {e}")
            log_event("GoogleMapsAgent", traceback.format_exc())
            # Try a different location as a test
            try:
                log_event("GoogleMapsAgent", "Trying fallback location: 'New York'")
                geocode_ny = gmaps.geocode("New York")
                if geocode_ny and geocode_ny[0].get("geometry"):
                    lat_ny = float(geocode_ny[0]["geometry"]["location"]["lat"])
                    lng_ny = float(geocode_ny[0]["geometry"]["location"]["lng"])
                    log_event("GoogleMapsAgent", f"places_nearby params: location=({lat_ny}, {lng_ny}), radius=1000")
                    places_ny = gmaps.places_nearby(
                        location=(lat_ny, lng_ny),
                        radius=1000
                    )
                    log_event("GoogleMapsAgent", f"places_nearby result for 'New York': {places_ny}")
            except Exception as e2:
                log_event("GoogleMapsAgent", f"Fallback places_nearby failed: {e2}")
                log_event("GoogleMapsAgent", traceback.format_exc())
            return []
        results = places.get("results", [])
        # Sort by rating, then user_ratings_total
        results = sorted(results, key=lambda x: (x.get("rating", 0), x.get("user_ratings_total", 0)), reverse=True)
        must_visit = []
        for place in results[:max_results]:
            photo_url = None
            if place.get("photos"):
                photo_ref = place["photos"][0]["photo_reference"]
                photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={GOOGLE_MAPS_API_KEY}"
            must_visit.append({
                "name": place.get("name"),
                "type": place.get("types", [None])[0],
                "rating": place.get("rating"),
                "address": place.get("vicinity"),
                "place_id": place.get("place_id"),
                "photo_url": photo_url,
                "open_now": place.get("opening_hours", {}).get("open_now") if place.get("opening_hours") else None
            })
        return must_visit
    except Exception as e:
        log_event("GoogleMapsAgent", f"Error in get_must_visit_places_nearby: {e}")
        log_event("GoogleMapsAgent", traceback.format_exc())
        log_event("GoogleMapsAgent", f"Params: location='{location}'")
        return {"error": f"Exception occurred: {e}"}

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
