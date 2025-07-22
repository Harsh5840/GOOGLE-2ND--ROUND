from textblob import TextBlob
from typing import Any, Dict, List, Tuple
import re

def analyze_sentiment(texts: List[Any]) -> Tuple[float, List[str]]:
    """
    Analyze sentiment of a list of texts (dicts or strings). Returns average polarity and top keywords.
    """
    if not texts:
        return 0.0, []
    scores = []
    keywords = []
    for t in texts:
        if not t:
            continue
        if isinstance(t, dict):
            content = t.get("text") or t.get("title") or t.get("description") or ""
        else:
            content = str(t)
        if content:
            blob = TextBlob(content)
            scores.append(blob.sentiment.polarity)
            keywords.extend(blob.noun_phrases)
    avg_score = sum(scores) / len(scores) if scores else 0.0
    top_keywords = list(set(keywords))[:5]
    return avg_score, top_keywords

def detect_events(texts: List[Any], source: str) -> List[Dict[str, Any]]:
    """
    Scan texts for event keywords and return a list of detected events with counts and source.
    """
    EVENT_KEYWORDS = [
        "accident", "protest", "festival", "fire", "parade", "closure", "celebration",
        "concert", "emergency", "strike", "jam", "block", "delay", "crowd", "police", "roadwork"
    ]
    event_counts = {}
    for t in texts:
        if not t:
            continue
        if isinstance(t, dict):
            content = t.get("text") or t.get("title") or t.get("description") or ""
        else:
            content = str(t)
        content_lower = content.lower()
        for keyword in EVENT_KEYWORDS:
            if re.search(rf"\b{re.escape(keyword)}\b", content_lower):
                event_counts[keyword] = event_counts.get(keyword, 0) + 1
    return [
        {"type": k, "count": v, "sources": [source]} for k, v in event_counts.items()
    ]

def aggregate_mood_from_unified_data(unified_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Given unified_data from the aggregator, compute mood label, score, source breakdown, and detected events.
    """
    twitter_data = unified_data.get("twitter", [])
    reddit_data = unified_data.get("reddit", [])
    news_data = unified_data.get("news", [])
    google_data = unified_data.get("google_search", [])
    maps_data = unified_data.get("maps", {})

    twitter_score, twitter_keywords = analyze_sentiment(twitter_data)
    reddit_score, reddit_keywords = analyze_sentiment(reddit_data)
    news_score, news_keywords = analyze_sentiment(news_data)
    google_score, google_keywords = analyze_sentiment(google_data)
    maps_score = -0.5 if maps_data and isinstance(maps_data, dict) and "duration_in_traffic" in maps_data and maps_data["duration_in_traffic"] != maps_data.get("duration") else 0.0
    maps_keywords = ["traffic"] if maps_score < 0 else []

    # Event detection for each source
    events = []
    for source, texts in [
        ("twitter", twitter_data),
        ("reddit", reddit_data),
        ("news", news_data),
        ("google_search", google_data)
    ]:
        events.extend(detect_events(texts, source))
    # Merge events with the same type from different sources
    merged_events = {}
    for event in events:
        key = event["type"]
        if key in merged_events:
            merged_events[key]["count"] += event["count"]
            merged_events[key]["sources"].extend(event["sources"])
        else:
            merged_events[key] = event
    merged_events_list = [
        {"type": k, "count": v["count"], "sources": list(set(v["sources"]))}
        for k, v in merged_events.items()
    ]

    source_scores = [twitter_score, reddit_score, news_score, google_score, maps_score]
    mood_score = sum(source_scores) / len(source_scores)
    if mood_score > 0.3:
        mood_label = "happy"
    elif mood_score < -0.3:
        mood_label = "tense"
    elif maps_score < 0:
        mood_label = "busy"
    else:
        mood_label = "neutral"
    return {
        "mood_label": mood_label,
        "mood_score": round(mood_score, 2),
        "events": merged_events_list,
        "source_breakdown": {
            "twitter": {"score": round(twitter_score, 2), "top_keywords": twitter_keywords},
            "reddit": {"score": round(reddit_score, 2), "top_keywords": reddit_keywords},
            "news": {"score": round(news_score, 2), "top_keywords": news_keywords},
            "google_search": {"score": round(google_score, 2), "top_keywords": google_keywords},
            "maps": {"score": round(maps_score, 2), "top_keywords": maps_keywords},
        }
    } 