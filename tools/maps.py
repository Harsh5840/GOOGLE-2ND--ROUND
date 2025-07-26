import os
from typing import Dict, Any
import googlemaps
from shared.utils.logger import log_event
import traceback

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

def get_best_route(current_location: str, destination: str, mode: str = "driving") -> str:
    if not GOOGLE_MAPS_API_KEY:
        log_event("MapsTool", "GOOGLE_MAPS_API_KEY not set.")
        return "Google Maps API key not configured."
    if not current_location or not str(current_location).strip():
        log_event("MapsTool", "get_best_route called with empty current_location.")
        return "Current location is required to find a route."
    if not destination or not str(destination).strip():
        log_event("MapsTool", "get_best_route called with empty destination.")
        return "Destination is required to find a route."
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
            return "No route found."
        route = directions_result[0]
        leg = route["legs"][0]
        summary = route.get("summary", "N/A")
        distance = leg.get("distance", {}).get("text", "N/A")
        duration = leg.get("duration", {}).get("text", "N/A")
        start = leg.get("start_address", "N/A")
        end = leg.get("end_address", "N/A")
        return f"Best route from {start} to {end} via {summary}: {distance}, {duration}."
    except Exception as e:
        error_msg = f"Google Maps API error: {e}"
        log_event("MapsTool", error_msg)
        return error_msg

def get_must_visit_places_nearby(location: str, max_results: int = 3) -> str:
    if not GOOGLE_MAPS_API_KEY:
        log_event("MapsTool", "GOOGLE_MAPS_API_KEY not set.")
        return "Google Maps API key not set."
    if not location or not location.strip():
        log_event("MapsTool", f"get_must_visit_places_nearby called with empty location: '{location}'")
        return "Location is required to find must-visit places."
    try:
        log_event("MapsTool", f"Geocoding location: '{location}'")
        geocode = gmaps.geocode(location)
        log_event("MapsTool", f"Geocode result: {geocode}")
        if not geocode or not geocode[0].get("geometry"):
            log_event("MapsTool", f"Geocoding failed for location: '{location}'")
            return f"Could not geocode location: {location}."
        lat = float(geocode[0]["geometry"]["location"]["lat"])
        lng = float(geocode[0]["geometry"]["location"]["lng"])
        
        # Try multiple search strategies with different parameters
        search_strategies = [
            # Strategy 1: Tourist attractions with larger radius
            {
                "radius": 5000,
                "type": "tourist_attraction",
                "keyword": None
            },
            # Strategy 2: Points of interest with larger radius
            {
                "radius": 5000,
                "type": None,
                "keyword": "tourist attraction"
            },
            # Strategy 3: General places with very large radius
            {
                "radius": 10000,
                "type": None,
                "keyword": "landmark"
            },
            # Strategy 4: Fallback - any place with large radius
            {
                "radius": 15000,
                "type": None,
                "keyword": None
            }
        ]
        
        results = []
        for i, strategy in enumerate(search_strategies):
            log_event("MapsTool", f"Search strategy {i+1}: radius={strategy['radius']}, type={strategy['type']}, keyword={strategy['keyword']}")
            
            try:
                places_params = {
                    "location": (lat, lng),
                    "radius": strategy["radius"]
                }
                
                if strategy["type"]:
                    places_params["type"] = strategy["type"]
                if strategy["keyword"]:
                    places_params["keyword"] = strategy["keyword"]
                
                places = gmaps.places_nearby(**places_params)
                log_event("MapsTool", f"Strategy {i+1} results: {len(places.get('results', []))} places found")
                
                if places.get("results"):
                    results = places.get("results", [])
                    break
                    
            except Exception as e:
                log_event("MapsTool", f"Strategy {i+1} failed: {e}")
                continue
        
        if not results:
            # Try a text search as last resort
            try:
                log_event("MapsTool", "Trying text search as fallback")
                text_search = gmaps.places(f"tourist attractions in {location}")
                results = text_search.get("results", [])
                log_event("MapsTool", f"Text search results: {len(results)} places found")
            except Exception as e:
                log_event("MapsTool", f"Text search failed: {e}")
        
        if not results:
            return f"No must-visit places found near {location}. Try searching for a more specific area or landmark."
        
        # Sort by rating and popularity
        results = sorted(results, key=lambda x: (x.get("rating", 0), x.get("user_ratings_total", 0)), reverse=True)
        
        must_visit = []
        for place in results[:max_results]:
            name = place.get("name", "Unknown")
            rating = place.get("rating", "No rating")
            address = place.get("vicinity", "Address not available")
            must_visit.append(f"{name} (Rating: {rating}, Address: {address})")
        
        log_event("MapsTool", f"must_visit: {must_visit}")
        return f"Must-visit places near {location}: " + "; ".join(must_visit)
        
    except Exception as e:
        log_event("MapsTool", f"Error in get_must_visit_places_nearby: {e}")
        log_event("MapsTool", traceback.format_exc())
        log_event("MapsTool", f"Params: location='{location}'")
        return f"Exception occurred: {e}"

def color_location(location):
    pass
