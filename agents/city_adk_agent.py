from agents.root_agent import run_investigation

async def run_city_agent(query: str) -> str:
    result = await run_investigation(query)
    return result.get('final_report', '[No report generated]') 