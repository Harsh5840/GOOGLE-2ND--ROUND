import os
from google.cloud import firestore
from dotenv import load_dotenv
from shared.utils.logger import log_event

load_dotenv()

# Initialize Firestore
db = firestore.Client()

COLLECTION_NAME = os.getenv("FIREBASE_COLLECTION_NAME", "city_reports")

USER_HISTORY_COLLECTION = "user_query_history"

from datetime import datetime

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

def store_user_query_history(user_id: str, query: str, response_data: dict) -> bool:
    """
    Store a user's query, timestamp, and response data in Firestore.
    """
    try:
        doc = {
            "user_id": user_id,
            "query": query,
            "timestamp": datetime.utcnow().isoformat(),
            "response_data": response_data
        }
        db.collection(USER_HISTORY_COLLECTION).add(doc)
        return True
    except Exception as e:
        log_event("FirestoreAgent", f"Error storing user query history: {e}")
        return False

def fetch_similar_user_queries(user_id: str, query: str, limit: int = 5) -> list:
    """
    Fetch past queries for a user that are similar to the current query (basic substring match).
    """
    try:
        docs = db.collection(USER_HISTORY_COLLECTION).where("user_id", "==", user_id).stream()
        similar = []
        for doc in docs:
            d = doc.to_dict()
            if query.lower() in d.get("query", "").lower():
                similar.append(d)
            if len(similar) >= limit:
                break
        return similar
    except Exception as e:
        log_event("FirestoreAgent", f"Error fetching similar user queries: {e}")
        return []
