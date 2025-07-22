from textblob import TextBlob
from typing import Any, Dict, List, Tuple

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

def aggregate_mood_from_unified_data(unified_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Given unified_data from the aggregator, compute mood label, score, and source breakdown.
    """
    twitter_score, twitter_keywords = analyze_sentiment(unified_data.get("twitter", []))
    reddit_score, reddit_keywords = analyze_sentiment(unified_data.get("reddit", []))
    news_score, news_keywords = analyze_sentiment(unified_data.get("news", []))
    google_score, google_keywords = analyze_sentiment(unified_data.get("google_search", []))
    maps_data = unified_data.get("maps", {})
    maps_score = -0.5 if maps_data and isinstance(maps_data, dict) and "duration_in_traffic" in maps_data and maps_data["duration_in_traffic"] != maps_data.get("duration") else 0.0
    maps_keywords = ["traffic"] if maps_score < 0 else []
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
        "source_breakdown": {
            "twitter": {"score": round(twitter_score, 2), "top_keywords": twitter_keywords},
            "reddit": {"score": round(reddit_score, 2), "top_keywords": reddit_keywords},
            "news": {"score": round(news_score, 2), "top_keywords": news_keywords},
            "google_search": {"score": round(google_score, 2), "top_keywords": google_keywords},
            "maps": {"score": round(maps_score, 2), "top_keywords": maps_keywords},
        }
    } 