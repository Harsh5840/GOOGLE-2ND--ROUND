import os
from typing import Dict, Any
import googlemaps
from shared.utils.logger import log_event
import traceback

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

def get_best_route(current_location: str, destination: str, mode: str = "driving") -> Dict[str, Any]:
    if not GOOGLE_MAPS_API_KEY:
        log_event("MapsTool", "GOOGLE_MAPS_API_KEY not set.")
        return {"error": "Google Maps API key not configured."}
    if not current_location or not str(current_location).strip():
        log_event("MapsTool", "get_best_route called with empty current_location.")
        return {"error": "Current location is required to find a route."}
    if not destination or not str(destination).strip():
        log_event("MapsTool", "get_best_route called with empty destination.")
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
        log_event("MapsTool", error_msg)
        return {"error": error_msg}

def get_must_visit_places_nearby(location: str, max_results: int = 3) -> list:
    if not GOOGLE_MAPS_API_KEY:
        log_event("MapsTool", "GOOGLE_MAPS_API_KEY not set.")
        return {"error": "Google Maps API key not set."}
    if not location or not location.strip():
        log_event("MapsTool", f"get_must_visit_places_nearby called with empty location: '{location}'")
        return {"error": "Location is required to find must-visit places."}
    try:
        log_event("MapsTool", f"Geocoding location: '{location}'")
        geocode = gmaps.geocode(location)
        log_event("MapsTool", f"Geocode result: {geocode}")
        if not geocode or not geocode[0].get("geometry"):
            log_event("MapsTool", f"Geocoding failed for location: '{location}'")
            return []
        lat = float(geocode[0]["geometry"]["location"]["lat"])
        lng = float(geocode[0]["geometry"]["location"]["lng"])
        log_event("MapsTool", f"places_nearby params: location=({lat}, {lng}), radius=1000")
        try:
            places = gmaps.places_nearby(
                location=(lat, lng),
                radius=1000,
                keyword='point of interest'
            )
        except Exception as e:
            log_event("MapsTool", f"places_nearby failed for '{location}': {e}")
            log_event("MapsTool", traceback.format_exc())
            try:
                log_event("MapsTool", "Trying fallback location: 'New York'")
                geocode_ny = gmaps.geocode("New York")
                if geocode_ny and geocode_ny[0].get("geometry"):
                    lat_ny = float(geocode_ny[0]["geometry"]["location"]["lat"])
                    lng_ny = float(geocode_ny[0]["geometry"]["location"]["lng"])
                    log_event("MapsTool", f"places_nearby params: location=({lat_ny}, {lng_ny}), radius=1000")
                    places_ny = gmaps.places_nearby(
                        location=(lat_ny, lng_ny),
                        radius=1000
                    )
                    log_event("MapsTool", f"places_nearby result for 'New York': {places_ny}")
            except Exception as e2:
                log_event("MapsTool", f"Fallback places_nearby failed: {e2}")
                log_event("MapsTool", traceback.format_exc())
            return []
        results = places.get("results", [])
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
        log_event("MapsTool", f"Error in get_must_visit_places_nearby: {e}")
        log_event("MapsTool", traceback.format_exc())
        log_event("MapsTool", f"Params: location='{location}'")
        return {"error": f"Exception occurred: {e}"} 