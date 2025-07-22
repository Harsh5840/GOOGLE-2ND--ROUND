

from agents.reddit_agent import fetch_reddit_posts
from agents.twitter_agent import fetch_twitter_posts
from agents.firestore_agent import fetch_firestore_reports
from agents.rag_search import get_rag_fallback
from agents.response_agent import generate_final_response
from agents.intent_extractor.agent import extract_intent
from agents.news_agent import fetch_city_news
from agents.googlemaps_agent import get_best_route
from agents.google_search_agent import google_search
from agents.agglomerator import aggregate_api_results


def city_chatbot_orchestrator(message: str) -> str:
    print("[Orchestrator] Running city_chatbot_orchestrator...")

    # Step 1: Extract intent and entities
    parsed = extract_intent(message)
    intent = parsed["intent"]
    entities = parsed["entities"]
    location = entities.get("location", "")
    topic = entities.get("topic", "")

    print(f"[Orchestrator] Intent: {intent} | Location: {location} | Topic: {topic}")

    # Step 2: Fetch external data sources
    reddit_data = fetch_reddit_posts(location, topic)
    twitter_data = fetch_twitter_posts(location, topic)
    firestore_data = fetch_firestore_reports(location, topic)
    rag_data = get_rag_fallback(location, topic)
    news_data = fetch_city_news(location)
    maps_data = get_best_route(location, topic)  # If topic is a destination, else adjust as needed

    print("[Orchestrator] Data from tools fetched successfully.")

    # Step 3: Fallback to Google Search if all are empty
    google_results = []
    if not (reddit_data or twitter_data or firestore_data or rag_data or news_data):
        google_results = google_search(message)
        rag_data = [f"{item['title']}: {item['snippet']} ({item['link']})" for item in google_results]

    # Step 4: Aggregate all results
    unified_data = aggregate_api_results(
        reddit_data=reddit_data,
        twitter_data=twitter_data,
        news_data=news_data,
        maps_data=maps_data,
        firestore_data=firestore_data,
        rag_data=rag_data,
        google_search_data=google_results
    )

    # Step 5: Fuse all info via Gemini response agent
    final_response = generate_final_response(
        user_message=message,
        intent=intent,
        location=location,
        topic=topic,
        unified_data=unified_data
    )

    return final_response
