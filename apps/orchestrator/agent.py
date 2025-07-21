# orchestrator/agent.py

from agents.tool_caller import fetch_reddit_posts
from agents.twitter_agent import fetch_twitter_posts
from agents.firestore_agent import fetch_firestore_reports
from agents.rag_search import get_rag_fallback
from agents.response_agent import generate_final_response
from agents.intent_extractor.agent import extract_intent


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

    print("[Orchestrator] Data from tools fetched successfully.")

    # Step 3: Fuse all info via Gemini response agent
    final_response = generate_final_response(
        user_message=message,
        intent=intent,
        location=location,
        topic=topic,
        reddit_posts=reddit_data,
        twitter_posts=twitter_data,
        firestore_reports=firestore_data,
        rag_docs=rag_data
    )

    return final_response
