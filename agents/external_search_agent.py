"""
External Search Agent
Finds real companies based on industry signals (NOT from Craigslist directly).
Uses web search to discover companies in specific industries/locations.
"""
from typing import List, Dict, Any, Optional
import re
import json

from models import JobSignal
from agents.client_agent import ClientAgent
from agents.company_research_agent import CompanyResearchAgent
from utils import get_logger

logger = get_logger(__name__)


class ExternalSearchAgent:
    """
    Agent for discovering companies externally based on job market signals.
    
    This agent takes industry/location signals from Craigslist and uses web search
    to find actual companies operating in those sectors - NOT extracting from posts.
    """
    
    def __init__(self, client_agent: Optional[ClientAgent] = None, use_web_search: bool = True):
        """
        Initialize External Search Agent.
        
        Args:
            client_agent: ClientAgent for AI calls
            use_web_search: Enable web search (required for this agent)
        """
        self.client = client_agent or ClientAgent()
        self.research_agent = CompanyResearchAgent(client_agent=self.client, use_web_search=use_web_search)
        
        if not use_web_search:
            logger.warning("ExternalSearchAgent requires web_search=True for optimal performance")
        
        logger.info("ExternalSearchAgent initialized with web search enabled")
    
    def find_companies_from_signals(
        self,
        signals: List[JobSignal],
        max_companies_per_industry: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Discover companies based on aggregated job signals.
        
        Args:
            signals: List of JobSignal objects from Craigslist
            max_companies_per_industry: Max companies to find per industry
            
        Returns:
            List of discovered companies with basic info:
            [
                {
                    'company_name': str,
                    'website': str,
                    'industry': str,
                    'location': str,
                    'matched_signals': [list of signals that led to this discovery],
                    'source': 'external_search'
                },
                ...
            ]
        """
        logger.info(f"Finding companies from {len(signals)} job signals")
        
        # Step 1: Aggregate signals by industry + location
        signal_groups = self._group_signals_by_industry_location(signals)
        logger.info(f"Identified {len(signal_groups)} industry/location combinations")
        
        # Step 2: For each group, search for companies
        discovered_companies = []
        
        for group_key, group_signals in signal_groups.items():
            industry, location = group_key
            logger.info(f"Searching for {industry} companies in {location} ({len(group_signals)} signals)")
            
            try:
                companies = self._search_companies_for_industry(
                    industry=industry,
                    location=location,
                    signals=group_signals,
                    max_results=max_companies_per_industry
                )
                
                logger.info(f"Found {len(companies)} companies for {industry} in {location}")
                discovered_companies.extend(companies)
                
            except Exception as e:
                logger.error(f"Error searching {industry} in {location}: {e}")
                continue
        
        logger.info(f"Total companies discovered: {len(discovered_companies)}")
        return discovered_companies
    
    def _group_signals_by_industry_location(
        self,
        signals: List[JobSignal]
    ) -> Dict[tuple, List[JobSignal]]:
        """
        Group job signals by (industry, location) pairs.
        
        Returns:
            Dictionary mapping (industry, location) -> [signals]
        """
        groups = {}
        
        for signal in signals:
            key = (signal.industry, signal.location)
            if key not in groups:
                groups[key] = []
            groups[key].append(signal)
        
        return groups
    
    def _search_companies_for_industry(
        self,
        industry: str,
        location: str,
        signals: List[JobSignal],
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for companies in a specific industry/location using AI web search.
        
        Args:
            industry: Industry name (e.g., "Technology")
            location: Location name (e.g., "San Francisco")
            signals: Related job signals (for context)
            max_results: Maximum companies to return
            
        Returns:
            List of company dictionaries
        """
        # Construct detailed search prompt for AI
        signal_summary = self._summarize_signals(signals)
        
        search_prompt = f"""Find companies in the {industry} industry located in {location} that are currently hiring or showing growth signals.

Market Context:
- We detected {len(signals)} hiring signals in this market
- Common job categories: {', '.join(set(s.job_category for s in signals[:5]))}
- Seniority levels being hired: {', '.join(set(s.seniority_level for s in signals[:5]))}
- Growth indicators observed: {', '.join(signals[0].growth_indicators[:3]) if signals[0].growth_indicators else 'None'}

Please search and identify up to {max_results} companies that match these criteria:
1. Operating in {industry} industry
2. Located in or near {location}
3. Currently hiring (check job boards: Indeed, LinkedIn Jobs, Glassdoor)
4. Showing growth signals (new offices, funding, expansion)

For each company, provide:
- Company name
- Website URL
- Brief description (1-2 sentences)
- Number of open positions (if available)
- Recent growth signals (if any)

Return a JSON array of companies."""

        try:
            # Use AI with web search to find companies
            response = self.client.client.chat.completions.create(
                model=self.client.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a company research assistant with access to web search. Find real companies based on industry and location criteria. Always return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": search_prompt
                    }
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Parse the result - it should contain a list of companies
            companies_list = result.get('companies', []) or result.get('results', []) or []
            
            # Standardize format
            standardized_companies = []
            for company in companies_list[:max_results]:
                standardized_companies.append({
                    'company_name': company.get('company_name') or company.get('name', 'Unknown'),
                    'website': company.get('website') or company.get('url', ''),
                    'industry': industry,
                    'location': location,
                    'description': company.get('description', ''),
                    'open_positions': company.get('open_positions') or company.get('job_count', 0),
                    'growth_signals': company.get('growth_signals', []),
                    'matched_signal_industries': [industry],
                    'source': 'external_search'
                })
            
            return standardized_companies
            
        except Exception as e:
            logger.error(f"Web search failed for {industry} in {location}: {e}")
            return []
    
    def _summarize_signals(self, signals: List[JobSignal]) -> str:
        """
        Create a brief summary of job signals for context.
        
        Args:
            signals: List of job signals
            
        Returns:
            Summary string
        """
        if not signals:
            return "No signals available"
        
        total = len(signals)
        categories = list(set(s.job_category for s in signals))[:5]
        urgency_high = sum(1 for s in signals if s.urgency_level == "high")
        senior_roles = sum(1 for s in signals if s.seniority_level in ["senior", "executive"])
        
        summary = (
            f"{total} signals detected. "
            f"Categories: {', '.join(categories)}. "
            f"High urgency: {urgency_high}. "
            f"Senior roles: {senior_roles}."
        )
        
        return summary
