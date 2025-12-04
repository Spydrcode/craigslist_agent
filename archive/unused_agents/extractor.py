"""Extractor Agent - Parse job postings into structured JSON."""

import json
import re
from datetime import datetime
from typing import Dict, Any, Optional


class ExtractorAgent:
    """Extracts structured data from Craigslist job postings."""

    def __init__(self):
        self.name = "ExtractorAgent"

    def extract(self, posting_html: str, posting_url: str) -> Dict[str, Any]:
        """
        Extract structured information from a Craigslist posting.

        Args:
            posting_html: Raw HTML content of the posting
            posting_url: URL of the posting

        Returns:
            Structured dict with extracted fields
        """
        try:
            # Extract basic fields
            company_name = self._extract_company_name(posting_html)
            job_title = self._extract_job_title(posting_html)
            posting_body = self._extract_posting_body(posting_html)
            salary = self._extract_salary(posting_body)
            location = self._extract_location(posting_html)
            contact_info = self._extract_contact_info(posting_body)
            posting_date = self._extract_posting_date(posting_html)

            # Extract contextual signals
            keywords = self._extract_keywords(posting_body)
            red_flags = self._detect_red_flags(posting_body)
            professionalism_score = self._calculate_professionalism(posting_body)

            result = {
                "company_name": company_name,
                "job_title": job_title,
                "location": location,
                "salary": salary,
                "posting_body": posting_body,
                "contact_info": contact_info,
                "posting_date": posting_date,
                "posting_url": posting_url,
                "keywords": keywords,
                "red_flags": red_flags,
                "professionalism_score": professionalism_score,
                "extracted_at": datetime.utcnow().isoformat(),
                "extraction_status": "success"
            }

            return result

        except Exception as e:
            return {
                "extraction_status": "error",
                "error_message": str(e),
                "posting_url": posting_url
            }

    def _extract_company_name(self, html: str) -> Optional[str]:
        """Extract company name from posting."""
        # Look for common patterns
        patterns = [
            r'<b>Company:</b>\s*([^<]+)',
            r'company[:\s]+([A-Z][A-Za-z0-9\s&.,]+?)(?:\n|<)',
            r'([A-Z][A-Za-z0-9\s&.,]{2,30})\s+(?:is hiring|seeks|looking for)'
        ]

        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _extract_job_title(self, html: str) -> Optional[str]:
        """Extract job title from posting."""
        # Look for title in heading or meta tags
        patterns = [
            r'<title>([^<]+?)\s*(?:-|–|\|)',
            r'class="postingtitle"[^>]*>([^<]+)',
            r'<h2[^>]*>([^<]+)</h2>'
        ]

        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                title = match.group(1).strip()
                # Clean up common suffixes
                title = re.sub(r'\s*-\s*craigslist.*$', '', title, flags=re.IGNORECASE)
                return title

        return None

    def _extract_posting_body(self, html: str) -> str:
        """Extract the main posting text."""
        # Look for posting body section
        match = re.search(r'<section id="postingbody">(.+?)</section>', html, re.DOTALL)
        if match:
            body = match.group(1)
            # Strip HTML tags
            body = re.sub(r'<[^>]+>', '', body)
            # Clean up whitespace
            body = re.sub(r'\s+', ' ', body).strip()
            return body

        # Fallback: strip all tags from entire HTML
        body = re.sub(r'<[^>]+>', ' ', html)
        body = re.sub(r'\s+', ' ', body).strip()
        return body[:5000]  # Limit length

    def _extract_salary(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract salary information."""
        # Patterns for salary
        patterns = [
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*-\s*\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:per\s+)?(year|yr|annual|hour|hr)',
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:per\s+)?(year|yr|annual|hour|hr)',
            r'(\d{1,3}(?:,\d{3})*)\s*(?:per\s+)?(year|yr|annual)'
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) >= 3:  # Range
                    return {
                        "min": float(groups[0].replace(',', '')),
                        "max": float(groups[1].replace(',', '')),
                        "period": groups[2].lower()
                    }
                else:  # Single value
                    return {
                        "value": float(groups[0].replace(',', '')),
                        "period": groups[1].lower() if len(groups) > 1 else "year"
                    }

        return None

    def _extract_location(self, html: str) -> Optional[str]:
        """Extract location from posting."""
        match = re.search(r'<small>([^<]+)</small>', html)
        if match:
            return match.group(1).strip()
        return None

    def _extract_contact_info(self, text: str) -> Dict[str, Any]:
        """Extract contact information."""
        contact = {}

        # Email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if email_match:
            contact['email'] = email_match.group(0)

        # Phone
        phone_match = re.search(r'(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})', text)
        if phone_match:
            contact['phone'] = phone_match.group(1)

        # Website
        website_match = re.search(r'https?://[\w\.-]+', text)
        if website_match:
            contact['website'] = website_match.group(0)

        return contact

    def _extract_posting_date(self, html: str) -> Optional[str]:
        """Extract posting date."""
        match = re.search(r'<time[^>]*datetime="([^"]+)"', html)
        if match:
            return match.group(1)
        return None

    def _extract_keywords(self, text: str) -> Dict[str, list]:
        """Extract relevant keywords from posting."""
        text_lower = text.lower()

        keywords = {
            "scale_indicators": [],
            "forecasting_signals": [],
            "industry_markers": [],
            "role_types": []
        }

        # Scale indicators
        scale_terms = [
            'multiple positions', 'hiring multiple', 'several openings',
            'manager', 'director', 'supervisor', 'lead',
            'benefits', 'health insurance', '401k', 'pto'
        ]
        keywords["scale_indicators"] = [term for term in scale_terms if term in text_lower]

        # Forecasting signals
        forecast_terms = [
            'seasonal', 'peak season', 'busy season',
            'project-based', 'contract', 'temporary',
            'volume', 'capacity', 'demand',
            'growth', 'expanding', 'scaling'
        ]
        keywords["forecasting_signals"] = [term for term in forecast_terms if term in text_lower]

        # Industry markers
        industry_terms = {
            'retail': ['retail', 'store', 'sales associate'],
            'hospitality': ['restaurant', 'hotel', 'hospitality'],
            'healthcare': ['medical', 'healthcare', 'clinic'],
            'construction': ['construction', 'contractor', 'builder'],
            'logistics': ['warehouse', 'logistics', 'distribution']
        }

        for industry, terms in industry_terms.items():
            if any(term in text_lower for term in terms):
                keywords["industry_markers"].append(industry)

        return keywords

    def _detect_red_flags(self, text: str) -> list:
        """Detect red flags in posting."""
        text_lower = text.lower()
        red_flags = []

        # MLM/Scam indicators
        mlm_terms = [
            'unlimited income', 'be your own boss', 'work from home',
            'no experience necessary', 'make money fast',
            'pyramid', 'multi-level marketing'
        ]
        if any(term in text_lower for term in mlm_terms):
            red_flags.append('mlm_language')

        # National chains
        chains = [
            'mcdonalds', 'walmart', 'target', 'starbucks',
            'home depot', 'lowes', 'cvs', 'walgreens'
        ]
        if any(chain in text_lower for chain in chains):
            red_flags.append('national_chain')

        # Poor quality indicators
        if len(text) < 100:
            red_flags.append('sparse_posting')

        if text.count('!') > 5:
            red_flags.append('excessive_punctuation')

        return red_flags

    def _calculate_professionalism(self, text: str) -> int:
        """Calculate professionalism score (1-10)."""
        score = 5  # Start at middle

        # Positive indicators
        if len(text) > 200:
            score += 1
        if re.search(r'benefits|insurance|401k', text, re.IGNORECASE):
            score += 1
        if re.search(r'qualifications|requirements|responsibilities', text, re.IGNORECASE):
            score += 1
        if '@' in text or 'http' in text:
            score += 1

        # Negative indicators
        if text.count('!') > 3:
            score -= 1
        if text.isupper():
            score -= 2
        if len(text) < 100:
            score -= 1

        return max(1, min(10, score))
