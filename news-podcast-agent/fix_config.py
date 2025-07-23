#!/usr/bin/env python3
"""Script to fix the corrupted config.py file by completely rewriting it."""

import os

# Clean config content
config_content = '''# Copyright 2025 Google LLC
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

import google.auth

# To use AI Studio credentials:
# 1. Create a .env file in the /app directory with:
#    GOOGLE_GENAI_USE_VERTEXAI=FALSE
#    GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE
# 2. This will override the default Vertex AI configuration

# Try to get project_id from google.auth, but handle the case where it might be None
try:
    _, project_id = google.auth.default()
    if project_id:
        os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
    else:
        # Use a default project ID if none is available from auth
        os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "news-podcast-agent-project")
except Exception:
    # Fallback if authentication fails
    os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "news-podcast-agent-project")

os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")


@dataclass
class ResearchConfiguration:
    """Configuration for research-related models and parameters.

    Attributes:
        critic_model (str): Model for evaluation tasks.
        worker_model (str): Model for working/generation tasks.
        max_search_iterations (int): Maximum search iterations allowed.
        news_api_key (str): API key for the News API.
        google_tts_credentials (str): Path or JSON for Google Cloud TTS credentials.
    """

    critic_model: str = "gemini-2.5-pro"
    worker_model: str = "gemini-2.5-flash"
    max_search_iterations: int = 5
    news_api_key: str = "4f30f4c22bf8475b8a6aa7a9c53e4e0b"
    google_tts_credentials: str = "tts_service_account.json"


config = ResearchConfiguration()
'''

def fix_config():
    """Fix the corrupted config.py file."""
    config_path = os.path.join("app", "config.py")
    
    # Remove the corrupted file
    if os.path.exists(config_path):
        os.remove(config_path)
        print(f"Removed corrupted {config_path}")
    
    # Write the clean content
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"Created clean {config_path}")
    
    # Verify the fix
    file_size = os.path.getsize(config_path)
    print(f"New file size: {file_size} bytes")
    
    if file_size < 5000:  # Should be around 2KB, not 62KB
        print("✅ Config file successfully fixed!")
    else:
        print("❌ Config file still has issues")

if __name__ == "__main__":
    fix_config()
