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
from google.cloud.storage import Bucket
from pydantic import ValidationError

from app.utils.gcs import create_bucket_if_not_exists
from app.utils.typing import Feedback
from app.utils.tracing import CloudTraceLoggingSpanExporter


@mock.patch("app.utils.gcs.storage")
def test_create_bucket_if_not_exists(mock_storage):
    """Test that create_bucket_if_not_exists works correctly."""
    # Setup mocks
    mock_client = mock.MagicMock()
    mock_storage.Client.return_value = mock_client
    mock_bucket = mock.MagicMock(spec=Bucket)
    mock_client.bucket.return_value = mock_bucket
    
    # Test with existing bucket
    mock_bucket.exists.return_value = True
    with mock.patch("app.utils.gcs.logging") as mock_logging:
        result = create_bucket_if_not_exists("test-bucket")
    
    mock_client.bucket.assert_called_with("test-bucket")
    mock_bucket.exists.assert_called_once()
    mock_logging.info.assert_called_with("Bucket test-bucket already exists")
    assert result == mock_bucket
    
    # Test with non-existing bucket
    mock_bucket.exists.return_value = False
    with mock.patch("app.utils.gcs.logging") as mock_logging:
        result = create_bucket_if_not_exists("test-bucket")
    
    mock_bucket.create.assert_called_once()
    mock_logging.info.assert_called_with("Created bucket test-bucket")
    assert result == mock_bucket
    
    # Test with gs:// prefix
    mock_bucket.exists.return_value = True
    with mock.patch("app.utils.gcs.logging"):
        result = create_bucket_if_not_exists("gs://test-bucket")
    
    mock_client.bucket.assert_called_with("test-bucket")
    assert result == mock_bucket


def test_feedback_model():
    """Test that Feedback model works correctly."""
    # Test valid feedback
    feedback = Feedback(
        score=5,
        text="Great service",
        invocation_id="test-invocation",
        user_id="test-user"
    )
    
    assert feedback.score == 5
    assert feedback.text == "Great service"
    assert feedback.invocation_id == "test-invocation"
    assert feedback.log_type == "feedback"
    assert feedback.service_name == "news-podcast-agent"
    assert feedback.user_id == "test-user"
    
    # Test invalid feedback (score out of range)
    with pytest.raises(ValidationError):
        Feedback(
            score=11,  # Invalid score
            text="Great service",
            invocation_id="test-invocation",
            user_id="test-user"
        )


@mock.patch("app.utils.tracing.logging")
@mock.patch("app.utils.tracing.storage")
@mock.patch("app.utils.tracing.CloudTraceSpanExporter")
def test_cloud_trace_logging_span_exporter(
    mock_trace_exporter, mock_storage, mock_logging
):
    """Test that CloudTraceLoggingSpanExporter works correctly."""
    # Setup mocks
    mock_client = mock.MagicMock()
    mock_storage.Client.return_value = mock_client
    mock_bucket = mock.MagicMock()
    mock_client.bucket.return_value = mock_bucket
    mock_blob = mock.MagicMock()
    mock_bucket.blob.return_value = mock_blob
    
    # Create exporter
    exporter = CloudTraceLoggingSpanExporter(
        project_id="test-project",
        bucket_name="test-bucket",
        debug=True
    )
    
    # Test initialization
    assert exporter.project_id == "test-project"
    assert exporter.bucket_name == "test-bucket"
    assert exporter.debug is True
    
    # Test export with large attribute
    mock_span = mock.MagicMock()
    mock_span.attributes = {"large_attr": "a" * 300}  # Attribute larger than 256 chars
    
    exporter.export([mock_span])
    
    # Verify large attribute was stored in GCS
    mock_bucket.blob.assert_called_once()
    mock_blob.upload_from_string.assert_called_once()
    mock_logging.info.assert_called()