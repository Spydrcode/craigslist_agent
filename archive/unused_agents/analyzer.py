"""Analyzer Agent - Identify forecasting pain points and opportunities."""

from typing import Dict, Any, List


class AnalyzerAgent:
    """Analyzes leads to identify specific forecasting pain points and value opportunities."""

    def __init__(self):
        self.name = "AnalyzerAgent"

    def analyze(self, scored_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze lead for forecasting pain points.

        Args:
            scored_data: Output from ScorerAgent

        Returns:
            Data with analysis added
        """
        # Skip analysis for low-quality leads
        if scored_data.get('score', 0) < 10:
            return {
                **scored_data,
                "analysis_status": "skipped",
                "analysis_reason": "score_too_low"
            }

        # Identify pain points
        pain_points = self._identify_pain_points(scored_data)

        # Identify forecasting opportunities
        forecast_opportunities = self._identify_forecast_opportunities(scored_data)

        # Generate insights
        insights = self._generate_insights(scored_data, pain_points, forecast_opportunities)

        result = {
            **scored_data,
            "pain_points": pain_points,
            "forecast_opportunities": forecast_opportunities,
            "insights": insights,
            "analysis_status": "success"
        }

        return result

    def _identify_pain_points(self, data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Identify specific pain points from posting data."""
        pain_points = []

        posting_body = data.get('posting_body', '').lower()
        keywords = data.get('keywords', {})
        forecast_signals = keywords.get('forecasting_signals', [])

        # Seasonal staffing challenges
        if any(term in str(forecast_signals).lower() for term in ['seasonal', 'peak season']):
            pain_points.append({
                "category": "seasonal_staffing",
                "description": "Struggling with seasonal demand fluctuations",
                "evidence": "Seasonal language in posting",
                "severity": "high"
            })

        # Project-based uncertainty
        if any(term in str(forecast_signals).lower() for term in ['project-based', 'contract']):
            pain_points.append({
                "category": "project_uncertainty",
                "description": "Difficulty planning headcount for project work",
                "evidence": "Project-based hiring needs",
                "severity": "medium"
            })

        # Volume variability
        if any(term in posting_body for term in ['volume', 'capacity', 'demand']):
            pain_points.append({
                "category": "volume_variability",
                "description": "Unpredictable volume affecting staffing needs",
                "evidence": "Volume/capacity mentions in posting",
                "severity": "high"
            })

        # Growth planning
        if any(term in str(forecast_signals).lower() for term in ['growth', 'expanding', 'scaling']):
            pain_points.append({
                "category": "growth_planning",
                "description": "Scaling challenges with workforce planning",
                "evidence": "Growth indicators in posting",
                "severity": "medium"
            })

        # Multiple hiring needs
        scale_indicators = keywords.get('scale_indicators', [])
        if any(term in str(scale_indicators).lower() for term in ['multiple', 'several']):
            pain_points.append({
                "category": "bulk_hiring",
                "description": "Need to hire multiple people simultaneously",
                "evidence": "Multiple positions mentioned",
                "severity": "medium"
            })

        return pain_points

    def _identify_forecast_opportunities(self, data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Identify what this company could forecast."""
        opportunities = []

        industry = (data.get('company_industry') or '').lower()
        pain_points = self._identify_pain_points(data)

        # Map industries to forecast opportunities
        industry_forecasts = {
            'retail': {
                'what': 'customer traffic and sales volume',
                'timeframe': '2-4 weeks',
                'benefit': 'optimize staffing levels',
                'problem': 'overstaffing during slow periods or understaffing during rushes'
            },
            'hospitality': {
                'what': 'guest reservations and dining volume',
                'timeframe': '3-6 weeks',
                'benefit': 'match staff to expected demand',
                'problem': 'labor costs eating into margins'
            },
            'healthcare': {
                'what': 'patient appointment volume',
                'timeframe': '4-8 weeks',
                'benefit': 'ensure adequate coverage',
                'problem': 'long wait times or idle staff'
            },
            'construction': {
                'what': 'project timelines and labor needs',
                'timeframe': '6-12 weeks',
                'benefit': 'plan crew assignments',
                'problem': 'project delays or excess labor costs'
            },
            'logistics': {
                'what': 'shipment volume and warehouse demand',
                'timeframe': '2-6 weeks',
                'benefit': 'right-size warehouse staff',
                'problem': 'overtime costs or missed deliveries'
            }
        }

        # Match industry to opportunity
        for ind, forecast in industry_forecasts.items():
            if ind in industry or ind in data.get('posting_body', '').lower():
                opportunities.append({
                    "forecast_type": ind,
                    "what_to_predict": forecast['what'],
                    "timeframe": forecast['timeframe'],
                    "benefit": forecast['benefit'],
                    "current_problem": forecast['problem']
                })

        # Default opportunity if no industry match
        if not opportunities:
            opportunities.append({
                "forecast_type": "general_staffing",
                "what_to_predict": "staffing needs",
                "timeframe": "4-6 weeks",
                "benefit": "optimize labor costs",
                "current_problem": "reactive hiring leading to understaffing or overstaffing"
            })

        return opportunities

    def _generate_insights(self, data: Dict[str, Any], pain_points: List[Dict],
                          opportunities: List[Dict]) -> Dict[str, Any]:
        """Generate strategic insights for outreach."""
        insights = {
            "primary_pain": None,
            "best_opportunity": None,
            "talk_track_angle": None,
            "urgency_level": "medium"
        }

        # Identify primary pain point
        if pain_points:
            high_severity = [p for p in pain_points if p['severity'] == 'high']
            insights['primary_pain'] = high_severity[0] if high_severity else pain_points[0]

        # Identify best opportunity
        if opportunities:
            insights['best_opportunity'] = opportunities[0]

        # Determine talk track angle
        score = data.get('score', 0)
        tier = data.get('tier', 5)

        if tier == 1:
            insights['talk_track_angle'] = 'direct_roi'
            insights['urgency_level'] = 'high'
        elif tier == 2:
            insights['talk_track_angle'] = 'pain_point_focused'
            insights['urgency_level'] = 'medium'
        else:
            insights['talk_track_angle'] = 'educational'
            insights['urgency_level'] = 'low'

        # Add specific call-out
        if insights['primary_pain']:
            category = insights['primary_pain']['category']
            insights['opening_hook'] = self._generate_opening_hook(category, data)

        return insights

    def _generate_opening_hook(self, pain_category: str, data: Dict[str, Any]) -> str:
        """Generate opening hook based on pain category."""
        company_name = data.get('company_name', 'your company')

        hooks = {
            'seasonal_staffing': f"I noticed {company_name} is hiring for seasonal roles",
            'project_uncertainty': f"Saw {company_name} is bringing on project-based staff",
            'volume_variability': f"Noticed {company_name} is scaling up capacity",
            'growth_planning': f"Saw {company_name} is expanding operations",
            'bulk_hiring': f"I see {company_name} is hiring multiple positions"
        }

        return hooks.get(pain_category, f"I came across {company_name}'s recent hiring post")
