# agents/rag_search.py

from vertexai.generative_models import GenerativeModel

gemini = GenerativeModel("gemini-1.5-pro")

def get_rag_fallback(location: str, topic: str) -> list:
    """
    If no strong results from Reddit, Twitter or Firestore,
    fallback to a search-style Gemini query on background knowledge.
    """

    prompt = f"""
You are a smart city assistant with access to background city data.
Answer the following query or summarize if available data is minimal.

Location: {location}
Topic: {topic}

Return a list of insights, not more than 5 bullet points.
Example:
- Waterlogging near XYZ Street reported in past 2 days
- Metro delays expected in the area
- Avoid stretch due to ongoing civic repair work
"""

    try:
        response = gemini.generate_content(prompt)
        bullets = [line.strip("- ").strip() for line in response.text.split("\n") if line.strip().startswith("-")]
        return bullets

    except Exception as e:
        print("[RAGSearch] Error:", e)
        return []
