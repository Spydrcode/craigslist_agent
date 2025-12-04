"""
Legacy Agent Compatibility Layer for Dashboard

Provides backward-compatible wrappers for old agent interfaces
that the dashboard expects, using the current agent architecture.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from agents import (
    ClientAgent,
    ParserAgent,
    CompanyResearchAgent,
)


class LeadAnalysisAgent:
    """
    Backward-compatible wrapper for LeadAnalysisAgent functionality.
    Uses current agents (Parser + CompanyResearch) to provide same interface.
    """
    
    def __init__(self):
        self.client = ClientAgent()
        self.parser = ParserAgent(self.client)
        self.researcher = CompanyResearchAgent(self.client)
    
    def analyze_posting(
        self,
        posting_text: str,
        posting_url: str = "",
        enable_web_search: bool = False,
        company_name: str = "",
        job_title: str = ""
    ) -> Dict[str, Any]:
        """
        Analyze a job posting and return lead data.

        Args:
            posting_text: Job description text
            posting_url: URL of the posting
            enable_web_search: Whether to research company via web
            company_name: Company name from search results
            job_title: Job title from search results

        Returns:
            Dictionary with lead analysis results
        """
        # Generate lead ID
        lead_id = str(uuid.uuid4())

        # Use provided company name and job title, or defaults
        initial_company_name = company_name if company_name else "Unknown"
        initial_job_title = job_title if job_title else "Job Posting"

        # Parse the job posting
        from models_enhanced import JobPostingEnhanced
        raw_job = JobPostingEnhanced(
            url=posting_url,
            title=initial_job_title,
            description=posting_text,
            location="Unknown",
            posted_date=datetime.utcnow().isoformat(),  # Convert to ISO format string
            company_name=initial_company_name,
            category="general"  # Default category
        )
        
        parsed_job = self.parser.parse_job(raw_job)

        # Extract company info - preserve the original company name if provided
        # Parser might not extract it correctly, so use what was passed in
        final_company_name = company_name if company_name else (parsed_job.company_name or "Unknown Company")

        # Basic company data
        company_data = {
            'name': final_company_name,
            'industry': getattr(parsed_job, 'industry', 'Unknown'),
            'size': 'Unknown',
            'location': parsed_job.location,
            'website': '',
        }
        
        # Research company if enabled
        if enable_web_search and final_company_name != "Unknown Company":
            try:
                profile = self.researcher.research_company(final_company_name)
                company_data.update({
                    'industry': profile.industry or company_data['industry'],
                    'size': profile.company_size or company_data['size'],
                    'website': profile.website or '',
                })
            except Exception as e:
                print(f"Warning: Company research failed: {e}")
        
        # Extract key information
        pain_points = getattr(parsed_job, 'pain_points', [])
        skills = getattr(parsed_job, 'skills', [])

        # If no pain points extracted, generate default ones based on job title and context
        if not pain_points:
            job_title_lower = parsed_job.title.lower()
            # Generate intelligent default pain points based on job type
            if any(term in job_title_lower for term in ['engineer', 'developer', 'architect']):
                pain_points = [
                    f"Need for qualified {parsed_job.title} to join the team",
                    "Expanding technical capabilities and project capacity",
                    "Building or scaling development operations"
                ]
            elif any(term in job_title_lower for term in ['manager', 'director', 'lead']):
                pain_points = [
                    f"Leadership gap requiring experienced {parsed_job.title}",
                    "Need to scale team management and operations",
                    "Strategic growth requiring senior talent"
                ]
            else:
                pain_points = [
                    f"Hiring need for {parsed_job.title} position",
                    "Team expansion and operational growth",
                    "Business requirements driving new hire"
                ]
        
        # Simple scoring logic
        score = 50  # Base score
        if len(pain_points) > 3:
            score += 20
        if len(skills) > 5:
            score += 15
        if 'cloud' in posting_text.lower():
            score += 10
        if 'devops' in posting_text.lower():
            score += 5
        
        # Determine tier
        if score >= 80:
            tier = "TIER 1"
        elif score >= 60:
            tier = "TIER 2"
        elif score >= 40:
            tier = "TIER 3"
        else:
            tier = "TIER 4"
        
        # Generate outreach strategy
        pain_points_text = "\n".join(f"• {p}" for p in pain_points[:3]) if pain_points else "• Need for technical expertise"

        email_template = f"""Subject: Helping {final_company_name} with {parsed_job.title}

Hi [Name],

I noticed your opening for {parsed_job.title} at {final_company_name}. Based on the job description, it seems you're looking to address:

{pain_points_text}

We specialize in helping companies like yours find the right technical talent and build strong development teams. I'd love to discuss how we can support your hiring goals.

Would you have 15 minutes this week for a quick call?

Best regards,
[Your Name]"""

        call_script = f"""Opening:
Hi, this is [Your Name] from [Your Company]. I'm reaching out about your {parsed_job.title} position.

Discovery Questions:
1. What's driving the need for this role right now?
2. What challenges has the team been facing that this hire will help solve?
3. How quickly are you looking to fill this position?

Key Pain Points to Address:
{pain_points_text}

Value Proposition:
We help companies like {final_company_name} find qualified {parsed_job.title} candidates who can hit the ground running.

Closing:
Would it make sense to schedule a brief call to discuss how we can help with your hiring needs?"""

        # Build result
        result = {
            'lead_id': lead_id,
            'company': company_data,
            'job_details': {
                'title': parsed_job.title,
                'location': parsed_job.location,
                'url': posting_url,
                'description': posting_text[:500],
                'skills_required': skills,
                'pain_points': pain_points,
            },
            'lead_scoring': {
                'total_score': score,
                'tier': tier,
                'pain_point_score': min(len(pain_points) * 5, 25),
                'skill_match_score': min(len(skills) * 3, 20),
                'growth_score': 15 if score > 60 else 10,
            },
            'outreach_strategy': {
                'email_template': email_template,
                'call_script': call_script,
            },
            'analysis_metadata': {
                'analyzed_at': datetime.utcnow().isoformat(),
                'web_search_enabled': enable_web_search,
                'confidence': 'medium',
            }
        }

        return result


class VectorAgent:
    """Mock VectorAgent for backward compatibility."""
    
    def __init__(self):
        print("Warning: VectorAgent is deprecated, using file-based storage")
    
    def search_similar(self, query: str, limit: int = 10) -> List[Dict]:
        return []


class DatabaseAgent:
    """Mock DatabaseAgent for backward compatibility."""
    
    def __init__(self):
        print("Warning: DatabaseAgent is deprecated, using file-based storage")
    
    def save_lead(self, lead_data: Dict) -> str:
        return str(uuid.uuid4())
    
    def get_stats(self) -> Dict:
        return {
            'total_jobs': 0,
            'remote_jobs': 0,
            'total_companies': 0,
        }


class JobQualifierAgent:
    """Mock JobQualifierAgent for backward compatibility."""
    
    def __init__(self):
        self.parser = ParserAgent(ClientAgent())
    
    def qualify_job(self, job_data: Dict) -> Dict:
        """Basic job qualification."""
        return {
            'qualified': True,
            'score': 60,
            'reason': 'Basic qualification passed'
        }
