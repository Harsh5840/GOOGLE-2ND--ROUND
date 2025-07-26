import os
from typing import Dict, Any, List, Tuple, Optional
import googlemaps
from shared.utils.logger import log_event
import traceback
from datetime import datetime

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

def get_best_route(current_location: str, destination: str, mode: str = "driving") -> Dict[str, Any]:
    """
    Get the best route between two locations with mood map integration.
    Returns route information and mood data for both origin and destination.
    """
    if not GOOGLE_MAPS_API_KEY:
        log_event("MapsTool", "GOOGLE_MAPS_API_KEY not set.")
        return {
            "success": False,
            "error": "Google Maps API key not configured.",
            "route_info": None,
            "mood_data": None,
            "locations_to_display": []
        }
    
    if not current_location or not str(current_location).strip():
        log_event("MapsTool", "get_best_route called with empty current_location.")
        return {
            "success": False,
            "error": "Current location is required to find a route.",
            "route_info": None,
            "mood_data": None,
            "locations_to_display": []
        }
    
    if not destination or not str(destination).strip():
        log_event("MapsTool", "get_best_route called with empty destination.")
        return {
            "success": False,
            "error": "Destination is required to find a route.",
            "route_info": None,
            "mood_data": None,
            "locations_to_display": []
        }
    
    try:
        # Get route information
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
            return {
                "success": False,
                "error": "No route found.",
                "route_info": None,
                "mood_data": None,
                "locations_to_display": []
            }
        
        route = directions_result[0]
        leg = route["legs"][0]
        summary = route.get("summary", "N/A")
        distance = leg.get("distance", {}).get("text", "N/A")
        duration = leg.get("duration", {}).get("text", "N/A")
        start = leg.get("start_address", "N/A")
        end = leg.get("end_address", "N/A")
        
        route_info = f"Best route from {start} to {end} via {summary}: {distance}, {duration}."
        
        # Get mood data for both locations
        mood_data = {
            "origin": get_location_mood_data(current_location),
            "destination": get_location_mood_data(destination)
        }
        
        # Prepare locations to display on frontend map
        locations_to_display = []
        
        # Add origin location
        origin_coords = get_location_coordinates(current_location)
        if origin_coords:
            locations_to_display.append({
                "type": "origin",
                "name": current_location,
                "address": start,
                "latitude": origin_coords["lat"],
                "longitude": origin_coords["lng"],
                "mood": mood_data["origin"]
            })
        
        # Add destination location
        dest_coords = get_location_coordinates(destination)
        if dest_coords:
            locations_to_display.append({
                "type": "destination",
                "name": destination,
                "address": end,
                "latitude": dest_coords["lat"],
                "longitude": dest_coords["lng"],
                "mood": mood_data["destination"]
            })
        
        # Add route waypoints if available
        if route.get("legs") and route["legs"][0].get("steps"):
            for i, step in enumerate(route["legs"][0]["steps"][::5]):  # Every 5th step to avoid too many points
                if step.get("end_location"):
                    locations_to_display.append({
                        "type": "waypoint",
                        "name": f"Waypoint {i+1}",
                        "address": step.get("end_address", ""),
                        "latitude": step["end_location"]["lat"],
                        "longitude": step["end_location"]["lng"],
                        "mood": None  # Waypoints don't have mood data
                    })
        
        return {
            "success": True,
            "route_info": route_info,
            "mood_data": mood_data,
            "locations_to_display": locations_to_display,
            "route_details": {
                "summary": summary,
                "distance": distance,
                "duration": duration,
                "start_address": start,
                "end_address": end,
                "mode": mode
            }
        }
        
    except Exception as e:
        error_msg = f"Google Maps API error: {e}"
        log_event("MapsTool", error_msg)
        return {
            "success": False,
            "error": error_msg,
            "route_info": None,
            "mood_data": None,
            "locations_to_display": []
        }

def get_must_visit_places_nearby(location: str, max_results: int = 3) -> Dict[str, Any]:
    """
    Get must-visit places near a location with mood map integration.
    Returns places information and mood data for the location.
    """
    if not GOOGLE_MAPS_API_KEY:
        log_event("MapsTool", "GOOGLE_MAPS_API_KEY not set.")
        return {
            "success": False,
            "error": "Google Maps API key not set.",
            "places": [],
            "mood_data": None,
            "locations_to_display": []
        }
    
    if not location or not location.strip():
        log_event("MapsTool", f"get_must_visit_places_nearby called with empty location: '{location}'")
        return {
            "success": False,
            "error": "Location is required to find must-visit places.",
            "places": [],
            "mood_data": None,
            "locations_to_display": []
        }
    
    try:
        log_event("MapsTool", f"Geocoding location: '{location}'")
        geocode = gmaps.geocode(location)
        log_event("MapsTool", f"Geocode result: {geocode}")
        
        if not geocode or not geocode[0].get("geometry"):
            log_event("MapsTool", f"Geocoding failed for location: '{location}'")
            return {
                "success": False,
                "error": f"Could not geocode location: {location}.",
                "places": [],
                "mood_data": None,
                "locations_to_display": []
            }
        
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
            return {
                "success": False,
                "error": f"No must-visit places found near {location}. Try searching for a more specific area or landmark.",
                "places": [],
                "mood_data": None,
                "locations_to_display": []
            }
        
        # Sort by rating and popularity
        results = sorted(results, key=lambda x: (x.get("rating", 0), x.get("user_ratings_total", 0)), reverse=True)
        
        # Get mood data for the main location
        mood_data = get_location_mood_data(location)
        
        # Prepare places list and locations to display
        places_list = []
        locations_to_display = []
        
        # Add main location
        locations_to_display.append({
            "type": "main_location",
            "name": location,
            "address": geocode[0].get("formatted_address", location),
            "latitude": lat,
            "longitude": lng,
            "mood": mood_data
        })
        
        # Add must-visit places
        for place in results[:max_results]:
            name = place.get("name", "Unknown")
            rating = place.get("rating", "No rating")
            address = place.get("vicinity", "Address not available")
            place_lat = place.get("geometry", {}).get("location", {}).get("lat")
            place_lng = place.get("geometry", {}).get("location", {}).get("lng")
            
            places_list.append(f"{name} (Rating: {rating}, Address: {address})")
            
            if place_lat and place_lng:
                # Get mood data for each place
                place_mood = get_location_mood_data(f"{name}, {address}")
                locations_to_display.append({
                    "type": "must_visit",
                    "name": name,
                    "address": address,
                    "latitude": place_lat,
                    "longitude": place_lng,
                    "rating": rating,
                    "mood": place_mood
                })
        
        log_event("MapsTool", f"must_visit: {places_list}")
        
        return {
            "success": True,
            "places": places_list,
            "mood_data": mood_data,
            "locations_to_display": locations_to_display,
            "summary": f"Must-visit places near {location}: " + "; ".join(places_list)
        }
        
    except Exception as e:
        log_event("MapsTool", f"Error in get_must_visit_places_nearby: {e}")
        log_event("MapsTool", traceback.format_exc())
        log_event("MapsTool", f"Params: location='{location}'")
        return {
            "success": False,
            "error": f"Exception occurred: {e}",
            "places": [],
            "mood_data": None,
            "locations_to_display": []
        }

def get_location_coordinates(location: str) -> Optional[Dict[str, float]]:
    """
    Get coordinates for a location string.
    """
    try:
        geocode = gmaps.geocode(location)
        if geocode and geocode[0].get("geometry", {}).get("location"):
            return geocode[0]["geometry"]["location"]
        return None
    except Exception as e:
        log_event("MapsTool", f"Error getting coordinates for {location}: {e}")
        return None

def get_location_mood_data(location: str) -> Dict[str, Any]:
    """
    Get mood data for a specific location.
    This integrates with the mood analysis system.
    """
    try:
        # Import here to avoid circular imports
        from shared.utils.mood import aggregate_mood
        from tools.firestore import get_unified_data_from_firestore
        
        # Get unified data for the location (don't force refresh to avoid infinite loops)
        unified_data_list = get_unified_data_from_firestore(location, hours=24, force_refresh=False)
        
        if unified_data_list:
            # Convert list of documents to the format expected by aggregate_mood
            unified_data = {}
            for doc in unified_data_list:
                data_type = doc.get("data_type", "unknown")
                data_content = doc.get("data", {})
                
                # Extract the actual data content based on data type
                if data_type == "twitter":
                    unified_data["twitter"] = data_content.get("posts", [])
                elif data_type == "reddit":
                    unified_data["reddit"] = data_content.get("posts", [])
                elif data_type == "news":
                    unified_data["news"] = data_content.get("articles", [])
                elif data_type == "google_search":
                    unified_data["google_search"] = data_content.get("results", [])
                elif data_type == "maps":
                    unified_data["maps"] = data_content
                elif data_type == "rag":
                    unified_data["rag"] = data_content.get("results", [])
            
            # Aggregate mood from the unified data
            mood_result = aggregate_mood(unified_data)
            return {
                "location": location,
                "timestamp": datetime.utcnow().isoformat(),
                **mood_result
            }
        else:
            # Return default mood data if no unified data available
            log_event("MapsTool", f"No unified data available for {location}, returning neutral mood")
            return {
                "location": location,
                "timestamp": datetime.utcnow().isoformat(),
                "mood_label": "neutral",
                "mood_score": 0.0,
                "events": [],
                "source_breakdown": {
                    "twitter": {"score": 0.0, "top_keywords": []},
                    "reddit": {"score": 0.0, "top_keywords": []},
                    "news": {"score": 0.0, "top_keywords": []},
                    "google_search": {"score": 0.0, "top_keywords": []},
                    "maps": {"score": 0.0, "top_keywords": []},
                }
            }
    except Exception as e:
        log_event("MapsTool", f"Error getting mood data for {location}: {e}")
        return {
            "location": location,
            "timestamp": datetime.utcnow().isoformat(),
            "mood_label": "neutral",
            "mood_score": 0.0,
            "events": [],
            "source_breakdown": {
                "twitter": {"score": 0.0, "top_keywords": []},
                "reddit": {"score": 0.0, "top_keywords": []},
                "news": {"score": 0.0, "top_keywords": []},
                "google_search": {"score": 0.0, "top_keywords": []},
                "maps": {"score": 0.0, "top_keywords": []},
            }
        }

def display_locations_on_map(locations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Prepare location data for frontend map display.
    This function formats location data with mood information for the frontend.
    """
    try:
        formatted_locations = []
        
        for location in locations:
            formatted_location = {
                "id": f"{location['type']}_{location['name']}_{location['latitude']}_{location['longitude']}",
                "type": location["type"],
                "name": location["name"],
                "address": location.get("address", ""),
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "mood": location.get("mood", {}),
                "rating": location.get("rating"),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add type-specific styling
            if location["type"] == "origin":
                formatted_location["icon"] = "🚀"
                formatted_location["color"] = "#10b981"  # Green
            elif location["type"] == "destination":
                formatted_location["icon"] = "🎯"
                formatted_location["color"] = "#ef4444"  # Red
            elif location["type"] == "must_visit":
                formatted_location["icon"] = "⭐"
                formatted_location["color"] = "#f59e0b"  # Amber
            elif location["type"] == "waypoint":
                formatted_location["icon"] = "📍"
                formatted_location["color"] = "#3b82f6"  # Blue
            else:
                formatted_location["icon"] = "📍"
                formatted_location["color"] = "#6b7280"  # Gray
            
            formatted_locations.append(formatted_location)
        
        return {
            "success": True,
            "locations": formatted_locations,
            "count": len(formatted_locations),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        log_event("MapsTool", f"Error formatting locations for map display: {e}")
        return {
            "success": False,
            "error": str(e),
            "locations": [],
            "count": 0,
            "timestamp": datetime.utcnow().isoformat()
        }

def color_location(location):
    pass
