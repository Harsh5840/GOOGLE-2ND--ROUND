from vertexai.generative_models import GenerativeModel

gemini = GenerativeModel("gemini-2.0-flash")

def generate_final_response(
    user_message: str,
    intent: str,
    location: str,
    topic: str,
    reddit_posts: list,
    twitter_posts: list,
    firestore_reports: list,
    rag_docs: list
) -> str:
    """
    Fuse data from multiple sources into a single, helpful city update.
    """

    prompt = f"""
You are CityPulseAI — a live Bangalore city assistant. Your job is to analyze reports from multiple sources and provide a clean, summarized response to the user.

User asked: "{user_message}"

Intent: {intent}
Location: {location}
Topic: {topic}

Here are the inputs:

Reddit Posts:
{reddit_posts if reddit_posts else "None"}

Twitter Posts:
{twitter_posts if twitter_posts else "None"}

Citizen Reports (Firestore):
{firestore_reports if firestore_reports else "None"}

RAG Background Info:
{rag_docs if rag_docs else "None"}

News Articles:
{news_articles if news_articles else "None"}

Maps Info:
{maps_info if maps_info else "None"}

Your task:
- Combine all this into a single short paragraph.
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
        print("[ResponseAgent] Error:", e)
        return "Sorry, I couldn't generate an answer right now."
