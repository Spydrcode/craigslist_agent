"""
Enhanced data models for intelligent company prospecting system.
Tracks growth signals, service opportunities, and ML features.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class GrowthStage(str, Enum):
    """Company growth stage classification."""
    EARLY_STAGE = "early_stage"
    RAPID_GROWTH = "rapid_growth"
    SCALING = "scaling"
    ESTABLISHED = "established"
    DECLINING = "declining"
    UNKNOWN = "unknown"


class HiringUrgency(str, Enum):
    """Hiring urgency classification."""
    CRITICAL = "critical"  # Multiple urgent positions
    HIGH = "high"  # Active hiring, growth signals
    MEDIUM = "medium"  # Regular hiring
    LOW = "low"  # Single position, no urgency
    UNKNOWN = "unknown"


class ServiceOpportunity(BaseModel):
    """Identified service opportunity for a company."""
    service_type: str  # e.g., "AI/ML Consulting", "Data Engineering", "Cloud Migration"
    confidence_score: float = Field(ge=0.0, le=1.0)
    reasoning: str
    pain_points_addressed: List[str] = Field(default_factory=list)
    estimated_value: Optional[str] = None  # e.g., "$50K-$100K"
    urgency: HiringUrgency = HiringUrgency.MEDIUM
    evidence: List[str] = Field(default_factory=list)  # Job posting excerpts, etc.


class GrowthSignals(BaseModel):
    """Detected growth indicators for a company."""
    is_hiring_multiple: bool = False
    multiple_departments: bool = False  # Hiring across departments
    leadership_positions: bool = False  # Hiring managers/directors
    expansion_mentioned: bool = False  # Explicit growth language
    new_location: bool = False
    funding_mentioned: bool = False
    technology_adoption: bool = False  # Adopting new tech

    # Calculated fields
    growth_score: float = Field(ge=0.0, le=1.0, default=0.0)
    growth_stage: GrowthStage = GrowthStage.UNKNOWN
    hiring_urgency: HiringUrgency = HiringUrgency.UNKNOWN

    # Supporting evidence
    evidence_text: List[str] = Field(default_factory=list)
    job_count: int = 0


class CompanyProfile(BaseModel):
    """Comprehensive company profile from multiple sources."""
    name: str
    domain: Optional[str] = None
    industry: Optional[str] = None
    size_range: Optional[str] = None  # e.g., "50-200"
    location: Optional[str] = None

    # Online presence
    linkedin_url: Optional[str] = None
    crunchbase_url: Optional[str] = None
    company_website: Optional[str] = None
    glassdoor_url: Optional[str] = None

    # Company data
    description: Optional[str] = None
    founded_year: Optional[int] = None
    funding_stage: Optional[str] = None  # Seed, Series A, etc.
    total_funding: Optional[str] = None
    employee_count_estimate: Optional[int] = None
    revenue_estimate: Optional[str] = None
    tech_stack: List[str] = Field(default_factory=list)

    # Growth signals
    growth_signals: Optional[GrowthSignals] = None

    # Contact information
    decision_makers: List[Dict[str, Any]] = Field(default_factory=list)
    contact_emails: List[str] = Field(default_factory=list)
    contact_phones: List[str] = Field(default_factory=list)

    # Metadata
    last_researched: datetime = Field(default_factory=datetime.utcnow)
    data_sources: List[str] = Field(default_factory=list)
    confidence_score: float = Field(ge=0.0, le=1.0, default=0.5)


class JobPostingEnhanced(BaseModel):
    """Enhanced job posting with growth signals and opportunities."""
    # Basic info
    title: str
    url: str
    description: str
    company_name: Optional[str] = None
    location: str
    posted_date: Optional[str] = None
    category: Optional[str] = None  # Job category

    # Extracted insights
    skills_required: List[str] = Field(default_factory=list)
    pain_points: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)

    # Compensation
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_text: Optional[str] = None

    # Work arrangement
    is_remote: bool = False
    is_hybrid: bool = False
    is_onsite: bool = True

    # Growth indicators (from posting)
    growth_indicators: List[str] = Field(default_factory=list)
    urgency_signals: List[str] = Field(default_factory=list)

    # Metadata
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ProspectLead(BaseModel):
    """Complete prospect lead with company profile and opportunities."""
    lead_id: str
    company_profile: CompanyProfile
    job_postings: List[JobPostingEnhanced] = Field(default_factory=list)

    # Opportunity analysis
    service_opportunities: List[ServiceOpportunity] = Field(default_factory=list)
    total_opportunity_score: float = Field(ge=0.0, le=1.0, default=0.0)

    # ML features for scoring
    ml_features: Dict[str, Any] = Field(default_factory=dict)

    # Lead scoring
    lead_score: float = Field(ge=0.0, le=100.0, default=0.0)
    priority_tier: str = "MEDIUM"  # LOW, MEDIUM, HIGH, URGENT

    # Outreach strategy
    recommended_approach: Optional[str] = None
    key_talking_points: List[str] = Field(default_factory=list)
    decision_maker_target: Optional[str] = None

    # Tracking
    status: str = "new"  # new, contacted, qualified, converted, rejected
    notes: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ResearchQuery(BaseModel):
    """Query for multi-platform company research."""
    company_name: str
    location: Optional[str] = None
    domain: Optional[str] = None

    # Search parameters
    search_platforms: List[str] = Field(
        default_factory=lambda: ["linkedin", "crunchbase", "google", "glassdoor"]
    )
    include_competitors: bool = False
    include_news: bool = True
    max_results_per_platform: int = 5


class MLFeatures(BaseModel):
    """Machine learning features for lead scoring."""
    # Company features
    company_size_encoded: float = 0.0
    industry_encoded: float = 0.0
    growth_stage_encoded: float = 0.0

    # Hiring features
    job_count: int = 0
    hiring_velocity: float = 0.0  # Jobs per week
    position_diversity: float = 0.0  # Variety of roles
    leadership_ratio: float = 0.0  # % of management positions

    # Urgency features
    urgency_keywords_count: int = 0
    salary_competitiveness: float = 0.0
    benefits_richness: float = 0.0

    # Technology features
    tech_stack_size: int = 0
    modern_tech_ratio: float = 0.0
    tech_debt_indicators: float = 0.0

    # Engagement features
    online_presence_score: float = 0.0
    social_media_activity: float = 0.0
    glassdoor_rating: Optional[float] = None

    # Calculated composite features
    growth_momentum_score: float = 0.0
    hiring_health_score: float = 0.0
    opportunity_fit_score: float = 0.0


class PlatformSearchResult(BaseModel):
    """Result from a platform search."""
    platform: str  # linkedin, crunchbase, google, etc.
    query: str
    results: List[Dict[str, Any]] = Field(default_factory=list)
    total_found: int = 0
    search_timestamp: datetime = Field(default_factory=datetime.utcnow)
    success: bool = True
    error_message: Optional[str] = None
