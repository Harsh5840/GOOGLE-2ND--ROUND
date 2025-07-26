from vertexai.generative_models import GenerativeModel
from shared.utils.logger import log_event

gemini = GenerativeModel("gemini-2.0-flash")

def generate_final_response(
    user_message: str,
    intent: str,
    location: str,
    topic: str,
    unified_data: dict
) -> str:
    """
    Fuse data from multiple sources into a single, helpful city update.
    """

    # Format must-visit places if present
    must_visit_places = unified_data.get('must_visit_places', [])
    if must_visit_places and isinstance(must_visit_places, list):
        must_visit_str = '\n'.join([
            f"- {place.get('name', 'Unknown')} ({place.get('type', 'N/A')}) — {place.get('address', 'No address')}" for place in must_visit_places
        ])
    else:
        must_visit_str = 'None'

    prompt = f"""
You are CityPulseAI — a live Bangalore city assistant. Your job is to analyze reports from multiple sources and provide a clean, summarized response to the user.

User asked: "{user_message}"

Intent: {intent}
Location: {location}
Topic: {topic}

Here are the unified inputs (from multiple APIs):

Reddit Posts:
{unified_data.get('reddit', 'None')}

Twitter Posts:
{unified_data.get('twitter', 'None')}

News Articles:
{unified_data.get('news', 'None')}

Maps Info:
{unified_data.get('maps', 'None')}

Must-Visit Places:
{must_visit_str}

Citizen Reports (Firestore):
{unified_data.get('firestore', 'None')}

RAG Background Info:
{unified_data.get('rag', 'None')}

Google Search Results:
{unified_data.get('google_search', 'None')}

Your task:
- Combine all this into a single short paragraph.
- If must-visit places are listed, mention them clearly in your answer.
- Mention actionable info if any.
- Mention location clearly.
- Be clear and helpful, no repetition.
- If nothing relevant, say so.

Final Answer:
"""
    try:
        response = gemini.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        log_event("ResponseAgent", f"Error: {e}")
        return "Sorry, I couldn't generate an answer right now."
