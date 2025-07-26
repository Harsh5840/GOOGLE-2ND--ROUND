import os
from .config import config
from typing import List, Dict
import json
import logging
logging.basicConfig(level=logging.INFO)

# News API client
try:
    from newsapi import NewsApiClient
except ImportError:
    NewsApiClient = None  # Will raise if used without install

# Google Cloud TTS client
try:
    from google.cloud import texttospeech
except ImportError:
    texttospeech = None


def fetch_local_news(city: str, max_articles: int = 5) -> List[Dict]:
    """Fetches local news articles for a given city using News API."""
    logging.info(f"[fetch_local_news] Fetching news for city={city}, max_articles={max_articles}")
    if NewsApiClient is None:
        logging.error("[fetch_local_news] newsapi-python is not installed.")
        raise ImportError("newsapi-python is not installed. Run 'pip install newsapi-python'.")
    newsapi = NewsApiClient(api_key=config.news_api_key)
    # NewsAPI does not support city directly, so use q and country if needed
    articles = newsapi.get_everything(q=city, language='en', sort_by='publishedAt', page_size=max_articles)
    logging.info(f"[fetch_local_news] Retrieved {len(articles.get('articles', []))} articles for city={city}")
    return articles.get('articles', [])


def synthesize_speech(
    text: str,
    output_path: str = "podcast_output.mp3",
    voice: str = "en-US-Studio-Q",  # Supported male Studio voice
    speaking_rate: float = 1.0  # Natural speaking rate for Studio voices
) -> str:
    """Converts text to speech using Google Cloud TTS with enhanced naturalness and human-like qualities."""
    try:
        if texttospeech is None:
            raise ImportError("google-cloud-texttospeech is not installed. Run 'pip install google-cloud-texttospeech'.")
        # Set up API key authentication for Google Cloud TTS
        if config.google_api_key and config.google_api_key != "your-google-api-key-here":
            os.environ["GOOGLE_API_KEY"] = config.google_api_key
            # Use API key authentication
            client = texttospeech.TextToSpeechClient()
        else:
            # Fallback to default authentication (ADC)
            client = texttospeech.TextToSpeechClient()
        # Handle SSML vs plain text based on voice type
        if '<speak>' not in text:
            # For newer voices (Studio, Neural2), use plain text only - no SSML at all
            if 'Studio' in voice or 'Neural2' in voice:
                # Use plain text input for Studio and Neural2 voices
                synthesis_input = texttospeech.SynthesisInput(text=text)
            else:
                # Standard voices can handle basic SSML
                enhanced_text = _enhance_text_for_natural_speech(text)
                rate_value = f"{speaking_rate:.2f}"
                ssml_text = f'<speak><prosody rate="{rate_value}">{enhanced_text}</prosody></speak>'
                synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)
        else:
            # Text already contains SSML, use SSML input
            synthesis_input = texttospeech.SynthesisInput(ssml=text)
        # Enhanced voice parameters for more natural sound
        voice_params = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name=voice,
        )
        # Enhanced audio configuration for better quality
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=speaking_rate,
            effects_profile_id=["headphone-class-device"],  # Optimized for headphones/speakers
            sample_rate_hertz=24000,  # Higher quality audio
        )
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice_params,
            audio_config=audio_config,
        )
        with open(output_path, "wb") as out:
            out.write(response.audio_content)
        logging.info(f"[synthesize_speech] Podcast audio saved to {output_path}")
        return output_path
    except Exception as e:
        logging.error(f"[synthesize_speech] Error generating podcast audio: {e}")
        raise


def _enhance_text_for_natural_speech(text: str) -> str:
    """Enhance text with minimal, valid SSML for newer Google TTS voices.
    
    Uses only the most basic SSML tags that are guaranteed to work with Neural2 and Studio voices.
    """
    import re
    import html
    
    # Escape any existing HTML/XML characters to prevent SSML conflicts
    text = html.escape(text)
    
    # For newer voices, use only basic sentence pauses with standard durations
    # Using only 1s, 2s, 3s as these are most widely supported
    text = re.sub(r'\. ', '. <break time="1s"/> ', text)
    text = re.sub(r'\! ', '! <break time="1s"/> ', text)
    text = re.sub(r'\? ', '? <break time="1s"/> ', text)
    
    # Very basic comma pauses
    text = re.sub(r', ', ', <break time="0.5s"/> ', text)
    
    # Remove any complex SSML that might cause validation issues
    # No emphasis tags, no complex prosody - just basic breaks
    
    # Clean up any double spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


# Tool wrappers for agent integration

def local_news_tool(city: str, max_articles: int = 5) -> str:
    """Agent tool: fetches local news for a city and returns as JSON string."""
    articles = fetch_local_news(city, max_articles)
    return json.dumps(articles)

def text_to_speech_tool(
    text: str,
    output_path: str = "podcast_output.mp3",
    voice: str = "en-US-Studio-Q",  # Supported male Studio voice
    speaking_rate: float = 1.0
) -> str:
    """Agent tool: converts text to speech and returns the audio file path."""
    logging.info(f"[text_to_speech_tool] Converting text to speech: output_path={output_path}, voice={voice}, rate={speaking_rate}")
    return synthesize_speech(text, output_path, voice, speaking_rate)