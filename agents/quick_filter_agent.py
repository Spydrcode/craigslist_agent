"""
Quick Filter Agent - Fast heuristic filtering of jobs to identify promising companies
Uses simple pattern matching and company grouping WITHOUT expensive AI calls.
"""
from typing import List, Dict, Tuple
from collections import defaultdict
import re

from utils import get_logger
from models import RawJobPosting

logger = get_logger(__name__)


class QuickFilterAgent:
    """Agent for quickly filtering jobs using heuristics before expensive AI analysis."""

    # Positive indicators - companies worth pursuing
    GROWTH_INDICATORS = [
        'startup', 'growing', 'expanding', 'scaling',
        'hiring', 'new team', 'rapid growth', 'fast-growing',
        'series a', 'series b', 'funded', 'venture',
        'remote-first', 'new office', 'opening',
    ]

    # Technical job titles we want (for software companies)
    TECH_TITLES = [
        'software engineer', 'developer', 'programmer',
        'data engineer', 'data scientist', 'ml engineer',
        'devops', 'sre', 'cloud engineer',
        'full stack', 'frontend', 'backend', 'full-stack',
        'architect', 'tech lead', 'engineering manager',
        'qa engineer', 'test engineer', 'sdet',
    ]

    # Titles indicating multiple roles/growth
    SENIOR_ROLES = ['senior', 'lead', 'principal', 'staff', 'architect']
    JUNIOR_ROLES = ['junior', 'entry', 'associate', 'intern']

    # Spam/low-quality indicators to filter out
    SPAM_INDICATORS = [
        'work from home', 'make money', 'earn $',
        'no experience', 'easy money', 'quick cash',
        'mlm', 'pyramid', 'commission only',
        'driver', 'delivery', 'uber', 'lyft', 'doordash',
        'warehouse', 'forklift', 'packer',
    ]

    def __init__(self):
        logger.info("QuickFilterAgent initialized")

    def filter_and_group_jobs(
        self,
        jobs: List[RawJobPosting],
        min_company_jobs: int = 2
    ) -> Dict[str, List[RawJobPosting]]:
        """
        Quickly filter and group jobs by company.

        Args:
            jobs: List of raw job postings
            min_company_jobs: Minimum jobs per company to consider

        Returns:
            Dictionary of {company_name: [jobs]} for promising companies
        """
        logger.info(f"Quick filtering {len(jobs)} jobs")

        # Step 1: Filter out obvious spam
        filtered_jobs = [job for job in jobs if not self._is_spam(job)]
        logger.info(f"After spam filter: {len(filtered_jobs)} jobs remain")

        # Step 2: Group by company
        company_jobs = self._group_by_company(filtered_jobs)
        logger.info(f"Found {len(company_jobs)} unique companies")

        # Step 3: Filter companies by quality signals
        promising_companies = {}
        for company_name, company_job_list in company_jobs.items():
            if self._is_promising_company(company_name, company_job_list, min_company_jobs):
                promising_companies[company_name] = company_job_list

        logger.info(f"Identified {len(promising_companies)} promising companies")

        # Sort by number of jobs (more jobs = more growth)
        sorted_companies = dict(
            sorted(
                promising_companies.items(),
                key=lambda x: len(x[1]),
                reverse=True
            )
        )

        return sorted_companies

    def _is_spam(self, job: RawJobPosting) -> bool:
        """Check if job appears to be spam/low-quality."""
        title_lower = job.title.lower()

        # Check for spam indicators
        for indicator in self.SPAM_INDICATORS:
            if indicator in title_lower:
                return True

        return False

    def _group_by_company(self, jobs: List[RawJobPosting]) -> Dict[str, List[RawJobPosting]]:
        """Group jobs by company name extracted from title or location."""
        company_jobs = defaultdict(list)

        for job in jobs:
            company = self._extract_company_name(job)
            company_jobs[company].append(job)

        return dict(company_jobs)

    def _extract_company_name(self, job: RawJobPosting) -> str:
        """
        Extract company name from job description (primary) or title (fallback).
        CRITICAL: Returns "Unknown Company" if no company can be identified.
        """
        # PRIORITY 1: Extract from description (most reliable)
        if hasattr(job, 'description') and job.description and job.description != "[Quick scan - full details not fetched]":
            description = job.description
            
            # Pattern 1: "Company Name is seeking/hiring/looking for"
            seeking_match = re.search(r'([A-Z][A-Za-z0-9\s&.,\'-]{2,50}?)\s+(?:is|are)\s+(?:seeking|hiring|looking for|searching for)', description, re.MULTILINE)
            if seeking_match:
                company = seeking_match.group(1).strip()
                if self._is_valid_company_name(company):
                    return company
            
            # Pattern 2: "Join Company Name" or "Work for/at Company Name"
            join_match = re.search(r'(?:join|work for|work at|employed by)\s+([A-Z][A-Za-z0-9\s&.,\'-]{2,50}?)(?:\s+(?:as|in|and|\.|!|,)|$)', description, re.IGNORECASE)
            if join_match:
                company = join_match.group(1).strip()
                if self._is_valid_company_name(company):
                    return company
            
            # Pattern 3: "About Company Name" or "Company Name Overview"
            about_match = re.search(r'(?:about|overview of|introduction to)\s+([A-Z][A-Za-z0-9\s&.,\'-]{2,50}?)(?:\s*:|-|\n)', description, re.IGNORECASE)
            if about_match:
                company = about_match.group(1).strip()
                if self._is_valid_company_name(company):
                    return company
            
            # Pattern 4: Email domain (e.g., "contact@companyname.com")
            email_match = re.search(r'@([a-zA-Z0-9-]+)\.[a-z]{2,}', description)
            if email_match:
                domain = email_match.group(1)
                # Clean up common patterns
                if domain not in ['gmail', 'yahoo', 'hotmail', 'outlook', 'aol', 'craigslist']:
                    # Capitalize properly
                    company = domain.replace('-', ' ').title()
                    return company
            
            # Pattern 5: "Company Name," at start of description
            start_match = re.search(r'^([A-Z][A-Za-z0-9\s&.,\'-]{2,50}?),\s+(?:a|an|the|is|located)', description)
            if start_match:
                company = start_match.group(1).strip()
                if self._is_valid_company_name(company):
                    return company
            
            # Pattern 6: Website URL (e.g., "visit www.companyname.com")
            url_match = re.search(r'(?:www\.|https?://)([a-zA-Z0-9-]+)\.[a-z]{2,}', description)
            if url_match:
                domain = url_match.group(1)
                if domain not in ['craigslist', 'indeed', 'linkedin', 'google']:
                    company = domain.replace('-', ' ').title()
                    return company

        # PRIORITY 2: Extract from title (less reliable)
        title = job.title
        
        # Pattern 1: "Company Name - Job Title"
        if ' - ' in title:
            parts = title.split(' - ')
            if len(parts) >= 2:
                company = parts[0].strip()
                if self._is_valid_company_name(company):
                    return company
        
        # Pattern 2: "Job Title at Company Name"
        if ' at ' in title.lower():
            match = re.search(r' at (.+?)(?:\s*\(|$)', title, re.IGNORECASE)
            if match:
                company = match.group(1).strip()
                if self._is_valid_company_name(company):
                    return company
        
        # Pattern 3: "Company: Job Title" or "Company | Job Title"
        for separator in [':', '|']:
            if separator in title:
                parts = title.split(separator)
                if len(parts) >= 2:
                    company = parts[0].strip()
                    if self._is_valid_company_name(company):
                        return company

        # No company name found
        return "Unknown Company"
    
    def _is_valid_company_name(self, name: str) -> bool:
        """
        Validate if extracted text is actually a company name.
        """
        if not name or len(name) < 2:
            return False
        
        name_lower = name.lower()
        
        # Filter out common false positives
        invalid_words = [
            'hiring', 'wanted', 'needed', 'seeking', 'looking', 'now hiring',
            'apply', 'click here', 'immediate', 'urgent', 'call', 'email',
            'job', 'position', 'role', 'opportunity', 'career',
            'full time', 'part time', 'remote', 'work from home',
            'we are', 'you will', 'must have', 'required', 'preferred'
        ]
        
        if any(word in name_lower for word in invalid_words):
            return False
        
        # Must start with capital letter or number
        if not name[0].isupper() and not name[0].isdigit():
            return False
        
        return True

    def _is_promising_company(
        self,
        company_name: str,
        jobs: List[RawJobPosting],
        min_jobs: int
    ) -> bool:
        """
        Determine if a company is promising based on ACTIVE HIRING VELOCITY.

        PRIMARY HYPOTHESIS: Companies with multiple active job postings are:
        1. Growing rapidly (need to scale team)
        2. Have budget (approved headcount)
        3. Have urgency (can't wait, need help NOW)
        4. Are desperate (will pay for external services)

        The more jobs they're posting, the more desperate they are = better prospect.
        """
        # CORE FILTER: Must have minimum number of jobs
        # This is THE most important signal
        if len(jobs) < min_jobs:
            return False

        # ANY company with 3+ active jobs is promising
        # This is our PRIMARY qualification metric
        return True

    def get_top_companies(
        self,
        company_jobs: Dict[str, List[RawJobPosting]],
        top_n: int = 30
    ) -> Dict[str, List[RawJobPosting]]:
        """Get top N companies sorted by job count."""
        sorted_companies = sorted(
            company_jobs.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )
        return dict(sorted_companies[:top_n])
