"""Scorer Agent - Calculate lead quality and assign tier."""

from typing import Dict, Any


class ScorerAgent:
    """Calculates lead quality score (0-30 points) and assigns tier (1-5)."""

    def __init__(self):
        self.name = "ScorerAgent"

    def score(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate lead score and assign tier.

        Args:
            research_data: Output from ResearcherAgent

        Returns:
            Data with score and tier added
        """
        # Check for disqualification
        if not research_data.get('is_valid_lead', True):
            return {
                **research_data,
                "score": 0,
                "tier": 5,
                "score_breakdown": {},
                "scoring_status": "disqualified",
                "disqualified": True
            }

        # Calculate score across 4 categories
        score_breakdown = {
            "company_scale": self._score_company_scale(research_data),
            "forecasting_pain": self._score_forecasting_pain(research_data),
            "accessibility": self._score_accessibility(research_data),
            "data_quality": self._score_data_quality(research_data)
        }

        total_score = sum(score_breakdown.values())
        tier = self._assign_tier(total_score)

        result = {
            **research_data,
            "score": total_score,
            "tier": tier,
            "score_breakdown": score_breakdown,
            "scoring_status": "success",
            "disqualified": False
        }

        return result

    def _score_company_scale(self, data: Dict[str, Any]) -> int:
        """Score company scale indicators (max 9 points)."""
        score = 0

        # Multiple positions (+3)
        keywords = data.get('keywords', {})
        scale_indicators = keywords.get('scale_indicators', [])
        if any(term in str(scale_indicators).lower() for term in ['multiple', 'several', 'hiring multiple']):
            score += 3

        # Salary $50K+ (+2)
        salary = data.get('salary')
        if salary:
            salary_value = salary.get('value') or salary.get('max', 0)
            period = salary.get('period', 'year')
            if period in ['year', 'yr', 'annual'] and salary_value >= 50000:
                score += 2
            elif period in ['hour', 'hr'] and salary_value >= 24:  # ~$50K annually
                score += 2

        # Manager/director roles (+2)
        job_title = data.get('job_title', '').lower()
        if any(term in job_title for term in ['manager', 'director', 'supervisor', 'lead']):
            score += 2

        # Benefits mentioned (+2)
        if any(term in str(scale_indicators).lower() for term in ['benefits', 'health insurance', '401k', 'pto']):
            score += 2

        return min(9, score)

    def _score_forecasting_pain(self, data: Dict[str, Any]) -> int:
        """Score forecasting pain indicators (max 12 points)."""
        score = 0

        keywords = data.get('keywords', {})
        forecast_signals = keywords.get('forecasting_signals', [])
        posting_body = data.get('posting_body', '').lower()

        # Seasonal business (+5)
        if any(term in str(forecast_signals).lower() for term in ['seasonal', 'peak season', 'busy season']):
            score += 5

        # Project-based work (+5)
        if any(term in str(forecast_signals).lower() for term in ['project-based', 'contract', 'temporary']):
            score += 5

        # Volume-driven operations (+4)
        if any(term in posting_body for term in ['volume', 'capacity', 'demand', 'fluctuating']):
            score += 4

        # Growth language (+3)
        if any(term in str(forecast_signals).lower() for term in ['growth', 'expanding', 'scaling']):
            score += 3

        return min(12, score)

    def _score_accessibility(self, data: Dict[str, Any]) -> int:
        """Score accessibility indicators (max 7 points)."""
        score = 0

        # Local company (+3)
        if data.get('is_local'):
            score += 3

        # Small/medium business < 200 employees (+2)
        employee_count = data.get('company_size')
        if employee_count and employee_count < 200:
            score += 2

        # Decision maker identified (+2)
        if data.get('decision_maker'):
            score += 2

        return min(7, score)

    def _score_data_quality(self, data: Dict[str, Any]) -> int:
        """Score data quality (max 2 points)."""
        professionalism = data.get('professionalism_score', 0)

        if professionalism >= 7:
            return 2
        elif professionalism >= 5:
            return 1
        else:
            return 0

    def _assign_tier(self, score: int) -> int:
        """Assign tier based on total score."""
        if score >= 20:
            return 1  # Hot lead
        elif score >= 15:
            return 2  # Warm lead
        elif score >= 10:
            return 3  # Medium lead
        elif score >= 5:
            return 4  # Cold lead
        else:
            return 5  # Very cold / disqualified
