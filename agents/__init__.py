"""
Agent modules for the Craigslist Agent system.

ACTIVE AGENTS (Two-Phase Workflow):
- Phase 1: scraper_agent, quick_filter_agent, company_scorer_enhanced
- Phase 2: parser_agent, growth_signal_analyzer, company_research_agent,
           service_matcher_agent, ml_scoring_agent
- On-demand: outreach_agent
- Supporting: client_agent
"""

# Core Active Agents
from .client_agent import ClientAgent
from .scraper_agent import ScraperAgent
from .parser_agent import ParserAgent
from .quick_filter_agent import QuickFilterAgent
from .company_scorer_enhanced import EnhancedCompanyScoringAgent

# Enhanced Prospecting Agents (Phase 2)
from .growth_signal_analyzer import GrowthSignalAnalyzerAgent
from .company_research_agent import CompanyResearchAgent
from .service_matcher_agent import ServiceMatcherAgent
from .ml_scoring_agent import MLScoringAgent
from .outreach_agent import OutreachAgent

# OpenAI Enhanced Agents
from .file_search_agent import FileSearchAgent
from .visualization_agent import VisualizationAgent
from .conversational_lead_agent import ConversationalLeadAgent, analyze_lead_conversationally
from .batch_processor_agent import BatchProcessorAgent, process_jobs_batch
from .deep_research_agent import DeepResearchAgent

__all__ = [
    # Core agents
    "ClientAgent",
    "ScraperAgent",
    "ParserAgent",
    "QuickFilterAgent",
    "EnhancedCompanyScoringAgent",

    # Phase 2 agents
    "GrowthSignalAnalyzerAgent",
    "CompanyResearchAgent",
    "ServiceMatcherAgent",
    "MLScoringAgent",
    "OutreachAgent",
    
    # OpenAI enhanced
    "FileSearchAgent",
    "VisualizationAgent",
    "ConversationalLeadAgent",
    "analyze_lead_conversationally",
    "BatchProcessorAgent",
    "process_jobs_batch",
    "DeepResearchAgent",
]
