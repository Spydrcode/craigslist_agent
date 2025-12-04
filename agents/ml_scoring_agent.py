"""
ML Scoring Agent
Uses machine learning features to score and prioritize leads.
"""
import numpy as np
from typing import List, Dict, Any, Optional
from sklearn.preprocessing import StandardScaler
from models_enhanced import (
    ProspectLead,
    MLFeatures,
    CompanyProfile,
    GrowthSignals,
    HiringUrgency
)
from utils import get_logger

logger = get_logger(__name__)


class MLScoringAgent:
    """
    Agent for scoring leads using machine learning features.
    Implements intelligent lead qualification and prioritization.
    """

    # Industry scoring weights
    INDUSTRY_SCORES = {
        'technology': 1.0,
        'software': 1.0,
        'fintech': 0.95,
        'healthcare tech': 0.9,
        'e-commerce': 0.85,
        'saas': 0.95,
        'consulting': 0.7,
        'manufacturing': 0.6,
        'retail': 0.5,
        'unknown': 0.3
    }

    # Company size scoring
    SIZE_SCORES = {
        '1-10': 0.3,
        '11-50': 0.6,
        '51-200': 0.9,
        '201-500': 1.0,
        '501-1000': 0.85,
        '1000+': 0.7,
        'unknown': 0.4
    }

    def __init__(self):
        """Initialize the ML Scoring Agent."""
        self.scaler = StandardScaler()
        logger.info("MLScoringAgent initialized")

    def score_lead(
        self,
        prospect: ProspectLead
    ) -> ProspectLead:
        """
        Score a prospect lead using ML features.

        Args:
            prospect: Prospect lead to score

        Returns:
            Prospect with updated scores and priority tier
        """
        logger.info(f"Scoring lead: {prospect.company_profile.name}")

        # Extract ML features
        features = self.extract_ml_features(prospect)
        prospect.ml_features = features.dict()

        # Calculate composite scores
        growth_score = self._calculate_growth_score(features)
        hiring_score = self._calculate_hiring_score(features)
        fit_score = self._calculate_fit_score(features, prospect.company_profile)
        opportunity_score = self._calculate_opportunity_score(prospect)

        # Weighted final score (0-100)
        weights = {
            'growth': 0.30,
            'hiring': 0.25,
            'fit': 0.25,
            'opportunity': 0.20
        }

        final_score = (
            growth_score * weights['growth'] +
            hiring_score * weights['hiring'] +
            fit_score * weights['fit'] +
            opportunity_score * weights['opportunity']
        ) * 100

        prospect.lead_score = min(final_score, 100.0)

        # Assign priority tier
        prospect.priority_tier = self._assign_priority_tier(prospect.lead_score)

        logger.info(
            f"Lead scored: {prospect.lead_score:.1f}/100, "
            f"Priority: {prospect.priority_tier}"
        )

        return prospect

    def extract_ml_features(
        self,
        prospect: ProspectLead
    ) -> MLFeatures:
        """
        Extract ML features from prospect data.

        Args:
            prospect: Prospect lead

        Returns:
            MLFeatures object
        """
        profile = prospect.company_profile
        growth_signals = profile.growth_signals
        postings = prospect.job_postings

        features = MLFeatures()

        # Company features
        features.company_size_encoded = self._encode_company_size(
            profile.size_range or 'unknown'
        )
        features.industry_encoded = self._encode_industry(
            profile.industry or 'unknown'
        )

        # Growth features
        if growth_signals:
            features.growth_stage_encoded = self._encode_growth_stage(
                growth_signals.growth_stage.value
            )
        else:
            features.growth_stage_encoded = 0.5

        # Hiring features
        features.job_count = len(postings)
        features.hiring_velocity = self._calculate_hiring_velocity(postings)
        features.position_diversity = self._calculate_position_diversity(postings)
        features.leadership_ratio = self._calculate_leadership_ratio(postings)

        # Urgency features
        features.urgency_keywords_count = sum(
            len(p.urgency_signals) for p in postings
        )
        features.salary_competitiveness = self._calculate_salary_competitiveness(postings)
        features.benefits_richness = self._calculate_benefits_richness(postings)

        # Technology features
        features.tech_stack_size = len(profile.tech_stack) if profile.tech_stack else 0
        features.modern_tech_ratio = self._calculate_modern_tech_ratio(profile.tech_stack or [])

        # Extract tech debt indicators from job postings
        tech_debt_keywords = ['legacy', 'migrate', 'modernize', 'rewrite', 'refactor']
        tech_debt_count = sum(
            1 for p in postings
            for keyword in tech_debt_keywords
            if keyword in p.description.lower()
        )
        features.tech_debt_indicators = min(tech_debt_count / max(len(postings), 1), 1.0)

        # Engagement features
        features.online_presence_score = self._calculate_online_presence(profile)

        # Calculated composite features
        features.growth_momentum_score = self._calculate_growth_score(features)
        features.hiring_health_score = self._calculate_hiring_score(features)
        features.opportunity_fit_score = self._calculate_fit_score(features, profile)

        return features

    def _encode_company_size(self, size_range: str) -> float:
        """Encode company size as numeric score."""
        for size_key, score in self.SIZE_SCORES.items():
            if size_key.lower() in size_range.lower():
                return score
        return self.SIZE_SCORES['unknown']

    def _encode_industry(self, industry: str) -> float:
        """Encode industry as numeric score."""
        industry_lower = industry.lower()
        for ind_key, score in self.INDUSTRY_SCORES.items():
            if ind_key in industry_lower:
                return score
        return self.INDUSTRY_SCORES['unknown']

    def _encode_growth_stage(self, stage: str) -> float:
        """Encode growth stage as numeric score."""
        stage_scores = {
            'early_stage': 0.6,
            'rapid_growth': 1.0,
            'scaling': 0.9,
            'established': 0.5,
            'declining': 0.1,
            'unknown': 0.4
        }
        return stage_scores.get(stage, 0.4)

    def _calculate_hiring_velocity(self, postings: List) -> float:
        """Calculate hiring velocity (jobs posted per time period)."""
        if not postings:
            return 0.0

        # Simplified: use number of postings as proxy
        # In production, calculate based on posting dates
        return min(len(postings) / 10.0, 1.0)  # Normalize to 0-1

    def _calculate_position_diversity(self, postings: List) -> float:
        """Calculate diversity of positions."""
        if not postings:
            return 0.0

        # Extract unique job families
        unique_families = set()
        for posting in postings:
            title_lower = posting.title.lower()
            if 'engineer' in title_lower or 'developer' in title_lower:
                unique_families.add('engineering')
            elif 'sales' in title_lower or 'account' in title_lower:
                unique_families.add('sales')
            elif 'marketing' in title_lower:
                unique_families.add('marketing')
            elif 'product' in title_lower:
                unique_families.add('product')
            elif 'design' in title_lower:
                unique_families.add('design')
            elif 'operations' in title_lower or 'ops' in title_lower:
                unique_families.add('operations')
            else:
                unique_families.add('other')

        return min(len(unique_families) / 5.0, 1.0)  # Normalize to 0-1

    def _calculate_leadership_ratio(self, postings: List) -> float:
        """Calculate ratio of leadership positions."""
        if not postings:
            return 0.0

        leadership_keywords = ['manager', 'director', 'vp', 'head of', 'lead', 'chief']
        leadership_count = sum(
            1 for posting in postings
            if any(kw in posting.title.lower() for kw in leadership_keywords)
        )

        return leadership_count / len(postings)

    def _calculate_salary_competitiveness(self, postings: List) -> float:
        """Calculate salary competitiveness score."""
        if not postings:
            return 0.5

        salaries = []
        for posting in postings:
            if posting.salary_max:
                salaries.append(posting.salary_max)
            elif posting.salary_min:
                salaries.append(posting.salary_min)

        if not salaries:
            return 0.5

        avg_salary = np.mean(salaries)

        # Score based on average salary ranges
        if avg_salary >= 150000:
            return 1.0
        elif avg_salary >= 120000:
            return 0.9
        elif avg_salary >= 100000:
            return 0.8
        elif avg_salary >= 80000:
            return 0.6
        elif avg_salary >= 60000:
            return 0.4
        else:
            return 0.2

    def _calculate_benefits_richness(self, postings: List) -> float:
        """Calculate benefits richness score."""
        if not postings:
            return 0.0

        benefit_keywords = [
            'health insurance', '401k', 'equity', 'stock options',
            'unlimited pto', 'remote', 'flexible', 'bonus',
            'dental', 'vision', 'gym', 'learning budget'
        ]

        total_benefits = 0
        for posting in postings:
            desc_lower = posting.description.lower()
            total_benefits += sum(
                1 for keyword in benefit_keywords
                if keyword in desc_lower
            )

        return min(total_benefits / (len(postings) * len(benefit_keywords)), 1.0)

    def _calculate_modern_tech_ratio(self, tech_stack: List[str]) -> float:
        """Calculate ratio of modern technologies."""
        if not tech_stack:
            return 0.5

        modern_tech = {
            'react', 'vue', 'angular', 'node', 'python', 'go', 'rust',
            'kubernetes', 'docker', 'aws', 'azure', 'gcp',
            'tensorflow', 'pytorch', 'spark', 'kafka',
            'typescript', 'graphql', 'mongodb', 'postgres'
        }

        modern_count = sum(
            1 for tech in tech_stack
            if any(mod in tech.lower() for mod in modern_tech)
        )

        return modern_count / len(tech_stack)

    def _calculate_online_presence(self, profile: CompanyProfile) -> float:
        """Calculate online presence score."""
        score = 0.0

        if profile.company_website:
            score += 0.3
        if profile.linkedin_url:
            score += 0.3
        if profile.crunchbase_url:
            score += 0.2
        if profile.glassdoor_url:
            score += 0.2

        return score

    def _calculate_growth_score(self, features: MLFeatures) -> float:
        """Calculate growth momentum score."""
        score = (
            features.growth_stage_encoded * 0.4 +
            features.hiring_velocity * 0.3 +
            features.position_diversity * 0.2 +
            features.leadership_ratio * 0.1
        )
        return min(score, 1.0)

    def _calculate_hiring_score(self, features: MLFeatures) -> float:
        """Calculate hiring health score."""
        score = (
            min(features.job_count / 10.0, 1.0) * 0.4 +
            features.salary_competitiveness * 0.3 +
            features.benefits_richness * 0.2 +
            (1.0 if features.urgency_keywords_count > 0 else 0.0) * 0.1
        )
        return min(score, 1.0)

    def _calculate_fit_score(
        self,
        features: MLFeatures,
        profile: CompanyProfile
    ) -> float:
        """Calculate opportunity fit score."""
        score = (
            features.industry_encoded * 0.4 +
            features.company_size_encoded * 0.3 +
            features.online_presence_score * 0.2 +
            features.modern_tech_ratio * 0.1
        )
        return min(score, 1.0)

    def _calculate_opportunity_score(self, prospect: ProspectLead) -> float:
        """Calculate total opportunity score."""
        if not prospect.service_opportunities:
            return 0.3  # Default baseline

        # Average confidence across opportunities
        avg_confidence = np.mean([
            opp.confidence_score for opp in prospect.service_opportunities
        ])

        # Weight by number of opportunities
        opportunity_count_factor = min(len(prospect.service_opportunities) / 3.0, 1.0)

        return (avg_confidence * 0.7 + opportunity_count_factor * 0.3)

    def _assign_priority_tier(self, score: float) -> str:
        """Assign priority tier based on score."""
        if score >= 80:
            return "URGENT"
        elif score >= 65:
            return "HIGH"
        elif score >= 45:
            return "MEDIUM"
        else:
            return "LOW"

    def batch_score_leads(
        self,
        prospects: List[ProspectLead]
    ) -> List[ProspectLead]:
        """
        Score multiple leads in batch for efficiency.

        Args:
            prospects: List of prospect leads

        Returns:
            List of scored prospects sorted by score
        """
        logger.info(f"Batch scoring {len(prospects)} leads")

        scored_prospects = [self.score_lead(p) for p in prospects]

        # Sort by score descending
        scored_prospects.sort(key=lambda x: x.lead_score, reverse=True)

        if scored_prospects:
            logger.info(
                f"Batch scoring complete. Top score: {scored_prospects[0].lead_score:.1f}"
            )
        else:
            logger.info("Batch scoring complete. No prospects to score.")

        return scored_prospects
