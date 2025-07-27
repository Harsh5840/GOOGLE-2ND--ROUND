#!/usr/bin/env python3
"""
Simplified News Podcast Agent
Creates news podcasts with multilingual support and ElevenLabs TTS.
"""

import os
import sys
import logging
import asyncio
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set ElevenLabs API key if not already set
if not os.getenv("ELEVENLABS_API_KEY"):
    os.environ["ELEVENLABS_API_KEY"] = "sk_f886d5ad5a673ac78a3d40008e84b565baac4dec83005a30"
    print("✅ ElevenLabs API key automatically set")

# Import our tools
from config import config
from tools import (
    fetch_local_news,
    translate_text,
    synthesize_speech_elevenlabs,
    create_podcast_script
)

class NewsPodcastAgent:
    """Simplified news podcast agent with multilingual support."""
    
    def __init__(self):
        """Initialize the agent."""
        self.supported_languages = {
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
        
        # ElevenLabs voice options - Male voice for all languages
        self.voice_options = {
            'en': 'pNInz6obpgDQGcFmaJgB',  # Adam - Male English
            'hi': 'pNInz6obpgDQGcFmaJgB',  # Adam - Male Hindi
            'kn': 'pNInz6obpgDQGcFmaJgB',  # Adam - Male Kannada
            'ta': 'pNInz6obpgDQGcFmaJgB',  # Adam - Male Tamil
            'te': 'pNInz6obpgDQGcFmaJgB',  # Adam - Male Telugu
            'ml': 'pNInz6obpgDQGcFmaJgB',  # Adam - Male Malayalam
            'es': 'pNInz6obpgDQGcFmaJgB',  # Adam - Male Spanish
            'fr': 'pNInz6obpgDQGcFmaJgB',  # Adam - Male French
            'de': 'pNInz6obpgDQGcFmaJgB',  # Adam - Male German
            'zh': 'pNInz6obpgDQGcFmaJgB',  # Adam - Male Chinese
            'ja': 'pNInz6obpgDQGcFmaJgB',  # Adam - Male Japanese
            'ko': 'pNInz6obpgDQGcFmaJgB',  # Adam - Male Korean
        }
    
    def validate_config(self):
        """Validate that all required API keys are configured."""
        try:
            # Check if ElevenLabs key is set
            elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
            if not elevenlabs_key:
                os.environ["ELEVENLABS_API_KEY"] = "sk_f886d5ad5a673ac78a3d40008e84b565baac4dec83005a30"
                print("✅ ElevenLabs API key automatically set")
            
            config.validate()
            print("✅ All API keys are configured")
            return True
        except ValueError as e:
            print(f"❌ Configuration error: {e}")
            return False
    
    def create_podcast(
        self,
        city: str,
        duration_minutes: int = 2,
        language: str = 'en',
        max_articles: int = 5,
        output_filename: Optional[str] = None
    ) -> dict:
        """
        Create a complete news podcast.
        
        Args:
            city: City for news
            duration_minutes: Podcast duration in minutes
            language: Language code (en, hi, kn, etc.)
            max_articles: Maximum number of news articles
            output_filename: Custom output filename
            
        Returns:
            Dictionary with results
        """
        try:
            print(f"\n🎙️ Creating {duration_minutes}-minute podcast for {city} in {self.supported_languages.get(language, language)}")
            
            # Step 1: Fetch news
            print("📰 Fetching news articles...")
            news_articles = fetch_local_news(city, max_articles)
            
            if not news_articles:
                print("⚠️ No news articles found")
                return {
                    'success': False,
                    'error': 'No news articles found',
                    'city': city,
                    'language': language
                }
            
            print(f"✅ Found {len(news_articles)} news articles")
            
            # Step 2: Create podcast script with proper timing
            print("📝 Creating podcast script...")
            script = create_podcast_script(news_articles, city, duration_minutes)
            
            if not script:
                print("❌ Failed to create podcast script")
                return {
                    'success': False,
                    'error': 'Failed to create podcast script',
                    'city': city,
                    'language': language
                }
            
            print("✅ Podcast script created")
            
            # Step 3: Translate if needed
            if language != 'en':
                print(f"🌍 Translating to {self.supported_languages.get(language, language)}...")
                translated_script = translate_text(script, language)
                if translated_script and translated_script != script:
                    script = translated_script
                    print("✅ Script translated")
                else:
                    print("⚠️ Translation failed, using original script")
            
            # Step 4: Generate audio with enhanced voice settings
            print("🎵 Generating audio with male voice...")
            if not output_filename:
                output_filename = f"podcast_{city.lower().replace(' ', '_')}_{language}.mp3"
            
            # Get appropriate voice for the language
            voice_id = self.voice_options.get(language, 'pNInz6obpgDQGcFmaJgB')
            audio_file = synthesize_speech_elevenlabs(script, output_filename, voice_id)
            
            # Check if audio generation was successful
            import os
            if audio_file.endswith('.mp3') and os.path.exists(audio_file) and os.path.getsize(audio_file) > 0:
                print("✅ Audio file generated successfully")
            else:
                print("⚠️ Audio generation failed, but script file was created")
                print(f"📄 Script available at: {audio_file}")
            
            # Step 5: Save script to text file
            script_file = output_filename.replace('.mp3', '.txt')
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(f"Podcast Script for {city}\n")
                f.write(f"Language: {self.supported_languages.get(language, language)}\n")
                f.write(f"Duration: {duration_minutes} minutes\n")
                f.write(f"Generated: {len(news_articles)} articles\n")
                f.write(f"Voice: Enhanced ElevenLabs (Adam - Male)\n\n")
                f.write(script)
            
            print("✅ Script saved to text file")
            
            # Return results
            result = {
                'success': True,
                'city': city,
                'language': language,
                'duration_minutes': duration_minutes,
                'articles_count': len(news_articles),
                'script_file': script_file,
                'audio_file': audio_file,
                'script_preview': script[:200] + "..." if len(script) > 200 else script
            }
            
            print(f"\n🎉 Podcast created successfully!")
            print(f"📄 Script: {script_file}")
            print(f"🎵 Audio: {audio_file}")
            
            return result
            
        except Exception as e:
            logging.error(f"Error creating podcast: {e}")
            return {
                'success': False,
                'error': str(e),
                'city': city,
                'language': language
            }
    
    def list_supported_languages(self):
        """List all supported languages."""
        print("\n🌍 Supported Languages:")
        for code, name in self.supported_languages.items():
            print(f"  {code}: {name}")

def main():
    """Main function for interactive podcast creation."""
    print("🎙️ News Podcast Agent")
    print("=" * 50)
    
    # Initialize agent
    agent = NewsPodcastAgent()
    
    # Validate configuration
    if not agent.validate_config():
        print("\nPlease set up your API keys in the .env file:")
        print("GOOGLE_API_KEY=your_google_api_key")
        print("NEWS_API_KEY=your_news_api_key") 
        print("ELEVENLABS_API_KEY=your_elevenlabs_api_key")
        return
    
    # Get user input
    print("\nEnter podcast details:")
    
    # City
    city = input(f"City (default: {config.default_city}): ").strip()
    if not city:
        city = config.default_city
    
    # Duration - Fix the timing issue
    try:
        duration_input = input(f"Duration in minutes (default: {config.default_duration_minutes}): ").strip()
        if duration_input:
            duration_minutes = int(duration_input)
            print(f"✅ Using {duration_minutes} minutes as requested")
        else:
            duration_minutes = config.default_duration_minutes
            print(f"✅ Using default duration: {duration_minutes} minutes")
    except ValueError:
        duration_minutes = config.default_duration_minutes
        print(f"⚠️ Invalid input, using default duration: {duration_minutes} minutes")
    
    # Language
    print("\nSupported languages:")
    agent.list_supported_languages()
    language = input("Language code (default: en): ").strip().lower()
    if not language or language not in agent.supported_languages:
        language = 'en'
    
    # Create podcast with the user's specified duration
    result = agent.create_podcast(
        city=city,
        duration_minutes=duration_minutes,  # Use the user's input
        language=language
    )
    
    if result['success']:
        print(f"\n🎉 Podcast created successfully!")
        print(f"📍 City: {result['city']}")
        print(f"🌍 Language: {agent.supported_languages.get(result['language'], result['language'])}")
        print(f"⏱️ Duration: {result['duration_minutes']} minutes")
        print(f"📰 Articles: {result['articles_count']}")
        print(f"📄 Script: {result['script_file']}")
        print(f"🎵 Audio: {result['audio_file']}")
        print(f"🎤 Voice: Enhanced ElevenLabs (Adam - Male)")
    else:
        print(f"\n❌ Failed to create podcast: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main() 