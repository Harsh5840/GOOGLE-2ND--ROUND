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
from google.adk.app import AdkApp
from google.adk.agent import Agent

from app.agent_engine_app import AgentEngineApp, deploy_agent_engine_app


@pytest.fixture
def mock_root_agent():
    return mock.MagicMock(spec=Agent)


def test_agent_engine_app_initialization(mock_root_agent):
    """Test that AgentEngineApp initializes correctly."""
    app = AgentEngineApp(root_agent=mock_root_agent)
    
    assert app.root_agent == mock_root_agent
    assert isinstance(app, AdkApp)


@mock.patch("app.agent_engine_app.setup_google_cloud_logging")
@mock.patch("app.agent_engine_app.setup_opentelemetry_tracing")
def test_agent_engine_app_setup_logging_and_tracing(
    mock_setup_tracing, mock_setup_logging, mock_root_agent
):
    """Test that AgentEngineApp sets up logging and tracing."""
    app = AgentEngineApp(root_agent=mock_root_agent)
    app.setup_logging_and_tracing()
    
    mock_setup_logging.assert_called_once()
    mock_setup_tracing.assert_called_once()


@mock.patch("app.agent_engine_app.aiplatform")
@mock.patch("app.agent_engine_app.AgentEngineApp")
@mock.patch("app.agent_engine_app.ArtifactService")
@mock.patch("app.agent_engine_app.create_bucket_if_not_exists")
@mock.patch("builtins.open", mock.mock_open(read_data="requirements\npackage1\npackage2"))
def test_deploy_agent_engine_app(
    mock_create_bucket, mock_artifact_service, mock_app_class, mock_aiplatform, mock_root_agent
):
    """Test that deploy_agent_engine_app works correctly."""
    # Setup mocks
    mock_app_instance = mock.MagicMock()
    mock_app_class.return_value = mock_app_instance
    mock_artifact_service_instance = mock.MagicMock()
    mock_artifact_service.return_value = mock_artifact_service_instance
    
    mock_agent_list = mock.MagicMock()
    mock_aiplatform.Agent.list.return_value = []
    
    # Call function
    with mock.patch.dict(os.environ, {
        "GOOGLE_CLOUD_PROJECT": "test-project",
        "GOOGLE_CLOUD_LOCATION": "test-location"
    }):
        deploy_agent_engine_app(
            root_agent=mock_root_agent,
            agent_display_name="test-agent",
            staging_bucket="gs://test-staging",
            artifact_bucket="gs://test-artifacts"
        )
    
    # Assertions
    mock_create_bucket.assert_any_call("gs://test-staging")
    mock_create_bucket.assert_any_call("gs://test-artifacts")
    
    mock_artifact_service.assert_called_once_with("gs://test-artifacts")
    mock_app_class.assert_called_once_with(
        root_agent=mock_root_agent,
        artifact_service=mock_artifact_service_instance
    )
    
    mock_aiplatform.init.assert_called_once()
    mock_aiplatform.Agent.create.assert_called_once()