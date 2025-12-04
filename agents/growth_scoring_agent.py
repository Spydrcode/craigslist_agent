"""
Growth Scoring Agent
Scores companies based on hiring velocity, reviews, web activity, and expansion signals.
Assigns growth scores from 0-100.
"""
from typing import List, Dict, Any, Optional
import json
import re
from datetime import datetime

from models import ExternalCompany
from agents.client_agent import ClientAgent
from utils import get_logger

logger = get_logger(__name__)


class GrowthScoringAgent:
    """
    Agent for scoring companies based on growth signals.
    
    Analyzes multiple signals to assign a growth score (0-100):
    - Hiring velocity: Number of open roles across job boards
    - Review activity: Recent reviews on Glassdoor/Google
    - Web activity: Website updates, blog posts, news
    - Expansion: Multiple locations, new offices, funding rounds
    """
    
    # Scoring weights (total = 100)
    WEIGHTS = {
        'hiring_velocity': 35,  # Number of open roles
        'review_activity': 20,  # Recent reviews/ratings
        'web_activity': 20,     # Website/blog activity
        'expansion': 25,        # Locations, funding, news
    }
    
    def __init__(self, client_agent: Optional[ClientAgent] = None, use_web_search: bool = True):
        """
        Initialize Growth Scoring Agent.
        
        Args:
            client_agent: ClientAgent for AI calls
            use_web_search: Enable web search (required for scoring)
        """
        self.client = client_agent or ClientAgent()
        self.use_web_search = use_web_search
        
        if not use_web_search:
            logger.warning("GrowthScoringAgent requires web_search=True for accurate scoring")
        
        logger.info("GrowthScoringAgent initialized")
    
    def score_companies(
        self,
        companies: List[Dict[str, Any]]
    ) -> List[ExternalCompany]:
        """
        Score multiple companies and return ExternalCompany objects.
        
        Args:
            companies: List of company dictionaries from ExternalSearchAgent
            
        Returns:
            List of ExternalCompany objects with growth scores
        """
        logger.info(f"Scoring {len(companies)} companies for growth signals")
        
        scored_companies = []
        
        for idx, company_data in enumerate(companies, 1):
            logger.info(f"Scoring company {idx}/{len(companies)}: {company_data.get('company_name', 'Unknown')}")
            
            try:
                scored_company = self._score_single_company(company_data)
                scored_companies.append(scored_company)
                
            except Exception as e:
                logger.error(f"Failed to score {company_data.get('company_name')}: {e}")
                # Create a basic ExternalCompany with 0 score
                scored_companies.append(self._create_fallback_company(company_data))
        
        # Sort by growth score (highest first)
        scored_companies.sort(key=lambda x: x.growth_score, reverse=True)
        
        logger.info(f"Scoring complete. Top company: {scored_companies[0].company_name if scored_companies else 'None'} ({scored_companies[0].growth_score:.1f})")
        
        return scored_companies
    
    def _score_single_company(self, company_data: Dict[str, Any]) -> ExternalCompany:
        """
        Score a single company using web search for growth signals.
        
        Args:
            company_data: Company information from external search
            
        Returns:
            ExternalCompany with growth_score and signals
        """
        company_name = company_data.get('company_name', 'Unknown')
        website = company_data.get('website', '')
        location = company_data.get('location', '')
        industry = company_data.get('industry', 'Unknown')
        
        # Use AI with web search to gather growth signals
        research_prompt = f"""Research the company "{company_name}" and assess their growth signals.

Company: {company_name}
Website: {website}
Location: {location}
Industry: {industry}

Please search and analyze the following growth indicators:

1. HIRING VELOCITY (35 points):
   - Search job boards (Indeed, LinkedIn, Glassdoor) for open positions
   - Count total open roles at this company
   - Note if they're hiring across multiple departments

2. REVIEW ACTIVITY (20 points):
   - Check Glassdoor, Google reviews for recent activity
   - Count reviews from last 30-60 days
   - Note overall rating trend (improving/stable/declining)

3. WEB ACTIVITY (20 points):
   - Check their website/blog for recent updates
   - Look for recent press releases or news articles
   - Note frequency of content updates

4. EXPANSION SIGNALS (25 points):
   - Multiple office locations or recent office openings
   - Funding rounds (Series A/B/C, acquisition, IPO)
   - New product launches or market expansions
   - Award recognition or rapid headcount growth

Provide a detailed JSON response with:
{{
    "hiring_velocity": {{
        "open_positions": <number>,
        "job_boards": ["Indeed", "LinkedIn", etc],
        "departments": ["Engineering", "Sales", etc],
        "score": <0-35>
    }},
    "review_activity": {{
        "recent_reviews": <count from last 60 days>,
        "rating_trend": "improving/stable/declining",
        "average_rating": <1-5>,
        "score": <0-20>
    }},
    "web_activity": {{
        "recent_blog_posts": <count from last 3 months>,
        "press_releases": <count from last 6 months>,
        "content_frequency": "high/medium/low",
        "score": <0-20>
    }},
    "expansion": {{
        "locations": ["City1", "City2", etc],
        "funding": "Series X / None / IPO / etc",
        "expansion_news": ["Opened Austin office", "Launched new product", etc],
        "score": <0-25>
    }},
    "total_score": <sum of all scores, 0-100>,
    "confidence": "high/medium/low"
}}

Be realistic with scoring. Return 0 or low scores if information is not available."""

        try:
            response = self.client.client.chat.completions.create(
                model=self.client.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a company growth analyst with access to web search. Analyze companies and provide accurate growth scores based on real data you find online."
                    },
                    {
                        "role": "user",
                        "content": research_prompt
                    }
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            scoring_data = json.loads(response.choices[0].message.content)
            
            # Extract scores and signals
            total_score = float(scoring_data.get('total_score', 0))
            
            # Build comprehensive signals dictionary
            signals = {
                'hiring_velocity': scoring_data.get('hiring_velocity', {}),
                'review_activity': scoring_data.get('review_activity', {}),
                'web_activity': scoring_data.get('web_activity', {}),
                'expansion': scoring_data.get('expansion', {}),
                'confidence': scoring_data.get('confidence', 'low'),
                'scored_at': datetime.utcnow().isoformat()
            }
            
            # Create ExternalCompany object
            external_company = ExternalCompany(
                company_name=company_name,
                website=website,
                industry=industry,
                location=location,
                growth_score=min(100.0, max(0.0, total_score)),  # Clamp to 0-100
                signals=signals,
                source=company_data.get('source', 'external_search'),
                matched_signal_industries=[industry]
            )
            
            logger.info(f"{company_name} scored {total_score:.1f}/100 (confidence: {signals['confidence']})")
            
            return external_company
            
        except Exception as e:
            logger.error(f"Web search scoring failed for {company_name}: {e}")
            # Return fallback
            return self._create_fallback_company(company_data)
    
    def _create_fallback_company(self, company_data: Dict[str, Any]) -> ExternalCompany:
        """
        Create an ExternalCompany with minimal data when scoring fails.
        
        Args:
            company_data: Basic company info
            
        Returns:
            ExternalCompany with default values
        """
        return ExternalCompany(
            company_name=company_data.get('company_name', 'Unknown'),
            website=company_data.get('website'),
            industry=company_data.get('industry', 'Unknown'),
            location=company_data.get('location', 'Unknown'),
            growth_score=0.0,
            signals={
                'error': 'Scoring failed',
                'confidence': 'none'
            },
            source=company_data.get('source', 'external_search'),
            matched_signal_industries=[company_data.get('industry', 'Unknown')]
        )
    
    def get_top_companies(
        self,
        scored_companies: List[ExternalCompany],
        min_score: float = 30.0,
        top_n: Optional[int] = None
    ) -> List[ExternalCompany]:
        """
        Filter and return top-scoring companies.
        
        Args:
            scored_companies: List of scored companies
            min_score: Minimum growth score to include
            top_n: Maximum number to return (None = all above min_score)
            
        Returns:
            Filtered list of top companies
        """
        # Filter by minimum score
        filtered = [c for c in scored_companies if c.growth_score >= min_score]
        
        # Sort by score (already sorted from score_companies, but just in case)
        filtered.sort(key=lambda x: x.growth_score, reverse=True)
        
        # Limit to top N if specified
        if top_n:
            filtered = filtered[:top_n]
        
        logger.info(f"Filtered to {len(filtered)} companies (min_score={min_score})")
        
        return filtered
