"""
Outreach Agent
Generates personalized emails and call scripts for prospects.
"""
from typing import Dict, Any, Optional
from datetime import datetime
from models_enhanced import ProspectLead, ServiceOpportunity
from agents.client_agent import ClientAgent
from utils import get_logger

logger = get_logger(__name__)


class OutreachAgent:
    """
    Agent for generating personalized outreach content.
    Creates emails and call scripts tailored to each prospect.
    """

    def __init__(self, client_agent: Optional[ClientAgent] = None):
        """Initialize the Outreach Agent."""
        self.client = client_agent or ClientAgent()
        logger.info("OutreachAgent initialized")

    def generate_email(
        self,
        prospect: ProspectLead,
        your_name: str,
        your_company: str,
        your_title: str = "Solutions Consultant",
        tone: str = "professional"
    ) -> Dict[str, str]:
        """
        Generate personalized outreach email.

        Args:
            prospect: Prospect to email
            your_name: Your name
            your_company: Your company name
            your_title: Your job title
            tone: Email tone (professional, casual, direct)

        Returns:
            Dictionary with subject, body, and metadata
        """
        logger.info(f"Generating email for {prospect.company_profile.name}")

        company_name = prospect.company_profile.name
        top_opportunity = prospect.service_opportunities[0] if prospect.service_opportunities else None

        if not top_opportunity:
            logger.warning(f"No opportunities found for {company_name}")
            return self._generate_generic_email(prospect, your_name, your_company, your_title)

        # Build context for AI
        context = self._build_prospect_context(prospect, top_opportunity)

        # Generate email using AI
        prompt = f"""Generate a personalized business development email with these details:

**Your Information:**
- Name: {your_name}
- Company: {your_company}
- Title: {your_title}

**Prospect Company:**
- Name: {company_name}
- Location: {prospect.company_profile.location or 'Unknown'}
- Growth Stage: {prospect.company_profile.growth_signals.growth_stage.value if prospect.company_profile.growth_signals else 'unknown'}

**Opportunity Identified:**
- Service: {top_opportunity.service_type}
- Confidence: {top_opportunity.confidence_score:.0%}
- Value Range: {top_opportunity.estimated_value}
- Reasoning: {top_opportunity.reasoning}

**Evidence:**
- They're hiring for {len(prospect.job_postings)} positions
- Job titles: {', '.join([p.title for p in prospect.job_postings[:3]])}
{f"- Growth indicators: {', '.join(prospect.company_profile.growth_signals.evidence_text[:2])}" if prospect.company_profile.growth_signals and prospect.company_profile.growth_signals.evidence_text else ""}

**Key Talking Points:**
{chr(10).join(f"- {point}" for point in prospect.key_talking_points[:3]) if prospect.key_talking_points else "- Your company is actively growing"}

**Requirements:**
1. Subject line should be attention-grabbing but professional
2. Email should be {tone} in tone
3. Reference their specific hiring activity
4. Mention the specific pain point/opportunity
5. Include a clear call-to-action (schedule a brief call)
6. Keep it under 200 words
7. Don't be salesy - be consultative
8. Use "you" and "your" (not "I" focused)

Generate the email in this exact format:

SUBJECT: [your subject line]

EMAIL:
[email body]

[signature block with your name, title, company]"""

        try:
            response = self.client._call_api(
                messages=[
                    {"role": "system", "content": "You are an expert business development writer specializing in B2B tech services."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=600
            )

            # Parse response
            email_dict = self._parse_email_response(response, your_name, your_company, your_title)
            email_dict['metadata'] = {
                'prospect_id': prospect.lead_id,
                'company_name': company_name,
                'opportunity': top_opportunity.service_type,
                'generated_at': datetime.utcnow().isoformat(),
                'tone': tone
            }

            logger.info(f"Generated email for {company_name}")
            return email_dict

        except Exception as e:
            logger.error(f"Email generation failed: {e}")
            return self._generate_generic_email(prospect, your_name, your_company, your_title)

    def generate_call_script(
        self,
        prospect: ProspectLead,
        your_name: str,
        your_company: str
    ) -> Dict[str, Any]:
        """
        Generate personalized call script.

        Args:
            prospect: Prospect to call
            your_name: Your name
            your_company: Your company name

        Returns:
            Dictionary with script sections and objection handling
        """
        logger.info(f"Generating call script for {prospect.company_profile.name}")

        company_name = prospect.company_profile.name
        top_opportunity = prospect.service_opportunities[0] if prospect.service_opportunities else None

        if not top_opportunity:
            return self._generate_generic_script(prospect, your_name, your_company)

        # Build context
        job_count = len(prospect.job_postings)
        growth_stage = prospect.company_profile.growth_signals.growth_stage.value if prospect.company_profile.growth_signals else "unknown"

        prompt = f"""Create a professional cold call script for B2B services with these details:

**Caller Information:**
- Name: {your_name}
- Company: {your_company}

**Prospect:**
- Company: {company_name}
- Currently hiring: {job_count} positions
- Growth stage: {growth_stage}
- Decision maker: {prospect.decision_maker_target or 'CTO/VP Engineering'}

**Opportunity:**
- Service: {top_opportunity.service_type}
- Value: {top_opportunity.estimated_value}
- Reasoning: {top_opportunity.reasoning}

**Evidence Points:**
- Job postings: {', '.join([p.title for p in prospect.job_postings[:3]])}
{f"- Urgency: {top_opportunity.urgency.value}" if top_opportunity else ""}

**Requirements:**
Create a structured call script with these sections:
1. OPENING (permission-based, not pushy)
2. PATTERN INTERRUPT (reference their hiring activity)
3. VALUE STATEMENT (what we do)
4. DISCOVERY QUESTION (get them talking)
5. MEETING REQUEST (specific time options)
6. COMMON OBJECTIONS (with responses)

Make it conversational, not scripted-sounding. Focus on being helpful, not selling."""

        try:
            response = self.client._call_api(
                messages=[
                    {"role": "system", "content": "You are an expert sales trainer specializing in consultative B2B selling."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )

            # Parse into structured script
            script = {
                'company_name': company_name,
                'decision_maker': prospect.decision_maker_target or 'CTO/VP Engineering',
                'full_script': response,
                'quick_reference': {
                    'opener': f"Hi, this is {your_name} with {your_company}. Is this {prospect.decision_maker_target or 'the CTO'}? Do you have 60 seconds?",
                    'hook': f"I noticed you're hiring {job_count} positions, which usually means you're either growing fast or having trouble keeping up with demand.",
                    'question': self._create_discovery_question(top_opportunity),
                    'close': "How does your calendar look for a quick 15-minute call this Thursday or Friday?"
                },
                'metadata': {
                    'prospect_id': prospect.lead_id,
                    'generated_at': datetime.utcnow().isoformat()
                }
            }

            logger.info(f"Generated call script for {company_name}")
            return script

        except Exception as e:
            logger.error(f"Call script generation failed: {e}")
            return self._generate_generic_script(prospect, your_name, your_company)

    def generate_linkedin_message(
        self,
        prospect: ProspectLead,
        your_name: str,
        connection_request: bool = True
    ) -> str:
        """
        Generate LinkedIn connection request or message.

        Args:
            prospect: Prospect to message
            your_name: Your name
            connection_request: If True, generate connection request (300 chars max)

        Returns:
            LinkedIn message text
        """
        company_name = prospect.company_profile.name
        top_opportunity = prospect.service_opportunities[0] if prospect.service_opportunities else None

        max_length = 300 if connection_request else 1000

        prompt = f"""Write a {'LinkedIn connection request message (MAX 300 characters)' if connection_request else 'LinkedIn direct message'} for:

Company: {company_name}
Their situation: Hiring {len(prospect.job_postings)} positions
Opportunity: {top_opportunity.service_type if top_opportunity else 'General consulting'}

Requirements:
- Be personable and genuine
- Reference their company's growth
- Don't be salesy
- Suggest a brief conversation
{f'- MUST be under {max_length} characters' if connection_request else ''}

Write only the message, no labels or extra text."""

        try:
            response = self.client._call_api(
                messages=[
                    {"role": "system", "content": "You are a LinkedIn networking expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150 if connection_request else 300
            )

            message = response.strip()

            # Enforce character limit for connection requests
            if connection_request and len(message) > 300:
                message = message[:297] + "..."

            return message

        except Exception as e:
            logger.error(f"LinkedIn message generation failed: {e}")
            return f"Hi! I noticed {company_name} is growing and thought we might have some insights to share. Would you be open to a brief conversation?"

    def _build_prospect_context(self, prospect: ProspectLead, opportunity: ServiceOpportunity) -> str:
        """Build context string for AI."""
        context_parts = [
            f"Company: {prospect.company_profile.name}",
            f"Hiring: {len(prospect.job_postings)} positions",
            f"Opportunity: {opportunity.service_type}",
            f"Evidence: {opportunity.reasoning}"
        ]

        if prospect.company_profile.growth_signals:
            context_parts.append(f"Growth: {prospect.company_profile.growth_signals.growth_stage.value}")

        return "\n".join(context_parts)

    def _parse_email_response(self, response: str, name: str, company: str, title: str) -> Dict[str, str]:
        """Parse AI response into structured email."""
        import re

        # Extract subject
        subject_match = re.search(r'SUBJECT:\s*(.+?)(?:\n|$)', response, re.IGNORECASE)
        subject = subject_match.group(1).strip() if subject_match else "Quick question about your growth"

        # Extract body (everything after SUBJECT: and EMAIL:)
        email_match = re.search(r'EMAIL:\s*(.+)', response, re.DOTALL | re.IGNORECASE)
        if email_match:
            body = email_match.group(1).strip()
        else:
            # If no EMAIL: marker, use everything after subject
            body = re.sub(r'SUBJECT:.+?\n+', '', response, flags=re.IGNORECASE).strip()

        # Ensure signature
        if name not in body:
            body += f"\n\nBest regards,\n{name}\n{title}\n{company}"

        return {
            'subject': subject,
            'body': body
        }

    def _generate_generic_email(self, prospect: ProspectLead, name: str, company: str, title: str) -> Dict[str, str]:
        """Generate generic email fallback."""
        company_name = prospect.company_profile.name

        return {
            'subject': f"Quick question about {company_name}'s growth",
            'body': f"""Hi,

I noticed {company_name} is actively hiring and wanted to reach out.

We specialize in helping growing tech companies optimize their operations and scale efficiently. Based on your current hiring activity, I think there might be some ways we could help.

Would you be open to a brief 15-minute conversation to explore if there's a fit?

Best regards,
{name}
{title}
{company}""",
            'metadata': {
                'prospect_id': prospect.lead_id,
                'company_name': company_name,
                'generated_at': datetime.utcnow().isoformat(),
                'type': 'generic'
            }
        }

    def _generate_generic_script(self, prospect: ProspectLead, name: str, company: str) -> Dict[str, Any]:
        """Generate generic call script fallback."""
        return {
            'company_name': prospect.company_profile.name,
            'decision_maker': 'Decision Maker',
            'full_script': f"Generic script for {prospect.company_profile.name}",
            'quick_reference': {
                'opener': f"Hi, this is {name} with {company}. Do you have 60 seconds?",
                'hook': f"I noticed you're hiring and wanted to see if we could help.",
                'question': "What's your biggest challenge right now with scaling your team?",
                'close': "Would you be open to a brief call this week?"
            }
        }

    def _create_discovery_question(self, opportunity: ServiceOpportunity) -> str:
        """Create discovery question based on opportunity."""
        questions = {
            'AI/ML Consulting': "How are you currently approaching your machine learning initiatives?",
            'Data Engineering': "What's your biggest challenge with data infrastructure right now?",
            'Cloud Migration': "Where are you in your cloud transformation journey?",
            'DevOps/Platform Engineering': "How are you handling deployments and infrastructure management currently?",
            'Full-Stack Development': "What's driving your need to expand the development team?",
            'API Development': "What integrations or APIs are you building out?",
            'Data Analytics & BI': "How are you making data-driven decisions today?",
            'Mobile App Development': "What's your mobile strategy looking like?",
            'Security & Compliance': "How are you handling security and compliance requirements?",
            'Process Automation': "What processes are taking up the most manual time?"
        }

        return questions.get(opportunity.service_type, "What's your biggest technical challenge right now?")
