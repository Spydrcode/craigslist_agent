"""
Data models for the Craigslist Agent system.
Uses Pydantic for data validation and serialization.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl


class RawJobPosting(BaseModel):
    """Raw job posting data from scraper."""

    title: str
    url: str
    description: str
    location: str
    category: str
    posted_date: Optional[str] = None
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    raw_html: Optional[str] = None


class ParsedJobPosting(BaseModel):
    """Parsed and structured job posting data."""

    # Basic information
    title: str
    url: str
    description: str
    location: str
    category: str
    company_name: Optional[str] = None  # Company name extracted from posting
    posted_date: Optional[str] = None

    # Extracted insights
    skills: List[str] = Field(default_factory=list)
    pain_points: List[str] = Field(default_factory=list)
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_text: Optional[str] = None

    # Work arrangement
    is_remote: bool = False
    is_hybrid: bool = False
    is_onsite: bool = True

    # Metadata
    relevance_score: Optional[float] = None
    parsed_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class JobEmbedding(BaseModel):
    """Job posting with embedding vector."""

    job_id: str
    url: str
    title: str
    description_embedding: List[float]
    pain_points_embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ScraperConfig(BaseModel):
    """Configuration for scraper agent."""

    city: str = "sfbay"
    category: str = "sof"  # software jobs
    keywords: Optional[List[str]] = None
    max_pages: int = 5

    # Two-phase scraping strategy:
    # Phase 1: Quick scan - get ALL job titles/URLs (fast, no full details)
    # Phase 2: Deep analysis - only fetch full details for top N candidates after filtering
    quick_scan_only: bool = True  # If True, skip fetching full job details (faster)
    max_jobs_to_analyze: int = 30  # After filtering, how many to do full AI analysis on

    delay_min: int = 2
    delay_max: int = 5


class SearchQuery(BaseModel):
    """Semantic search query."""

    query_text: str
    top_k: int = 10
    filter_metadata: Optional[Dict[str, Any]] = None
    min_score: float = 0.7


class JobAnalysis(BaseModel):
    """AI-generated analysis of a job posting."""

    job_url: str
    pain_points: List[str]
    required_skills: List[str]
    nice_to_have_skills: List[str]
    salary_insights: Optional[str] = None
    work_arrangement: str  # remote, hybrid, onsite
    relevance_score: float
    summary: str
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)


class JobSignal(BaseModel):
    """
    Signal data extracted from Craigslist job posting.
    Used to identify industry trends, NOT company contacts.
    """
    # Source posting
    job_url: str
    job_title: str
    posted_date: Optional[str] = None
    
    # Signal classification
    industry: str  # e.g., "Technology", "Healthcare", "Construction"
    job_category: str  # e.g., "Software Engineering", "Sales", "Operations"
    location: str  # City/region
    
    # Growth indicators
    urgency_level: str  # "high", "medium", "low" based on language
    num_roles: int = 1  # Number of positions being filled
    seniority_level: str  # "junior", "mid", "senior", "executive"
    
    # Additional signals
    growth_indicators: List[str] = Field(default_factory=list)  # "expanding", "new office", etc.
    required_skills: List[str] = Field(default_factory=list)
    is_remote: bool = False
    
    # Metadata
    extracted_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ExternalCompany(BaseModel):
    """
    Company discovered through external search (NOT from Craigslist).
    Represents a potential growth opportunity found via industry signals.
    """
    # Company identity
    company_name: str
    website: Optional[str] = None
    industry: str
    location: str
    
    # Growth scoring (0-100)
    growth_score: float = 0.0
    
    # Growth signals (evidence)
    signals: Dict[str, Any] = Field(default_factory=dict)
    # Example signals:
    # {
    #   "hiring_velocity": 12,  # number of open roles
    #   "job_boards": ["Indeed", "LinkedIn"],
    #   "recent_reviews": 5,  # reviews in last 30 days
    #   "website_activity": "high",
    #   "locations": ["San Francisco", "Austin"],
    #   "expansion_news": ["Opened Austin office Q4 2024"],
    #   "funding": "Series B"
    # }
    
    # Discovery metadata
    source: str = "industry-match"  # How we found this company
    matched_signal_industries: List[str] = Field(default_factory=list)
    discovered_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
