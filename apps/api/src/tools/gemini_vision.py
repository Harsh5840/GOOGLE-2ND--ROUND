"""
Gemini Vision API tool for photo classification and analysis.
"""

import base64
import json
from typing import Dict, Any
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import os
from shared.utils.logger import log_event

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

async def classify_photo_with_gemini(image_data: bytes, latitude: float, longitude: float) -> Dict[str, Any]:
    """
    Classify a photo using Gemini Vision API and generate title, description, category, and severity.
    
    Args:
        image_data: Raw image bytes
        latitude: Location latitude
        longitude: Location longitude
        
    Returns:
        Dict containing classification results
    """
    try:
        # Initialize Gemini Vision model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Convert image to base64 for Gemini
        image_b64 = base64.b64encode(image_data).decode('utf-8')
        
        # Create the prompt for photo classification
        prompt = f"""
        Analyze this image taken at coordinates ({latitude}, {longitude}) and provide a detailed classification for a smart city reporting system.

        Please provide your response in the following JSON format:
        {{
            "title": "Brief, descriptive title (max 50 characters)",
            "description": "Detailed description of what you see (max 200 characters)",
            "category": "One of: traffic, infrastructure, events, emergency, weather, pollution, construction, maintenance, safety, other",
            "severity": "One of: low, medium, high, critical",
            "confidence": "Confidence score from 0.0 to 1.0",
            "detected_objects": ["list", "of", "key", "objects", "detected"],
            "suggested_actions": "Brief suggestion for city authorities (max 100 characters)",
            "time_sensitivity": "One of: immediate, urgent, routine, informational"
        }}

        Focus on:
        1. Urban infrastructure issues (potholes, broken lights, damaged signs)
        2. Traffic conditions and violations
        3. Public safety concerns
        4. Environmental issues (pollution, waste)
        5. Construction or maintenance needs
        6. Public events or gatherings
        7. Emergency situations

        Be specific and actionable in your analysis. Consider the location context for better classification.
        """
        
        # Create image part for Gemini
        image_part = {
            "mime_type": "image/jpeg",
            "data": image_b64
        }
        
        # Generate response
        response = model.generate_content(
            [prompt, image_part],
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }
        )
        
        # Parse the JSON response
        response_text = response.text.strip()
        
        # Clean up the response to extract JSON
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].strip()
        
        try:
            classification_result = json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback parsing if JSON is malformed
            log_event("GeminiVision", f"Failed to parse JSON response: {response_text}")
            classification_result = {
                "title": "Image Analysis",
                "description": response_text[:200] if len(response_text) > 200 else response_text,
                "category": "other",
                "severity": "medium",
                "confidence": 0.7,
                "detected_objects": [],
                "suggested_actions": "Review image for city planning",
                "time_sensitivity": "routine"
            }
        
        # Validate and sanitize the response
        classification_result = validate_classification_result(classification_result)
        
        log_event("GeminiVision", f"Successfully classified photo at ({latitude}, {longitude})")
        return classification_result
        
    except Exception as e:
        log_event("GeminiVision", f"Error classifying photo: {str(e)}")
        # Return fallback classification
        return {
            "title": "User Report",
            "description": "Image uploaded by user for city reporting",
            "category": "other",
            "severity": "medium",
            "confidence": 0.5,
            "detected_objects": [],
            "suggested_actions": "Manual review required",
            "time_sensitivity": "routine"
        }

def validate_classification_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and sanitize the classification result from Gemini.
    """
    # Valid categories
    valid_categories = [
        "traffic", "infrastructure", "events", "emergency", "weather", 
        "pollution", "construction", "maintenance", "safety", "other"
    ]
    
    # Valid severities
    valid_severities = ["low", "medium", "high", "critical"]
    
    # Valid time sensitivities
    valid_time_sensitivities = ["immediate", "urgent", "routine", "informational"]
    
    # Sanitize and validate fields
    sanitized = {
        "title": str(result.get("title", "User Report"))[:50],
        "description": str(result.get("description", "Image uploaded by user"))[:200],
        "category": result.get("category", "other") if result.get("category") in valid_categories else "other",
        "severity": result.get("severity", "medium") if result.get("severity") in valid_severities else "medium",
        "confidence": max(0.0, min(1.0, float(result.get("confidence", 0.7)))),
        "detected_objects": result.get("detected_objects", [])[:10],  # Limit to 10 objects
        "suggested_actions": str(result.get("suggested_actions", "Review required"))[:100],
        "time_sensitivity": result.get("time_sensitivity", "routine") if result.get("time_sensitivity") in valid_time_sensitivities else "routine"
    }
    
    return sanitized

def get_category_emoji(category: str) -> str:
    """
    Get emoji for category visualization.
    """
    category_emojis = {
        "traffic": "🚗",
        "infrastructure": "🏗️",
        "events": "🎉",
        "emergency": "🚨",
        "weather": "🌤️",
        "pollution": "🏭",
        "construction": "🚧",
        "maintenance": "🔧",
        "safety": "⚠️",
        "other": "📷"
    }
    return category_emojis.get(category, "📷")

def get_severity_color(severity: str) -> str:
    """
    Get color code for severity visualization.
    """
    severity_colors = {
        "low": "#10b981",      # Green
        "medium": "#f59e0b",   # Yellow
        "high": "#ef4444",     # Red
        "critical": "#dc2626"  # Dark Red
    }
    return severity_colors.get(severity, "#6b7280")  # Gray default
