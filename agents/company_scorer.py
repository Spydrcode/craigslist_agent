"""
Company Scoring Agent - Intelligent qualification and ranking of companies
Uses comprehensive criteria to identify the best prospects for services.
"""
from typing import List, Dict, Tuple
from dataclasses import dataclass
import re

from utils import get_logger
from models import RawJobPosting

logger = get_logger(__name__)


@dataclass
class CompanyScore:
    """Detailed scoring breakdown for a company."""
    company_name: str
    total_score: float
    tier: str  # HOT, QUALIFIED, POTENTIAL, SKIP
    job_count: int

    # Score components
    job_count_score: float
    technical_debt_score: float
    growth_signals_score: float
    tech_stack_score: float
    seniority_mix_score: float

    # Extracted insights
    pain_points: List[str]
    tech_stack: List[str]
    growth_indicators: List[str]
    jobs: List[RawJobPosting]


class CompanyScoringAgent:
    """Agent for scoring and ranking companies based on qualification criteria."""

    # Technical debt indicators (25 points max)
    TECH_DEBT_KEYWORDS = [
        'legacy', 'outdated', 'modernize', 'migrate', 'refactor',
        'technical debt', 'rewrite', 'rebuild', 'scaling issues',
        'performance problems', 'slow', 'bottleneck'
    ]

    # Growth stage indicators (20 points max)
    GROWTH_KEYWORDS = [
        'startup', 'early stage', 'series a', 'series b', 'series c',
        'funded', 'venture', 'scaling', 'expanding', 'rapid growth',
        'fast-growing', 'new market', 'recent funding', 'well-funded'
    ]

    # Modern tech stack indicators (15 points max)
    MODERN_TECH = [
        'react', 'vue', 'angular', 'next.js', 'typescript',
        'aws', 'gcp', 'azure', 'kubernetes', 'docker',
        'microservices', 'graphql', 'ci/cd', 'terraform',
        'serverless', 'postgres', 'mongodb', 'redis'
    ]

    # Seniority levels
    SENIOR_KEYWORDS = ['senior', 'lead', 'principal', 'staff', 'architect', 'manager']
    JUNIOR_KEYWORDS = ['junior', 'entry', 'associate', 'intern', 'graduate']

    # Red flags (disqualifiers)
    AGENCY_KEYWORDS = ['agency', 'consulting firm', 'staffing', 'recruiting', 'headhunter']
    SPAM_KEYWORDS = [
        'make money', 'work from home', 'no experience needed',
        'earn $', 'mlm', 'pyramid', 'commission only',
        'driver', 'delivery', 'warehouse', 'forklift'
    ]

    # Pain point patterns
    PAIN_POINT_PATTERNS = [
        'overwhelmed', 'backlog', 'need to move faster',
        'quality issues', 'slow deployment', 'manual process',
        'technical challenges', 'struggling with', 'problems with'
    ]

    def __init__(self):
        logger.info("CompanyScoringAgent initialized")

    def score_companies(
        self,
        company_jobs_dict: Dict[str, List[RawJobPosting]]
    ) -> List[CompanyScore]:
        """
        Score and rank all companies.

        Args:
            company_jobs_dict: Dictionary of {company_name: [jobs]}

        Returns:
            List of CompanyScore objects, sorted by score (highest first)
        """
        logger.info(f"Scoring {len(company_jobs_dict)} companies")

        scores = []
        for company_name, jobs in company_jobs_dict.items():
            score = self._score_company(company_name, jobs)
            if score:  # Skip if None (disqualified)
                scores.append(score)

        # Sort by total score descending
        scores.sort(key=lambda x: x.total_score, reverse=True)

        # Log summary
        hot = sum(1 for s in scores if s.tier == 'HOT')
        qualified = sum(1 for s in scores if s.tier == 'QUALIFIED')
        potential = sum(1 for s in scores if s.tier == 'POTENTIAL')

        logger.info(
            f"Scored companies: {hot} HOT, {qualified} QUALIFIED, "
            f"{potential} POTENTIAL, {len(scores)} total"
        )

        return scores

    def _score_company(
        self,
        company_name: str,
        jobs: List[RawJobPosting]
    ) -> CompanyScore:
        """Score a single company based on all criteria."""

        # Check for red flags first
        if self._has_red_flags(company_name, jobs):
            logger.debug(f"Disqualified (red flags): {company_name}")
            return None

        # Combine all job text for analysis
        all_text = self._get_combined_text(jobs)

        # Score components
        job_count_score = self._score_job_count(len(jobs))
        tech_debt_score = self._score_technical_debt(all_text)
        growth_score = self._score_growth_signals(all_text)
        tech_stack_score = self._score_tech_stack(all_text)
        seniority_score = self._score_seniority_mix(all_text)

        # Calculate base score
        # HIRING VELOCITY is now 70% of the score (max 70 pts out of 100)
        # Everything else is supporting evidence (max 30 pts total)
        base_score = (
            job_count_score +           # Max 70 pts (70%)
            tech_debt_score * 0.6 +     # Max 15 pts (15%) - reduced from 25
            growth_score * 0.5 +        # Max 10 pts (10%) - reduced from 20
            tech_stack_score * 0.33 +   # Max 5 pts (5%) - reduced from 15
            seniority_score * 0.0       # 0 pts - removed, not important
        )

        # Apply multipliers
        multiplier = 1.0

        # 2x if funded
        if any(keyword in all_text for keyword in ['funded', 'series a', 'series b', 'series c']):
            multiplier *= 2.0
            logger.debug(f"{company_name}: Funding multiplier applied (2x)")

        # 1.5x if explicit pain points mentioned
        if any(keyword in all_text for keyword in self.PAIN_POINT_PATTERNS):
            multiplier *= 1.5
            logger.debug(f"{company_name}: Pain point multiplier applied (1.5x)")

        total_score = min(base_score * multiplier, 100)  # Cap at 100

        # Determine tier
        if total_score >= 80:
            tier = 'HOT'
        elif total_score >= 60:
            tier = 'QUALIFIED'
        elif total_score >= 40:
            tier = 'POTENTIAL'
        else:
            tier = 'SKIP'

        # Extract insights
        pain_points = self._extract_pain_points(all_text)
        tech_stack = self._extract_tech_stack(all_text)
        growth_indicators = self._extract_growth_indicators(all_text)

        return CompanyScore(
            company_name=company_name,
            total_score=round(total_score, 1),
            tier=tier,
            job_count=len(jobs),
            job_count_score=job_count_score,
            technical_debt_score=tech_debt_score,
            growth_signals_score=growth_score,
            tech_stack_score=tech_stack_score,
            seniority_mix_score=seniority_score,
            pain_points=pain_points,
            tech_stack=tech_stack,
            growth_indicators=growth_indicators,
            jobs=jobs
        )

    def _has_red_flags(self, company_name: str, jobs: List[RawJobPosting]) -> bool:
        """Check if company should be disqualified."""
        all_text = self._get_combined_text(jobs).lower()
        company_lower = company_name.lower()

        # Check for agency/staffing
        if any(keyword in company_lower or keyword in all_text for keyword in self.AGENCY_KEYWORDS):
            return True

        # Check for spam
        if any(keyword in all_text for keyword in self.SPAM_KEYWORDS):
            return True

        return False

    def _get_combined_text(self, jobs: List[RawJobPosting]) -> str:
        """Combine all job titles and descriptions into one text block."""
        texts = []
        for job in jobs:
            texts.append(job.title.lower())
            if job.description and job.description != "[Quick scan - full details not fetched]":
                texts.append(job.description.lower())
        return ' '.join(texts)

    def _score_job_count(self, count: int) -> float:
        """
        Score based on ACTIVE HIRING VELOCITY (max 70 points - INCREASED WEIGHT).

        This is THE PRIMARY indicator of a company that needs help.

        HYPOTHESIS: More jobs = More desperate = Better prospect

        Scoring:
        - 10+ jobs: EXTREMELY DESPERATE (70 pts) - Will pay anything
        - 7-9 jobs: VERY DESPERATE (60 pts) - Urgent need
        - 5-6 jobs: DESPERATE (50 pts) - Clear growth
        - 3-4 jobs: GROWING (35 pts) - Starting to scale
        - 2 jobs: MAYBE (15 pts) - Small signal
        - 1 job: SKIP (0 pts) - Not growing
        """
        if count >= 10:
            return 70.0  # EXTREMELY DESPERATE
        elif count >= 7:
            return 60.0  # VERY DESPERATE
        elif count >= 5:
            return 50.0  # DESPERATE
        elif count >= 3:
            return 35.0  # GROWING
        elif count >= 2:
            return 15.0  # MAYBE
        else:
            return 0.0   # SKIP

    def _score_technical_debt(self, text: str) -> float:
        """Score technical debt indicators (max 25 points)."""
        matches = sum(1 for keyword in self.TECH_DEBT_KEYWORDS if keyword in text)
        # 5 points per keyword, cap at 25
        return min(matches * 5, 25.0)

    def _score_growth_signals(self, text: str) -> float:
        """Score growth stage indicators (max 20 points)."""
        matches = sum(1 for keyword in self.GROWTH_KEYWORDS if keyword in text)
        # 4 points per keyword, cap at 20
        return min(matches * 4, 20.0)

    def _score_tech_stack(self, text: str) -> float:
        """Score modern tech stack (max 15 points)."""
        matches = sum(1 for tech in self.MODERN_TECH if tech in text)
        # 2 points per tech, cap at 15
        return min(matches * 2, 15.0)

    def _score_seniority_mix(self, text: str) -> float:
        """Score seniority mix (max 10 points)."""
        has_senior = any(keyword in text for keyword in self.SENIOR_KEYWORDS)
        has_junior = any(keyword in text for keyword in self.JUNIOR_KEYWORDS)

        if has_senior and has_junior:
            return 10.0  # Full team building
        elif has_senior:
            return 6.0  # Senior only
        elif has_junior:
            return 3.0  # Junior only
        else:
            return 0.0

    def _extract_pain_points(self, text: str) -> List[str]:
        """Extract mentioned pain points."""
        found = []
        for pattern in self.PAIN_POINT_PATTERNS:
            if pattern in text:
                found.append(pattern)

        for keyword in self.TECH_DEBT_KEYWORDS:
            if keyword in text and keyword not in found:
                found.append(keyword)

        return found[:10]  # Limit to top 10

    def _extract_tech_stack(self, text: str) -> List[str]:
        """Extract mentioned technologies."""
        found = []
        for tech in self.MODERN_TECH:
            if tech in text:
                found.append(tech)
        return found

    def _extract_growth_indicators(self, text: str) -> List[str]:
        """Extract growth stage indicators."""
        found = []
        for indicator in self.GROWTH_KEYWORDS:
            if indicator in text:
                found.append(indicator)
        return found

    def get_top_companies(
        self,
        scored_companies: List[CompanyScore],
        tier_filter: str = None,
        top_n: int = 30
    ) -> List[CompanyScore]:
        """
        Get top N companies, optionally filtered by tier.

        Args:
            scored_companies: List of scored companies
            tier_filter: Only return companies of this tier (HOT, QUALIFIED, POTENTIAL)
            top_n: Max number to return

        Returns:
            Filtered and limited list
        """
        if tier_filter:
            filtered = [c for c in scored_companies if c.tier == tier_filter]
        else:
            # Skip "SKIP" tier by default
            filtered = [c for c in scored_companies if c.tier != 'SKIP']

        return filtered[:top_n]
