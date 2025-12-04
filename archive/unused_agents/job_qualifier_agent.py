"""
Job Qualifier Agent for Forecasta.
Pre-filters job postings to identify companies likely to need workforce analytics services.
Uses AI to analyze job titles and basic info to determine relevance BEFORE full scraping.
"""
from typing import List, Dict, Any
from agents.client_agent import ClientAgent
from utils import get_logger

logger = get_logger(__name__)


class JobQualifierAgent:
    """
    Agent that pre-qualifies job postings to identify high-value targets.
    Filters jobs to find companies actively hiring at scale (need workforce analytics).
    """
    
    # Industries most likely to need Forecasta
    TARGET_INDUSTRIES = [
        'construction',
        'manufacturing',
        'healthcare',
        'retail',
        'hospitality',
        'warehousing',
        'logistics',
        'staffing',
        'recruiting',
        'skilled trades',
        'engineering',
        'technology'
    ]
    
    # Job title patterns indicating high hiring volume
    HIGH_VOLUME_INDICATORS = [
        'multiple positions',
        'multiple openings',
        'immediate hire',
        'mass hiring',
        'hiring event',
        'open house',
        'walk-in',
        'urgent',
        'asap',
        'immediate start',
        'hiring now',
        'positions available',
        'all shifts',
        '24/7',
        'full-time and part-time',
        'day shift and night shift'
    ]
    
    # Company size indicators
    COMPANY_SIZE_INDICATORS = [
        'locations',
        'nationwide',
        'multiple sites',
        'growing company',
        'expanding',
        'established',
        'fortune',
        'industry leader'
    ]
    
    def __init__(self, client_agent: ClientAgent = None):
        """Initialize the Job Qualifier Agent."""
        self.client = client_agent or ClientAgent()
        logger.info("JobQualifierAgent initialized")
    
    def qualify_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter jobs to only those from companies likely to need Forecasta.
        
        Args:
            jobs: List of job postings with title, description, etc.
            
        Returns:
            Filtered list of qualified jobs with qualification scores
        """
        logger.info(f"Qualifying {len(jobs)} job postings...")
        
        qualified_jobs = []
        
        for job in jobs:
            score = self._calculate_qualification_score(job)
            
            # Only include jobs scoring 15+ out of 100 (lowered threshold since we only have titles)
            if score >= 15:
                job['qualification_score'] = score
                job['qualification_reason'] = self._get_qualification_reason(job, score)
                qualified_jobs.append(job)
                logger.info(f"QUALIFIED (score: {score}): {job.get('title', 'Unknown')}")
            else:
                logger.debug(f"REJECTED (score: {score}): {job.get('title', 'Unknown')}")
        
        logger.info(f"Qualified {len(qualified_jobs)}/{len(jobs)} jobs")
        return qualified_jobs
    
    def _calculate_qualification_score(self, job: Dict[str, Any]) -> int:
        """
        Calculate 0-100 qualification score for a job posting.
        
        Scoring criteria:
        - High volume hiring indicators (40 points)
        - Target industry match (30 points)
        - Company size indicators (20 points)
        - Compensation listed (10 points)
        """
        score = 0
        title = job.get('title', '').lower()
        description = job.get('description', '').lower()
        combined = f"{title} {description}"
        
        # HIGH VOLUME HIRING (40 points)
        volume_matches = sum(1 for indicator in self.HIGH_VOLUME_INDICATORS if indicator in combined)
        if volume_matches >= 3:
            score += 40
        elif volume_matches >= 2:
            score += 30
        elif volume_matches >= 1:
            score += 15
        
        # TARGET INDUSTRY (30 points)
        industry_matches = sum(1 for industry in self.TARGET_INDUSTRIES if industry in combined)
        if industry_matches >= 2:
            score += 30
        elif industry_matches >= 1:
            score += 25
        
        # COMPANY SIZE (20 points)
        size_matches = sum(1 for indicator in self.COMPANY_SIZE_INDICATORS if indicator in combined)
        if size_matches >= 2:
            score += 20
        elif size_matches >= 1:
            score += 10
        
        # COMPENSATION LISTED (10 points)
        # Companies listing pay are more serious/professional
        if job.get('compensation'):
            score += 10
        
        # BONUS: If it's clearly a job posting (not gig/task), add base points
        if any(word in combined for word in ['manager', 'supervisor', 'director', 'coordinator', 'specialist', 'engineer', 'technician', 'operator']):
            score += 15
        
        return min(score, 100)
    
    def _get_qualification_reason(self, job: Dict[str, Any], score: int) -> str:
        """Generate human-readable reason for qualification."""
        title = job.get('title', '').lower()
        description = job.get('description', '').lower()
        combined = f"{title} {description}"
        
        reasons = []
        
        # Check what matched
        volume_matches = [ind for ind in self.HIGH_VOLUME_INDICATORS if ind in combined]
        if volume_matches:
            reasons.append(f"High-volume hiring ({', '.join(volume_matches[:2])})")
        
        industry_matches = [ind for ind in self.TARGET_INDUSTRIES if ind in combined]
        if industry_matches:
            reasons.append(f"Target industry ({', '.join(industry_matches[:2])})")
        
        size_matches = [ind for ind in self.COMPANY_SIZE_INDICATORS if ind in combined]
        if size_matches:
            reasons.append(f"Large company ({', '.join(size_matches[:1])})")
        
        if job.get('compensation'):
            reasons.append("Professional posting (lists compensation)")
        
        if reasons:
            return " • ".join(reasons)
        else:
            return "Basic qualification met"
    
    def ai_qualify_batch(self, jobs: List[Dict[str, Any]], top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Use AI to intelligently rank and select the best job postings.
        More sophisticated than rule-based qualification.
        
        Args:
            jobs: List of job postings
            top_n: Number of top jobs to return
            
        Returns:
            Top N jobs most likely to need Forecasta
        """
        logger.info(f"AI qualifying {len(jobs)} jobs to find top {top_n}...")
        
        # First pass: rule-based filtering
        qualified = self.qualify_jobs(jobs)
        
        if len(qualified) <= top_n:
            return qualified
        
        # Second pass: AI ranking of qualified jobs
        try:
            job_summaries = []
            for idx, job in enumerate(qualified[:50]):  # Limit to top 50 for API cost
                job_summaries.append(
                    f"{idx}. {job.get('title', 'Unknown')} | "
                    f"{job.get('location', '')} | "
                    f"{job.get('compensation', 'Not listed')}"
                )
            
            prompt = f"""You are analyzing job postings to identify companies that need workforce analytics software.

Forecasta helps companies:
- Predict hiring needs and workforce demand
- Optimize recruitment timing and budgets
- Reduce turnover through data insights
- Plan staffing for seasonal demand

Which companies from this list are MOST likely to need these services?
Prioritize companies that:
1. Are hiring many people at once (high volume)
2. Have ongoing/recurring hiring needs
3. Are in industries with workforce challenges (construction, healthcare, retail, manufacturing)
4. Are large/established companies with budgets

Job Postings:
{chr(10).join(job_summaries)}

Return ONLY the indices (numbers) of the top {top_n} most promising jobs, comma-separated.
Example response: 3,7,12,19,22,31,35,40,42,48

Your response:"""

            response = self.client.generate_response(
                prompt=prompt,
                max_tokens=100,
                temperature=0.3
            )
            
            # Parse AI response
            try:
                indices = [int(x.strip()) for x in response.split(',')]
                top_jobs = [qualified[i] for i in indices if i < len(qualified)]
                
                logger.info(f"AI selected {len(top_jobs)} top jobs")
                return top_jobs[:top_n]
                
            except Exception as e:
                logger.error(f"Failed to parse AI response: {e}")
                # Fallback to rule-based ranking
                return sorted(qualified, key=lambda x: x.get('qualification_score', 0), reverse=True)[:top_n]
        
        except Exception as e:
            logger.error(f"AI qualification failed: {e}")
            # Fallback to rule-based ranking
            return sorted(qualified, key=lambda x: x.get('qualification_score', 0), reverse=True)[:top_n]
