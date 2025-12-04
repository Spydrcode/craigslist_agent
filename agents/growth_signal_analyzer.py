"""
Growth Signal Analyzer Agent
Analyzes job postings to detect company growth signals and hiring urgency.
"""
import re
from typing import List, Dict, Any
from models_enhanced import (
    JobPostingEnhanced,
    GrowthSignals,
    GrowthStage,
    HiringUrgency
)
from utils import get_logger

logger = get_logger(__name__)


class GrowthSignalAnalyzerAgent:
    """
    Agent specialized in detecting growth signals from job postings.
    Identifies companies in growth/hiring phases suitable for service offerings.
    """

    # Keywords indicating growth
    GROWTH_KEYWORDS = [
        r'\bexpanding\b', r'\bgrowth\b', r'\bgrowing\b', r'\bscaling\b',
        r'\bnew location\b', r'\bnew office\b', r'\bnew market\b',
        r'\brapid growth\b', r'\bfast growing\b', r'\bfast-paced\b',
        r'\bfunded\b', r'\bseries [a-z]\b', r'\binvestment\b',
        r'\bdouble digit\b', r'\byear over year\b'
    ]

    # Urgency indicators
    URGENCY_KEYWORDS = [
        r'\bimmediate\b', r'\burgent\b', r'\basap\b', r'\bstart immediately\b',
        r'\bhiring now\b', r'\bneeded now\b', r'\bquickly\b',
        r'\bmultiple positions\b', r'\bseveral openings\b',
        r'\b\d+\+ positions\b', r'\b\d+ or more\b'
    ]

    # Leadership indicators
    LEADERSHIP_KEYWORDS = [
        r'\bmanager\b', r'\bdirector\b', r'\bvp\b', r'\bhead of\b',
        r'\blead\b', r'\bchief\b', r'\bsenior manager\b',
        r'\bteam lead\b', r'\bleadership\b'
    ]

    # Technology adoption
    TECH_ADOPTION_KEYWORDS = [
        r'\bmoving to\b', r'\bmigrating to\b', r'\badopting\b',
        r'\bmodernizing\b', r'\btransformation\b', r'\bdigital\b',
        r'\bcloud\b', r'\bai\b', r'\bmachine learning\b', r'\bml\b',
        r'\bdata science\b', r'\bautomat\w+\b'
    ]

    def __init__(self):
        """Initialize the Growth Signal Analyzer."""
        logger.info("GrowthSignalAnalyzerAgent initialized")

    def analyze_posting(
        self,
        posting: JobPostingEnhanced
    ) -> GrowthSignals:
        """
        Analyze a single job posting for growth signals.

        Args:
            posting: Enhanced job posting to analyze

        Returns:
            GrowthSignals object with detected indicators
        """
        text = f"{posting.title} {posting.description}".lower()

        signals = GrowthSignals()
        signals.evidence_text = []

        # Check for multiple positions
        signals.is_hiring_multiple = self._detect_multiple_positions(text, posting)

        # Check for leadership positions
        signals.leadership_positions = self._detect_leadership(text)

        # Check for expansion/growth language
        signals.expansion_mentioned = self._detect_expansion(text, signals)

        # Check for new locations
        signals.new_location = self._detect_new_location(text, signals)

        # Check for funding mentions
        signals.funding_mentioned = self._detect_funding(text, signals)

        # Check for technology adoption
        signals.technology_adoption = self._detect_tech_adoption(text, signals)

        # Calculate growth score
        signals.growth_score = self._calculate_growth_score(signals)

        # Classify growth stage
        signals.growth_stage = self._classify_growth_stage(signals)

        # Assess hiring urgency
        signals.hiring_urgency = self._assess_urgency(text, signals)

        logger.debug(
            f"Growth analysis: score={signals.growth_score:.2f}, "
            f"stage={signals.growth_stage}, urgency={signals.hiring_urgency}"
        )

        return signals

    def analyze_multiple_postings(
        self,
        postings: List[JobPostingEnhanced],
        company_name: str
    ) -> GrowthSignals:
        """
        Analyze multiple postings from the same company.

        Args:
            postings: List of job postings from same company
            company_name: Company name

        Returns:
            Aggregated growth signals
        """
        if not postings:
            return GrowthSignals()

        signals = GrowthSignals()
        signals.job_count = len(postings)
        signals.is_hiring_multiple = len(postings) >= 3

        # Aggregate evidence from all postings
        all_text = " ".join([
            f"{p.title} {p.description}" for p in postings
        ]).lower()

        # Check for multiple departments
        departments = self._extract_departments(postings)
        signals.multiple_departments = len(departments) >= 2

        # Check for leadership across postings
        leadership_count = sum(
            1 for p in postings
            if self._detect_leadership(f"{p.title} {p.description}".lower())
        )
        signals.leadership_positions = leadership_count >= 1

        # Check growth indicators
        signals.expansion_mentioned = self._detect_expansion(all_text, signals)
        signals.new_location = self._detect_new_location(all_text, signals)
        signals.funding_mentioned = self._detect_funding(all_text, signals)
        signals.technology_adoption = self._detect_tech_adoption(all_text, signals)

        # Calculate aggregate score
        signals.growth_score = self._calculate_growth_score(signals)
        signals.growth_stage = self._classify_growth_stage(signals)
        signals.hiring_urgency = self._assess_urgency(all_text, signals)

        logger.info(
            f"Analyzed {len(postings)} postings for {company_name}: "
            f"growth_score={signals.growth_score:.2f}, "
            f"stage={signals.growth_stage}"
        )

        return signals

    def _detect_multiple_positions(
        self,
        text: str,
        posting: JobPostingEnhanced
    ) -> bool:
        """Detect if posting is for multiple positions."""
        # Look for explicit mentions
        patterns = [
            r'(\d+)\s*positions',
            r'(\d+)\s*openings',
            r'multiple\s+positions',
            r'several\s+openings',
            r'hiring\s+(\d+)'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                return True

        # Check if urgency signals indicate multiple hires
        for keyword in self.URGENCY_KEYWORDS:
            if re.search(keyword, text):
                if 'multiple' in text or 'several' in text:
                    return True

        return False

    def _detect_leadership(self, text: str) -> bool:
        """Detect leadership positions."""
        for keyword in self.LEADERSHIP_KEYWORDS:
            if re.search(keyword, text):
                return True
        return False

    def _detect_expansion(self, text: str, signals: GrowthSignals) -> bool:
        """Detect expansion/growth language."""
        for keyword in self.GROWTH_KEYWORDS:
            if re.search(keyword, text):
                # Extract context around keyword
                match = re.search(f'(.{{0,50}}{keyword}.{{0,50}})', text)
                if match:
                    signals.evidence_text.append(match.group(1))
                return True
        return False

    def _detect_new_location(self, text: str, signals: GrowthSignals) -> bool:
        """Detect new location openings."""
        patterns = [
            r'new\s+(office|location|site|facility)',
            r'opening\s+(in|at)\s+\w+',
            r'expanding\s+to\s+\w+'
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                signals.evidence_text.append(match.group(0))
                return True
        return False

    def _detect_funding(self, text: str, signals: GrowthSignals) -> bool:
        """Detect funding mentions."""
        patterns = [
            r'series\s+[a-z]',
            r'\$\d+[kmb]\s+(funding|investment)',
            r'recently\s+funded',
            r'backed\s+by',
            r'venture\s+capital'
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                signals.evidence_text.append(match.group(0))
                return True
        return False

    def _detect_tech_adoption(self, text: str, signals: GrowthSignals) -> bool:
        """Detect technology adoption signals."""
        for keyword in self.TECH_ADOPTION_KEYWORDS:
            if re.search(keyword, text):
                match = re.search(f'(.{{0,40}}{keyword}.{{0,40}})', text)
                if match:
                    signals.evidence_text.append(match.group(1))
                return True
        return False

    def _extract_departments(self, postings: List[JobPostingEnhanced]) -> set:
        """Extract department types from job titles."""
        departments = set()
        dept_keywords = {
            'engineering': ['engineer', 'developer', 'software', 'technical'],
            'sales': ['sales', 'account', 'business development'],
            'marketing': ['marketing', 'growth', 'brand'],
            'operations': ['operations', 'ops', 'logistics'],
            'finance': ['finance', 'accounting', 'controller'],
            'hr': ['hr', 'human resources', 'recruiter', 'people'],
            'product': ['product', 'pm'],
            'design': ['design', 'ux', 'ui'],
            'customer_success': ['customer success', 'support', 'service']
        }

        for posting in postings:
            title_lower = posting.title.lower()
            for dept, keywords in dept_keywords.items():
                if any(kw in title_lower for kw in keywords):
                    departments.add(dept)

        return departments

    def _calculate_growth_score(self, signals: GrowthSignals) -> float:
        """Calculate overall growth score (0-1)."""
        score = 0.0

        # Weight different signals
        if signals.is_hiring_multiple:
            score += 0.25
        if signals.multiple_departments:
            score += 0.15
        if signals.leadership_positions:
            score += 0.15
        if signals.expansion_mentioned:
            score += 0.15
        if signals.new_location:
            score += 0.10
        if signals.funding_mentioned:
            score += 0.10
        if signals.technology_adoption:
            score += 0.10

        return min(score, 1.0)

    def _classify_growth_stage(self, signals: GrowthSignals) -> GrowthStage:
        """Classify company growth stage based on signals."""
        score = signals.growth_score

        if score >= 0.7:
            if signals.funding_mentioned or signals.expansion_mentioned:
                return GrowthStage.RAPID_GROWTH
            return GrowthStage.SCALING

        elif score >= 0.4:
            if signals.technology_adoption or signals.new_location:
                return GrowthStage.SCALING
            return GrowthStage.ESTABLISHED

        elif score >= 0.2:
            return GrowthStage.ESTABLISHED

        return GrowthStage.UNKNOWN

    def _assess_urgency(
        self,
        text: str,
        signals: GrowthSignals
    ) -> HiringUrgency:
        """Assess hiring urgency."""
        urgency_count = sum(
            1 for keyword in self.URGENCY_KEYWORDS
            if re.search(keyword, text)
        )

        if urgency_count >= 3 or signals.is_hiring_multiple:
            return HiringUrgency.CRITICAL

        elif urgency_count >= 2 or signals.expansion_mentioned:
            return HiringUrgency.HIGH

        elif urgency_count >= 1 or signals.growth_score >= 0.5:
            return HiringUrgency.MEDIUM

        return HiringUrgency.LOW
