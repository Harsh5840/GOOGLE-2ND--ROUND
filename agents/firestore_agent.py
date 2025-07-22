# agents/firestore_agent.py

import os
from google.cloud import firestore
from dotenv import load_dotenv
from shared.utils.logger import log_event

load_dotenv()

# Initialize Firestore
db = firestore.Client()

COLLECTION_NAME = os.getenv("FIREBASE_COLLECTION_NAME", "city_reports")

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
