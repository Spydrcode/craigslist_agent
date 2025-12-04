"""
Lead Analysis Agent for Forecasta.
Implements the 8-step lead qualification workflow for job posting analysis.
"""
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from utils import get_logger
from agents.client_agent import ClientAgent
from prompts import (
    get_system_prompt,
    get_step_instructions,
    get_complete_prompt,
    LEAD_SCORING_ALGORITHM,
    PAIN_POINTS_BY_INDUSTRY,
    VALUE_PROP_EXAMPLES
)

logger = get_logger(__name__)


class LeadAnalysisAgent:
    """
    Agent for analyzing job postings and qualifying leads for Forecasta.
    Implements the complete 8-step workflow.
    """

    def __init__(self, client_agent: Optional[ClientAgent] = None):
        """
        Initialize the Lead Analysis Agent.

        Args:
            client_agent: ClientAgent instance for AI-powered analysis
        """
        self.client = client_agent or ClientAgent()
        logger.info("LeadAnalysisAgent initialized")

    def analyze_posting(
        self,
        posting_text: str,
        posting_url: str = None,
        enable_web_search: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze a job posting through the complete 8-step workflow.

        Args:
            posting_text: Raw job posting text
            posting_url: URL of the posting (optional)
            enable_web_search: Whether to perform web research (Step 2)

        Returns:
            Complete lead analysis dictionary
        """
        logger.info("Starting lead analysis workflow")

        # Generate unique lead ID
        lead_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        # Initialize result structure
        result = {
            "lead_id": lead_id,
            "version": "1.0",
            "created_timestamp": timestamp,
            "last_updated": timestamp,
            "source": "craigslist",
            "posting_url": posting_url
        }

        try:
            # STEP 1: Data Extraction & Structuring
            logger.info("STEP 1: Data Extraction & Structuring")
            extraction_data = self._step_1_extract_data(posting_text)
            result.update(extraction_data)

            # STEP 2: Company Research (if enabled)
            if enable_web_search and result.get('company', {}).get('name'):
                logger.info("STEP 2: Company Research")
                research_data = self._step_2_company_research(
                    result['company']['name'],
                    result['company'].get('location', '')
                )
                result['company_research'] = research_data
            else:
                logger.info("STEP 2: Skipped (web search disabled or no company name)")
                result['company_research'] = self._get_empty_research()

            # STEP 3: Lead Scoring
            logger.info("STEP 3: Lead Scoring")
            scoring_data = self._step_3_lead_scoring(result)
            result['lead_scoring'] = scoring_data

            # Check if lead is disqualified
            if scoring_data.get('disqualified', False):
                logger.info(f"Lead DISQUALIFIED: {scoring_data.get('disqualification_reason')}")
                result['outcome_tracking'] = {
                    "status": "disqualified",
                    "contact_attempts": 0,
                    "last_contact_date": None,
                    "conversion_probability": 0.0,
                    "notes": [f"Disqualified: {scoring_data.get('disqualification_reason')}"]
                }
                # Skip remaining steps for disqualified leads
                return result

            # STEP 4: Needs Analysis
            logger.info("STEP 4: Needs Analysis")
            needs_data = self._step_4_needs_analysis(result)
            result['needs_analysis'] = needs_data

            # STEP 5: Value Proposition Generation
            logger.info("STEP 5: Value Proposition Generation")
            value_props = self._step_5_value_propositions(result)
            result['value_propositions'] = value_props

            # STEP 6: Call Script Generation
            logger.info("STEP 6: Call Script Generation")
            call_script = self._step_6_call_script(result)
            result['call_script'] = call_script

            # STEP 7: ML Features
            logger.info("STEP 7: ML Feature Engineering")
            ml_features = self._step_7_ml_features(result)
            result['ml_features'] = ml_features

            # STEP 8: Outcome Tracking Setup
            result['outcome_tracking'] = {
                "status": "new",
                "contact_attempts": 0,
                "last_contact_date": None,
                "conversion_probability": self._calculate_conversion_probability(
                    scoring_data.get('final_score', 0)
                ),
                "notes": []
            }

            logger.info(
                f"Lead analysis complete. Tier: {scoring_data.get('tier')}, "
                f"Score: {scoring_data.get('final_score')}/30"
            )

            return result

        except Exception as e:
            logger.error(f"Lead analysis failed: {e}", exc_info=True)
            result['error'] = str(e)
            result['outcome_tracking'] = {
                "status": "error",
                "notes": [f"Analysis failed: {str(e)}"]
            }
            return result

    def _step_1_extract_data(self, posting_text: str) -> Dict[str, Any]:
        """
        STEP 1: Extract structured data from job posting.
        """
        step_1_schema = get_step_instructions(1)
        
        prompt = f"""Extract structured data from this job posting. You MUST return ONLY valid JSON matching this exact schema:

{{
  "company": {{
    "name": "exact company name or null",
    "location": "location or null",
    "contact": {{
      "phone": "phone or null",
      "email": "email or null",
      "website": "website or null"
    }},
    "posting_date": "YYYY-MM-DD or null"
  }},
  "job": {{
    "title": "job title",
    "positions_count": number or null,
    "employment_type": "full-time/part-time/contract/etc",
    "compensation": "salary text",
    "experience_level": "experience description",
    "benefits": ["benefit1", "benefit2"]
  }},
  "business_signals": {{
    "industry": "Trucking/Logistics, Construction/Trades, Manufacturing, Restaurant/Hospitality, Healthcare, Technology, Professional Services, Retail, or Other",
    "business_model": ["project-based", "seasonal", "volume-driven", "service-based", "recurring"],
    "multiple_positions": true or false,
    "growth_language": true or false,
    "manager_roles": true or false,
    "salary_50k_plus": true or false,
    "benefits_mentioned": true or false,
    "professionalism_score": number from 1-10
  }},
  "red_flags": {{
    "duplicate_posting": true or false,
    "mlm_language": true or false,
    "recruiting_agency": true or false,
    "no_company_name": true or false,
    "spam_indicators": true or false,
    "unprofessional": true or false,
    "total_red_flags": number
  }}
}}

Job Posting:
{posting_text}

CRITICAL INSTRUCTIONS:
- multiple_positions: true if hiring 2+ people
- growth_language: true if words like "expanding", "growing", "new location" appear
- manager_roles: true if hiring manager/supervisor positions
- salary_50k_plus: true if any salary mentioned is $50,000+ per year
- benefits_mentioned: true if ANY benefits are mentioned
- industry: MUST be one of the exact options listed
- business_model: MUST be an array with one or more of the exact options
- professionalism_score: 1-10 based on quality, grammar, specificity
- total_red_flags: count of true red flags

Return ONLY the JSON, no explanation."""

        response = self.client._call_api(
            messages=[
                {"role": "system", "content": "You are a data extraction specialist. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=2000
        )

        try:
            # Extract JSON from response
            data = self._extract_json(response)
            data['raw_posting_text'] = posting_text
            return data
        except Exception as e:
            logger.error(f"Failed to parse Step 1 response: {e}")
            return self._get_empty_step_1()

    def _step_2_company_research(self, company_name: str, location: str) -> Dict[str, Any]:
        """
        STEP 2: Research company online.
        Note: This is a placeholder. Actual web search requires additional tools.
        """
        # TODO: Implement web search integration
        # For now, return empty research data
        logger.warning("Web search not implemented. Returning placeholder research data.")

        return {
            "website": None,
            "verified_legitimate": True,  # Default to true without verification
            "employee_count_estimate": "unknown",
            "revenue_estimate": None,
            "ownership_type": "unknown",
            "years_in_business": None,
            "decision_makers": [],
            "linkedin_company_url": None,
            "online_presence_quality": "unknown",
            "recent_growth_signals": [],
            "research_timestamp": datetime.utcnow().isoformat(),
            "note": "Web search not enabled"
        }

    def _step_3_lead_scoring(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        STEP 3: Score lead using qualification algorithm.
        """
        # Extract relevant data
        business_signals = lead_data.get('business_signals', {})
        red_flags = lead_data.get('red_flags', {})
        company_research = lead_data.get('company_research', {})

        # Check automatic disqualifiers
        total_red_flags = red_flags.get('total_red_flags', 0)
        verified_legitimate = company_research.get('verified_legitimate', True)
        recruiting_agency = red_flags.get('recruiting_agency', False)
        mlm_language = red_flags.get('mlm_language', False)
        ownership_type = company_research.get('ownership_type', 'unknown')

        # Disqualification check
        if total_red_flags >= 2:
            return self._create_disqualified_score("2 or more red flags detected")

        if not verified_legitimate:
            return self._create_disqualified_score("Company could not be verified as legitimate")

        if recruiting_agency:
            return self._create_disqualified_score("Posting is from recruiting agency, not direct employer")

        if ownership_type == "national chain":
            return self._create_disqualified_score("National chain company (not ideal target)")

        if mlm_language:
            return self._create_disqualified_score("MLM/commission-only language detected")

        # Calculate category scores
        company_scale_score = self._score_company_scale(business_signals, company_research)
        forecasting_pain_score = self._score_forecasting_pain(business_signals)
        accessibility_score = self._score_accessibility(business_signals, company_research, red_flags)
        data_quality_score = self._score_data_quality(business_signals)

        final_score = (
            company_scale_score +
            forecasting_pain_score +
            accessibility_score +
            data_quality_score
        )

        # Assign tier
        tier, tier_label, recommendation = self._assign_tier(final_score)

        return {
            "disqualified": False,
            "disqualification_reason": None,
            "category_scores": {
                "company_scale": company_scale_score,
                "forecasting_pain": forecasting_pain_score,
                "accessibility": accessibility_score,
                "data_quality": data_quality_score
            },
            "final_score": final_score,
            "tier": tier,
            "tier_label": tier_label,
            "recommendation": recommendation
        }

    def _step_4_needs_analysis(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        STEP 4: Analyze forecasting needs and pain points.
        """
        business_signals = lead_data.get('business_signals', {})
        industry = business_signals.get('industry', 'Other')
        business_model = business_signals.get('business_model', [])

        # Identify applicable pain points
        pain_points = []

        if 'project-based' in business_model or industry in ['Construction/Trades']:
            pain_points.append({
                "pain_category": "Project-Based Demand",
                "specific_challenge": "Lumpy demand makes staffing decisions difficult",
                "business_impact": "Over-hire = idle labor costs, Under-hire = missed revenue/delays",
                "current_approach_likely": "Gut feel based on pipeline",
                "forecasta_solution": "Pipeline-to-capacity forecasting"
            })

        if 'seasonal' in business_model:
            pain_points.append({
                "pain_category": "Seasonal Workforce Planning",
                "specific_challenge": "When to ramp up/down workforce for peak seasons",
                "business_impact": "Hire too early = payroll waste, Hire too late = can't serve demand",
                "current_approach_likely": "Last year's calendar + weather watching",
                "forecasta_solution": "Multi-year pattern analysis + leading indicators"
            })

        if 'volume-driven' in business_model or industry in ['Manufacturing', 'Restaurant/Hospitality']:
            pain_points.append({
                "pain_category": "Volume-Driven Staffing",
                "specific_challenge": "Matching production/call volume to staffing levels",
                "business_impact": "Overstaffed = labor waste, Understaffed = SLA misses",
                "current_approach_likely": "React to last week's numbers",
                "forecasta_solution": "Demand forecasting with 30-60 day horizon"
            })

        if industry == 'Trucking/Logistics':
            pain_points.append({
                "pain_category": "Driver Capacity Planning",
                "specific_challenge": "Driver capacity planning by lane/route type",
                "business_impact": "Wrong driver mix = deadhead miles or contract penalties",
                "current_approach_likely": "Dispatch manager's intuition",
                "forecasta_solution": "Route volume forecasting + driver tier optimization"
            })

        if business_signals.get('growth_language', False):
            pain_points.append({
                "pain_category": "High-Growth Scaling",
                "specific_challenge": "Scaling headcount without over-hiring",
                "business_impact": "Cash flow constraints + hiring lag time",
                "current_approach_likely": "Reactive hiring when overwhelmed",
                "forecasta_solution": "Growth-adjusted capacity forecasting"
            })

        # Default if no specific pain points identified
        if not pain_points:
            pain_points.append({
                "pain_category": "General Workforce Planning",
                "specific_challenge": "Difficulty predicting staffing needs ahead of time",
                "business_impact": "Reactive hiring leads to understaffing or overstaffing",
                "current_approach_likely": "Historical patterns and manager intuition",
                "forecasta_solution": "Data-driven workforce forecasting"
            })

        # Determine forecast types and horizon
        forecast_types = ["workforce", "capacity"]
        forecast_horizon = "30-90 days"

        if 'seasonal' in business_model:
            forecast_horizon = "quarterly"
            forecast_types.append("seasonal")

        if 'volume-driven' in business_model:
            forecast_types.append("demand")

        # Estimate pain severity
        pain_severity = "MEDIUM"
        if business_signals.get('multiple_positions', False) and business_signals.get('growth_language', False):
            pain_severity = "HIGH"
        elif len(pain_points) <= 1:
            pain_severity = "LOW"

        return {
            "primary_pain_points": pain_points[:3],  # Top 3
            "forecast_types_needed": list(set(forecast_types)),
            "forecast_horizon_recommended": forecast_horizon,
            "estimated_pain_severity": pain_severity
        }

    def _step_5_value_propositions(self, lead_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        STEP 5: Generate custom value propositions.
        """
        business_signals = lead_data.get('business_signals', {})
        needs_analysis = lead_data.get('needs_analysis', {})
        company_name = lead_data.get('company', {}).get('name', 'your company')
        industry = business_signals.get('industry', 'Other')

        pain_points = needs_analysis.get('primary_pain_points', [])
        if not pain_points:
            pain_points = [{"pain_category": "General Workforce Planning"}]

        top_pain = pain_points[0]

        # Generate value props
        value_props = []

        # Short version
        short_value_prop = self._generate_value_prop(
            industry=industry,
            pain_category=top_pain.get('pain_category', ''),
            company_name=company_name,
            length='short'
        )

        value_props.append({
            "version": "short",
            "text": short_value_prop,
            "pain_addressed": top_pain.get('pain_category', ''),
            "outcome_emphasized": "Time savings and accuracy"
        })

        # Medium version (recommended)
        medium_value_prop = self._generate_value_prop(
            industry=industry,
            pain_category=top_pain.get('pain_category', ''),
            company_name=company_name,
            length='medium'
        )

        value_props.append({
            "version": "medium",
            "text": medium_value_prop,
            "pain_addressed": top_pain.get('pain_category', ''),
            "outcome_emphasized": "Specific forecasting outcome"
        })

        return value_props

    def _step_6_call_script(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        STEP 6: Generate personalized call script.
        """
        company = lead_data.get('company', {})
        job = lead_data.get('job', {})
        needs = lead_data.get('needs_analysis', {})
        value_props = lead_data.get('value_propositions', [])

        company_name = company.get('name', 'the company')
        job_title = job.get('title', 'position')
        positions_count = job.get('positions_count')
        
        # Convert positions_count to int if it's a string
        if isinstance(positions_count, str):
            try:
                # Extract number from string like "5+" or "5-7"
                import re
                match = re.search(r'\d+', positions_count)
                if match:
                    positions_count = int(match.group())
                else:
                    positions_count = None
            except:
                positions_count = None

        pain_points = needs.get('primary_pain_points', [])
        top_pain = pain_points[0] if pain_points else {}

        recommended_value_prop = value_props[0]['text'] if value_props else "forecast your workforce needs more accurately"

        # Determine target contact
        target_contact = "Operations Manager or Owner"
        if job.get('title', '').lower().__contains__('manager'):
            target_contact = "Operations Manager"

        # Create diagnosis question
        diagnosis_question = self._create_diagnosis_question(
            top_pain.get('pain_category', 'Workforce Planning'),
            lead_data.get('business_signals', {}).get('industry', 'Other')
        )

        script = {
            "target_contact": target_contact,
            "main_script": {
                "introduction": f'Hi, this is [Your Name] with Forecasta - is this [Decision Maker]? Great. Do you have about 60 seconds? I promise this isn\'t a typical sales call.',
                "pattern_interrupt": f'I saw you guys posted for {positions_count if positions_count and positions_count > 1 else "a"} {job_title} position{"s" if positions_count and positions_count > 1 else ""} recently, which usually means you\'re either growing or having trouble keeping up with demand.',
                "diagnosis_question": diagnosis_question,
                "value_statement": f'That\'s exactly what we help companies like {company_name} solve. {recommended_value_prop}',
                "meeting_ask": f'I\'d love to show you how this would work for {company_name} specifically. Are you free for 15 minutes this Thursday at 10am, or would Friday afternoon work better?'
            },
            "alternative_openings": [
                f"Quick question about your {job_title} hiring...",
                f"I noticed {company_name} is expanding your team...",
                f"Saw your posting for {job_title} - got a minute?"
            ],
            "objection_handling": {
                "not_interested": f"Totally fair - can I ask, how are you currently forecasting your staffing needs for next quarter? [Listen] That's a solid approach. The reason I called is because most {lead_data.get('business_signals', {}).get('industry', 'companies')} tell us {top_pain.get('specific_challenge', 'predicting staffing needs is challenging')}. Is that something you're experiencing too?",
                "send_info": "I could do that, but honestly, a generic email won't be as useful as 15 minutes where I can look at your actual situation. How about this - let's jump on a quick call Thursday, and if it's not relevant, you can hang up and I'll never bother you again. Fair?",
                "no_budget": "I totally understand budget constraints. This isn't about buying software - it's about having visibility into your capacity needs so you can make better hiring decisions. Even if you never buy anything, would 15 minutes to see if this approach makes sense be valuable?",
                "already_doing_this": f"That's great! How are you currently forecasting? [Listen] That's a solid approach. The reason I'm reaching out is because we've found that even companies doing forecasting manually often struggle with {top_pain.get('specific_challenge', 'accuracy')}. Would you be open to comparing approaches?"
            },
            "notes_for_caller": [
                f"They're hiring {positions_count if positions_count else 'for'} {job_title}, so they're definitely thinking about capacity",
                f"Their pain severity is estimated as {needs.get('estimated_pain_severity', 'MEDIUM')}",
                "If they're resistant, pivot to asking how they currently forecast - people love talking about their processes"
            ]
        }

        return script

    def _step_7_ml_features(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        STEP 7: Generate ML feature encodings.
        """
        business_signals = lead_data.get('business_signals', {})
        company_research = lead_data.get('company_research', {})
        lead_scoring = lead_data.get('lead_scoring', {})
        needs = lead_data.get('needs_analysis', {})

        # Industry encoding
        industry = business_signals.get('industry', 'Other')
        industry_code = industry.lower().replace('/', '_').replace(' ', '_')

        # Business model encoding
        business_model = business_signals.get('business_model', [])
        business_model_code = '_'.join(sorted(business_model)) if business_model else 'unknown'

        # Company size bucket
        employee_estimate = company_research.get('employee_count_estimate', 'unknown')
        company_size_bucket = self._bucket_company_size(employee_estimate)

        # Pain severity (0-1)
        pain_severity_map = {'LOW': 0.33, 'MEDIUM': 0.66, 'HIGH': 1.0}
        pain_severity_score = pain_severity_map.get(
            needs.get('estimated_pain_severity', 'MEDIUM'),
            0.5
        )

        # Accessibility score (0-1)
        accessibility_raw = lead_scoring.get('category_scores', {}).get('accessibility', 0)
        accessibility_score = min(accessibility_raw / 7.0, 1.0)

        # Data quality score (0-1)
        professionalism = business_signals.get('professionalism_score')
        if professionalism is not None:
            data_quality_score = min(professionalism / 10.0, 1.0)
        else:
            data_quality_score = 0.5  # Default to middle score

        return {
            "industry_code": industry_code,
            "business_model_code": business_model_code,
            "company_size_bucket": company_size_bucket,
            "pain_severity_score": pain_severity_score,
            "accessibility_score": accessibility_score,
            "data_quality_score": data_quality_score
        }

    # Helper methods

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON object from text response."""
        # Try to find JSON in code blocks
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))

        # Try to find JSON object directly
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))

        raise ValueError("No valid JSON found in response")

    def _get_empty_step_1(self) -> Dict[str, Any]:
        """Return empty Step 1 data structure."""
        return {
            "company": {"name": None, "location": None, "contact": {}, "posting_date": None},
            "job": {"title": None, "positions_count": None, "employment_type": None,
                    "compensation": None, "experience_level": None, "benefits": []},
            "business_signals": {"industry": "Other", "business_model": [],
                                 "professionalism_score": 5},
            "red_flags": {"total_red_flags": 0},
            "raw_posting_text": ""
        }

    def _get_empty_research(self) -> Dict[str, Any]:
        """Return empty research data."""
        return {
            "website": None,
            "verified_legitimate": True,
            "employee_count_estimate": "unknown",
            "revenue_estimate": None,
            "ownership_type": "unknown",
            "years_in_business": None,
            "decision_makers": [],
            "linkedin_company_url": None,
            "online_presence_quality": "unknown",
            "recent_growth_signals": [],
            "research_timestamp": datetime.utcnow().isoformat()
        }

    def _create_disqualified_score(self, reason: str) -> Dict[str, Any]:
        """Create a disqualified scoring result."""
        return {
            "disqualified": True,
            "disqualification_reason": reason,
            "category_scores": {
                "company_scale": 0,
                "forecasting_pain": 0,
                "accessibility": 0,
                "data_quality": 0
            },
            "final_score": 0,
            "tier": "TIER 5",
            "tier_label": "REJECT",
            "recommendation": "REJECT"
        }

    def _score_company_scale(self, signals: Dict, research: Dict) -> int:
        """Calculate company scale score (max 9 points)."""
        score = 0

        if signals.get('multiple_positions', False):
            score += 3
        if signals.get('salary_50k_plus', False):
            score += 2
        if signals.get('manager_roles', False):
            score += 2
        if signals.get('benefits_mentioned', False):
            score += 2

        employee_count = research.get('employee_count_estimate', 'unknown')
        if '20' in str(employee_count) or '50' in str(employee_count) or '100' in str(employee_count):
            score += 2
        elif '200' in str(employee_count) or '+' in str(employee_count):
            score += 1

        return min(score, 9)

    def _score_forecasting_pain(self, signals: Dict) -> int:
        """Calculate forecasting pain score (max 12 points)."""
        score = 0

        industry = signals.get('industry', '')
        business_model = signals.get('business_model', [])

        # Seasonal business
        if 'seasonal' in business_model or industry in ['Construction/Trades']:
            score += 5

        # Project-based
        if 'project-based' in business_model:
            score += 5

        # Volume-dependent
        if 'volume-driven' in business_model or industry in ['Manufacturing', 'Restaurant/Hospitality']:
            score += 4

        # Growth language
        if signals.get('growth_language', False):
            score += 3

        # Multiple positions
        positions = signals.get('positions_count')
        if positions is not None and positions >= 5:
            score += 3

        return min(score, 12)

    def _score_accessibility(self, signals: Dict, research: Dict, red_flags: Dict) -> int:
        """Calculate accessibility score (max 7 points)."""
        score = 0

        ownership = research.get('ownership_type', 'unknown')
        if ownership in ['local', 'regional']:
            score += 3

        employee_count = research.get('employee_count_estimate', 'unknown')
        if 'unknown' not in str(employee_count).lower():
            try:
                # Parse employee count
                if '<' in str(employee_count) or '20' in str(employee_count) or '50' in str(employee_count):
                    score += 2
            except:
                pass

        if research.get('decision_makers', []):
            score += 2

        if not red_flags.get('recruiting_agency', False):
            score += 1

        return min(score, 7)

    def _score_data_quality(self, signals: Dict) -> int:
        """Calculate data quality score (max 2 points)."""
        professionalism = signals.get('professionalism_score')

        # Handle None or missing professionalism score
        if professionalism is None:
            return 1  # Default to middle score

        if professionalism >= 7:
            return 2
        elif professionalism >= 5:
            return 1
        else:
            return 0

    def _assign_tier(self, score: int) -> tuple:
        """Assign tier based on final score."""
        if score >= 20:
            return "TIER 1", "TOP PRIORITY", "PURSUE"
        elif score >= 15:
            return "TIER 2", "QUALIFIED LEAD", "PURSUE"
        elif score >= 10:
            return "TIER 3", "MONITOR", "MONITOR"
        elif score >= 5:
            return "TIER 4", "LOW PRIORITY", "MONITOR"
        else:
            return "TIER 5", "REJECT", "REJECT"

    def _calculate_conversion_probability(self, score: int) -> float:
        """Estimate conversion probability based on score."""
        # Simple linear mapping
        return min(score / 30.0, 1.0)

    def _bucket_company_size(self, employee_estimate: str) -> str:
        """Bucket company size."""
        estimate_lower = str(employee_estimate).lower()

        if 'unknown' in estimate_lower:
            return 'unknown'

        try:
            if '<20' in estimate_lower or '1-' in estimate_lower:
                return 'micro'
            elif '20-' in estimate_lower or '50-' in estimate_lower:
                return 'small'
            elif '100' in estimate_lower or '200' in estimate_lower:
                return 'medium'
            else:
                return 'unknown'
        except:
            return 'unknown'

    def _generate_value_prop(
        self,
        industry: str,
        pain_category: str,
        company_name: str,
        length: str = 'medium'
    ) -> str:
        """Generate custom value proposition."""
        # Use examples as templates
        if industry == 'Construction/Trades':
            base = "Turn your project pipeline into crew capacity forecasts so you know if you need 5 or 15 workers next quarter - not next week."
        elif industry == 'Trucking/Logistics':
            base = "Predict driver requirements by lane type 90 days out so you match capacity to contracts instead of paying deadhead miles or missing revenue."
        elif industry == 'Manufacturing':
            base = "Align warehouse staffing to production forecasts automatically so you stop paying idle workers or missing shipments."
        elif industry == 'Restaurant/Hospitality':
            base = "Forecast staffing needs by location and season so you're not overstaffed in January or understaffed in June."
        else:
            base = f"Forecast your workforce needs 60-90 days ahead so you stop reactive hiring and start planning with confidence."

        if length == 'short':
            return base.split(' so ')[0] + '.'

        return base

    def _create_diagnosis_question(self, pain_category: str, industry: str) -> str:
        """Create targeted diagnosis question."""
        if 'Project' in pain_category:
            return "When you're looking at your project pipeline right now, how far ahead can you confidently predict whether you'll need 5 crew members or 15?"
        elif 'Seasonal' in pain_category:
            return "How do you currently decide when to start ramping up your workforce for the busy season?"
        elif 'Volume' in pain_category or 'Demand' in pain_category:
            return "How far ahead can you accurately forecast your staffing needs based on expected volume?"
        elif industry == 'Trucking/Logistics':
            return "How are you currently planning driver capacity across your different routes and lanes?"
        else:
            return "How are you currently forecasting your staffing needs for the next 60-90 days?"

    def generate_dashboard_summary(self, lead_data: Dict[str, Any]) -> str:
        """
        STEP 8: Generate markdown dashboard summary.

        Args:
            lead_data: Complete lead analysis data

        Returns:
            Markdown formatted summary
        """
        company = lead_data.get('company', {})
        scoring = lead_data.get('lead_scoring', {})
        research = lead_data.get('company_research', {})
        needs = lead_data.get('needs_analysis', {})
        value_props = lead_data.get('value_propositions', [])
        call_script = lead_data.get('call_script', {})

        company_name = company.get('name', 'Unknown Company')
        tier = scoring.get('tier', 'TIER 5')
        tier_label = scoring.get('tier_label', 'UNKNOWN')
        score = scoring.get('final_score', 0)
        industry = lead_data.get('business_signals', {}).get('industry', 'Unknown')

        # Determine priority
        priority = "LOW"
        if 'TIER 1' in tier or 'TIER 2' in tier:
            priority = "HIGH"
        elif 'TIER 3' in tier:
            priority = "MEDIUM"

        # Get top pain point
        pain_points = needs.get('primary_pain_points', [])
        top_pain = pain_points[0].get('specific_challenge', 'Unknown pain point') if pain_points else 'No specific pain points identified'

        # Get recommended value prop
        recommended_value_prop = value_props[0]['text'] if value_props else "No value proposition generated"

        # Get decision maker info
        decision_makers = research.get('decision_makers', [])
        decision_maker_str = f"{decision_makers[0]['name']}, {decision_makers[0]['title']}" if decision_makers else "To be identified"

        # Build summary
        summary = f"""# Lead Summary: {company_name}

## Quick Stats
- **Tier:** {tier} - {tier_label}
- **Score:** {score}/30
- **Industry:** {industry}
- **Priority:** {priority}
- **Status:** {lead_data.get('outcome_tracking', {}).get('status', 'New')}

## Company Overview
- **Size:** {research.get('employee_count_estimate', 'Unknown')}
- **Location:** {company.get('location', 'Unknown')}
- **Website:** {research.get('website', 'None found')}
- **Decision Maker:** {decision_maker_str}

## Why They Need Forecasta
{top_pain}

## Recommended Approach
**Contact:** {call_script.get('target_contact', 'Operations Manager')}
**Opening Line:** "{call_script.get('main_script', {}).get('diagnosis_question', 'N/A')}"
**Value Prop:** "{recommended_value_prop}"

## Next Actions
1. [ ] Call {call_script.get('target_contact', 'decision maker')} at {company.get('contact', {}).get('phone', 'phone TBD')}
2. [ ] If no answer, LinkedIn message
3. [ ] Follow-up email

## Research Notes
- {research.get('online_presence_quality', 'Unknown')} online presence
- Pain severity: {needs.get('estimated_pain_severity', 'MEDIUM')}
- Recommended forecast horizon: {needs.get('forecast_horizon_recommended', '30-90 days')}

---
*Lead generated: {lead_data.get('created_timestamp', 'Unknown')}*
*Full data: lead_{lead_data.get('lead_id', 'unknown')}.json*
"""

        return summary
