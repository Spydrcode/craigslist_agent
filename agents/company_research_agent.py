"""
Company Research Agent
Performs multi-platform research to build comprehensive company profiles.
"""
import re
import requests
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import time
from models_enhanced import (
    CompanyProfile,
    ResearchQuery,
    PlatformSearchResult
)
from agents.client_agent import ClientAgent
from utils import get_logger

logger = get_logger(__name__)


class CompanyResearchAgent:
    """
    Agent for researching companies across multiple platforms.
    Builds comprehensive profiles including size, tech stack, and contacts.
    """

    def __init__(self, client_agent: Optional[ClientAgent] = None, use_web_search: bool = True):
        """
        Initialize the Company Research Agent.
        
        Args:
            client_agent: ClientAgent instance for AI calls
            use_web_search: Enable OpenAI web search (recommended)
        """
        self.client = client_agent or ClientAgent()
        self.use_web_search = use_web_search
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        logger.info(f"CompanyResearchAgent initialized (web_search={use_web_search})")

    def research_company(
        self,
        query: ResearchQuery
    ) -> CompanyProfile:
        """
        Research a company across multiple platforms.

        Args:
            query: Research query with company details

        Returns:
            Comprehensive company profile
        """
        logger.info(f"Researching company: {query.company_name}")

        profile = CompanyProfile(
            name=query.company_name,
            location=query.location,
            data_sources=[]
        )

        # PRIORITY: Use OpenAI web search if enabled (faster and more reliable)
        if self.use_web_search:
            logger.info("Using OpenAI web search for company research")
            try:
                web_research = self.client.research_company_web(
                    company_name=query.company_name,
                    context=f"Location: {query.location}, Industry: {query.industry or 'Unknown'}"
                )
                
                # Parse web research results and enrich profile
                profile = self._enrich_from_web_search(profile, web_research)
                profile.data_sources.append("openai_web_search")
                
                logger.info(f"Web search completed for {query.company_name}")
                
                # Return early if web search provided sufficient data
                if profile.employee_count or profile.revenue_range:
                    return profile
                    
            except Exception as e:
                logger.warning(f"Web search failed, falling back to manual scraping: {e}")

        # FALLBACK: Manual platform scraping (slower)
        # Research on each platform
        for platform in query.search_platforms:
            try:
                if platform == "google":
                    result = self._search_google(query)
                    self._enrich_from_google(profile, result)
                elif platform == "linkedin":
                    result = self._search_linkedin(query)
                    self._enrich_from_linkedin(profile, result)
                elif platform == "crunchbase":
                    result = self._search_crunchbase(query)
                    self._enrich_from_crunchbase(profile, result)
                elif platform == "glassdoor":
                    result = self._search_glassdoor(query)
                    self._enrich_from_glassdoor(profile, result)

                time.sleep(1)  # Rate limiting

            except Exception as e:
                logger.error(f"Error researching on {platform}: {e}")

        # Use AI to enhance profile
        profile = self._ai_enhance_profile(profile)

        # Calculate confidence score
        profile.confidence_score = self._calculate_confidence(profile)

        logger.info(
            f"Research complete for {query.company_name}. "
            f"Sources: {', '.join(profile.data_sources)}, "
            f"Confidence: {profile.confidence_score:.2f}"
        )

        return profile

    def _search_google(self, query: ResearchQuery) -> PlatformSearchResult:
        """
        Search Google for company information.
        Note: This is a simplified version. For production, use Google Custom Search API.
        """
        result = PlatformSearchResult(
            platform="google",
            query=f"{query.company_name} {query.location or ''}"
        )

        try:
            # Construct search query
            search_terms = [
                f"{query.company_name} company",
                query.location or "",
                "employees size revenue"
            ]
            search_query = " ".join(filter(None, search_terms))

            # For now, return structured placeholder
            # In production, implement actual Google search or use API
            result.results = [{
                "title": f"{query.company_name} - Company Information",
                "snippet": f"Information about {query.company_name}",
                "url": query.domain or ""
            }]
            result.total_found = 1
            result.success = True

        except Exception as e:
            logger.error(f"Google search error: {e}")
            result.success = False
            result.error_message = str(e)

        return result

    def _search_linkedin(self, query: ResearchQuery) -> PlatformSearchResult:
        """
        Search LinkedIn for company profile.
        Note: Requires LinkedIn API access or web scraping (with caution).
        """
        result = PlatformSearchResult(
            platform="linkedin",
            query=query.company_name
        )

        try:
            # Construct LinkedIn company URL guess
            company_slug = query.company_name.lower().replace(' ', '-').replace(',', '')
            linkedin_url = f"https://www.linkedin.com/company/{company_slug}"

            result.results = [{
                "url": linkedin_url,
                "company_name": query.company_name
            }]
            result.total_found = 1
            result.success = True

        except Exception as e:
            logger.error(f"LinkedIn search error: {e}")
            result.success = False
            result.error_message = str(e)

        return result

    def _search_crunchbase(self, query: ResearchQuery) -> PlatformSearchResult:
        """
        Search Crunchbase for funding and company data.
        Note: Requires Crunchbase API key for production use.
        """
        result = PlatformSearchResult(
            platform="crunchbase",
            query=query.company_name
        )

        try:
            # Placeholder for Crunchbase integration
            # In production, use Crunchbase API
            company_slug = query.company_name.lower().replace(' ', '-')
            crunchbase_url = f"https://www.crunchbase.com/organization/{company_slug}"

            result.results = [{
                "url": crunchbase_url,
                "company_name": query.company_name
            }]
            result.total_found = 1
            result.success = True

        except Exception as e:
            logger.error(f"Crunchbase search error: {e}")
            result.success = False
            result.error_message = str(e)

        return result

    def _search_glassdoor(self, query: ResearchQuery) -> PlatformSearchResult:
        """Search Glassdoor for company reviews and size."""
        result = PlatformSearchResult(
            platform="glassdoor",
            query=query.company_name
        )

        try:
            # Placeholder for Glassdoor integration
            result.results = []
            result.total_found = 0
            result.success = True

        except Exception as e:
            logger.error(f"Glassdoor search error: {e}")
            result.success = False
            result.error_message = str(e)

        return result

    def _enrich_from_google(
        self,
        profile: CompanyProfile,
        result: PlatformSearchResult
    ):
        """Enrich profile from Google search results."""
        if not result.success or not result.results:
            return

        profile.data_sources.append("google")

        # Extract domain from results
        for item in result.results:
            if 'url' in item and item['url']:
                domain = self._extract_domain(item['url'])
                if domain and not profile.domain:
                    profile.domain = domain
                    profile.company_website = item['url']

    def _enrich_from_linkedin(
        self,
        profile: CompanyProfile,
        result: PlatformSearchResult
    ):
        """Enrich profile from LinkedIn data."""
        if not result.success or not result.results:
            return

        profile.data_sources.append("linkedin")

        for item in result.results:
            if 'url' in item:
                profile.linkedin_url = item['url']

    def _enrich_from_crunchbase(
        self,
        profile: CompanyProfile,
        result: PlatformSearchResult
    ):
        """Enrich profile from Crunchbase data."""
        if not result.success or not result.results:
            return

        profile.data_sources.append("crunchbase")

        for item in result.results:
            if 'url' in item:
                profile.crunchbase_url = item['url']

    def _enrich_from_glassdoor(
        self,
        profile: CompanyProfile,
        result: PlatformSearchResult
    ):
        """Enrich profile from Glassdoor data."""
        if not result.success or not result.results:
            return

        profile.data_sources.append("glassdoor")

    def _ai_enhance_profile(self, profile: CompanyProfile) -> CompanyProfile:
        """Use AI to enhance and fill gaps in company profile."""
        if not profile.description and profile.company_website:
            try:
                # Use AI to generate company description
                prompt = f"""Based on the company name "{profile.name}" and location "{profile.location or 'unknown'}",
                provide a brief 2-3 sentence description of what this company likely does.
                Keep it factual and professional. If you don't have information, say "Unable to determine"."""

                description = self.client._call_api(
                    messages=[
                        {"role": "system", "content": "You are a business analyst providing company insights."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=150
                )

                if "unable to determine" not in description.lower():
                    profile.description = description.strip()

            except Exception as e:
                logger.error(f"AI enhancement error: {e}")

        return profile

    def _extract_domain(self, url: str) -> Optional[str]:
        """Extract domain from URL."""
        match = re.search(r'https?://([^/]+)', url)
        if match:
            domain = match.group(1)
            # Remove www prefix
            domain = re.sub(r'^www\.', '', domain)
            return domain
        return None

    def _calculate_confidence(self, profile: CompanyProfile) -> float:
        """Calculate confidence score based on data completeness."""
        score = 0.0

        # Data source diversity
        source_count = len(profile.data_sources)
        score += min(source_count * 0.15, 0.45)  # Max 0.45 for sources

        # Profile completeness
        if profile.domain:
            score += 0.10
        if profile.description:
            score += 0.10
        if profile.linkedin_url:
            score += 0.10
        if profile.employee_count_estimate:
            score += 0.10
        if profile.industry:
            score += 0.10
        if profile.tech_stack:
            score += 0.05

        return min(score, 1.0)

    def find_decision_makers(
        self,
        company_name: str,
        titles: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Find decision makers at a company.

        Args:
            company_name: Company name
            titles: Target titles (e.g., ["CTO", "VP Engineering"])

        Returns:
            List of decision makers with contact info
        """
        if titles is None:
            titles = ["CTO", "VP Engineering", "Director of Engineering", "CEO", "COO"]

        logger.info(f"Finding decision makers at {company_name}")

        decision_makers = []

        # Placeholder implementation
        # In production, integrate with:
        # - LinkedIn Sales Navigator API
        # - Hunter.io for email finding
        # - RocketReach or similar services

        logger.info(f"Found {len(decision_makers)} decision makers")
        return decision_makers
    
    def _enrich_from_web_search(self, profile: CompanyProfile, web_research: Dict[str, Any]) -> CompanyProfile:
        """
        Enrich company profile from OpenAI web search results.
        
        Args:
            profile: Company profile to enrich
            web_research: Web research results from ClientAgent
            
        Returns:
            Enriched company profile
        """
        research_text = web_research.get('research_summary', '')
        
        if not research_text or 'error' in web_research:
            logger.warning(f"Web research returned no useful data for {profile.name}")
            return profile
        
        logger.info(f"Enriching profile from web search results ({len(research_text)} chars)")
        
        # Use structured function calling to extract key data points
        try:
            company_data = self.client.extract_company_info_structured(
                job_description=research_text,
                job_title=f"Research: {profile.name}"
            )
            
            # Update profile with extracted data
            if 'company_size' in company_data and company_data['company_size'] != 'unknown':
                # Convert size range to employee count estimate
                size_map = {
                    "1-10": 5,
                    "11-50": 30,
                    "51-200": 125,
                    "201-500": 350,
                    "501-1000": 750,
                    "1001-5000": 3000,
                    "5000+": 10000
                }
                profile.employee_count = size_map.get(company_data['company_size'], None)
            
            if 'industry' in company_data:
                profile.industry = company_data['industry']
            
            if 'growth_indicators' in company_data:
                for indicator in company_data['growth_indicators']:
                    if indicator not in profile.growth_signals.expansion_indicators:
                        profile.growth_signals.expansion_indicators.append(indicator)
            
            if 'hiring_volume_signals' in company_data:
                profile.growth_signals.hiring_indicators = company_data['hiring_volume_signals']
            
            # Store fit score in description for now
            if 'forecasta_fit_score' in company_data:
                profile.description = f"Forecasta Fit: {company_data['forecasta_fit_score']}/10 - {company_data.get('forecasta_fit_reasoning', '')}"
            
            logger.info(f"Profile enriched: {profile.name} ({profile.employee_count} employees, {profile.industry})")
            
        except Exception as e:
            logger.error(f"Failed to extract structured data from web search: {e}")
        
        return profile

    def enrich_with_tech_stack(
        self,
        profile: CompanyProfile
    ) -> CompanyProfile:
        """
        Enrich profile with technology stack information.

        Args:
            profile: Company profile to enrich

        Returns:
            Enriched profile with tech stack
        """
        if not profile.company_website:
            return profile

        try:
            # Use BuiltWith API, Wappalyzer, or similar
            # Placeholder implementation
            logger.info(f"Enriching tech stack for {profile.name}")

            # In production, integrate with:
            # - BuiltWith API
            # - Wappalyzer
            # - StackShare

        except Exception as e:
            logger.error(f"Tech stack enrichment error: {e}")

        return profile
