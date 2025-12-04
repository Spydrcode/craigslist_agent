"""
Helper functions for data processing and extraction.
"""
import hashlib
import re
from typing import List, Tuple, Optional, Dict
from datetime import datetime
from models import RawJobPosting, ParsedJobPosting


def generate_job_id(url: str) -> str:
    """
    Generate a unique ID for a job posting based on its URL.

    Args:
        url: Job posting URL

    Returns:
        Unique hash-based ID
    """
    return hashlib.md5(url.encode()).hexdigest()


def extract_salary_info(text: str) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    """
    Extract salary information from job description text.

    Args:
        text: Job description text

    Returns:
        Tuple of (min_salary, max_salary, original_text)
    """
    # Common salary patterns
    patterns = [
        r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*-\s*\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',  # $50,000 - $80,000
        r'\$\s*(\d+(?:,\d{3})*)\s*-\s*(\d+(?:,\d{3})*)',  # $50,000-80,000
        r'(\d+(?:,\d{3})*)\s*-\s*(\d+(?:,\d{3})*)\s*(?:per year|annually|/year|/yr)',  # 50,000-80,000 per year
        r'\$\s*(\d+)k\s*-\s*\$?\s*(\d+)k',  # $50k-$80k
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                min_val = float(match.group(1).replace(',', ''))
                max_val = float(match.group(2).replace(',', ''))

                # Convert 'k' notation to full number
                if 'k' in pattern.lower():
                    min_val *= 1000
                    max_val *= 1000

                return min_val, max_val, match.group(0)
            except (ValueError, AttributeError):
                continue

    # Single salary value
    single_patterns = [
        r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:per year|annually|/year|/yr)',
        r'\$\s*(\d+)k',
    ]

    for pattern in single_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                val = float(match.group(1).replace(',', ''))
                if 'k' in pattern.lower():
                    val *= 1000
                return val, val, match.group(0)
            except (ValueError, AttributeError):
                continue

    return None, None, None


def detect_work_arrangement(text: str) -> Dict[str, bool]:
    """
    Detect work arrangement from job description.

    Args:
        text: Job description text

    Returns:
        Dictionary with is_remote, is_hybrid, is_onsite flags
    """
    text_lower = text.lower()

    # Remote indicators
    remote_keywords = [
        'remote', 'work from home', 'wfh', 'telecommute',
        'distributed', 'anywhere', 'location independent'
    ]
    is_remote = any(keyword in text_lower for keyword in remote_keywords)

    # Hybrid indicators
    hybrid_keywords = [
        'hybrid', 'flexible', 'some remote', 'partially remote',
        'days in office', 'days remote'
    ]
    is_hybrid = any(keyword in text_lower for keyword in hybrid_keywords)

    # Onsite indicators (if not remote or hybrid)
    onsite_keywords = [
        'on-site', 'onsite', 'in-person', 'office based',
        'must be located', 'local candidates'
    ]
    is_onsite = any(keyword in text_lower for keyword in onsite_keywords)

    # Default to onsite if nothing else detected
    if not is_remote and not is_hybrid and not is_onsite:
        is_onsite = True

    return {
        'is_remote': is_remote,
        'is_hybrid': is_hybrid,
        'is_onsite': is_onsite
    }


def deduplicate_jobs(jobs: List[ParsedJobPosting]) -> List[ParsedJobPosting]:
    """
    Remove duplicate job postings based on URL.

    Args:
        jobs: List of job postings

    Returns:
        Deduplicated list of jobs
    """
    seen_urls = set()
    unique_jobs = []

    for job in jobs:
        if job.url not in seen_urls:
            seen_urls.add(job.url)
            unique_jobs.append(job)

    return unique_jobs


def clean_text(text: str) -> str:
    """
    Clean and normalize text for processing.

    Args:
        text: Raw text

    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove HTML entities
    text = re.sub(r'&[a-zA-Z]+;', ' ', text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def chunk_text(text: str, max_tokens: int = 8000) -> List[str]:
    """
    Split text into chunks that fit within token limits.

    Args:
        text: Text to chunk
        max_tokens: Maximum tokens per chunk (approximate)

    Returns:
        List of text chunks
    """
    # Rough estimate: 1 token ≈ 4 characters
    max_chars = max_tokens * 4

    if len(text) <= max_chars:
        return [text]

    # Split by paragraphs first
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = []
    current_length = 0

    for para in paragraphs:
        para_length = len(para)

        if current_length + para_length > max_chars:
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = [para]
                current_length = para_length
            else:
                # Single paragraph is too long, split by sentences
                sentences = para.split('. ')
                for sentence in sentences:
                    if current_length + len(sentence) > max_chars:
                        if current_chunk:
                            chunks.append('. '.join(current_chunk))
                        current_chunk = [sentence]
                        current_length = len(sentence)
                    else:
                        current_chunk.append(sentence)
                        current_length += len(sentence)
        else:
            current_chunk.append(para)
            current_length += para_length

    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))

    return chunks
