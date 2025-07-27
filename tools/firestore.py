import os
from google.cloud import firestore
from google.oauth2 import service_account
from dotenv import load_dotenv
from shared.utils.logger import log_event
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from agents.agglomerator import aggregate_api_results
import json

load_dotenv()

def initialize_firestore():
    """Initialize Firestore client with proper error handling"""
    try:
        # Method 1: Service account JSON file path
        firebase_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
        if firebase_path and os.path.exists(firebase_path):
            log_event("FirestoreTool", f"Using service account file: {firebase_path}")
            credentials = service_account.Credentials.from_service_account_file(firebase_path)
            return firestore.Client(credentials=credentials)
            
        # Method 2: Service account JSON content
        firebase_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
        if firebase_json:
            try:
                log_event("FirestoreTool", "Using service account JSON from environment variable")
                credentials = service_account.Credentials.from_service_account_info(json.loads(firebase_json))
                return firestore.Client(credentials=credentials)
            except json.JSONDecodeError as e:
                log_event("FirestoreTool", f"Invalid JSON in FIREBASE_SERVICE_ACCOUNT_JSON: {e}")
                return None
            except Exception as e:
                log_event("FirestoreTool", f"Error parsing service account JSON: {e}")
                return None
                
        # Method 3: Default credentials (GOOGLE_APPLICATION_CREDENTIALS)
        google_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if google_creds and os.path.exists(google_creds):
            log_event("FirestoreTool", f"Using default credentials: {google_creds}")
            return firestore.Client()
            
        # Method 4: Default credentials without file
        log_event("FirestoreTool", "Using default credentials (GOOGLE_APPLICATION_CREDENTIALS)")
        return firestore.Client()
        
    except FileNotFoundError as e:
        log_event("FirestoreTool", f"Service account file not found: {e}")
        return None
    except PermissionError as e:
        log_event("FirestoreTool", f"Permission denied accessing service account file: {e}")
        return None
    except Exception as e:
        log_event("FirestoreTool", f"Failed to initialize Firestore: {e}")
        return None

# Initialize Firestore client
db = initialize_firestore()

if db is None:
    log_event("FirestoreTool", "WARNING: Firestore client initialization failed. Some features may not work.")
    # Create a dummy client to prevent crashes
    class DummyFirestoreClient:
        def collection(self, name):
            return DummyCollection()
    
    class DummyCollection:
        def document(self, name):
            return DummyDocument()
        def where(self, field, op, value):
            return DummyQuery()
        def stream(self):
            return []
        def order_by(self, field, direction=None):
            return self
    
    class DummyDocument:
        def get(self):
            return DummyDocumentSnapshot()
        def set(self, data):
            return None
        def update(self, data):
            return None
        def delete(self):
            return None
    
    class DummyDocumentSnapshot:
        def exists(self):
            return False
        def to_dict(self):
            return {}
    
    class DummyQuery:
        def stream(self):
            return []
        def limit(self, count):
            return self
    
    db = DummyFirestoreClient()

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
        exports_ref = db.collection(USER_DATA_EXPORTS_COLLECTION).where("user_id", "==", user_id).order_by("export_timestamp", direction=firestore.Query.DESCENDING)
        
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
        
        # Use original .where() syntax for compatibility
        recent_ref = db.collection(LOCATION_HISTORY_COLLECTION).where("user_id", "==", user_id).where("timestamp", ">=", cutoff_time.isoformat()).order_by("timestamp", direction=firestore.Query.DESCENDING).limit(1)
        
        docs = recent_ref.stream()
        for doc in docs:
            data = doc.to_dict()
            return {
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude")
            }
        
        return None
        
    except Exception as e:
        log_event("FirestoreTool", f"Error getting recent location for {user_id}: {e}")
        return None

def get_user_location_history(user_id: str, days: int = 7) -> List[Dict[str, Any]]:
    """Get user's location history for the specified number of days"""
    try:
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        # Use original .where() syntax for compatibility
        history_ref = db.collection(LOCATION_HISTORY_COLLECTION).where("user_id", "==", user_id).where("timestamp", ">=", cutoff_time.isoformat()).order_by("timestamp", direction=firestore.Query.DESCENDING)
        
        docs = history_ref.stream()
        history = [doc.to_dict() for doc in docs]
        
        return history
        
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

# Unified Data Management with Firestore as Primary Source
def load_unified_data_to_firestore(location: str, data_sources: List[str] = None) -> Dict[str, Any]:
    """
    Load unified data from various sources into Firestore for a specific location.
    This function fetches data from APIs and stores it in Firestore for later retrieval.
    """
    try:
        if data_sources is None:
            data_sources = ['reddit', 'twitter', 'news', 'maps', 'rag']
        
        unified_data = {}
        timestamp = datetime.utcnow().isoformat()
        
        # Load Reddit data
        if 'reddit' in data_sources:
            try:
                from tools.reddit import fetch_reddit_posts
                import asyncio
                
                # Use location as subreddit name, normalize it for Reddit
                subreddit_name = location.lower().replace(' ', '')
                if subreddit_name in ["bengaluru", "bangalore"]:
                    subreddit_name = "bangalore"
                elif subreddit_name in ["newyork", "newyorkcity"]:
                    subreddit_name = "nyc"
                elif subreddit_name in ["london"]:
                    subreddit_name = "london"
                else:
                    subreddit_name = "news"  # fallback to general news
                
                # Handle async call properly
                try:
                    reddit_data = asyncio.run(fetch_reddit_posts(subreddit=subreddit_name, limit=10))
                except RuntimeError:
                    # If there's already an event loop running, use a different approach
                    loop = asyncio.get_event_loop()
                    reddit_data = loop.run_until_complete(fetch_reddit_posts(subreddit=subreddit_name, limit=10))
                
                if reddit_data:
                    store_unified_data(location, "reddit", {
                        "data": reddit_data,
                        "source": "reddit",
                        "timestamp": timestamp,
                        "location": location
                    })
                    unified_data['reddit'] = reddit_data
                    log_event("FirestoreTool", f"Loaded Reddit data for {location}")
            except Exception as e:
                log_event("FirestoreTool", f"Error loading Reddit data for {location}: {e}")
        
        # Load Twitter data
        if 'twitter' in data_sources:
            try:
                from tools.twitter import fetch_twitter_posts
                twitter_data = fetch_twitter_posts(location=location, topic="city events", limit=10)
                if twitter_data:
                    store_unified_data(location, "twitter", {
                        "data": twitter_data,
                        "source": "twitter",
                        "timestamp": timestamp,
                        "location": location
                    })
                    unified_data['twitter'] = twitter_data
                    log_event("FirestoreTool", f"Loaded Twitter data for {location}")
            except Exception as e:
                log_event("FirestoreTool", f"Error loading Twitter data for {location}: {e}")
        
        # Load News data
        if 'news' in data_sources:
            try:
                from tools.news import fetch_city_news
                news_data = fetch_city_news(city=location, limit=5)
                if news_data:
                    store_unified_data(location, "news", {
                        "data": news_data,
                        "source": "news",
                        "timestamp": timestamp,
                        "location": location
                    })
                    unified_data['news'] = news_data
                    log_event("FirestoreTool", f"Loaded News data for {location}")
            except Exception as e:
                log_event("FirestoreTool", f"Error loading News data for {location}: {e}")
        
        # Load Maps data
        if 'maps' in data_sources:
            try:
                from tools.maps import get_must_visit_places_nearby
                maps_data = get_must_visit_places_nearby(location, max_results=10)
                if maps_data:
                    store_unified_data(location, "maps", {
                        "data": maps_data,
                        "source": "maps",
                        "timestamp": timestamp,
                        "location": location
                    })
                    unified_data['maps'] = maps_data
                    log_event("FirestoreTool", f"Loaded Maps data for {location}")
            except Exception as e:
                log_event("FirestoreTool", f"Error loading Maps data for {location}: {e}")
        
        # Load RAG data (if available)
        if 'rag' in data_sources:
            try:
                from tools.rag import query_rag_system
                rag_data = query_rag_system(f"events and activities in {location}")
                if rag_data:
                    store_unified_data(location, "rag", {
                        "data": rag_data,
                        "source": "rag",
                        "timestamp": timestamp,
                        "location": location
                    })
                    unified_data['rag'] = rag_data
                    log_event("FirestoreTool", f"Loaded RAG data for {location}")
            except Exception as e:
                log_event("FirestoreTool", f"Error loading RAG data for {location}: {e}")
        
        # Store aggregated data
        if unified_data:
            store_unified_data(location, "aggregated", {
                "data": unified_data,
                "sources": list(unified_data.keys()),
                "timestamp": timestamp,
                "location": location,
                "total_sources": len(unified_data)
            })
            log_event("FirestoreTool", f"Stored aggregated unified data for {location}")
        
        return {
            "success": True,
            "location": location,
            "sources_loaded": list(unified_data.keys()),
            "timestamp": timestamp,
            "data": unified_data
        }
        
    except Exception as e:
        log_event("FirestoreTool", f"Error loading unified data to Firestore for {location}: {e}")
        return {"success": False, "error": str(e)}

def get_unified_data_from_firestore(location: str, data_type: Optional[str] = None,
                                   hours: int = 24, force_refresh: bool = False, 
                                   _recursion_depth: int = 0) -> List[Dict[str, Any]]:
    """
    Get unified data from Firestore. If force_refresh is True or data is stale,
    it will reload data from sources first.
    """
    # Prevent infinite recursion
    if _recursion_depth > 1:
        log_event("FirestoreTool", f"Preventing infinite recursion for {location}, returning empty data")
        return []
    
    try:
        # Check if we need to refresh data
        if force_refresh:
            load_unified_data_to_firestore(location)

        # Get data from Firestore using simple queries to avoid composite index requirements
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        # Get all documents for the location and filter in memory
        data_ref = db.collection(UNIFIED_DATA_COLLECTION).where("location", "==", location)

        docs = data_ref.stream()
        all_data = [doc.to_dict() for doc in docs]

        # Filter by timestamp and data_type in memory
        filtered_data = []
        for doc in all_data:
            doc_timestamp = datetime.fromisoformat(doc.get("timestamp", "1970-01-01T00:00:00"))
            if doc_timestamp >= cutoff_time:
                if data_type is None or doc.get("data_type") == data_type:
                    filtered_data.append(doc)

        # Sort by timestamp (most recent first)
        filtered_data.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        # If no recent data and not forcing refresh, try to load fresh data (but only once)
        if not filtered_data and not force_refresh and _recursion_depth == 0:
            log_event("FirestoreTool", f"No recent data found for {location}, loading fresh data")
            load_result = load_unified_data_to_firestore(location)
            if load_result["success"]:
                # Try to get the data again, but increment recursion depth
                return get_unified_data_from_firestore(location, data_type, hours, force_refresh=False, _recursion_depth=_recursion_depth + 1)

        return filtered_data

    except Exception as e:
        log_event("FirestoreTool", f"Error getting unified data from Firestore for {location}: {e}")
        return []

def get_aggregated_location_data_from_firestore(location: str, hours: int = 24) -> Dict[str, Any]:
    """
    Get aggregated location data from Firestore, combining all data sources.
    """
    try:
        # Get aggregated data first
        aggregated_data = get_unified_data_from_firestore(location, "aggregated", hours)
        
        if aggregated_data:
            # Return the most recent aggregated data
            latest_aggregated = aggregated_data[0]
            return {
                "success": True,
                "location": location,
                "timestamp": latest_aggregated.get("timestamp"),
                "sources": latest_aggregated.get("sources", []),
                "total_sources": latest_aggregated.get("total_sources", 0),
                "data": latest_aggregated.get("data", {})
            }
        else:
            # If no aggregated data, try to load fresh data
            load_result = load_unified_data_to_firestore(location)
            if load_result["success"]:
                return get_aggregated_location_data_from_firestore(location, hours)
            else:
                return {
                    "success": False,
                    "location": location,
                    "error": "No data available and failed to load fresh data"
                }
        
    except Exception as e:
        log_event("FirestoreTool", f"Error getting aggregated location data from Firestore for {location}: {e}")
        return {
            "success": False,
            "location": location,
            "error": str(e)
        }

def refresh_unified_data_for_location(location: str, data_sources: List[str] = None) -> Dict[str, Any]:
    """
    Force refresh unified data for a specific location by loading fresh data from all sources.
    """
    try:
        result = load_unified_data_to_firestore(location, data_sources)
        if result["success"]:
            log_event("FirestoreTool", f"Successfully refreshed unified data for {location}")
        return result
    except Exception as e:
        log_event("FirestoreTool", f"Error refreshing unified data for {location}: {e}")
        return {"success": False, "error": str(e)}

def get_unified_data_sources_for_location(location: str) -> List[str]:
    """
    Get list of available data sources for a location from Firestore.
    """
    try:
        data = get_unified_data_from_firestore(location, hours=168)  # Last 7 days
        sources = set()
        for item in data:
            if item.get("data_type") != "aggregated":
                sources.add(item.get("data_type", ""))
        return list(sources)
    except Exception as e:
        log_event("FirestoreTool", f"Error getting data sources for {location}: {e}")
        return []

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
    """
    Get unified data for a location within specified hours.
    This function now uses Firestore as the primary source and will load data if needed.
    """
    try:
        # Use the new Firestore-based function
        return get_unified_data_from_firestore(location, data_type, hours, force_refresh=False)
        
    except Exception as e:
        log_event("FirestoreTool", f"Error getting unified data for {location}: {e}")
        return []

def get_aggregated_location_data(location: str, hours: int = 24) -> Dict[str, Any]:
    """
    Get aggregated data from all sources for a location.
    This function now uses Firestore as the primary source and will load data if needed.
    """
    try:
        # Use the new Firestore-based function
        return get_aggregated_location_data_from_firestore(location, hours)
        
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
        photos_ref = db.collection(EVENT_PHOTOS_COLLECTION).where("user_id", "==", user_id).order_by("upload_timestamp", direction=firestore.Query.DESCENDING).limit(limit)
        
        docs = photos_ref.stream()
        return [doc.to_dict() for doc in docs]
        
    except Exception as e:
        log_event("FirestoreTool", f"Error getting user event photos for {user_id}: {e}")
        return []

def get_location_event_photos(latitude: float, longitude: float, 
                            radius_km: float = 5.0, limit: int = 50) -> List[Dict[str, Any]]:
    """Get event photos within a radius of the specified location"""
    try:
        # Convert radius from km to degrees (approximate)
        lat_degree = radius_km / 111.0  # 1 degree latitude ≈ 111 km
        lng_degree = radius_km / (111.0 * abs(latitude / 90.0))  # Adjust for longitude
        
        # Use original .where() syntax for compatibility
        photos_ref = db.collection(EVENT_PHOTOS_COLLECTION).where("latitude", ">=", latitude - lat_degree).where("latitude", "<=", latitude + lat_degree).where("longitude", ">=", longitude - lng_degree).where("longitude", "<=", longitude + lng_degree).order_by("upload_timestamp", direction=firestore.Query.DESCENDING).limit(limit)
        
        docs = photos_ref.stream()
        photos = []
        for doc in docs:
            photo_data = doc.to_dict()
            # Add file URL for frontend access
            photo_data["file_url"] = f"/uploads/event_photos/{photo_data.get('filename', '')}"
            photos.append(photo_data)
        
        return photos
        
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
        # Get all documents for the user and sort in memory to avoid composite index requirement
        history_ref = db.collection(USER_HISTORY_COLLECTION).where("user_id", "==", user_id)

        docs = history_ref.stream()
        history = [doc.to_dict() for doc in docs]

        # Sort by timestamp in descending order (most recent first)
        history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        # Return limited results
        return history[:limit]

    except Exception as e:
        log_event("FirestoreTool", f"Error getting user query history for {user_id}: {e}")
        return []

# Legacy functions (keeping for backward compatibility)
def fetch_firestore_reports(location: str, topic: str, limit: int = 5) -> str:
    """Fetch reports from Firestore based on location and topic"""
    try:
        # This would typically query a reports collection
        # For now, return a placeholder response
        log_event("FirestoreTool", f"Fetching reports for location: {location}, topic: {topic}")
        return f"Reports for {topic} in {location}: No reports found in database."
    except Exception as e:
        log_event("FirestoreTool", f"Error fetching reports: {e}")
        return f"Error fetching reports: {e}"

def fetch_similar_user_queries(user_id: str, query: str, limit: int = 5) -> str:
    """Fetch similar queries from user's query history"""
    try:
        # Get user's query history
        history = get_user_query_history(user_id, limit=50)
        
        # Simple similarity check (in production, use proper NLP)
        similar_queries = []
        query_lower = query.lower()
        
        for hist_query in history:
            hist_text = hist_query.get("query", "").lower()
            # Check if queries share common words
            query_words = set(query_lower.split())
            hist_words = set(hist_text.split())
            
            if query_words & hist_words:  # Intersection
                similar_queries.append(hist_query.get("query", ""))
        
        if similar_queries:
            return f"Similar queries to '{query}':\n" + "\n".join(similar_queries[:limit])
        else:
            return f"No similar queries found for '{query}'"
            
    except Exception as e:
        log_event("FirestoreTool", f"Error fetching similar queries: {e}")
        return f"Error fetching similar queries: {e}"

def clear_empty_cached_data(location: str, data_type: str) -> bool:
    """Clear empty or invalid cached data from Firestore"""
    try:
        # Get all data for the location and type
        data_ref = db.collection(UNIFIED_DATA_COLLECTION).where("location", "==", location)
        docs = data_ref.stream()

        deleted_count = 0
        for doc in docs:
            doc_data = doc.to_dict()
            if doc_data.get("data_type") == data_type:
                # Check if data is empty or invalid
                data_content = doc_data.get("data", {})
                is_empty = False

                if data_type == "maps":
                    places = data_content.get("places", [])
                    # Check for empty places
                    is_empty = not places or len(places) == 0 or all(place.strip() == "" for place in places)

                    # Check for error messages in places
                    if not is_empty and places:
                        error_indicators = [
                            "no must-visit places found",
                            "no places found",
                            "could not find",
                            "error",
                            "exception",
                            "not found"
                        ]
                        places_text = " ".join(places).lower()
                        is_empty = any(indicator in places_text for indicator in error_indicators)

                elif data_type == "news":
                    articles = data_content.get("articles", [])
                    is_empty = not articles or len(articles) == 0

                    # Check for error messages in articles
                    if not is_empty and articles:
                        error_indicators = ["error", "exception", "not found", "no articles found"]
                        articles_text = " ".join(articles).lower()
                        is_empty = any(indicator in articles_text for indicator in error_indicators)

                elif data_type == "reddit":
                    posts = data_content.get("posts", [])
                    is_empty = not posts or len(posts) == 0

                    # Check for error messages in posts
                    if not is_empty and posts:
                        error_indicators = ["error", "exception", "not found", "no posts found"]
                        posts_text = " ".join(posts).lower()
                        is_empty = any(indicator in posts_text for indicator in error_indicators)

                if is_empty:
                    doc.reference.delete()
                    deleted_count += 1
                    log_event("FirestoreTool", f"Deleted empty/invalid cached data for {location}, type: {data_type}")

        if deleted_count > 0:
            log_event("FirestoreTool", f"Cleared {deleted_count} empty/invalid cached entries for {location}, type: {data_type}")

        return True

    except Exception as e:
        log_event("FirestoreTool", f"Error clearing empty cached data for {location}, type {data_type}: {e}")
        return False 
