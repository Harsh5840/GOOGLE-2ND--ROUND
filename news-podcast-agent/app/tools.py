# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging
import os
from typing import List, Dict
from newsapi import NewsApiClient
from config import config

def fetch_local_news(city: str, max_articles: int = 5) -> List[Dict]:
    """Fetch local news for a specific city using News API."""
    try:
        if not config.news_api_key:
            logging.error("News API key not configured")
            return []
        
        newsapi = NewsApiClient(api_key=config.news_api_key)
        
        # Search for news about the city
        query = f"{city} news"
        articles = newsapi.get_everything(
            q=query,
            language='en',
            sort_by='publishedAt',
            page_size=max_articles
        )
        
        # Extract relevant information
        news_list = []
        for article in articles.get('articles', []):
            news_item = {
                'title': article.get('title', ''),
                'description': article.get('description', ''),
                'url': article.get('url', ''),
                'publishedAt': article.get('publishedAt', ''),
                'source': article.get('source', {}).get('name', '')
            }
            news_list.append(news_item)
        
        logging.info(f"Fetched {len(news_list)} news articles for {city}")
        return news_list
        
    except Exception as e:
        logging.error(f"Error fetching news for {city}: {e}")
        return []

def translate_text(text: str, target_language: str) -> str:
    """Translate text using Gemini API."""
    try:
        import google.generativeai as genai
        
        if not config.google_api_key:
            logging.error("Google API key not configured")
            return text
        
        # Configure Gemini
        genai.configure(api_key=config.google_api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Language mapping
        language_map = {
            'en': 'English',
            'hi': 'Hindi',
            'kn': 'Kannada',
            'ta': 'Tamil',
            'te': 'Telugu',
            'ml': 'Malayalam',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ko': 'Korean'
        }
        
        target_lang_name = language_map.get(target_language, target_language)
        
        prompt = f"""
        Translate the following text to {target_lang_name}. 
        Keep the translation natural and conversational, suitable for a podcast.
        Maintain the original tone and style.
        
        Text to translate:
        {text}
        
        Translation:
        """
        
        response = model.generate_content(prompt)
        translated_text = response.text.strip()
        
        logging.info(f"Translated text to {target_lang_name}")
        return translated_text
        
    except Exception as e:
        logging.error(f"Translation error: {e}")
        return text

def synthesize_speech_elevenlabs(
    text: str,
    output_path: str = "podcast_output.mp3",
    voice_id: str = "pNInz6obpgDQGcFmaJgB",  # Adam - Male voice
    model_id: str = "eleven_monolingual_v1"
) -> str:
    """Convert text to speech using ElevenLabs API with Gemini fallback."""
    import time
    
    # Always use the provided ElevenLabs API key
    elevenlabs_key = "sk_f886d5ad5a673ac78a3d40008e84b565baac4dec83005a30"
    
    # Try ElevenLabs up to 3 times with retries
    for attempt in range(3):
        try:
            from elevenlabs import generate, save, set_api_key
            
            print(f"🎵 Attempting ElevenLabs audio generation (attempt {attempt + 1}/3)...")
            
            # Set API key
            set_api_key(elevenlabs_key)
            
            # Generate audio with enhanced settings using the correct API
            print("📡 Connecting to ElevenLabs API...")
            audio = generate(
                text=text,
                voice=voice_id,
                model=model_id
            )
            
            # Save audio file
            print("💾 Saving audio file...")
            save(audio, output_path)
            
            # Verify file was created
            import os
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                print(f"✅ ElevenLabs audio successfully saved to {output_path}")
                logging.info(f"ElevenLabs audio saved to {output_path}")
                return output_path
            else:
                raise Exception("Audio file was not created or is empty")
                
        except Exception as e:
            print(f"⚠️ ElevenLabs attempt {attempt + 1} failed: {str(e)}")
            if attempt < 2:  # Not the last attempt
                print("🔄 Retrying ElevenLabs in 2 seconds...")
                time.sleep(2)
            else:
                print("❌ ElevenLabs failed after 3 attempts. Trying Gemini TTS fallback...")
                break
    
    # If ElevenLabs failed, try gTTS as fallback
    try:
        print("🤖 Attempting gTTS fallback...")
        return synthesize_speech_gemini(text, output_path)
    except Exception as e:
        print(f"❌ gTTS fallback also failed: {str(e)}")
        logging.error(f"Both ElevenLabs and gTTS failed: {e}")
        
        # Create text file as final fallback
        text_file_path = output_path.replace('.mp3', '.txt')
        with open(text_file_path, "w", encoding="utf-8") as f:
            f.write(f"Podcast Script:\n\n{text}\n\n")
            f.write(f"Audio generation failed for both ElevenLabs and gTTS\n")
            f.write(f"ElevenLabs error: API connection issues\n")
            f.write(f"gTTS error: {str(e)}\n")
        
        return text_file_path

def synthesize_speech_gemini(
    text: str,
    output_path: str = "podcast_output.mp3"
) -> str:
    """Convert text to speech using gTTS (Google Text-to-Speech) as fallback."""
    try:
        print("🔧 Setting up gTTS fallback...")
        
        # Try to import gTTS
        try:
            from gtts import gTTS
        except ImportError:
            print("📦 Installing gTTS...")
            import subprocess
            import sys
            subprocess.check_call([sys.executable, "-m", "pip", "install", "gtts"])
            from gtts import gTTS
        
        print("📡 Connecting to Google TTS service...")
        
        # Create gTTS object with English language and slow speed for better quality
        tts = gTTS(text=text, lang='en', slow=False)
        
        # Save the audio file
        print("💾 Saving gTTS audio file...")
        tts.save(output_path)
        
        # Verify file was created
        import os
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print(f"✅ gTTS audio successfully saved to {output_path}")
            logging.info(f"gTTS audio saved to {output_path}")
            return output_path
        else:
            raise Exception("gTTS audio file was not created or is empty")
            
    except Exception as e:
        print(f"❌ gTTS failed: {str(e)}")
        logging.error(f"gTTS error: {e}")
        raise e

def create_podcast_script(news_articles: List[Dict], city: str, duration_minutes: int = 2) -> str:
    """Create a focused news podcast script with proper timing, greetings, and send-off."""
    try:
        import google.generativeai as genai
        
        if not config.google_api_key:
            logging.error("Google API key not configured")
            return f"Welcome to the {city} news podcast. Here are the latest updates from {city}."
        
        # Configure Gemini
        genai.configure(api_key=config.google_api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Prepare news data for the prompt
        news_text = ""
        for i, article in enumerate(news_articles, 1):
            news_text += f"{i}. {article.get('title', '')}\n"
            news_text += f"   {article.get('description', '')}\n\n"
        
        # Calculate target word count for timing (approximately 150 words per minute)
        target_words = duration_minutes * 150
        
        prompt = f"""
        Create a {duration_minutes}-minute news podcast script for {city} with exactly {target_words} words (±10%).
        
        IMPORTANT: Write ONLY the spoken content. Do NOT include:
        - Stage directions like "(music)" or "(transition)"
        - Formatting like "**Host:**" or "**Greeting:**"
        - Timing notes like "(15 seconds)" or "(10-15 seconds)"
        - Any text in parentheses or brackets
        - Section headers or labels
        
        Structure the content as:
        1. A warm greeting to listeners
        2. The news stories (focus only on the provided articles)
        3. A thank you and sign-off
        
        Requirements:
        - Write ONLY what should be spoken aloud
        - Focus ONLY on the news content - no filler, no questions, no commentary
        - Make it engaging and conversational but professional
        - Ensure accurate timing for {duration_minutes} minutes
        - Include smooth transitions between stories
        - Keep the tone informative and engaging
        - Write in a flowing, natural speaking style
        
        News Articles:
        {news_text}
        
        Create the complete spoken script (no formatting, no directions):
        """
        
        response = model.generate_content(prompt)
        script = response.text.strip()
        
        # Clean up any remaining formatting or directions
        import re
        # Remove any remaining stage directions in parentheses
        script = re.sub(r'\([^)]*\)', '', script)
        # Remove any remaining formatting markers
        script = re.sub(r'\*\*[^*]*\*\*:', '', script)
        script = re.sub(r'\[[^\]]*\]', '', script)
        # Clean up extra whitespace
        script = re.sub(r'\n\s*\n', '\n\n', script)
        script = script.strip()
        
        logging.info(f"Created podcast script for {city} with target duration {duration_minutes} minutes")
        return script
        
    except Exception as e:
        logging.error(f"Script creation error: {e}")
        return f"Welcome to the {city} news podcast. Here are the latest updates from {city}."

# Tool wrappers for compatibility
def local_news_tool(city: str, max_articles: int = 5) -> str:
    """Tool wrapper for fetching local news."""
    articles = fetch_local_news(city, max_articles)
    return json.dumps(articles)

def text_to_speech_tool(
    text: str,
    output_path: str = "podcast_output.mp3",
    voice_id: str = "pNInz6obpgDQGcFmaJgB"
) -> str:
    """Tool wrapper for text-to-speech."""
    return synthesize_speech_elevenlabs(text, output_path, voice_id)