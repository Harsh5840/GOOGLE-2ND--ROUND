# 🏙️ CityScape
![CityScape Dashboard Preview](https://raw.githubusercontent.com/Harsh5840/GOOGLE-2ND--ROUND/29a1a01949033e6d79c1fc22f4f0f96de51b6c18/logo.jpeg)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Vertex%20AI-orange.svg)](https://cloud.google.com/vertex-ai)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

![logo](https://raw.githubusercontent.com/Harsh5840/GOOGLE-2ND--ROUND/29a1a01949033e6d79c1fc22f4f0f96de51b6c18/demo.png)


CityScape is an intelligent, agent-driven platform for real-time city event analysis and prediction. By processing multi-source data streams (social media, user uploads, web scraping), CityScape delivers live insights, proactive alerts, and user-specific summaries through an interactive dashboard. Built on Google Cloud and agentic AI, it empowers cities with actionable intelligence.

---

## ✨ Features

- 📡 **Multi-Source Data Ingestion**: Twitter, Reddit, Instagram, geo-tagged uploads, web scraping
- 🧠 **Agentic Reasoning**: Modular agents for prediction, reasoning, and interaction
- 📊 **Predictive Analytics**: Detects trends, mood shifts, and cascading city events
- 🗺️ **Live Dashboard**: Real-time map overlays, mood visualization, and incident plotting
- 🔔 **Proactive Notifications**: Personalized alerts and summaries via Firebase Cloud Messaging
- ⚡ **Cloud-Native**: Built on Vertex AI, Pub/Sub, Firestore, and Cloud Functions
- 🛡️ **Deduplication & Synthesis**: Cleans, normalizes, and fuses data for actionable insights

---

## 📰 News Podcast Agent

CityScape includes a powerful **News Podcast Agent** that generates personalized, local news podcasts using the News API and Google Cloud Text-to-Speech. This agent can fetch the latest news for any city, generate AI-powered scripts, and produce high-quality audio podcasts—making city updates accessible and engaging.

**Key Features:**
- 🎯 Local news fetching for any city
- 🤖 AI script generation (Gemini-powered)
- 🎙️ Studio-quality TTS (Google Cloud)
- 🚀 FastAPI backend for easy integration
- 🌐 Ready-to-use web interface
- 📱 Next.js compatible frontend
- 🔒 Secure API key integration
- ⚡ Async podcast generation

**Quick Start:**
```bash
cd news-podcast-agent
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.template .env  # Add your API keys
python run_api.py
```
Visit [http://localhost:8000/docs](http://localhost:8000/docs) for API documentation.

For full details, see [news-podcast-agent/README.md](news-podcast-agent/README.md).

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/cityscape.git
cd cityscape/GOOGLE-2ND--ROUND
```

### 2. Set Up Environment
```bash
# (Recommended) Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Google Cloud & API Keys
- Set up your Google Cloud project and enable:
  - Vertex AI API
  - Firestore
  - Pub/Sub
  - Cloud Functions
  - Firebase Cloud Messaging
- Add your credentials and API keys as environment variables or in a `.env` file (see `python-dotenv` usage).

### 4. Run the Backend/API
```bash
# Example: Run orchestrator or API gateway
python apps/orchestrator/main.py
# or
python apps/api-gateway/server.py
```

### 5. Start the Frontend Dashboard
```bash
cd apps/frontend
npm install
npm run dev
```

---

## 📁 Project Structure

```
cityscape/
├── agents/              # Modular agent logic (Twitter, Reddit, News, Maps, etc.)
├── apps/
│   ├── api-gateway/     # API gateway (Python FastAPI)
│   ├── frontend/        # Next.js dashboard (real-time UI)
│   └── orchestrator/    # Orchestration logic
├── data/                # Sample data and Firestore schema
├── infra/               # Deployment configs (Cloud Run, etc.)
├── shared/              # Shared schemas and utilities
├── tests/               # Unit and integration tests
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

- **agents/**: Specialized agents for data ingestion, reasoning, and response
- **apps/frontend/**: Next.js dashboard with live map, mood overlays, and notifications
- **apps/api-gateway/**: FastAPI server for backend APIs
- **apps/orchestrator/**: Orchestrates agent workflows and data pipelines
- **infra/**: Cloud Run and infrastructure-as-code configs
- **shared/**: Common schemas and utility functions
- **data/**: Sample events and Firestore schema
- **tests/**: Test coverage for agents and APIs

---

## 📦 Requirements

- **Python 3.10+**
- **Node.js 18+** (for frontend)
- **Google Cloud SDK** ([Install](https://cloud.google.com/sdk/docs/install))
- **Firebase CLI** (for notifications)
- **Terraform** (optional, for infra)
- See `requirements.txt` and `req.txt` for Python dependencies

---

## 🧑‍💻 Usage

### API Endpoints
- **Start API Gateway:**
  ```bash
  python apps/api-gateway/server.py
  ```
- **Orchestrator:**
  ```bash
  python apps/orchestrator/main.py
  ```
- **Example API Calls:**
  - Ingest event data
  - Query predictions
  - Fetch dashboard summaries

### Frontend Dashboard
- **Start Next.js UI:**
  ```bash
  cd apps/frontend
  npm install
  npm run dev
  ```
- Visit [http://localhost:3000](http://localhost:3000) for the live dashboard

---

## ☁️ Deployment

- **Cloud Run:** See `infra/cloudrun.yaml` for deployment config
- **GCP Setup:**
  - Enable required APIs (Vertex AI, Firestore, Pub/Sub, Cloud Functions, Firebase)
  - Deploy backend and frontend to Cloud Run or App Engine
- **Firebase:** Configure for notifications and hosting
- **Terraform:** Use for infrastructure provisioning (see `news-podcast-agent/deployment/` for example)

---

## 🧪 Testing

- Unit and integration tests in `tests/`
- Run with:
  ```bash
  pytest tests/
  ```
- Add new tests for agents and API endpoints as needed

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a pull request

---

## 📝 License

Distributed under the Apache 2.0 License. See `LICENSE` for more information.
