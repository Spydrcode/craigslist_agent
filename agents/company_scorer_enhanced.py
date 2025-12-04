"""
Enhanced Company Scoring Agent - Advanced growth signal detection
Uses sophisticated multi-signal intelligence to identify truly growing companies.

Based on real Craigslist patterns that indicate actual business growth:
- Cross-functional hiring
- Expansion language
- Revenue-driving roles
- Capacity stress signals
- Operational maturity indicators
"""
from typing import List, Dict, Set, Optional
from dataclasses import dataclass, field
from collections import Counter
import re

from utils import get_logger
from models import RawJobPosting

logger = get_logger(__name__)


@dataclass
class GrowthSignals:
    """Detected growth signals for a company."""
    # Signal categories
    cross_functional_hiring: bool = False
    expansion_language_found: bool = False
    revenue_roles: int = 0
    capacity_stress_signals: int = 0
    operational_maturity_signals: int = 0

    # Detailed indicators
    job_categories: Set[str] = field(default_factory=set)
    expansion_phrases: List[str] = field(default_factory=list)
    revenue_role_types: List[str] = field(default_factory=list)
    stress_indicators: List[str] = field(default_factory=list)
    maturity_indicators: List[str] = field(default_factory=list)

    # Metadata
    wage_premium: bool = False
    multi_location: bool = False
    structured_recruiting: bool = False
    high_volume_hiring: bool = False

    # Contact info (for cross-posting detection)
    phone_numbers: Set[str] = field(default_factory=set)
    email_addresses: Set[str] = field(default_factory=set)


@dataclass
class CompanyScore:
    """Enhanced scoring breakdown for a company."""
    company_name: str
    total_score: float
    tier: str  # HOT, QUALIFIED, POTENTIAL, SKIP
    job_count: int

    # Core score components (New weighting)
    hiring_velocity_score: float  # 30% - Still important but not dominant
    growth_signals_score: float   # 40% - NEW: Multi-signal intelligence
    expansion_indicators_score: float  # 20% - NEW: Explicit expansion language
    maturity_score: float         # 10% - NEW: Operational sophistication

    # Growth signals detected
    growth_signals: GrowthSignals

    # Legacy components (for compatibility)
    technical_debt_score: float = 0.0
    tech_stack_score: float = 0.0

    # Extracted insights
    pain_points: List[str] = field(default_factory=list)
    tech_stack: List[str] = field(default_factory=list)
    growth_indicators: List[str] = field(default_factory=list)
    jobs: List[RawJobPosting] = field(default_factory=list)


class EnhancedCompanyScoringAgent:
    """
    Enhanced agent using sophisticated growth detection.

    NEW SCORING MODEL:
    - 30%: Hiring Velocity (job count)
    - 40%: Growth Signals (cross-functional, expansion language, stress)
    - 20%: Expansion Indicators (explicit growth language)
    - 10%: Operational Maturity (structured processes, tech adoption)
    """

    # ==================== EXPANSION LANGUAGE (Indicator #2) ====================
    EXPANSION_KEYWORDS = [
        # Direct expansion
        "we're expanding", "we are expanding", "expanding operations",
        "opening a new location", "opening new locations", "new office",
        "new location", "new branch",

        # Demand-driven
        "due to increased demand", "increased demand", "high demand",
        "rapidly growing", "rapid growth", "fast-growing",
        "high-volume", "high volume",

        # Scaling
        "scaling operations", "we are scaling", "we're scaling",

        # Contract/client growth
        "new contracts", "new clients", "new customers",
        "immediate hires", "hiring immediately", "start immediately",

        # Territory expansion
        "expanding service area", "new service area", "new territory",
        "serving new area", "now hiring for", "expanding route"
    ]

    # ==================== REVENUE-DRIVING ROLES (Indicator #3) ====================
    REVENUE_ROLES = {
        'sales': ['sales rep', 'sales representative', 'account executive', 'business development'],
        'customer_success': ['customer success', 'account manager', 'client success'],
        'appointment_setter': ['appointment setter', 'lead generation', 'appointment coordinator'],
        'technician': ['technician', 'field tech', 'service tech', 'installer', 'repair tech'],
        'driver': ['driver', 'delivery driver', 'route driver', 'courier'],
        'dispatcher': ['dispatcher', 'dispatch coordinator', 'route coordinator'],
        'project_coordinator': ['project coordinator', 'project manager', 'operations coordinator'],
        'fulfillment': ['warehouse', 'picker', 'packer', 'fulfillment', 'shipping'],
    }

    # ==================== CAPACITY STRESS (Indicator #7) ====================
    STRESS_SIGNALS = [
        "need people to start immediately", "start immediately", "immediate start",
        "we are behind on work", "behind on work", "backlog",
        "can't keep up", "cannot keep up", "struggling to keep up",
        "tons of work", "lots of work", "overwhelmed with work",
        "need help asap", "hiring asap", "urgent hiring",
        "overtime available", "overtime guaranteed", "ot available",
        "all the work you can handle", "as much work as you want",
    ]

    # ==================== OPERATIONAL MATURITY (Indicator #8) ====================
    MATURITY_SIGNALS = {
        'crm_systems': ['salesforce', 'hubspot', 'crm', 'zoho', 'pipedrive'],
        'scheduling': ['scheduling software', 'dispatch software', 'route planning'],
        'accounting': ['quickbooks', 'xero', 'accounting software', 'erp'],
        'automation': ['automation', 'ai tools', 'automated', 'workflow automation'],
        'data_tools': ['data entry', 'excel', 'google sheets', 'reporting'],
    }

    STRUCTURED_RECRUITING_SIGNALS = [
        'scheduled interview', 'interview process', 'pre-screen',
        'training program', 'onboarding', 'orientation',
        'career advancement', 'career path', 'promotion opportunities',
        'performance review', 'quarterly reviews'
    ]

    # ==================== HIGH-VOLUME HIRING (Indicator #4) ====================
    VOLUME_PATTERNS = [
        r'hiring (\d+)\+',  # "hiring 10+"
        r'need (\d+)',      # "need 5 technicians"
        r'(\d+) positions', # "15 positions available"
        r'multiple (\w+)',  # "multiple movers"
    ]

    # ==================== RED FLAGS ====================
    AGENCY_KEYWORDS = ['agency', 'staffing', 'recruiting', 'headhunter', 'placement']
    SPAM_KEYWORDS = ['make money from home', 'earn $', 'mlm', 'pyramid', 'commission only']

    def __init__(self):
        logger.info("EnhancedCompanyScoringAgent initialized")

    def score_companies(
        self,
        company_jobs_dict: Dict[str, List[RawJobPosting]]
    ) -> List[CompanyScore]:
        """Score companies using advanced growth signal detection."""
        logger.info(f"Scoring {len(company_jobs_dict)} companies with enhanced signals")

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
    ) -> Optional[CompanyScore]:
        """Score a single company with enhanced signal detection."""

        # Check for red flags first
        if self._has_red_flags(company_name, jobs):
            logger.debug(f"Disqualified (red flags): {company_name}")
            return None

        # Detect growth signals
        growth_signals = self._detect_growth_signals(jobs)

        # Calculate score components
        hiring_velocity_score = self._score_hiring_velocity(len(jobs))
        growth_signals_score = self._score_growth_signals(growth_signals)
        expansion_score = self._score_expansion_indicators(growth_signals)
        maturity_score = self._score_operational_maturity(growth_signals)

        # Calculate total score (NEW WEIGHTING)
        total_score = (
            hiring_velocity_score * 0.30 +   # 30% - Hiring velocity
            growth_signals_score * 0.40 +    # 40% - Growth signals (NEW)
            expansion_score * 0.20 +         # 20% - Expansion indicators (NEW)
            maturity_score * 0.10            # 10% - Maturity (NEW)
        )

        # Apply multipliers
        multiplier = 1.0

        # 2x if explicit expansion language
        if growth_signals.expansion_language_found:
            multiplier *= 2.0
            logger.debug(f"{company_name}: Expansion language multiplier (2x)")

        # 1.5x if cross-functional hiring
        if growth_signals.cross_functional_hiring:
            multiplier *= 1.5
            logger.debug(f"{company_name}: Cross-functional hiring multiplier (1.5x)")

        # 1.3x if capacity stress signals
        if growth_signals.capacity_stress_signals >= 2:
            multiplier *= 1.3
            logger.debug(f"{company_name}: Capacity stress multiplier (1.3x)")

        total_score = min(total_score * multiplier, 100)  # Cap at 100

        # Determine tier (ADJUSTED FOR REAL-WORLD DATA)
        if total_score >= 60:  # Lowered from 80
            tier = 'HOT'
        elif total_score >= 40:  # Lowered from 60
            tier = 'QUALIFIED'
        elif total_score >= 25:  # Lowered from 40
            tier = 'POTENTIAL'
        else:
            tier = 'SKIP'

        # Extract insights
        pain_points = self._extract_pain_points(jobs)

        return CompanyScore(
            company_name=company_name,
            total_score=round(total_score, 1),
            tier=tier,
            job_count=len(jobs),
            hiring_velocity_score=hiring_velocity_score,
            growth_signals_score=growth_signals_score,
            expansion_indicators_score=expansion_score,
            maturity_score=maturity_score,
            growth_signals=growth_signals,
            pain_points=pain_points,
            growth_indicators=growth_signals.expansion_phrases,
            jobs=jobs
        )

    def _detect_growth_signals(self, jobs: List[RawJobPosting]) -> GrowthSignals:
        """Detect all growth signals from job postings."""
        signals = GrowthSignals()
        all_text = self._get_combined_text(jobs).lower()

        # 1. Cross-functional hiring (multiple categories)
        categories = self._detect_job_categories(jobs)
        signals.job_categories = categories
        signals.cross_functional_hiring = len(categories) >= 2

        # 2. Expansion language
        for keyword in self.EXPANSION_KEYWORDS:
            if keyword in all_text:
                signals.expansion_language_found = True
                signals.expansion_phrases.append(keyword)

        # 3. Revenue-driving roles
        for role_type, keywords in self.REVENUE_ROLES.items():
            for keyword in keywords:
                if keyword in all_text:
                    signals.revenue_roles += 1
                    signals.revenue_role_types.append(role_type)
                    break  # Count each role type once

        # 4. High-volume hiring
        signals.high_volume_hiring = self._detect_high_volume(all_text)

        # 7. Capacity stress signals
        for signal in self.STRESS_SIGNALS:
            if signal in all_text:
                signals.capacity_stress_signals += 1
                signals.stress_indicators.append(signal)

        # 8. Operational maturity
        for category, tools in self.MATURITY_SIGNALS.items():
            for tool in tools:
                if tool in all_text:
                    signals.operational_maturity_signals += 1
                    signals.maturity_indicators.append(tool)
                    break

        # 9. Structured recruiting
        for signal in self.STRUCTURED_RECRUITING_SIGNALS:
            if signal in all_text:
                signals.structured_recruiting = True
                signals.maturity_indicators.append(signal)
                break

        # 6. Multi-location indicators
        signals.multi_location = self._detect_multi_location(jobs)

        # Extract contact info (for future cross-posting detection)
        signals.phone_numbers = self._extract_phone_numbers(all_text)
        signals.email_addresses = self._extract_emails(all_text)

        return signals

    def _score_hiring_velocity(self, count: int) -> float:
        """
        Score based on hiring velocity (30% of total).
        Reduced from 70% to 30% in favor of growth signals.
        """
        if count >= 10:
            return 100.0  # EXTREMELY DESPERATE
        elif count >= 7:
            return 85.0   # VERY DESPERATE
        elif count >= 5:
            return 70.0   # DESPERATE
        elif count >= 3:
            return 50.0   # GROWING
        elif count >= 2:
            return 25.0   # MAYBE
        else:
            return 0.0    # SKIP

    def _score_growth_signals(self, signals: GrowthSignals) -> float:
        """
        Score based on detected growth signals (40% of total).
        This is now the PRIMARY scoring component.
        """
        score = 0.0

        # Cross-functional hiring (up to 30 pts)
        if signals.cross_functional_hiring:
            score += 30.0

        # Revenue-driving roles (up to 30 pts)
        score += min(signals.revenue_roles * 10, 30.0)

        # Capacity stress (up to 20 pts)
        score += min(signals.capacity_stress_signals * 10, 20.0)

        # High-volume hiring (20 pts)
        if signals.high_volume_hiring:
            score += 20.0

        return min(score, 100.0)

    def _score_expansion_indicators(self, signals: GrowthSignals) -> float:
        """
        Score based on explicit expansion language (20% of total).
        These are gold-standard signals.
        """
        score = 0.0

        # Expansion language (50 pts)
        if signals.expansion_language_found:
            score += 50.0

        # Multi-location (30 pts)
        if signals.multi_location:
            score += 30.0

        # Multiple expansion phrases (20 pts)
        if len(signals.expansion_phrases) >= 3:
            score += 20.0

        return min(score, 100.0)

    def _score_operational_maturity(self, signals: GrowthSignals) -> float:
        """
        Score based on operational maturity (10% of total).
        Shows company is scaling with systems.
        """
        score = 0.0

        # Tech adoption (40 pts)
        score += min(signals.operational_maturity_signals * 10, 40.0)

        # Structured recruiting (40 pts)
        if signals.structured_recruiting:
            score += 40.0

        # Contact consistency (20 pts) - placeholder for cross-posting
        if len(signals.phone_numbers) > 0 or len(signals.email_addresses) > 0:
            score += 20.0

        return min(score, 100.0)

    def _detect_job_categories(self, jobs: List[RawJobPosting]) -> Set[str]:
        """Detect job categories from titles."""
        categories = set()

        for job in jobs:
            title_lower = job.title.lower()

            # Map titles to categories
            if any(kw in title_lower for kw in ['sales', 'account executive', 'business development']):
                categories.add('sales')
            elif any(kw in title_lower for kw in ['marketing', 'content', 'social media']):
                categories.add('marketing')
            elif any(kw in title_lower for kw in ['operations', 'coordinator', 'project manager']):
                categories.add('operations')
            elif any(kw in title_lower for kw in ['admin', 'assistant', 'receptionist']):
                categories.add('admin')
            elif any(kw in title_lower for kw in ['driver', 'delivery', 'courier']):
                categories.add('drivers')
            elif any(kw in title_lower for kw in ['technician', 'installer', 'repair']):
                categories.add('technicians')
            elif any(kw in title_lower for kw in ['customer service', 'support', 'customer success']):
                categories.add('customer_service')
            elif any(kw in title_lower for kw in ['warehouse', 'fulfillment', 'logistics']):
                categories.add('fulfillment')
            elif any(kw in title_lower for kw in ['engineer', 'developer', 'software']):
                categories.add('engineering')

        return categories

    def _detect_high_volume(self, text: str) -> bool:
        """Detect high-volume hiring indicators."""
        for pattern in self.VOLUME_PATTERNS:
            matches = re.findall(pattern, text)
            if matches:
                # Check if number >= 5
                for match in matches:
                    if match.isdigit() and int(match) >= 5:
                        return True

        # Keywords indicating high volume
        volume_keywords = ['hiring multiple', 'multiple positions', 'several openings', 'many positions']
        return any(kw in text for kw in volume_keywords)

    def _detect_multi_location(self, jobs: List[RawJobPosting]) -> bool:
        """Detect if company is hiring in multiple locations."""
        locations = set()
        for job in jobs:
            if job.location:
                locations.add(job.location.lower())
        return len(locations) >= 2

    def _extract_phone_numbers(self, text: str) -> Set[str]:
        """Extract phone numbers from text."""
        # Simple regex for US phone numbers
        pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        matches = re.findall(pattern, text)
        return set(matches)

    def _extract_emails(self, text: str) -> Set[str]:
        """Extract email addresses from text."""
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(pattern, text)
        return set(matches)

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
        """Combine all job titles and descriptions."""
        texts = []
        for job in jobs:
            texts.append(job.title.lower())
            if job.description and job.description != "[Quick scan - full details not fetched]":
                texts.append(job.description.lower())
        return ' '.join(texts)

    def _extract_pain_points(self, jobs: List[RawJobPosting]) -> List[str]:
        """Extract pain points from jobs."""
        pain_points = []
        all_text = self._get_combined_text(jobs)

        stress_found = [sig for sig in self.STRESS_SIGNALS if sig in all_text]
        expansion_found = [kw for kw in self.EXPANSION_KEYWORDS if kw in all_text]

        pain_points.extend(stress_found[:5])  # Top 5
        pain_points.extend(expansion_found[:5])  # Top 5

        return pain_points[:10]

    def get_top_companies(
        self,
        scored_companies: List[CompanyScore],
        tier_filter: str = None,
        top_n: int = 30
    ) -> List[CompanyScore]:
        """Get top N companies, optionally filtered by tier."""
        if tier_filter:
            filtered = [c for c in scored_companies if c.tier == tier_filter]
        else:
            # Skip "SKIP" tier by default
            filtered = [c for c in scored_companies if c.tier != 'SKIP']

        return filtered[:top_n]
