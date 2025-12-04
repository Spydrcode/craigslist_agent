"""
Service Matcher Agent
Identifies specific service opportunities based on company needs and job postings.
"""
from typing import List, Dict, Any
from models_enhanced import (
    JobPostingEnhanced,
    CompanyProfile,
    ServiceOpportunity,
    HiringUrgency,
    ProspectLead
)
from agents.client_agent import ClientAgent
from utils import get_logger

logger = get_logger(__name__)


class ServiceMatcherAgent:
    """
    Agent for identifying service opportunities from company profiles.
    Analyzes pain points and matches them to service offerings.
    """

    # Service taxonomy with indicators
    SERVICE_INDICATORS = {
        'AI/ML Consulting': {
            'keywords': [
                'machine learning', 'artificial intelligence', 'deep learning',
                'neural networks', 'nlp', 'computer vision', 'data science',
                'predictive analytics', 'recommendation engine'
            ],
            'pain_points': [
                'building ml models', 'data insights', 'automation',
                'predictive capabilities', 'ai strategy'
            ],
            'value_range': '$75K-$200K'
        },
        'Data Engineering': {
            'keywords': [
                'data pipeline', 'etl', 'data warehouse', 'data lake',
                'big data', 'spark', 'kafka', 'airflow', 'data infrastructure'
            ],
            'pain_points': [
                'data quality', 'data integration', 'scaling data',
                'real-time data', 'data architecture'
            ],
            'value_range': '$50K-$150K'
        },
        'Cloud Migration': {
            'keywords': [
                'cloud migration', 'aws', 'azure', 'gcp', 'kubernetes',
                'docker', 'cloud infrastructure', 'serverless', 'microservices'
            ],
            'pain_points': [
                'legacy infrastructure', 'scalability', 'cloud adoption',
                'modernization', 'infrastructure cost'
            ],
            'value_range': '$100K-$300K'
        },
        'DevOps/Platform Engineering': {
            'keywords': [
                'devops', 'ci/cd', 'automation', 'infrastructure as code',
                'terraform', 'ansible', 'jenkins', 'gitlab', 'deployment'
            ],
            'pain_points': [
                'deployment speed', 'infrastructure management',
                'reliability', 'monitoring', 'automation'
            ],
            'value_range': '$60K-$150K'
        },
        'API Development': {
            'keywords': [
                'api', 'rest', 'graphql', 'microservices', 'api gateway',
                'integration', 'webhooks', 'third-party integration'
            ],
            'pain_points': [
                'system integration', 'api design', 'scalable apis',
                'api performance', 'integration complexity'
            ],
            'value_range': '$40K-$100K'
        },
        'Full-Stack Development': {
            'keywords': [
                'full stack', 'react', 'angular', 'vue', 'node',
                'frontend', 'backend', 'web application', 'saas'
            ],
            'pain_points': [
                'product development', 'feature velocity',
                'user experience', 'application performance'
            ],
            'value_range': '$80K-$200K'
        },
        'Data Analytics & BI': {
            'keywords': [
                'analytics', 'business intelligence', 'reporting',
                'dashboard', 'metrics', 'kpi', 'tableau', 'powerbi',
                'data visualization'
            ],
            'pain_points': [
                'data visibility', 'reporting', 'metrics tracking',
                'business insights', 'decision making'
            ],
            'value_range': '$30K-$100K'
        },
        'Mobile App Development': {
            'keywords': [
                'mobile', 'ios', 'android', 'react native', 'flutter',
                'mobile app', 'cross-platform'
            ],
            'pain_points': [
                'mobile presence', 'app development', 'mobile strategy',
                'cross-platform', 'mobile experience'
            ],
            'value_range': '$60K-$180K'
        },
        'Security & Compliance': {
            'keywords': [
                'security', 'compliance', 'gdpr', 'hipaa', 'soc 2',
                'penetration testing', 'cybersecurity', 'encryption'
            ],
            'pain_points': [
                'security vulnerabilities', 'compliance requirements',
                'data protection', 'security audit', 'risk management'
            ],
            'value_range': '$50K-$150K'
        },
        'Process Automation': {
            'keywords': [
                'automation', 'workflow', 'rpa', 'process optimization',
                'efficiency', 'streamline', 'automate'
            ],
            'pain_points': [
                'manual processes', 'efficiency', 'operational overhead',
                'repetitive tasks', 'workflow optimization'
            ],
            'value_range': '$40K-$120K'
        }
    }

    def __init__(self, client_agent: ClientAgent = None):
        """Initialize the Service Matcher Agent."""
        self.client = client_agent or ClientAgent()
        logger.info("ServiceMatcherAgent initialized")

    def identify_opportunities(
        self,
        prospect: ProspectLead
    ) -> List[ServiceOpportunity]:
        """
        Identify service opportunities for a prospect.

        Args:
            prospect: Prospect lead with company and job data

        Returns:
            List of identified service opportunities
        """
        logger.info(f"Identifying opportunities for {prospect.company_profile.name}")

        opportunities = []

        # Analyze job postings for service indicators
        for service_type, indicators in self.SERVICE_INDICATORS.items():
            opportunity = self._match_service(
                service_type,
                indicators,
                prospect.job_postings,
                prospect.company_profile
            )

            if opportunity and opportunity.confidence_score >= 0.4:
                opportunities.append(opportunity)

        # Use AI to enhance opportunity analysis
        if opportunities:
            opportunities = self._ai_enhance_opportunities(
                opportunities,
                prospect
            )

        # Sort by confidence score
        opportunities.sort(key=lambda x: x.confidence_score, reverse=True)

        logger.info(
            f"Identified {len(opportunities)} opportunities for "
            f"{prospect.company_profile.name}"
        )

        return opportunities[:5]  # Return top 5

    def _match_service(
        self,
        service_type: str,
        indicators: Dict[str, Any],
        postings: List[JobPostingEnhanced],
        profile: CompanyProfile
    ) -> ServiceOpportunity:
        """Match a service type against job postings and profile."""

        # Combine all posting text
        all_text = " ".join([
            f"{p.title} {p.description}" for p in postings
        ]).lower()

        # Count keyword matches
        keyword_matches = sum(
            1 for keyword in indicators['keywords']
            if keyword.lower() in all_text
        )

        # Count pain point matches
        pain_point_matches = []
        for pain in indicators['pain_points']:
            if pain.lower() in all_text:
                pain_point_matches.append(pain)

        # Calculate confidence score
        keyword_score = min(keyword_matches / len(indicators['keywords']), 1.0)
        pain_score = len(pain_point_matches) / len(indicators['pain_points'])

        # Weight: 60% keywords, 40% pain points
        confidence_score = (keyword_score * 0.6 + pain_score * 0.4)

        if confidence_score < 0.3:
            return None

        # Extract evidence
        evidence = self._extract_evidence(
            all_text,
            indicators['keywords']
        )

        # Determine urgency
        urgency = self._determine_urgency(postings)

        # Generate reasoning
        reasoning = self._generate_reasoning(
            service_type,
            keyword_matches,
            pain_point_matches,
            len(postings)
        )

        opportunity = ServiceOpportunity(
            service_type=service_type,
            confidence_score=confidence_score,
            reasoning=reasoning,
            pain_points_addressed=pain_point_matches,
            estimated_value=indicators['value_range'],
            urgency=urgency,
            evidence=evidence[:3]  # Top 3 pieces of evidence
        )

        return opportunity

    def _extract_evidence(
        self,
        text: str,
        keywords: List[str]
    ) -> List[str]:
        """Extract evidence snippets from text."""
        import re
        evidence = []

        for keyword in keywords:
            pattern = f'.{{0,50}}{re.escape(keyword)}.{{0,50}}'
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                evidence.append(matches[0].strip())

        return evidence

    def _determine_urgency(
        self,
        postings: List[JobPostingEnhanced]
    ) -> HiringUrgency:
        """Determine hiring urgency from postings."""
        urgency_signals_count = sum(
            len(p.urgency_signals) for p in postings
        )

        if len(postings) >= 5 or urgency_signals_count >= 5:
            return HiringUrgency.CRITICAL
        elif len(postings) >= 3 or urgency_signals_count >= 3:
            return HiringUrgency.HIGH
        elif len(postings) >= 2 or urgency_signals_count >= 1:
            return HiringUrgency.MEDIUM
        else:
            return HiringUrgency.LOW

    def _generate_reasoning(
        self,
        service_type: str,
        keyword_matches: int,
        pain_points: List[str],
        posting_count: int
    ) -> str:
        """Generate reasoning for opportunity identification."""
        reasoning_parts = []

        if keyword_matches > 0:
            reasoning_parts.append(
                f"Found {keyword_matches} relevant keywords indicating need for {service_type}"
            )

        if pain_points:
            reasoning_parts.append(
                f"Company experiencing pain points in: {', '.join(pain_points[:2])}"
            )

        if posting_count > 1:
            reasoning_parts.append(
                f"Multiple job postings ({posting_count}) suggest active hiring in this area"
            )

        return ". ".join(reasoning_parts)

    def _ai_enhance_opportunities(
        self,
        opportunities: List[ServiceOpportunity],
        prospect: ProspectLead
    ) -> List[ServiceOpportunity]:
        """Use AI to enhance and validate opportunities."""

        # Prepare context for AI
        context = self._build_context(prospect)

        for opportunity in opportunities:
            try:
                # Ask AI to refine the reasoning
                prompt = f"""Given this company context:
{context}

Validate and enhance this service opportunity:
Service: {opportunity.service_type}
Current reasoning: {opportunity.reasoning}
Evidence: {', '.join(opportunity.evidence[:2])}

Provide a refined 1-2 sentence reasoning for why this service would be valuable to this company.
Focus on specific business impact."""

                enhanced_reasoning = self.client._call_api(
                    messages=[
                        {"role": "system", "content": "You are a business development analyst identifying service opportunities."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.5,
                    max_tokens=150
                )

                # Update reasoning if AI provides better insight
                if len(enhanced_reasoning) > 20:
                    opportunity.reasoning = enhanced_reasoning.strip()

            except Exception as e:
                logger.error(f"AI enhancement error: {e}")

        return opportunities

    def _build_context(self, prospect: ProspectLead) -> str:
        """Build context string for AI analysis."""
        profile = prospect.company_profile
        postings = prospect.job_postings

        context_parts = [
            f"Company: {profile.name}",
            f"Industry: {profile.industry or 'Unknown'}",
            f"Size: {profile.size_range or 'Unknown'}",
            f"Active job postings: {len(postings)}"
        ]

        if postings:
            job_titles = [p.title for p in postings[:3]]
            context_parts.append(f"Hiring for: {', '.join(job_titles)}")

        if profile.growth_signals:
            context_parts.append(
                f"Growth stage: {profile.growth_signals.growth_stage.value}"
            )

        return "\n".join(context_parts)

    def create_opportunity_summary(
        self,
        opportunities: List[ServiceOpportunity]
    ) -> str:
        """
        Create a summary of service opportunities.

        Args:
            opportunities: List of identified opportunities

        Returns:
            Formatted summary string
        """
        if not opportunities:
            return "No significant service opportunities identified."

        summary = "**Identified Service Opportunities:**\n\n"

        for i, opp in enumerate(opportunities, 1):
            summary += f"{i}. **{opp.service_type}** "
            summary += f"(Confidence: {opp.confidence_score:.0%})\n"
            summary += f"   - {opp.reasoning}\n"
            summary += f"   - Estimated Value: {opp.estimated_value}\n"
            summary += f"   - Urgency: {opp.urgency.value.upper()}\n\n"

        return summary
