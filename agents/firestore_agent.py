# agents/firestore_agent.py

import os
from google.cloud import firestore
from dotenv import load_dotenv
from shared.utils.logger import log_event
from typing import List, Dict, Any, Optional

load_dotenv()

# Initialize Firestore
db = firestore.Client()

COLLECTION_NAME = os.getenv("FIREBASE_COLLECTION_NAME", "city_reports")
TRAVEL_PREDICTION_COLLECTION = "travel_predictions"

def fetch_firestore_reports(location: str, topic: str, limit: int = 5) -> list:
    """
    Fetch user-submitted incident reports from Firestore.
    Uses the collection defined in FIREBASE_COLLECTION_NAME (.env).
    """
    try:
        reports_ref = (
            db.collection(COLLECTION_NAME)
              .where("location", "==", location)
              .where("topic", "==", topic)
              .order_by("timestamp", direction=firestore.Query.DESCENDING)
              .limit(limit)
        )
        docs = reports_ref.stream()
        return [
            {
                "description": doc.to_dict().get("description"),
                "timestamp": doc.to_dict().get("timestamp").isoformat()
            }
            for doc in docs
        ]
    except Exception as e:
        log_event("FirestoreAgent", f"Error fetching reports for {location}/{topic}: {e}")
        return []

def store_travel_time_record(
    route: str,
    datetime_str: str,
    travel_time_minutes: float,
    twitter_events: Optional[list] = None,
    reddit_events: Optional[list] = None,
    news_events: Optional[list] = None,
    google_search_events: Optional[list] = None,
    weather: Optional[str] = None
) -> bool:
    """
    Store a historical travel time record and associated event data for prediction.
    """
    try:
        doc = {
            "route": route,
            "datetime": datetime_str,
            "travel_time_minutes": travel_time_minutes,
            "twitter_events": twitter_events or [],
            "reddit_events": reddit_events or [],
            "news_events": news_events or [],
            "google_search_events": google_search_events or [],
            "weather": weather or ""
        }
        db.collection(TRAVEL_PREDICTION_COLLECTION).add(doc)
        return True
    except Exception as e:
        log_event("FirestoreAgent", f"Error storing travel time record: {e}")
        return False

def fetch_travel_time_records(
    route: str,
    weekday: int,
    hour: int,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Fetch historical travel time records for a route, filtered by weekday and hour.
    """
    try:
        # Firestore does not support extracting weekday/hour, so store them as fields if needed
        records_ref = (
            db.collection(TRAVEL_PREDICTION_COLLECTION)
              .where("route", "==", route)
              .where("weekday", "==", weekday)
              .where("hour", "==", hour)
              .order_by("datetime", direction=firestore.Query.DESCENDING)
              .limit(limit)
        )
        docs = records_ref.stream()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        log_event("FirestoreAgent", f"Error fetching travel time records: {e}")
        return []
