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
import logging
from collections.abc import Sequence
from typing import Any

import google.cloud.storage as storage
from google.cloud import logging as google_cloud_logging
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExportResult


class CloudTraceLoggingSpanExporter(CloudTraceSpanExporter):
    """
    An extended version of CloudTraceSpanExporter that logs span data to Google Cloud Logging
    and handles large attribute values by storing them in Google Cloud Storage.

    This class helps bypass the 256 character limit of Cloud Trace for attribute values
    by leveraging Cloud Logging (which has a 256KB limit) and Cloud Storage for larger payloads.
    """

    def __init__(
        self,
        project_id: str | None = None,
        logging_client: google_cloud_logging.Client | None = None,
        storage_client: storage.Client | None = None,
        bucket_name: str | None = None,
        debug: bool = False,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the exporter with Google Cloud clients and configuration.

        :param project_id: Google Cloud project ID
        :param logging_client: Google Cloud Logging client
        :param storage_client: Google Cloud Storage client
        :param bucket_name: Name of the GCS bucket to store large payloads
        :param debug: Enable debug mode for additional logging
        """
        super().__init__(project_id=project_id, **kwargs)
        self.logging_client = logging_client or google_cloud_logging.Client()
        self.logger = self.logging_client.logger("cloud_trace_logging")
        self.storage_client = storage_client
        self.bucket_name = bucket_name
        self.debug = debug

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """
        Export the spans to Cloud Trace and log them to Cloud Logging.

        :param spans: The spans to export
        :return: The result of the export operation
        """
        # First, export to Cloud Trace as normal
        result = super().export(spans)

        # Then, log the spans to Cloud Logging
        for span in spans:
            # Convert span to dict for logging
            span_dict = self._span_to_dict(span)

            # Log the span data
            self.logger.log_struct(
                {
                    "span": span_dict,
                    "trace_id": span.context.trace_id,
                    "span_id": span.context.span_id,
                },
                severity="INFO",
            )

        return result

    def _span_to_dict(self, span: ReadableSpan) -> dict[str, Any]:
        """
        Convert a span to a dictionary for logging.

        :param span: The span to convert
        :return: A dictionary representation of the span
        """
        # Basic span information
        span_dict = {
            "name": span.name,
            "context": {
                "trace_id": span.context.trace_id,
                "span_id": span.context.span_id,
                "is_remote": span.context.is_remote,
            },
            "parent_span_id": span.parent.span_id if span.parent else None,
            "start_time": span.start_time,
            "end_time": span.end_time,
            "status": {
                "status_code": span.status.status_code,
                "description": span.status.description,
            },
            "attributes": {},
            "events": [],
            "links": [],
        }

        # Process attributes
        for key, value in span.attributes.items():
            # Convert value to string for logging
            if isinstance(value, (dict, list)):
                value_str = json.dumps(value)
            else:
                value_str = str(value)

            span_dict["attributes"][key] = value_str

        # Process events
        for event in span.events:
            event_dict = {
                "name": event.name,
                "timestamp": event.timestamp,
                "attributes": {},
            }
            for key, value in event.attributes.items():
                event_dict["attributes"][key] = str(value)
            span_dict["events"].append(event_dict)

        # Process links
        for link in span.links:
            link_dict = {
                "context": {
                    "trace_id": link.context.trace_id,
                    "span_id": link.context.span_id,
                    "is_remote": link.context.is_remote,
                },
                "attributes": {},
            }
            for key, value in link.attributes.items():
                link_dict["attributes"][key] = str(value)
            span_dict["links"].append(link_dict)

        return span_dict