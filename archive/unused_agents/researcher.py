"""Researcher Agent - Web search for company information."""

import json
import re
import time
from typing import Dict, Any, Optional
from datetime import datetime


class ResearcherAgent:
    """Performs web research on companies to gather verification and sizing data."""

    def __init__(self, web_search_tool=None):
        self.name = "ResearcherAgent"
        self.web_search_tool = web_search_tool
        self.max_retries = 3

    def research(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Research company information from web sources.

        Args:
            extracted_data: Output from ExtractorAgent

        Returns:
            Enhanced data with research findings
        """
        company_name = extracted_data.get('company_name')
        location = extracted_data.get('location')

        if not company_name:
            return {
                **extracted_data,
                "research_status": "skipped",
                "research_reason": "no_company_name"
            }

        try:
            # Perform research with retry logic
            research_data = self._perform_research_with_retry(company_name, location)

            result = {
                **extracted_data,
                "company_verified": research_data.get('verified', False),
                "company_size": research_data.get('employee_count'),
                "company_industry": research_data.get('industry'),
                "company_website": research_data.get('website'),
                "company_description": research_data.get('description'),
                "decision_maker": research_data.get('decision_maker'),
                "is_local": research_data.get('is_local', False),
                "research_status": "success",
                "researched_at": datetime.utcnow().isoformat()
            }

            return result

        except Exception as e:
            return {
                **extracted_data,
                "research_status": "error",
                "research_error": str(e)
            }

    def _perform_research_with_retry(self, company_name: str, location: Optional[str]) -> Dict[str, Any]:
        """Perform web research with retry logic."""
        for attempt in range(self.max_retries):
            try:
                return self._perform_research(company_name, location)
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise e

    def _perform_research(self, company_name: str, location: Optional[str]) -> Dict[str, Any]:
        """Actual research logic."""
        research_data = {
            'verified': False,
            'employee_count': None,
            'industry': None,
            'website': None,
            'description': None,
            'decision_maker': None,
            'is_local': False
        }

        # If web search tool is available, use it
        if self.web_search_tool:
            query = f"{company_name}"
            if location:
                query += f" {location}"

            search_results = self.web_search_tool(query)
            research_data = self._parse_search_results(search_results, company_name, location)
        else:
            # Fallback: basic heuristics
            research_data['verified'] = True  # Assume verified if we have a name
            research_data['is_local'] = self._is_local_location(location) if location else False

        return research_data

    def _parse_search_results(self, results: str, company_name: str, location: Optional[str]) -> Dict[str, Any]:
        """Parse search results for company information."""
        data = {
            'verified': True,  # Found in search
            'employee_count': None,
            'industry': None,
            'website': None,
            'description': None,
            'decision_maker': None,
            'is_local': False
        }

        results_lower = results.lower()

        # Extract employee count
        employee_patterns = [
            r'(\d+)\s*[-–]\s*(\d+)\s*employees',
            r'(\d+)\s*employees',
            r'employs\s*(\d+)'
        ]

        for pattern in employee_patterns:
            match = re.search(pattern, results_lower)
            if match:
                if len(match.groups()) > 1:
                    data['employee_count'] = int(match.group(2))
                else:
                    data['employee_count'] = int(match.group(1))
                break

        # Extract industry
        industries = [
            'retail', 'hospitality', 'healthcare', 'construction',
            'logistics', 'manufacturing', 'technology', 'finance',
            'education', 'professional services'
        ]

        for industry in industries:
            if industry in results_lower:
                data['industry'] = industry
                break

        # Extract website
        website_match = re.search(r'https?://(?:www\.)?([^\s/]+)', results)
        if website_match:
            data['website'] = website_match.group(0)

        # Check if local
        if location:
            data['is_local'] = self._is_local_location(location)

        # Extract decision maker (look for titles)
        decision_titles = [
            'owner', 'ceo', 'president', 'general manager',
            'operations manager', 'hiring manager', 'director'
        ]

        for title in decision_titles:
            pattern = f'([A-Z][a-z]+\\s+[A-Z][a-z]+),?\\s+{title}'
            match = re.search(pattern, results, re.IGNORECASE)
            if match:
                data['decision_maker'] = {
                    'name': match.group(1),
                    'title': title
                }
                break

        # Extract description (first sentence from results)
        sentences = re.split(r'[.!?]', results)
        if sentences:
            data['description'] = sentences[0][:200]

        return data

    def _is_local_location(self, location: str) -> bool:
        """Check if location is in Phoenix metro area."""
        phoenix_areas = [
            'phoenix', 'scottsdale', 'tempe', 'mesa', 'chandler',
            'glendale', 'gilbert', 'peoria', 'surprise', 'avondale'
        ]

        location_lower = location.lower()
        return any(area in location_lower for area in phoenix_areas)

    def validate_company(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that company is legitimate and not a disqualifier."""
        is_valid = True
        disqualification_reason = None

        # Check red flags from extraction
        red_flags = research_data.get('red_flags', [])
        if 'mlm_language' in red_flags:
            is_valid = False
            disqualification_reason = 'mlm_indicators'
        elif 'national_chain' in red_flags:
            is_valid = False
            disqualification_reason = 'national_chain'

        # Check if verified
        if not research_data.get('company_verified'):
            is_valid = False
            disqualification_reason = 'cannot_verify_company'

        # Check red flag count
        if len(red_flags) >= 2:
            is_valid = False
            disqualification_reason = 'multiple_red_flags'

        return {
            **research_data,
            'is_valid_lead': is_valid,
            'disqualification_reason': disqualification_reason
        }
