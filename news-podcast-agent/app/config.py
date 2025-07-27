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

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class NewsPodcastConfig:
    """Configuration for the news podcast agent.

    Attributes:
        google_api_key (str): Google API key for Gemini models.
        news_api_key (str): API key for the News API.
        elevenlabs_api_key (str): API key for ElevenLabs TTS.
        default_city (str): Default city for news.
        default_duration_minutes (int): Default podcast duration.
    """

    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    news_api_key: str = os.getenv("NEWS_API_KEY", "")
    elevenlabs_api_key: str = os.getenv("ELEVENLABS_API_KEY", "your-elevenlabs-api-key-here")
    default_city: str = "Bengaluru"
    default_duration_minutes: int = 2

    def validate(self):
        """Validate that required API keys are set."""
        missing_keys = []
        if not self.google_api_key or self.google_api_key == "your-google-api-key-here":
            missing_keys.append("GOOGLE_API_KEY")
        if not self.news_api_key:
            missing_keys.append("NEWS_API_KEY")
        # ElevenLabs key is hardcoded in tools.py, so we don't need to validate it here
        
        if missing_keys:
            raise ValueError(f"Missing required API keys: {', '.join(missing_keys)}")
    
    def get_elevenlabs_key(self):
        """Get ElevenLabs API key with placeholder handling."""
        if not self.elevenlabs_api_key or self.elevenlabs_api_key == "your-elevenlabs-api-key-here":
            print("⚠️  ElevenLabs API key not set")
            print("   Get your free API key from: https://elevenlabs.io/")
            print("   Add it to your .env file as: ELEVENLABS_API_KEY=your_key_here")
            return None
        return self.elevenlabs_api_key

config = NewsPodcastConfig()
