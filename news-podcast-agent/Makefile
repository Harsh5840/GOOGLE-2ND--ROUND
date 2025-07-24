# Makefile for news-podcast-agent

.PHONY: install dev dev-backend dev-frontend api backend test lint setup-dev-env

# Install dependencies
install:
	uv pip install -e .
	uv pip install -r .requirements.txt

# Start the ADK API server and React frontend development server simultaneously
dev:
	make dev-backend & make dev-frontend

# Start the ADK API server
dev-backend:
	uv run python -m app.agent_engine_app --local

# Start the React frontend development server
dev-frontend:
	cd frontend && npm start

# Start FastAPI server for REST API endpoints
api:
	uv run uvicorn app.api_server:app --reload --host 0.0.0.0 --port 8000

# Deploy agent to Agent Engine
backend:
	uv run python -m app.agent_engine_app

# Run unit and integration tests
test:
	uv run pytest

# Run code quality checks
lint:
	uv run ruff check .
	uv run mypy .
	uv run codespell

# Set up development environment resources using Terraform
setup-dev-env:
	cd deployment && terraform init && terraform apply