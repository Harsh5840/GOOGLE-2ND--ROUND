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

# mypy: disable-error-code="attr-defined,arg-type"
import copy
import datetime
import json
import logging
import os
import sys
from typing import Any, List, Dict

import google.auth
import vertexai
from google.adk.artifacts import GcsArtifactService
from google.cloud import logging as google_cloud_logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, export
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

from agent import root_agent  # Now the podcast orchestrator agent
from config import config
from utils.gcs import create_bucket_if_not_exists
from utils.tracing import CloudTraceLoggingSpanExporter
from utils.typing import Feedback
from sys import path as sys_path
sys_path.append("../../agents")

# Initialize Google ADK
try:
    from init_adk import init_adk
    init_adk()
except ImportError:
    print("⚠️  Could not import init_adk.py")

from multilingual_wrapper import multilingual_wrapper


class AgentEngineApp(AdkApp):
    def set_up(self) -> None:
        """Set up logging and tracing for the agent engine app."""
        super().set_up()
        logging_client = google_cloud_logging.Client()
        self.logger = logging_client.logger(__name__)
        provider = TracerProvider()
        processor = export.BatchSpanProcessor(
            CloudTraceLoggingSpanExporter(
                project_id=os.environ.get("GOOGLE_CLOUD_PROJECT")
            )
        )
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)

    def register_feedback(self, feedback: dict[str, Any]) -> None:
        """Collect and log feedback."""
        feedback_obj = Feedback.model_validate(feedback)
        self.logger.log_struct(feedback_obj.model_dump(), severity="INFO")

    def register_operations(self) -> dict[str, list[str]]:
        """Registers the operations of the Agent.

        Extends the base operations to include feedback registration functionality.
        """
        operations = super().register_operations()
        operations[""] = operations[""] + ["register_feedback"]
        return operations

    def clone(self) -> "AgentEngineApp":
        """Returns a clone of the ADK application."""
        template_attributes = self._tmpl_attrs

        return self.__class__(
            agent=copy.deepcopy(template_attributes["agent"]),
            enable_tracing=bool(template_attributes.get("enable_tracing", False)),
            session_service_builder=template_attributes.get("session_service_builder"),
            artifact_service_builder=template_attributes.get(
                "artifact_service_builder"
            ),
            env_vars=template_attributes.get("env_vars"),
        )


def deploy_agent_engine_app(
    project: str,
    location: str,
    agent_name: str | None = None,
    requirements_file: str = ".requirements.txt",
    extra_packages: list[str] = ["./app"],
    env_vars: dict[str, str] = {},
) -> agent_engines.AgentEngine:
    """Deploy the agent engine app to Vertex AI."""

    staging_bucket_uri = f"gs://{project}-agent-engine"
    artifacts_bucket_name = f"{project}-news-podcast-agent-logs-data"
    create_bucket_if_not_exists(
        bucket_name=artifacts_bucket_name, project=project, location=location
    )
    create_bucket_if_not_exists(
        bucket_name=staging_bucket_uri, project=project, location=location
    )

    vertexai.init(project=project, location=location, staging_bucket=staging_bucket_uri)

    # Read requirements
    with open(requirements_file) as f:
        requirements = f.read().strip().split("\n")

    agent_engine = AgentEngineApp(
        agent=root_agent,
        artifact_service_builder=lambda: GcsArtifactService(
            bucket_name=artifacts_bucket_name
        ),
    )

    # Set worker parallelism to 1
    env_vars["NUM_WORKERS"] = "1"

    # Common configuration for both create and update operations
    agent_config = {
        "agent_engine": agent_engine,
        "display_name": agent_name,
        "description": "A production-ready fullstack research agent that uses Gemini to strategize, research, and synthesize comprehensive reports with human-in-the-loop collaboration",
        "extra_packages": extra_packages,
        "env_vars": env_vars,
    }
    logging.info(f"Agent config: {agent_config}")
    agent_config["requirements"] = requirements

    # Check if an agent with this name already exists
    existing_agents = list(agent_engines.list(filter=f"display_name={agent_name}"))
    if existing_agents:
        # Update the existing agent with new configuration
        logging.info(f"Updating existing agent: {agent_name}")
        remote_agent = existing_agents[0].update(**agent_config)
    else:
        # Create a new agent if none exists
        logging.info(f"Creating new agent: {agent_name}")
        remote_agent = agent_engines.create(**agent_config)

    config = {
        "remote_agent_engine_id": remote_agent.resource_name,
        "deployment_timestamp": datetime.datetime.now().isoformat(),
    }
    config_file = "deployment_metadata.json"

    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)

    logging.info(f"Agent Engine ID written to {config_file}")

    return remote_agent


if __name__ == "__main__":
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="Test podcast agent locally or deploy to Vertex AI")
    parser.add_argument('--local', action='store_true', help='Run the podcast agent locally (no cloud deployment)')
    parser.add_argument('--project', default=None, help='GCP project ID (for cloud deployment)')
    parser.add_argument('--location', default='us-central1', help='GCP region (for cloud deployment)')
    parser.add_argument('--agent-name', default='news-podcast-agent', help='Name for the agent engine (cloud deployment)')
    parser.add_argument('--requirements-file', default='.requirements.txt', help='Path to requirements.txt file (cloud deployment)')
    parser.add_argument('--extra-packages', nargs='+', default=['./app'], help='Additional packages to include (cloud deployment)')
    parser.add_argument('--set-env-vars', help='Comma-separated list of environment variables in KEY=VALUE format (cloud deployment)')
    args = parser.parse_args()

    if args.local:
        import asyncio
        from agent import root_agent
        from google.adk.sessions import InMemorySessionService
        from google.adk.runners import Runner
        from google.genai import types

        print("\n==== Local Podcast Agent Test ====")
        city = input(f"Enter city for local news (default: {config.default_city}): ").strip() or config.default_city
        length = input("Enter desired podcast length (minutes): ")
        user_lang = input("Enter your language code (e.g., en, es, fr, de, zh): ").strip() or "en"

        prompt = f"Create a {length}-minute podcast for {city}."

        # Multilingual: translate prompt to English if needed
        english_prompt = asyncio.run(multilingual_wrapper.translate_to_english(prompt, user_lang)) if user_lang != "en" else prompt
        message = types.Content(role="user", parts=[types.Part.from_text(text=english_prompt)])

        session_service = InMemorySessionService()
        session = session_service.create_session_sync(user_id="local_user", app_name="local_test")
        runner = Runner(agent=root_agent, session_service=session_service, app_name="local_test")

        print("\n=== Podcast Generation Result ===")
        try:
            events = runner.run(new_message=message, user_id="local_user", session_id=session.id)
            for event in events:
                # Print all text parts from the event
                if hasattr(event, "content") and event.content:
                    if hasattr(event.content, "parts"):
                        for part in event.content.parts:
                            if hasattr(part, "text"):
                                # Multilingual: translate response back to user's language
                                output_text = part.text
                                if user_lang != "en":
                                    output_text = asyncio.run(multilingual_wrapper.translate_from_english(output_text, user_lang))
                                print(output_text)
                    elif hasattr(event.content, "text"):
                        output_text = event.content.text
                        if user_lang != "en":
                            output_text = asyncio.run(multilingual_wrapper.translate_from_english(output_text, user_lang))
                        print(output_text)
                elif hasattr(event, "text"):
                    print(event.text)
                else:
                    print(event)
        except Exception as e:
            print(f"Error running agent locally: {e}")
            import sys
            sys.exit(1)
    else:
        # Cloud deployment logic (original)
        # Parse environment variables if provided
        env_vars = {}
        if args.set_env_vars:
            for pair in args.set_env_vars.split(","):
                key, value = pair.split("=", 1)
                env_vars[key] = value

        if not args.project:
            import google.auth
            _, args.project = google.auth.default()

        print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   🤖 DEPLOYING AGENT TO VERTEX AI AGENT ENGINE 🤖         ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

        deploy_agent_engine_app(
            project=args.project,
            location=args.location,
            agent_name=args.agent_name,
            requirements_file=args.requirements_file,
            extra_packages=args.extra_packages,
            env_vars=env_vars,
        )
