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
from unittest import mock

import pytest
from google.adk.agent import Agent, AgentContext, AgentResponse
from google.adk.agent.runner import Runner
from google.adk.agent.session import InMemorySessionService

from app.agent import (
    NewsResearcher,
    PodcastScripter,
    PodcastProducer,
    PodcastPipeline,
    PodcastOrchestrator,
    root_agent,
)


@pytest.fixture
def mock_context():
    context = mock.MagicMock(spec=AgentContext)
    context.session_id = "test-session"
    return context


@pytest.fixture
def mock_news_data():
    return [
        {
            "source": {"id": "test-source", "name": "Test Source"},
            "author": "Test Author",
            "title": "Test Title",
            "description": "Test Description",
            "url": "https://example.com/test",
            "content": "Test Content",
        }
    ]


@mock.patch("app.agent.fetch_local_news")
def test_news_researcher(mock_fetch_news, mock_context, mock_news_data):
    # Setup mock
    mock_fetch_news.return_value = mock_news_data

    # Create agent
    agent = NewsResearcher()

    # Test execute method
    response = agent.execute(mock_context, {"city": "Test City", "max_articles": 5})

    # Assertions
    mock_fetch_news.assert_called_once_with("Test City", max_articles=5)
    assert response.data == {"news_summaries": mock_news_data}


def test_podcast_scripter(mock_context, mock_news_data):
    # Create agent
    agent = PodcastScripter()

    # Test execute method
    response = agent.execute(
        mock_context, {"news_summaries": mock_news_data, "podcast_length": "short"}
    )

    # Assertions
    assert "podcast_script" in response.data
    assert isinstance(response.data["podcast_script"], str)


@mock.patch("app.agent.synthesize_speech")
def test_podcast_producer(mock_synthesize, mock_context):
    # Setup mock
    mock_synthesize.return_value = "test_output.mp3"

    # Create agent
    agent = PodcastProducer()

    # Test execute method
    response = agent.execute(
        mock_context, {"podcast_script": "This is a test podcast script."}
    )

    # Assertions
    mock_synthesize.assert_called_once()
    assert response.data["audio_file_path"] == "test_output.mp3"


@mock.patch("app.agent.PodcastProducer.execute")
@mock.patch("app.agent.PodcastScripter.execute")
@mock.patch("app.agent.NewsResearcher.execute")
def test_podcast_pipeline(
    mock_researcher_execute, mock_scripter_execute, mock_producer_execute, mock_context
):
    # Setup mocks
    mock_researcher_execute.return_value = AgentResponse(
        data={"news_summaries": mock_news_data}
    )
    mock_scripter_execute.return_value = AgentResponse(
        data={"podcast_script": "Test script"}
    )
    mock_producer_execute.return_value = AgentResponse(
        data={"audio_file_path": "test_output.mp3", "podcast_script": "Test script"}
    )

    # Create agent
    agent = PodcastPipeline()

    # Test execute method
    response = agent.execute(mock_context, {"city": "Test City", "podcast_length": "short"})

    # Assertions
    mock_researcher_execute.assert_called_once()
    mock_scripter_execute.assert_called_once()
    mock_producer_execute.assert_called_once()
    assert response.data["audio_file_path"] == "test_output.mp3"
    assert response.data["podcast_script"] == "Test script"


@mock.patch("app.agent.PodcastPipeline.execute")
def test_podcast_orchestrator(mock_pipeline_execute, mock_context):
    # Setup mock
    mock_pipeline_execute.return_value = AgentResponse(
        data={
            "audio_file_path": "test_output.mp3",
            "podcast_script": "Test script",
        }
    )

    # Create agent
    agent = PodcastOrchestrator()

    # Test execute method with user input
    response = agent.execute(
        mock_context, {"user_input": "Create a podcast about Seattle for 5 minutes"}
    )

    # Assertions
    mock_pipeline_execute.assert_called_once()
    assert "audio_file_path" in response.data
    assert "podcast_script" in response.data


def test_root_agent():
    # Verify root_agent is set correctly
    assert isinstance(root_agent, PodcastOrchestrator)