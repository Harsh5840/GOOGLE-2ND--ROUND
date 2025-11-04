import os
from google.cloud import storage
from tools.firestore import db
from uuid import uuid4
from datetime import datetime
from shared.utils.logger import log_event
from typing import Optional, List

USER_PHOTO_BUCKET = os.getenv("USER_PHOTO_BUCKET") or "user-photo-bucket"
USER_PHOTO_COLLECTION = "user_photos"

def save_user_photo(file, lat: float, lng: float, description: Optional[str], user_id: Optional[str]) -> Optional[str]:
    """
    Save a user photo to GCS and metadata to Firestore. Returns the photo URL or None on error.
    """
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(USER_PHOTO_BUCKET)
        photo_id = str(uuid4())
        ext = file.filename.split(".")[-1]
        blob = bucket.blob(f"photos/{photo_id}.{ext}")
        content = file.file.read() if hasattr(file, 'file') else file.read()
        blob.upload_from_string(content, content_type=file.content_type)
        photo_url = f"https://storage.googleapis.com/{USER_PHOTO_BUCKET}/photos/{photo_id}.{ext}"
        doc = {
            "photo_url": photo_url,
            "lat": lat,
            "lng": lng,
            "description": description or "",
            "user_id": user_id or "",
            "timestamp": datetime.utcnow().isoformat()
        }
        db.collection(USER_PHOTO_COLLECTION).add(doc)
        return photo_url
    except Exception as e:
        log_event("UserPhoto", f"Error saving user photo: {e}")
        return None

def fetch_user_photos_nearby(lat: float, lng: float, radius_m: int = 500) -> List[dict]:
    """
    Fetch user photos within radius_m meters of the given lat/lng.
    """
    try:
        docs = db.collection(USER_PHOTO_COLLECTION).stream()
        from math import radians, cos, sin, sqrt, atan2
        def haversine(lat1, lng1, lat2, lng2):
            R = 6371000  # meters
            phi1, phi2 = radians(lat1), radians(lat2)
            dphi = radians(lat2 - lat1)
            dlambda = radians(lng2 - lng1)
            a = sin(dphi/2)**2 + cos(phi1)*cos(phi2)*sin(dlambda/2)**2
            return R * 2 * atan2(sqrt(a), sqrt(1-a))
        photos = []
        for doc in docs:
            d = doc.to_dict()
            if "lat" in d and "lng" in d:
                dist = haversine(lat, lng, d["lat"], d["lng"])
                if dist <= radius_m:
                    photos.append(d)
        return photos
    except Exception as e:
        log_event("UserPhoto", f"Error fetching user photos: {e}")
        return [] 