from typing import Any, Dict, List

def aggregate_api_results(
    reddit_data: Dict[str, Any] = None,
    twitter_data: Dict[str, Any] = None,
    news_data: Dict[str, Any] = None,
    maps_data: Dict[str, Any] = None,
    firestore_data: List[Dict[str, Any]] = None,
    rag_data: List[str] = None,
    google_search_data: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Aggregate and normalize results from multiple APIs into a unified structure.
    """
    unified = {
        "reddit": reddit_data.get("posts") if reddit_data and "posts" in reddit_data else [],
        "twitter": twitter_data.get("tweets") if twitter_data and "tweets" in twitter_data else [],
        "news": news_data.get("articles") if news_data and "articles" in news_data else [],
        "maps": maps_data if maps_data else {},
        "firestore": firestore_data if firestore_data else [],
        "rag": rag_data if rag_data else [],
        "google_search": google_search_data if google_search_data else [],
    }
    # Optionally, deduplicate or prioritize here
    return unified
