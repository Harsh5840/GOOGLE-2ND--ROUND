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
import tempfile
from unittest import mock

import pytest
from google.adk.agent import AgentContext


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def mock_agent_context():
    """Create a mock AgentContext for testing."""
    context = mock.MagicMock(spec=AgentContext)
    context.session_id = "test-session-id"
    context.invocation_id = "test-invocation-id"
    context.user_id = "test-user-id"
    return context


@pytest.fixture
def mock_news_api_response():
    """Create a mock response from the News API."""
    return {
        "status": "ok",
        "totalResults": 2,
        "articles": [
            {
                "source": {"id": "test-source-1", "name": "Test Source 1"},
                "author": "Test Author 1",
                "title": "Test Title 1",
                "description": "Test Description 1",
                "url": "https://example.com/test1",
                "urlToImage": "https://example.com/test1.jpg",
                "publishedAt": "2023-01-01T00:00:00Z",
                "content": "Test Content 1",
            },
            {
                "source": {"id": "test-source-2", "name": "Test Source 2"},
                "author": "Test Author 2",
                "title": "Test Title 2",
                "description": "Test Description 2",
                "url": "https://example.com/test2",
                "urlToImage": "https://example.com/test2.jpg",
                "publishedAt": "2023-01-02T00:00:00Z",
                "content": "Test Content 2",
            },
        ],
    }


@pytest.fixture
def mock_tts_response():
    """Create a mock response from the Google Cloud Text-to-Speech API."""
    mock_response = mock.MagicMock()
    mock_response.audio_content = b"test audio content"
    return mock_response


@pytest.fixture
def sample_podcast_script():
    """Return a sample podcast script for testing."""
    return """
    <speak>
    <prosody rate="medium" pitch="default">
    Welcome to the Local News Podcast for Test City. Here are today's top stories:
    
    First, Test Title 1. Test Description 1.
    
    Next, Test Title 2. Test Description 2.
    
    That's all for today's local news update. Thanks for listening!
    </prosody>
    </speak>
    """


@pytest.fixture
def mock_env_vars():
    """Set up mock environment variables for testing."""
    with mock.patch.dict(os.environ, {
        "GOOGLE_CLOUD_PROJECT": "test-project",
        "GOOGLE_CLOUD_LOCATION": "test-location",
        "NEWS_API_KEY": "test-news-api-key"
    }):
        yield