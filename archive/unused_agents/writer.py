"""Writer Agent - Generate value propositions and call scripts."""

from typing import Dict, Any, Optional


class WriterAgent:
    """Generates customized value propositions, call scripts, and email templates."""

    def __init__(self):
        self.name = "WriterAgent"

    def write(self, analyzed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate sales collateral for lead.

        Args:
            analyzed_data: Output from AnalyzerAgent

        Returns:
            Data with generated scripts and emails
        """
        tier = analyzed_data.get('tier', 5)

        # Skip writing for tier 4-5 leads
        if tier >= 4:
            return {
                **analyzed_data,
                "writing_status": "skipped",
                "writing_reason": "tier_too_low"
            }

        # Generate value proposition
        value_prop = self._generate_value_prop(analyzed_data)

        # Generate call script
        call_script = self._generate_call_script(analyzed_data, value_prop)

        # Generate email template
        email_template = self._generate_email(analyzed_data, value_prop)

        result = {
            **analyzed_data,
            "value_proposition": value_prop,
            "call_script": call_script,
            "email_template": email_template,
            "writing_status": "success"
        }

        return result

    def _generate_value_prop(self, data: Dict[str, Any]) -> str:
        """Generate value proposition using formula."""
        # Formula: "Predict [specific thing] [timeframe] ahead so you [benefit] instead of [current problem]"

        opportunities = data.get('forecast_opportunities', [])
        if not opportunities:
            return "Predict staffing needs 4-6 weeks ahead so you optimize labor costs instead of reactive hiring."

        opp = opportunities[0]
        what = opp.get('what_to_predict', 'staffing needs')
        timeframe = opp.get('timeframe', '4-6 weeks')
        benefit = opp.get('benefit', 'optimize operations')
        problem = opp.get('current_problem', 'reactive planning')

        value_prop = f"Predict {what} {timeframe} ahead so you {benefit} instead of {problem}."

        return value_prop

    def _generate_call_script(self, data: Dict[str, Any], value_prop: str) -> Dict[str, str]:
        """Generate structured call script."""
        company_name = data.get('company_name', 'the company')
        insights = data.get('insights', {})
        opening_hook = insights.get('opening_hook', f"I came across {company_name}'s recent job posting")
        primary_pain = data.get('pain_points', [{}])[0] if data.get('pain_points') else {}
        pain_description = primary_pain.get('description', 'staffing challenges')

        script = {
            "intro": f"Hi, this is [YOUR NAME] with Forecasta. Do you have 60 seconds?",

            "pattern_interrupt": f"{opening_hook} and wanted to reach out.",

            "diagnosis_question": f"Quick question - what's your biggest challenge right now when it comes to {pain_description.lower()}?",

            "value_statement": f"The reason I'm calling is we help companies like {company_name} {value_prop.lower()}",

            "social_proof": "We work with similar companies in [INDUSTRY] who were facing the same challenges.",

            "meeting_ask": "I'd love to show you how this works. Do you have 15 minutes Thursday at 10am or would Friday afternoon work better?",

            "objection_handling": {
                "not_interested": "I totally understand. Just curious - are you currently dealing with [PAIN POINT]? [If yes] That's exactly what we solve. Just 15 minutes to show you how.",

                "too_busy": "That's exactly why I'm calling. Our customers save 5-10 hours per week on workforce planning. When's a better time to chat?",

                "send_info": "Happy to - but I've found a quick call is more helpful since every business is different. How about 10 minutes tomorrow morning?"
            }
        }

        return script

    def _generate_email(self, data: Dict[str, Any], value_prop: str) -> Dict[str, str]:
        """Generate email template."""
        company_name = data.get('company_name', '[Company Name]')
        insights = data.get('insights', {})
        opening_hook = insights.get('opening_hook', f"I noticed {company_name} is hiring")
        primary_pain = data.get('pain_points', [{}])[0] if data.get('pain_points') else {}
        pain_category = primary_pain.get('category', 'staffing')

        # Determine recipient
        decision_maker = data.get('decision_maker')
        if decision_maker:
            recipient = decision_maker.get('name', '[Name]')
            title = decision_maker.get('title', '')
        else:
            recipient = '[Hiring Manager]'
            title = ''

        subject = self._generate_subject_line(pain_category, company_name)

        body = f"""Hi {recipient},

{opening_hook} and wanted to reach out.

Most companies like {company_name} struggle with [PAIN POINT] - either overstaffing and burning budget, or understaffing and missing opportunities.

That's where Forecasta comes in: {value_prop}

Quick example: [SIMILAR COMPANY] was dealing with [SIMILAR PROBLEM]. Using our platform, they [SPECIFIC RESULT - e.g., reduced overtime costs by 30%, improved coverage during peak season].

Would you be open to a 15-minute demo to see how this would work for {company_name}?

Best,
[YOUR NAME]
Forecasta

P.S. - Happy to share the [SIMILAR COMPANY] case study if you'd like to see the details.
"""

        email = {
            "to": recipient,
            "subject": subject,
            "body": body,
            "follow_up_1": self._generate_follow_up(company_name, 1),
            "follow_up_2": self._generate_follow_up(company_name, 2)
        }

        return email

    def _generate_subject_line(self, pain_category: str, company_name: str) -> str:
        """Generate compelling subject line."""
        subjects = {
            'seasonal_staffing': f"Seasonal staffing for {company_name}",
            'project_uncertainty': f"Project headcount planning - {company_name}",
            'volume_variability': f"Forecasting volume at {company_name}",
            'growth_planning': f"Scaling workforce @ {company_name}",
            'bulk_hiring': f"Re: Multiple open positions at {company_name}"
        }

        return subjects.get(pain_category, f"Quick question about staffing at {company_name}")

    def _generate_follow_up(self, company_name: str, follow_up_number: int) -> str:
        """Generate follow-up email templates."""
        if follow_up_number == 1:
            return f"""Hi [Name],

Following up on my email from [DAY].

I know inbox overload is real, so I'll keep this short:

If you're dealing with unpredictable staffing needs at {company_name}, I'd love to show you how we help companies forecast this 4-6 weeks out.

15 minutes - that's it.

Work for you?

[YOUR NAME]
"""
        else:
            return f"""Hi [Name],

Last attempt here - I promise!

If forecasting staffing/demand isn't a priority for {company_name} right now, totally understand.

But if it is, and you just haven't had time to respond, let me know and I'll send over some times.

[YOUR NAME]

P.S. - If this isn't the right person to talk to about workforce planning, who should I reach out to?
"""
