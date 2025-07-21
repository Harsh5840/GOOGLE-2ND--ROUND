# agents/llm_response/response_agent.py

from vertexai.language_models import ChatModel
import json

chat_model = ChatModel.from_pretrained("chat-bison")

def generate_reply(intent: str, entities: dict, tool_results: list, rag_results: list) -> str:
    """
    Uses Gemini to craft a natural-language chatbot response from structured data.
    """
    prompt = f"""
You are a city assistant chatbot.

Craft a friendly, informative response based on:
- User intent: {intent}
- Entities: {json.dumps(entities, indent=2)}
- Tool output (Reddit, real-time tools): {json.dumps(tool_results[:3], indent=2)}
- RAG output (local events): {json.dumps(rag_results[:3], indent=2)}

Respond in 2–4 sentences. Be helpful and local.
If there are no results, say so politely.
"""

    chat = chat_model.start_chat()
    response = chat.send_message(prompt)
    return response.text.strip()
