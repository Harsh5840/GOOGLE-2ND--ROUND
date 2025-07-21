# agents/firestore_agent.py

from google.cloud import firestore

db = firestore.Client()

def fetch_firestore_reports(location: str, topic: str, limit: int = 5) -> list:
    """
    Fetch user-submitted incident reports from Firestore.
    Assumes collection is named 'city_reports' with fields:
    - location: str
    - topic: str
    - description: str
    - timestamp: datetime
    """

    try:
        reports_ref = db.collection("city_reports") \
                        .where("location", "==", location) \
                        .where("topic", "==", topic) \
                        .order_by("timestamp", direction=firestore.Query.DESCENDING) \
                        .limit(limit)

        docs = reports_ref.stream()
        return [
            {
                "description": doc.to_dict().get("description"),
                "timestamp": doc.to_dict().get("timestamp").isoformat()
            }
            for doc in docs
        ]

    except Exception as e:
        print("[FirestoreAgent] Error:", e)
        return []
