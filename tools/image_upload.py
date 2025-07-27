import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import base64
from PIL import Image
import io

import vertexai
from vertexai.generative_models import GenerativeModel, Part

from shared.utils.logger import log_event
from tools.firestore import store_event_photo_firestore, store_user_location

# Create uploads directory if it doesn't exist
UPLOADS_DIR = Path("uploads/event_photos")
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# Metadata storage file (keeping for backward compatibility)
METADATA_FILE = Path("data/event_photos_metadata.json")
METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)

def load_metadata() -> List[Dict]:
    """Load existing metadata from file (legacy support)"""
    if METADATA_FILE.exists():
        try:
            with open(METADATA_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    return []

def save_metadata(metadata: List[Dict]):
    """Save metadata to file (legacy support)"""
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=2, default=str)

def analyze_image_with_gemini(image_data: bytes) -> str:
    """Use Gemini Vision API to analyze and summarize the image"""
    try:
        # Initialize Gemini model
        model = GenerativeModel("gemini-2.0-flash-exp")
        
        # Convert image to base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Create the prompt for image analysis
        prompt = """
        Analyze this image and provide a concise summary (2-3 sentences) describing:
        1. What you see in the image
        2. Any notable events, activities, or situations
        3. The overall mood or atmosphere
        4. Any safety concerns or important details
        
        Focus on aspects that would be relevant for city event reporting.
        """
        
        # Create the image part
        image_part = Part.from_data(
            data=image_data,
            mime_type="image/jpeg"
        )
        
        # Generate response
        response = model.generate_content([prompt, image_part])
        
        if response.text:
            return response.text.strip()
        else:
            return "Unable to analyze image content."
            
    except Exception as e:
        log_event("ImageUpload", f"Error analyzing image with Gemini: {str(e)}")
        return f"Error analyzing image: {str(e)}"

def save_image_file(image_data: bytes, filename: str) -> str:
    """Save image file and return the file path"""
    try:
        # Validate image
        image = Image.open(io.BytesIO(image_data))
        
        # Save image
        file_path = UPLOADS_DIR / filename
        image.save(file_path, format='JPEG', quality=85)
        
        return str(file_path)
        
    except Exception as e:
        log_event("ImageUpload", f"Error saving image file: {str(e)}")
        raise

def upload_event_photo(
    image_data: bytes,
    latitude: float,
    longitude: float,
    user_id: str,
    description: Optional[str] = None
) -> Dict:
    """
    Upload a geotagged image for city event reporting with Firestore integration.
    
    Args:
        image_data: Raw image bytes
        latitude: GPS latitude
        longitude: GPS longitude
        user_id: User identifier
        description: Optional user description
    
    Returns:
        Dict containing upload status and metadata
    """
    try:
        # Generate unique filename
        photo_id = str(uuid.uuid4())
        filename = f"{photo_id}.jpg"
        
        # Save image file
        file_path = save_image_file(image_data, filename)
        
        # Analyze image with Gemini
        log_event("ImageUpload", f"Analyzing image {photo_id} with Gemini Vision API")
        gemini_summary = analyze_image_with_gemini(image_data)
        
        # Create metadata
        metadata = {
            "id": photo_id,
            "filename": filename,
            "file_path": file_path,
            "latitude": latitude,
            "longitude": longitude,
            "user_id": user_id,
            "description": description,
            "gemini_summary": gemini_summary,
            "upload_timestamp": datetime.utcnow().isoformat(),
            "status": "uploaded"
        }
        
        # Store in Firestore (primary storage)
        firestore_result = store_event_photo_firestore(metadata)
        if not firestore_result.get("success"):
            log_event("ImageUpload", f"Warning: Failed to store in Firestore: {firestore_result.get('error')}")
        
        # Store user location in Firestore
        location_result = store_user_location(
            user_id=user_id,
            latitude=latitude,
            longitude=longitude,
            location_name=description or f"Photo upload at {latitude:.4f}, {longitude:.4f}",
            activity_type="photo_upload"
        )
        if not location_result.get("success"):
            log_event("ImageUpload", f"Warning: Failed to store location: {location_result.get('error')}")
        
        # Save metadata to local file (legacy support)
        try:
            existing_metadata = load_metadata()
            existing_metadata.append(metadata)
            save_metadata(existing_metadata)
        except Exception as e:
            log_event("ImageUpload", f"Warning: Failed to save local metadata: {str(e)}")
        
        log_event("ImageUpload", f"Successfully uploaded event photo {photo_id}")
        
        return {
            "success": True,
            "photo_id": photo_id,
            "message": "Event photo uploaded successfully",
            "metadata": metadata
        }
        
    except Exception as e:
        log_event("ImageUpload", f"Error uploading event photo: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to upload event photo"
        }

def get_all_event_photos() -> List[Dict]:
    """Get all uploaded event photos with their metadata from Firestore"""
    try:
        from tools.firestore import db, EVENT_PHOTOS_COLLECTION
        from google.cloud import firestore
        
        # Get photos from Firestore
        photos_ref = db.collection(EVENT_PHOTOS_COLLECTION).order_by("upload_timestamp", direction=firestore.Query.DESCENDING)
        docs = photos_ref.stream()
        
        photos = []
        for doc in docs:
            photo_data = doc.to_dict()
            # Add file URL for frontend access
            photo_data["file_url"] = f"/uploads/event_photos/{photo_data.get('filename', '')}"
            photos.append(photo_data)
        
        return photos
        
    except Exception as e:
        log_event("ImageUpload", f"Error retrieving event photos from Firestore: {str(e)}")
        # Fallback to local file if Firestore fails
        try:
            metadata = load_metadata()
            for photo in metadata:
                photo["file_url"] = f"/uploads/event_photos/{photo['filename']}"
            return metadata
        except Exception as fallback_error:
            log_event("ImageUpload", f"Error with fallback to local file: {str(fallback_error)}")
            return []

def get_event_photo_by_id(photo_id: str) -> Optional[Dict]:
    """Get a specific event photo by ID from Firestore"""
    try:
        from tools.firestore import db, EVENT_PHOTOS_COLLECTION
        
        # Get photo from Firestore
        photo_ref = db.collection(EVENT_PHOTOS_COLLECTION).document(photo_id)
        doc = photo_ref.get()
        
        if doc.exists:
            photo_data = doc.to_dict()
            # Add file URL for frontend access
            photo_data["file_url"] = f"/uploads/event_photos/{photo_data.get('filename', '')}"
            return photo_data
        
        return None
        
    except Exception as e:
        log_event("ImageUpload", f"Error retrieving event photo {photo_id} from Firestore: {str(e)}")
        # Fallback to local file if Firestore fails
        try:
            metadata = load_metadata()
            for photo in metadata:
                if photo["id"] == photo_id:
                    photo["file_url"] = f"/uploads/event_photos/{photo['filename']}"
                    return photo
            return None
        except Exception as fallback_error:
            log_event("ImageUpload", f"Error with fallback to local file: {str(fallback_error)}")
            return None 