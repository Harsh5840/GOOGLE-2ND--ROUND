import os
from google.cloud import aiplatform
from typing import Dict

# === CONFIGURATION ===
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
LOCATION = os.getenv("GCP_REGION", "us-central1")
ENDPOINT_ID = os.getenv("VERTEX_AI_ENDPOINT_ID")  # Set this to your deployed model endpoint ID

# Example feature vector (update with real values as needed)
example_instance = {
    "weekday": 0,  # Monday
    "hour": 8,
    "weather": "Clear",
    "twitter_event_count": 2,
    "reddit_event_count": 1,
    "news_event_count": 0,
    "google_search_event_count": 1
}

def predict_travel_time(instance: Dict):
    aiplatform.init(project=PROJECT_ID, location=LOCATION)
    endpoint = aiplatform.Endpoint(ENDPOINT_ID)
    response = endpoint.predict(instances=[instance])
    print("Prediction response:", response)
    if response and hasattr(response, 'predictions'):
        print("Predicted travel time (minutes):", response.predictions[0])
    else:
        print("No prediction returned.")

if __name__ == "__main__":
    predict_travel_time(example_instance) 