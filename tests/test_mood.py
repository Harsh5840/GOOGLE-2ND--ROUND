from shared.utils.mood import aggregate_mood

def test_neutral_mood_score():
    # All sources empty, so all scores are 0.0
    unified_data = {
        "twitter": [],
        "reddit": [],
        "news": [],
        "google_search": [],
        "maps": {},
    }
    result = aggregate_mood(unified_data)
    assert result["mood_label"] == "neutral"
    assert result["mood_score"] == 0.0 