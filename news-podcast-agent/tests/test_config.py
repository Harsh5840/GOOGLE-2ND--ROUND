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
from unittest import mock

import pytest

from app.config import ResearchConfiguration


def test_research_configuration_defaults():
    """Test that ResearchConfiguration has the expected default values."""
    config = ResearchConfiguration()
    
    assert config.critic_model == "gemini-1.5-pro"
    assert config.worker_model == "gemini-1.5-pro"
    assert config.max_search_iterations == 3
    assert config.news_api_key == ""
    assert config.google_tts_credentials == "tts_service_account.json"


def test_research_configuration_custom_values():
    """Test that ResearchConfiguration accepts custom values."""
    config = ResearchConfiguration(
        critic_model="custom-model",
        worker_model="custom-worker",
        max_search_iterations=5,
        news_api_key="test-api-key",
        google_tts_credentials="custom-credentials.json"
    )
    
    assert config.critic_model == "custom-model"
    assert config.worker_model == "custom-worker"
    assert config.max_search_iterations == 5
    assert config.news_api_key == "test-api-key"
    assert config.google_tts_credentials == "custom-credentials.json"


@mock.patch.dict(os.environ, {"NEWS_API_KEY": "env-api-key"})
def test_research_configuration_env_vars():
    """Test that ResearchConfiguration reads from environment variables."""
    config = ResearchConfiguration()
    
    assert config.news_api_key == "env-api-key"


@mock.patch.dict(os.environ, {
    "GOOGLE_CLOUD_PROJECT": "test-project",
    "GOOGLE_CLOUD_LOCATION": "test-location"
})
def test_google_cloud_env_vars():
    """Test that Google Cloud environment variables are set correctly."""
    from app.config import GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION
    
    assert GOOGLE_CLOUD_PROJECT == "test-project"
    assert GOOGLE_CLOUD_LOCATION == "test-location"