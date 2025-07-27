import os
import time
import logging
from typing import Dict, Tuple, Optional

# Try to import the shared logger, fallback to standard logging if not available
try:
    from shared.utils.logger import log_event
except ImportError:
    # Fallback to standard logging
    def log_event(component: str, message: str):
        logging.info(f"[{component}] {message}")

# Initialize Gemini model for multilingual processing
try:
    import google.generativeai as genai
    from google.generativeai import GenerativeModel
    
    # Configure API key authentication
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key and api_key != "your-google-api-key-here":
        genai.configure(api_key=api_key)
        gemini_multilingual = GenerativeModel("gemini-2.0-flash")
        log_event("MultilingualWrapper", "Gemini API initialized successfully with API key")
    else:
        raise Exception("GOOGLE_API_KEY not set")
    
except Exception as e:
    log_event("MultilingualWrapper", f"Failed to initialize Gemini API: {e}")
    # Create a mock model for testing
    class MockGenerativeModel:
        def generate_content(self, prompt):
            class MockResponse:
                def __init__(self, text):
                    self.text = text
            # Simple mock responses for testing
            if "detect" in prompt.lower():
                return MockResponse("en")
            elif "translate" in prompt.lower():
                return MockResponse("Translated text")
            else:
                return MockResponse("Mock response")
    
    gemini_multilingual = MockGenerativeModel()
    log_event("MultilingualWrapper", "Using mock model for testing")

class MultilingualWrapper:
    def __init__(self):
        self.user_languages = {}  # Store user's preferred language
        self.conversation_context = {}  # Store conversation context per user
    
    async def detect_language(self, text: str) -> str:
        """Detect the language of the input text using Gemini."""
        try:
            prompt = f"""
            Detect the language of this text and respond with only the ISO 639-1 language code (e.g., 'en', 'es', 'fr', 'de', 'zh', 'ja', 'ko', 'ar', 'hi', 'pt', 'it', 'ru', 'nl', 'sv', 'no', 'da', 'fi', 'pl', 'tr', 'th', 'vi', 'id', 'ms', 'tl', 'bn', 'ur', 'fa', 'he', 'am', 'sw', 'yo', 'ig', 'zu', 'af', 'xh', 'zu').
            
            Text: "{text}"
            
            Language code:"""
            
            response = gemini_multilingual.generate_content(prompt)
            detected_lang = response.text.strip().lower()
            
            # Validate language code
            valid_langs = ['en', 'es', 'fr', 'de', 'zh', 'ja', 'ko', 'ar', 'hi', 'pt', 'it', 'ru', 'nl', 'sv', 'no', 'da', 'fi', 'pl', 'tr', 'th', 'vi', 'id', 'ms', 'tl', 'bn', 'ur', 'fa', 'he', 'am', 'sw', 'yo', 'ig', 'zu', 'af', 'xh', 'zu']
            if detected_lang not in valid_langs:
                detected_lang = 'en'  # Default to English
                
            log_event("MultilingualWrapper", f"Detected language: {detected_lang} for text: {text[:50]}...")
            return detected_lang
            
        except Exception as e:
            log_event("MultilingualWrapper", f"Error detecting language: {e}")
            return 'en'  # Default to English
    
    async def translate_to_english(self, text: str, source_lang: str) -> str:
        """Translate text to English if it's not already in English."""
        if source_lang == 'en':
            return text
            
        try:
            prompt = f"""
            Translate the following text from {source_lang} to English. 
            Maintain the original meaning and context. Only return the translated text, nothing else.
            
            Text: "{text}"
            
            English translation:"""
            
            response = gemini_multilingual.generate_content(prompt)
            translated = response.text.strip()
            
            log_event("MultilingualWrapper", f"Translated from {source_lang} to English: {text[:50]}... -> {translated[:50]}...")
            return translated
            
        except Exception as e:
            log_event("MultilingualWrapper", f"Error translating to English: {e}")
            return text  # Return original if translation fails
    
    async def translate_from_english(self, text: str, target_lang: str) -> str:
        """Translate text from English to target language."""
        if target_lang == 'en':
            return text
            
        try:
            prompt = f"""
            Translate the following English text to {target_lang}. 
            Maintain the original meaning, tone, and context. Only return the translated text, nothing else.
            
            English text: "{text}"
            
            {target_lang} translation:"""
            
            response = gemini_multilingual.generate_content(prompt)
            translated = response.text.strip()
            
            log_event("MultilingualWrapper", f"Translated from English to {target_lang}: {text[:50]}... -> {translated[:50]}...")
            return translated
            
        except Exception as e:
            log_event("MultilingualWrapper", f"Error translating from English: {e}")
            return text  # Return original if translation fails
    
    async def process_multilingual_message(self, user_id: str, message: str, agent_response: str) -> Tuple[str, str]:
        """
        Process a multilingual message:
        1. Detect language
        2. Translate to English if needed
        3. Translate response back to user's language
        4. Store user's language preference
        
        Returns: (translated_message_for_agent, translated_response_for_user)
        """
        try:
            # Detect language of user input
            detected_lang = await self.detect_language(message)
            
            # Store user's language preference
            self.user_languages[user_id] = detected_lang
            
            # Translate user message to English for agent processing
            english_message = await self.translate_to_english(message, detected_lang)
            
            # Translate agent response back to user's language
            translated_response = await self.translate_from_english(agent_response, detected_lang)
            
            log_event("MultilingualWrapper", f"Processed multilingual message for user {user_id}: {detected_lang}")
            
            return english_message, translated_response
            
        except Exception as e:
            log_event("MultilingualWrapper", f"Error in multilingual processing: {e}")
            return message, agent_response  # Return original if processing fails
    
    def get_user_language(self, user_id: str) -> str:
        """Get the stored language preference for a user."""
        return self.user_languages.get(user_id, 'en')
    
    def update_conversation_context(self, user_id: str, message: str, response: str):
        """Update conversation context for better multilingual responses."""
        if user_id not in self.conversation_context:
            self.conversation_context[user_id] = []
        
        self.conversation_context[user_id].append({
            'user_message': message,
            'agent_response': response,
            'timestamp': time.time()
        })
        
        # Keep only last 10 messages for context
        if len(self.conversation_context[user_id]) > 10:
            self.conversation_context[user_id] = self.conversation_context[user_id][-10:]

# Global instance
multilingual_wrapper = MultilingualWrapper() 