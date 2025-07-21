# agents/rag_search/rag_agent.py

from typing import List, Dict
import os
import json

# Optional: Vertex AI Vector Search setup
USE_VERTEX_VECTOR = os.getenv("USE_VERTEX_VECTOR", "false").lower() == "true"

def semantic_search_fallback(query: str) -> List[Dict]:
    """
    Fallback RAG implementation: searches local JSON event file for relevance.
    """
    try:
        with open("data/sample_events.json", "r") as f:
            events = json.load(f)
    except FileNotFoundError:
        return []

    matches = []
    for event in events:
        if query.lower() in event.get("description", "").lower() or \
           query.lower() in event.get("title", "").lower():
            matches.append(event)
    return matches[:5]


# Placeholder for Vertex Vector Search
def search_vector_db(query: str) -> List[Dict]:
    """
    TODO: Connect this with Vertex Vector Search index for real embeddings.
    """
    print("[RAG Agent] Would call Vertex Vector Search for:", query)
    return []


def get_rag_results(query: str) -> List[Dict]:
    if USE_VERTEX_VECTOR:
        return search_vector_db(query)
    else:
        return semantic_search_fallback(query)
