import os
from google.cloud import firestore
from dotenv import load_dotenv
from shared.utils.logger import log_event
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json

load_dotenv()

db = firestore.Client()
COLLECTION_NAME = os.getenv("FIREBASE_COLLECTION_NAME", "city_reports")
USER_HISTORY_COLLECTION = "user_query_history"
USER_PROFILES_COLLECTION = "user_profiles"
LOCATION_HISTORY_COLLECTION = "location_history"
UNIFIED_DATA_COLLECTION = "unified_data"
EVENT_PHOTOS_COLLECTION = "event_photos"

# User Profile Management
def create_or_update_user_profile(user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create or update a user profile with preferences and settings"""
    try:
        user_ref = db.collection(USER_PROFILES_COLLECTION).document(user_id)
        
        # Get existing profile or create new one
        existing_doc = user_ref.get()
        if existing_doc.exists:
            existing_data = existing_doc.to_dict()
            # Merge with existing data, keeping existing fields if not provided
            merged_data = {**existing_data, **profile_data}
            merged_data['last_updated'] = datetime.utcnow().isoformat()
        else:
            merged_data = {
                **profile_data,
                'created_at': datetime.utcnow().isoformat(),
                'last_updated': datetime.utcnow().isoformat(),
                'preferences': profile_data.get('preferences', {
                    'default_location': None,
                    'favorite_locations': [],
                    'notification_settings': {
                        'email': True,
                        'push': True,
                        'frequency': 'daily'
                    },
                    'map_settings': {
                        'default_zoom': 12,
                        'default_center': None,
                        'show_traffic': True,
                        'show_events': True
                    }
                })
            }
        
        user_ref.set(merged_data)
        log_event("FirestoreTool", f"User profile updated for {user_id}")
        return {"success": True, "profile": merged_data}
        
    except Exception as e:
        log_event("FirestoreTool", f"Error creating/updating user profile for {user_id}: {e}")
        return {"success": False, "error": str(e)}

def get_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user profile by user ID"""
    try:
        user_ref = db.collection(USER_PROFILES_COLLECTION).document(user_id)
        doc = user_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None
    except Exception as e:
        log_event("FirestoreTool", f"Error getting user profile for {user_id}: {e}")
        return None

def get_user_default_location(user_id: str) -> Optional[Dict[str, float]]:
    """Get user's default location for maps and other functions"""
    try:
        profile = get_user_profile(user_id)
        if profile and profile.get('preferences', {}).get('default_location'):
            return profile['preferences']['default_location']
        
        # Fallback: get most recent location from history
        recent_location = get_recent_user_location(user_id)
        if recent_location:
            # Update user profile with this location as default
            create_or_update_user_profile(user_id, {
                'preferences': {
                    'default_location': recent_location
                }
            })
            return recent_location
        
        return None
    except Exception as e:
        log_event("FirestoreTool", f"Error getting default location for {user_id}: {e}")
        return None

# Location History Management
def store_user_location(user_id: str, latitude: float, longitude: float, 
                       location_name: Optional[str] = None, 
                       activity_type: Optional[str] = None) -> Dict[str, Any]:
    """Store user location history"""
    try:
        location_data = {
            "user_id": user_id,
            "latitude": latitude,
            "longitude": longitude,
            "location_name": location_name,
            "activity_type": activity_type,
            "timestamp": datetime.utcnow().isoformat(),
            "coordinates": firestore.GeoPoint(latitude, longitude)
        }
        
        db.collection(LOCATION_HISTORY_COLLECTION).add(location_data)
        log_event("FirestoreTool", f"Location stored for user {user_id}: {latitude}, {longitude}")
        return {"success": True, "location": location_data}
        
    except Exception as e:
        log_event("FirestoreTool", f"Error storing location for {user_id}: {e}")
        return {"success": False, "error": str(e)}

def get_recent_user_location(user_id: str, hours: int = 24) -> Optional[Dict[str, float]]:
    """Get user's most recent location within specified hours"""
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        locations_ref = (
            db.collection(LOCATION_HISTORY_COLLECTION)
              .where("user_id", "==", user_id)
              .where("timestamp", ">=", cutoff_time.isoformat())
              .order_by("timestamp", direction=firestore.Query.DESCENDING)
              .limit(1)
        )
        
        docs = list(locations_ref.stream())
        if docs:
            location_data = docs[0].to_dict()
            return {
                "latitude": location_data["latitude"],
                "longitude": location_data["longitude"]
            }
        return None
        
    except Exception as e:
        log_event("FirestoreTool", f"Error getting recent location for {user_id}: {e}")
        return None

def get_user_location_history(user_id: str, days: int = 7) -> List[Dict[str, Any]]:
    """Get user's location history for specified number of days"""
    try:
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        locations_ref = (
            db.collection(LOCATION_HISTORY_COLLECTION)
              .where("user_id", "==", user_id)
              .where("timestamp", ">=", cutoff_time.isoformat())
              .order_by("timestamp", direction=firestore.Query.DESCENDING)
        )
        
        docs = locations_ref.stream()
        return [doc.to_dict() for doc in docs]
        
    except Exception as e:
        log_event("FirestoreTool", f"Error getting location history for {user_id}: {e}")
        return []

def get_favorite_locations(user_id: str) -> List[Dict[str, Any]]:
    """Get user's favorite locations"""
    try:
        profile = get_user_profile(user_id)
        if profile and profile.get('preferences', {}).get('favorite_locations'):
            return profile['preferences']['favorite_locations']
        return []
    except Exception as e:
        log_event("FirestoreTool", f"Error getting favorite locations for {user_id}: {e}")
        return []

def add_favorite_location(user_id: str, latitude: float, longitude: float, 
                         location_name: str) -> Dict[str, Any]:
    """Add a location to user's favorites"""
    try:
        profile = get_user_profile(user_id)
        current_favorites = profile.get('preferences', {}).get('favorite_locations', []) if profile else []
        
        new_favorite = {
            "latitude": latitude,
            "longitude": longitude,
            "location_name": location_name,
            "added_at": datetime.utcnow().isoformat()
        }
        
        # Check if location already exists
        for favorite in current_favorites:
            if (abs(favorite['latitude'] - latitude) < 0.001 and 
                abs(favorite['longitude'] - longitude) < 0.001):
                return {"success": False, "error": "Location already in favorites"}
        
        current_favorites.append(new_favorite)
        
        create_or_update_user_profile(user_id, {
            'preferences': {
                'favorite_locations': current_favorites
            }
        })
        
        return {"success": True, "favorite": new_favorite}
        
    except Exception as e:
        log_event("FirestoreTool", f"Error adding favorite location for {user_id}: {e}")
        return {"success": False, "error": str(e)}

# Unified Data Storage
def store_unified_data(location: str, data_type: str, data: Dict[str, Any], 
                      user_id: Optional[str] = None) -> Dict[str, Any]:
    """Store unified data from various sources (Twitter, Reddit, News, etc.)"""
    try:
        unified_data = {
            "location": location,
            "data_type": data_type,  # 'twitter', 'reddit', 'news', 'maps', 'aggregated'
            "data": data,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "processed": True
        }
        
        db.collection(UNIFIED_DATA_COLLECTION).add(unified_data)
        log_event("FirestoreTool", f"Unified data stored for {location}, type: {data_type}")
        return {"success": True, "data_id": unified_data.get("id")}
        
    except Exception as e:
        log_event("FirestoreTool", f"Error storing unified data for {location}: {e}")
        return {"success": False, "error": str(e)}

def get_unified_data(location: str, data_type: Optional[str] = None, 
                    hours: int = 24) -> List[Dict[str, Any]]:
    """Get unified data for a location within specified hours"""
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        query = (
            db.collection(UNIFIED_DATA_COLLECTION)
              .where("location", "==", location)
              .where("timestamp", ">=", cutoff_time.isoformat())
              .order_by("timestamp", direction=firestore.Query.DESCENDING)
        )
        
        if data_type:
            query = query.where("data_type", "==", data_type)
        
        docs = query.stream()
        return [doc.to_dict() for doc in docs]
        
    except Exception as e:
        log_event("FirestoreTool", f"Error getting unified data for {location}: {e}")
        return []

def get_aggregated_location_data(location: str, hours: int = 24) -> Dict[str, Any]:
    """Get aggregated data from all sources for a location"""
    try:
        all_data = get_unified_data(location, hours=hours)
        
        aggregated = {
            "location": location,
            "timestamp": datetime.utcnow().isoformat(),
            "data_sources": {},
            "summary": {
                "total_mentions": 0,
                "sentiment_score": 0,
                "top_topics": [],
                "recent_events": []
            }
        }
        
        for data_item in all_data:
            data_type = data_item.get("data_type")
            if data_type not in aggregated["data_sources"]:
                aggregated["data_sources"][data_type] = []
            aggregated["data_sources"][data_type].append(data_item["data"])
        
        return aggregated
        
    except Exception as e:
        log_event("FirestoreTool", f"Error getting aggregated data for {location}: {e}")
        return {"error": str(e)}

# Enhanced Event Photos Storage
def store_event_photo_firestore(photo_data: Dict[str, Any]) -> Dict[str, Any]:
    """Store event photo metadata in Firestore"""
    try:
        photo_data["stored_at"] = datetime.utcnow().isoformat()
        photo_data["firestore_id"] = photo_data.get("id")  # Keep original ID
        
        db.collection(EVENT_PHOTOS_COLLECTION).document(photo_data["id"]).set(photo_data)
        log_event("FirestoreTool", f"Event photo stored in Firestore: {photo_data['id']}")
        return {"success": True, "photo_id": photo_data["id"]}
        
    except Exception as e:
        log_event("FirestoreTool", f"Error storing event photo in Firestore: {e}")
        return {"success": False, "error": str(e)}

def get_user_event_photos(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Get all event photos uploaded by a specific user"""
    try:
        photos_ref = (
            db.collection(EVENT_PHOTOS_COLLECTION)
              .where("user_id", "==", user_id)
              .order_by("upload_timestamp", direction=firestore.Query.DESCENDING)
              .limit(limit)
        )
        
        docs = photos_ref.stream()
        return [doc.to_dict() for doc in docs]
        
    except Exception as e:
        log_event("FirestoreTool", f"Error getting user event photos for {user_id}: {e}")
        return []

def get_location_event_photos(latitude: float, longitude: float, 
                            radius_km: float = 5.0, limit: int = 50) -> List[Dict[str, Any]]:
    """Get event photos within a radius of specified coordinates"""
    try:
        # Simple bounding box approximation (for production, use proper geospatial queries)
        lat_degree = radius_km / 111.0  # Approximate km per degree latitude
        lng_degree = radius_km / (111.0 * abs(latitude / 90.0))  # Approximate km per degree longitude
        
        photos_ref = (
            db.collection(EVENT_PHOTOS_COLLECTION)
              .where("latitude", ">=", latitude - lat_degree)
              .where("latitude", "<=", latitude + lat_degree)
              .where("longitude", ">=", longitude - lng_degree)
              .where("longitude", "<=", longitude + lng_degree)
              .order_by("upload_timestamp", direction=firestore.Query.DESCENDING)
              .limit(limit)
        )
        
        docs = photos_ref.stream()
        return [doc.to_dict() for doc in docs]
        
    except Exception as e:
        log_event("FirestoreTool", f"Error getting location event photos: {e}")
        return []

# Enhanced Query History
def store_user_query_history(user_id: str, query: str, response_data: dict, 
                           location: Optional[str] = None) -> str:
    """Enhanced user query history storage with location tracking"""
    try:
        doc = {
            "user_id": user_id,
            "query": query,
            "location": location,
            "timestamp": datetime.utcnow().isoformat(),
            "response_data": response_data,
            "query_type": "general"  # Can be extended to categorize queries
        }
        db.collection(USER_HISTORY_COLLECTION).add(doc)
        
        # Update user's last activity
        create_or_update_user_profile(user_id, {
            "last_activity": datetime.utcnow().isoformat(),
            "last_query": query
        })
        
        return "Success"
    except Exception as e:
        log_event("FirestoreTool", f"Error storing user query history: {e}")
        return f"Error storing user query history: {e}"

def get_user_query_history(user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Get user's query history"""
    try:
        history_ref = (
            db.collection(USER_HISTORY_COLLECTION)
              .where("user_id", "==", user_id)
              .order_by("timestamp", direction=firestore.Query.DESCENDING)
              .limit(limit)
        )
        
        docs = history_ref.stream()
        return [doc.to_dict() for doc in docs]
        
    except Exception as e:
        log_event("FirestoreTool", f"Error getting user query history for {user_id}: {e}")
        return []

# Legacy functions (keeping for backward compatibility)
def fetch_firestore_reports(location: str, topic: str, limit: int = 5) -> str:
    try:
        reports_ref = (
            db.collection(COLLECTION_NAME)
              .where("location", "==", location)
              .where("topic", "==", topic)
              .order_by("timestamp", direction=firestore.Query.DESCENDING)
              .limit(limit)
        )
        docs = reports_ref.stream()
        results = [
            f"{doc.to_dict().get('description')} (at {doc.to_dict().get('timestamp').isoformat()})"
            for doc in docs
        ]
        if not results:
            return f"No reports found for {location} on {topic}."
        return f"Reports for {location} on {topic}: " + " | ".join(results)
    except Exception as e:
        log_event("FirestoreTool", f"Error fetching reports for {location}/{topic}: {e}")
        return f"Error fetching reports: {e}"

def fetch_similar_user_queries(user_id: str, query: str, limit: int = 5) -> str:
    try:
        docs = db.collection(USER_HISTORY_COLLECTION).where("user_id", "==", user_id).stream()
        similar = []
        for doc in docs:
            d = doc.to_dict()
            if query.lower() in d.get("query", "").lower():
                similar.append(f"{d.get('query')} (at {d.get('timestamp')})")
            if len(similar) >= limit:
                break
        if not similar:
            return f"No similar queries found for user {user_id}."
        return f"Similar queries for user {user_id}: " + " | ".join(similar)
    except Exception as e:
        log_event("FirestoreTool", f"Error fetching similar user queries: {e}")
        return f"Error fetching similar user queries: {e}" 