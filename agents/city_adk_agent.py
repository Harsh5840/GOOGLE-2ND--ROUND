from agents.root_agent import run_investigation

def run_city_agent(query: str) -> str:
    result = run_investigation(query)
    return result.get('final_report', '[No report generated]') 