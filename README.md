# 🌐 CityScape

CityScape is an intelligent, agent-driven platform that analyzes and predicts events in a city by processing multi-source data streams. Designed with Google Cloud technologies and agentic AI, it delivers real-time insights, proactive alerts, and user-specific summaries through an interactive dashboard.

---

## 🚀 Features

✅ **Data Ingestion & Processing**

* Pulls data from social APIs (Twitter, Instagram, Reddit) using Pub/Sub.
* Supports geo-tagged user uploads and web scraping.
* Normalizes and synthesizes data with Vertex AI.

✅ **Predictive Analytics**

* Detects city-wide trends and mood shifts.
* Predicts cascading effects using Vertex AI models.
* Provides actionable predictions for 3rd order effects (e.g., traffic surges, event escalations).

✅ **Reasoning & Actions**

* Deduplicates and classifies multi-source data.
* Generates summaries and plots incidents on live maps.
* Drives decisions using Vertex Agent Builder (Google ADK).

✅ **Interactive Dashboard**

* Built with Next.js for real-time updates.
* Displays mood overlays and geo-tagged reports.
* Supports offline summaries via Gemini API.

✅ **Proactive Notifications**

* Sends predictive alerts and user-specific summaries.
* Filters notifications using Firebase Cloud Messaging.

---

## ⚙️ Tech Stack

### Google Cloud Platform (GCP):

* **Pub/Sub** – Data stream ingestion
* **Vertex AI** – Predictive models, summarization
* **Firestore** – Real-time database for app state
* **Cloud Functions** – Event-driven processing
* **Firebase Hosting & Cloud Messaging** – Frontend hosting & notifications

### Frontend:

* **Next.js** – Interactive, real-time dashboard
* **Tailwind CSS** – UI styling

### Backend:

* **Node.js / Python** – Cloud Functions logic
* **Google ADK (Agent Builder)** – Reasoning workflows

---

## 🧠 System Architecture

```
[Data Ingestion & Processing]
        |
[Predictive Agent] ---> [Reasoning & Actions Agent]
        |                          |
[Frontend Interaction Agent]       |
        |                          |
[Notifications Agent] <-------------
```

* **Ingestion**: Social APIs, user uploads, web scraping.
* **Processing**: Clean, deduplicate, synthesize.
* **Prediction**: Detect trends and future events.
* **Reasoning**: Summarize, decide actions.
* **Interaction**: Display data and notify users.

---

## 🏆 Built For

This project was built as part of the **Google Cloud Hackathon** to showcase agentic AI systems leveraging Google ADK and Firebase for real-time city intelligence.

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---
