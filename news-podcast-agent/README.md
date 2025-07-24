# 🎙️ News Podcast Agent

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-TTS-orange.svg)](https://cloud.google.com/text-to-speech)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

A production-ready AI agent that creates personalized local news podcasts using the News API and Google Cloud Text-to-Speech. Features a complete FastAPI backend for easy frontend integration with Next.js, React, or any web framework.

## ✨ Features

- 🎯 **Local News Fetching** - Get latest news for any city
- 🤖 **AI Script Generation** - Gemini-powered podcast script creation
- 🎙️ **High-Quality TTS** - Google Cloud Text-to-Speech with Studio voices
- 🚀 **FastAPI Backend** - Complete REST API for frontend integration
- 🌐 **Web Interface** - Ready-to-use HTML frontend
- 📱 **Next.js Compatible** - Perfect for modern web frameworks
- 🔒 **Secure Authentication** - API key-based Google Cloud integration
- ⚡ **Async Processing** - Non-blocking podcast generation with job tracking

Agent generated with [`googleCloudPlatform/agent-starter-pack`](https://github.com/GoogleCloudPlatform/agent-starter-pack) version `0.9.2`

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/news-podcast-agent.git
cd news-podcast-agent
```

### 2. Set Up Environment
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

### 3. Configure API Keys
```bash
# Copy environment template
cp .env.template .env

# Edit .env and add your API keys:
# GOOGLE_API_KEY=your-google-api-key-here
```

### 4. Start the API Server
```bash
python run_api.py
```

### 5. Open the Web Interface
Open `frontend_example.html` in your browser or visit http://localhost:8000/docs for API documentation.

## 📁 Project Structure

```
news-podcast-agent/
├── app/                    # Core application code
│   ├── agent.py           # Main agent logic with podcast roles
│   ├── api_server.py      # FastAPI server with REST endpoints
│   ├── podcast_wrapper.py # Simple API wrapper for podcast generation
│   ├── config.py          # Configuration settings
│   ├── tools.py           # TTS and news fetching tools
│   └── utils/             # Utility functions
├── outputs/               # Generated audio files
├── frontend_example.html  # Web interface example
├── run_api.py            # API server startup script
├── .env.template         # Environment variables template
├── API_README.md         # Detailed API documentation
└── pyproject.toml        # Project dependencies
```

## Requirements

Before you begin, ensure you have:
- **Python 3.10+**: Required for Google ADK compatibility
- **News API Key**: Register at [newsapi.org](https://newsapi.org/register) to get your API key
- **Google Cloud SDK**: For GCP services - [Install](https://cloud.google.com/sdk/docs/install)
- **Terraform**: For infrastructure deployment - [Install](https://developer.hashicorp.com/terraform/downloads)
- **make**: Build automation tool - [Install](https://www.gnu.org/software/make/) (pre-installed on most Unix-based systems)

Enable the following Google Cloud APIs:
- Vertex AI API
- Text-to-Speech API
- Cloud Storage API
- Cloud Logging API


## Quick Start (Local Testing)

Install required packages and launch the local development environment:

```bash
make install && make playground
```

## Commands

| Command              | Description                                                                                 |
| -------------------- | ------------------------------------------------------------------------------------------- |
| `make install`       | Install all required dependencies using uv                                                  |
| `make dev`       | Start the ADK API server and React frontend development server simultaneously |
| `make dev-backend`       | Start the ADK API server |
| `make dev-frontend`       | Start the React frontend development server |
| `make api`           | Start the FastAPI server for REST API endpoints                   |
| `make backend`       | Deploy agent to Agent Engine |
| `make test`          | Run unit and integration tests                                                              |
| `make lint`          | Run code quality checks (codespell, ruff, mypy)                                             |
| `make setup-dev-env` | Set up development environment resources using Terraform                         |
| `uv run jupyter lab` | Launch Jupyter notebook                                                                     |

For full command options and usage, refer to the [Makefile](Makefile).


## Usage

The News Podcast Agent creates personalized local news podcasts for any city. Here's how to use it:

### Using the FastAPI Server

1. Start the FastAPI server:
   ```bash
   python -m app.api_server
   # or
   uvicorn app.api_server:app --reload
   ```

2. Access the API endpoints:
   - **Generate Podcast**: `POST /api/v1/podcast`
   - **Get News**: `GET /api/v1/news/{city}`
   - **API Documentation**: `http://localhost:8000/docs`

3. Example API request:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/podcast" \
        -H "Content-Type: application/json" \
        -d '{"city": "Bengaluru", "duration_minutes": 5}'
   ```

### Using the Command Line

```bash
python -m app.agent_engine_app --local
```

When prompted, enter a request like "Create a podcast about Seattle for 5 minutes" and the agent will generate the podcast.

### Agent Architecture

The agent uses a multi-agent architecture with specialized roles:

1. **NewsResearcher**: Finds and summarizes local news articles
2. **PodcastScripter**: Creates a well-structured podcast script from news summaries
3. **PodcastProducer**: Converts the script to audio using Text-to-Speech
4. **PodcastPipeline**: Coordinates the workflow between the specialized agents
5. **PodcastOrchestrator**: Handles user input and manages the overall process


## Deployment

> **Note:** For a streamlined one-command deployment of the entire CI/CD pipeline and infrastructure using Terraform, you can use the [`agent-starter-pack setup-cicd` CLI command](https://googlecloudplatform.github.io/agent-starter-pack/cli/setup_cicd.html). Currently only supporting Github.

### Dev Environment

You can test deployment towards a Dev Environment using the following command:

```bash
gcloud config set project <your-dev-project-id>
make backend
```


The repository includes a Terraform configuration for the setup of the Dev Google Cloud project.
See [deployment/README.md](deployment/README.md) for instructions.

### Production Deployment

The repository includes a Terraform configuration for the setup of a production Google Cloud project. Refer to [deployment/README.md](deployment/README.md) for detailed instructions on how to deploy the infrastructure and application.


## Monitoring and Observability
> You can use [this Looker Studio dashboard](https://lookerstudio.google.com/reporting/46b35167-b38b-4e44-bd37-701ef4307418/page/tEnnC
) template for visualizing events being logged in BigQuery. See the "Setup Instructions" tab to getting started.

The application uses OpenTelemetry for comprehensive observability with all events being sent to Google Cloud Trace and Logging for monitoring and to BigQuery for long term storage.
