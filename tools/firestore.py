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
USER_DATA_EXPORTS_COLLECTION = "user_data_exports"

# User Profile Management with Enhanced Retention
def create_or_update_user_profile(user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create or update a user profile with enhanced data retention features"""
    try:
        user_ref = db.collection(USER_PROFILES_COLLECTION).document(user_id)
        
        # Get existing profile or create new one
        existing_doc = user_ref.get()
        if existing_doc.exists:
            existing_data = existing_doc.to_dict()
            # Merge with existing data, preserving all existing fields
            merged_data = {**existing_data, **profile_data}
            merged_data['last_updated'] = datetime.utcnow().isoformat()
            merged_data['data_version'] = existing_data.get('data_version', 1) + 1
            
            # Preserve important retention fields
            if 'created_at' not in merged_data:
                merged_data['created_at'] = existing_data.get('created_at')
            if 'first_login' not in merged_data:
                merged_data['first_login'] = existing_data.get('first_login')
        else:
            merged_data = {
                **profile_data,
                'created_at': datetime.utcnow().isoformat(),
                'first_login': datetime.utcnow().isoformat(),
                'last_updated': datetime.utcnow().isoformat(),
                'data_version': 1,
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
                    },
                    'data_retention': {
                        'keep_history_days': 365,
                        'auto_backup': True,
                        'export_frequency': 'monthly'
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

# Data Export/Import for User Retention
def export_user_data(user_id: str) -> Dict[str, Any]:
    """Export all user data for backup and retention"""
    try:
        export_data = {
            "export_timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "profile": get_user_profile(user_id),
            "query_history": get_user_query_history(user_id, limit=1000),
            "location_history": get_user_location_history(user_id, days=365),
            "favorite_locations": get_favorite_locations(user_id),
            "event_photos": get_user_event_photos(user_id, limit=1000),
            "unified_data": []  # Get user-specific unified data
        }
        
        # Store export record
        export_id = f"{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        db.collection(USER_DATA_EXPORTS_COLLECTION).document(export_id).set({
            "export_id": export_id,
            "user_id": user_id,
            "export_timestamp": datetime.utcnow().isoformat(),
            "data_size": len(json.dumps(export_data)),
            "record_count": sum(len(v) if isinstance(v, list) else 1 for v in export_data.values())
        })
        
        log_event("FirestoreTool", f"User data exported for {user_id}: {export_id}")
        return {"success": True, "export_id": export_id, "data": export_data}
        
    except Exception as e:
        log_event("FirestoreTool", f"Error exporting user data for {user_id}: {e}")
        return {"success": False, "error": str(e)}

def get_user_data_exports(user_id: str) -> List[Dict[str, Any]]:
    """Get user's data export history"""
    try:
        exports_ref = (
            db.collection(USER_DATA_EXPORTS_COLLECTION)
              .where("user_id", "==", user_id)
              .order_by("export_timestamp", direction=firestore.Query.DESCENDING)
        )
        
        docs = exports_ref.stream()
        return [doc.to_dict() for doc in docs]
        
    except Exception as e:
        log_event("FirestoreTool", f"Error getting user data exports for {user_id}: {e}")
        return []

def restore_user_data(user_id: str, backup_data: Dict[str, Any]) -> Dict[str, Any]:
    """Restore user data from backup"""
    try:
        # Validate backup data
        if not backup_data.get('user_id') or backup_data['user_id'] != user_id:
            return {"success": False, "error": "Invalid backup data for user"}
        
        # Restore profile
        if backup_data.get('profile'):
            create_or_update_user_profile(user_id, backup_data['profile'])
        
        # Restore location history
        if backup_data.get('location_history'):
            for location in backup_data['location_history']:
                store_user_location(
                    user_id=user_id,
                    latitude=location['latitude'],
                    longitude=location['longitude'],
                    location_name=location.get('location_name'),
                    activity_type=location.get('activity_type')
                )
        
        # Restore favorite locations
        if backup_data.get('favorite_locations'):
            for fav in backup_data['favorite_locations']:
                add_favorite_location(
                    user_id=user_id,
                    latitude=fav['latitude'],
                    longitude=fav['longitude'],
                    location_name=fav['location_name']
                )
        
        log_event("FirestoreTool", f"User data restored for {user_id}")
        return {"success": True, "message": "User data restored successfully"}
        
    except Exception as e:
        log_event("FirestoreTool", f"Error restoring user data for {user_id}: {e}")
        return {"success": False, "error": str(e)}

# Enhanced Data Retention Analytics
def get_user_retention_analytics(user_id: str) -> Dict[str, Any]:
    """Get analytics about user data retention and usage"""
    try:
        profile = get_user_profile(user_id)
        query_history = get_user_query_history(user_id, limit=1000)
        location_history = get_user_location_history(user_id, days=365)
        
        unique_locations = len(set(
            f"{loc['latitude']},{loc['longitude']}" 
            for loc in location_history
        ))
        
        analytics = {
            "user_id": user_id,
            "profile_created": profile.get('created_at') if profile else None,
            "total_queries": len(query_history),
            "unique_locations_visited": unique_locations,
            "total_photos_uploaded": len(get_user_event_photos(user_id, limit=1000)),
            "favorite_locations_count": len(get_favorite_locations(user_id)),
            "last_activity": profile.get('last_activity') if profile else None,
            "data_version": profile.get('data_version', 1) if profile else 1,
            "retention_score": calculate_retention_score(user_id, profile, query_history)
        }
        
        return {"success": True, "analytics": analytics}
        
    except Exception as e:
        log_event("FirestoreTool", f"Error getting retention analytics for {user_id}: {e}")
        return {"success": False, "error": str(e)}

def calculate_retention_score(user_id: str, profile: Optional[Dict], queries: List[Dict]) -> float:
    """Calculate a retention score based on user activity"""
    try:
        if not profile:
            return 0.0
        
        score = 0.0
        
        # Query activity (higher is better)
        score += min(len(queries) * 0.5, 30)  # Max 30 points
        
        # Location diversity (higher is better)
        unique_locations = len(set(
            f"{loc['latitude']},{loc['longitude']}" 
            for loc in get_user_location_history(user_id, days=365)
        ))
        score += min(unique_locations * 2, 25)  # Max 25 points
        
        # Photo uploads (higher is better)
        photo_count = len(get_user_event_photos(user_id, limit=1000))
        score += min(photo_count * 1.5, 20)  # Max 20 points
        
        # Recent activity (higher is better)
        if profile.get('last_activity'):
            days_since_last_activity = (datetime.utcnow() - datetime.fromisoformat(profile['last_activity'])).days
            if days_since_last_activity <= 7:
                score += 25  # Active in last week
            elif days_since_last_activity <= 30:
                score += 15  # Active in last month
            elif days_since_last_activity <= 90:
                score += 5   # Active in last quarter
        
        return min(score, 100.0)  # Cap at 100
        
    except Exception as e:
        log_event("FirestoreTool", f"Error calculating retention score for {user_id}: {e}")
        return 0.0

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