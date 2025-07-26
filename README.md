# City Project - Smart City Chatbot

A FastAPI-based chatbot system for smart city queries with direct tool integration and robust fallback mechanisms.

## Architecture

### Core Components

- **FastAPI Orchestrator** (`apps/orchestrator/main.py`): Main entry point that handles user queries, intent extraction, and tool dispatch
- **Intent Extractor** (`agents/intent_extractor/agent.py`): Combines regex patterns and LLM for intent/entity recognition
- **Direct Tool Integration**: Tools are called directly from the orchestrator for reliability
- **Gemini Fallback Agent**: Robust LLM fallback when tools fail or return errors

### Tool Modules

- **Twitter** (`tools/twitter.py`): Fetch Twitter posts by location and topic
- **Reddit** (`tools/reddit.py`): Fetch Reddit posts by subreddit
- **News** (`tools/news.py`): Fetch city-specific news articles
- **Maps** (`tools/maps.py`): Get must-visit places and route information
- **Firestore** (`tools/firestore.py`): Database operations for reports and similar queries
- **Google Search** (`tools/google_search.py`): Web search functionality

### Agent Components

- **Gemini Fallback Agent** (`agents/gemini_fallback_agent.py`): LLM-based fallback for failed tool calls
- **Agent Router** (`agents/agent_router.py`): Minimal router for fallback cases
- **Session Service** (`agents/session_service.py`): Centralized session management

## Recent Improvements

### Removed Redundancies

- **Deleted unused ADK agent files**: `research_agent.py`, `data_agent.py`, `analysis_agent.py`, `report_agent.py`, `root_agent.py`, `city_adk_agent.py`
- **Simplified agent_router**: Now only handles minimal fallback cases
- **Cleaned up imports**: Removed unused `TextBlob` and `sys` imports
- **Implemented missing tools**: Added news tool integration

### Architecture Benefits

- **Direct tool calls**: Bypasses ADK complexity for reliability
- **Structured error handling**: Clear success/failure responses with fallback
- **Centralized orchestration**: Single point of control for all queries
- **Robust fallback**: Multiple layers of fallback ensure user always gets a response

## Usage

### Start the Server

```bash
cd city-proj
python -m apps.orchestrator.main
```

### API Endpoints

- `POST /chat`: Main chatbot endpoint
- `POST /location_mood`: Location-based mood aggregation

### Example Query

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "What is Twitter saying about New York City?"
  }'
```

## Environment Variables

Required environment variables:
- `GOOGLE_CLOUD_PROJECT`: Google Cloud project ID
- `GOOGLE_CLOUD_LOCATION`: Vertex AI location
- `GOOGLE_MAPS_API_KEY`: Google Maps API key
- `NEWS_API_KEY`: News API key
- `REDDIT_CLIENT_ID`: Reddit API credentials
- `REDDIT_CLIENT_SECRET`: Reddit API credentials
- `TWITTER_BEARER_TOKEN`: Twitter API credentials

## Development

The system uses a clean, direct architecture:
1. User query → Intent extraction
2. Intent → Direct tool dispatch
3. Tool response → User or fallback to LLM
4. Always returns meaningful response

This approach eliminates the complexity of multi-agent coordination while maintaining reliability and functionality.
