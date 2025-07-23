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
import os
import tempfile
from unittest import mock

import pytest

from app.tools import fetch_local_news, synthesize_speech


@mock.patch("app.tools.NewsApiClient")
def test_fetch_local_news(mock_news_api):
    # Setup mock
    mock_news_api_instance = mock.MagicMock()
    mock_news_api.return_value = mock_news_api_instance
    mock_news_api_instance.get_everything.return_value = {
        "articles": [
            {
                "source": {"id": "test-source", "name": "Test Source"},
                "author": "Test Author",
                "title": "Test Title",
                "description": "Test Description",
                "url": "https://example.com/test",
                "urlToImage": "https://example.com/test.jpg",
                "publishedAt": "2023-01-01T00:00:00Z",
                "content": "Test Content",
            }
        ]
    }

    # Call function
    result = fetch_local_news("Test City", max_articles=5)

    # Assertions
    mock_news_api_instance.get_everything.assert_called_once_with(
        q="Test City", language="en", sort_by="publishedAt", page_size=5
    )
    assert len(result) == 1
    assert result[0]["title"] == "Test Title"
    assert result[0]["source"]["name"] == "Test Source"


@mock.patch("app.tools.texttospeech")
def test_synthesize_speech(mock_tts):
    # Setup mock
    mock_tts_client = mock.MagicMock()
    mock_tts.TextToSpeechClient.return_value = mock_tts_client
    mock_response = mock.MagicMock()
    mock_response.audio_content = b"test audio content"
    mock_tts_client.synthesize_speech.return_value = mock_response

    # Create a temporary file for output
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = temp_file.name

    try:
        # Call function
        result = synthesize_speech(
            "Test text", output_path=temp_path, voice="en-US-Studio-O", speaking_rate=1.0
        )

        # Assertions
        assert result == temp_path
        assert os.path.exists(temp_path)
        with open(temp_path, "rb") as f:
            assert f.read() == b"test audio content"

        # Verify correct SSML was used
        synthesis_input = mock_tts.SynthesisInput(
            ssml="<speak><prosody rate=\"medium\" pitch=\"default\">Test text</prosody></speak>"
        )
        voice_params = mock_tts.VoiceSelectionParams(
            language_code="en-US", name="en-US-Studio-O"
        )
        audio_config = mock_tts.AudioConfig(
            audio_encoding=mock_tts.AudioEncoding.MP3, speaking_rate=1.0
        )

        mock_tts_client.synthesize_speech.assert_called_once()

    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)