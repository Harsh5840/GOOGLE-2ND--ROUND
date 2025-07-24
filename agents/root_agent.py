from google.adk.agents import Agent
from agents.research_agent import create_research_agent, run_research_agent, session_service as research_session_service
from agents.data_agent import create_data_agent, run_data_agent
from agents.analysis_agent import create_analysis_agent, run_analysis_agent
from agents.report_agent import create_report_agent, run_report_agent
import uuid

# Root Agent definition (unchanged)
def create_root_agent():
    return Agent(
        model="gemini-2.0-flash-001",
        name="root_agent",
        instruction="You are the Root Agent. Coordinate the investigation workflow by transferring control to the appropriate specialized agent based on the phase and context.",
        tools=[]
    )

# Phase-based orchestration with real state passing
def run_investigation(query: str, context: dict = None) -> dict:
    context = context or {}
    if 'session_id' not in context:
        context['session_id'] = str(uuid.uuid4())
    if 'user_id' not in context:
        context['user_id'] = 'testuser'
    # Create the session ONCE, before any agent runs
    research_session_service.create_session(
        session_id=context['session_id'],
        user_id=context['user_id'],
        app_name="research_agent"
    )
    # Phase 1: Research
    research_results = run_research_agent(query, context)
    context['research_results'] = research_results
    # Phase 2: Data
    data_results = run_data_agent(query, context)
    context['data_results'] = data_results
    # Phase 3: Analysis
    analysis_results = run_analysis_agent(query, research_results, data_results, context)
    context['analysis_results'] = analysis_results
    # Phase 4: Report
    report_results = run_report_agent(query, research_results, data_results, analysis_results, context)
    context['report_results'] = report_results
    return report_results 