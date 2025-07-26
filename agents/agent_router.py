from agents.gemini_fallback_agent import run_gemini_fallback_agent

async def agent_router(tool_name: str, args: dict, fallback: str = "gemini") -> str:
    """
    Minimal router for fallback cases. Routes to Gemini LLM fallback.
    Args:
        tool_name (str): The name of the tool/agent to use (unused in current implementation).
        args (dict): Arguments for the tool.
        fallback (str): Always defaults to 'gemini'.
    Returns:
        str: The fallback agent's response.
    """
    try:
        # Currently only handles fallback to Gemini LLM
        return await run_gemini_fallback_agent(args.get('query', ''), user_id=args.get('user_id', 'testuser'))
    except Exception as e:
        return f"Error in fallback: {e}" 