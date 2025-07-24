from agents.rag_agent import run_rag_agent
from agents.firestore_history_agent import run_firestore_history_agent
from agents.gemini_fallback_agent import run_gemini_fallback_agent

async def agent_router(tool_name: str, args: dict, fallback: str = "gemini") -> str:
    """
    Routes the tool call to the correct single-tool agent. Falls back to Gemini LLM or Google Search if tool is not found or fails.
    Args:
        tool_name (str): The name of the tool/agent to use.
        args (dict): Arguments for the tool.
        fallback (str): 'gemini' or 'google_search'.
    Returns:
        str: The agent's response.
    """
    try:
        if tool_name == "get_rag_fallback":
            return await run_rag_agent(**args)
        elif tool_name == "store_user_query_history":
            return await run_firestore_history_agent(**args)
        else:
            return f"[Fallback: Gemini] {await run_gemini_fallback_agent(args.get('query', ''))}"
    except Exception as e:
        return f"[Fallback: Gemini] {await run_gemini_fallback_agent(args.get('query', ''))}" 