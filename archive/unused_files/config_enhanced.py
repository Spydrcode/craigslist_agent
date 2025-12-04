"""
Enhanced configuration for intelligent prospecting system.
Includes settings for ML scoring, company research, and multi-platform integration.
"""
import os
from typing import Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class EnhancedConfig:
    """Enhanced configuration for intelligent prospecting."""

    # ==========================================
    # Core AI Configuration
    # ==========================================
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    # ==========================================
    # Vector Database
    # ==========================================
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENVIRONMENT: str = os.getenv("PINECONE_ENVIRONMENT", "")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "company-prospects")
    EMBEDDING_DIMENSION: int = 1536

    # ==========================================
    # Database
    # ==========================================
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

    # ==========================================
    # Company Research APIs
    # ==========================================
    # Google Custom Search
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GOOGLE_CSE_ID: str = os.getenv("GOOGLE_CSE_ID", "")

    # LinkedIn (requires premium/Sales Navigator)
    LINKEDIN_ACCESS_TOKEN: str = os.getenv("LINKEDIN_ACCESS_TOKEN", "")

    # Crunchbase
    CRUNCHBASE_API_KEY: str = os.getenv("CRUNCHBASE_API_KEY", "")

    # Clearbit for company enrichment
    CLEARBIT_API_KEY: str = os.getenv("CLEARBIT_API_KEY", "")

    # Hunter.io for email finding
    HUNTER_API_KEY: str = os.getenv("HUNTER_API_KEY", "")

    # BuiltWith for tech stack detection
    BUILTWITH_API_KEY: str = os.getenv("BUILTWITH_API_KEY", "")

    # ==========================================
    # Scraping Configuration
    # ==========================================
    SCRAPING_DELAY_MIN: int = int(os.getenv("SCRAPING_DELAY_MIN", "2"))
    SCRAPING_DELAY_MAX: int = int(os.getenv("SCRAPING_DELAY_MAX", "5"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

    # ==========================================
    # ML Scoring Configuration
    # ==========================================
    # Minimum scores for qualification
    MIN_GROWTH_SCORE: float = float(os.getenv("MIN_GROWTH_SCORE", "0.3"))
    MIN_LEAD_SCORE: float = float(os.getenv("MIN_LEAD_SCORE", "40.0"))
    MIN_OPPORTUNITY_CONFIDENCE: float = float(os.getenv("MIN_OPPORTUNITY_CONFIDENCE", "0.4"))

    # Feature weights for ML scoring
    GROWTH_WEIGHT: float = 0.30
    HIRING_WEIGHT: float = 0.25
    FIT_WEIGHT: float = 0.25
    OPPORTUNITY_WEIGHT: float = 0.20

    # ==========================================
    # Service Offerings Configuration
    # ==========================================
    # Your service offerings (customize based on your business)
    SERVICE_OFFERINGS: List[str] = [
        "AI/ML Consulting",
        "Data Engineering",
        "Cloud Migration",
        "DevOps/Platform Engineering",
        "API Development",
        "Full-Stack Development",
        "Data Analytics & BI",
        "Mobile App Development",
        "Security & Compliance",
        "Process Automation"
    ]

    # Your company information for value propositions
    YOUR_COMPANY_NAME: str = os.getenv("YOUR_COMPANY_NAME", "Your Company")
    YOUR_COMPANY_SPECIALTIES: List[str] = [
        "Machine Learning",
        "Data Engineering",
        "Cloud Infrastructure"
    ]

    # ==========================================
    # Outreach Configuration
    # ==========================================
    # Target decision maker titles
    TARGET_DECISION_MAKERS: List[str] = [
        "CTO",
        "VP Engineering",
        "VP Technology",
        "Director of Engineering",
        "Head of Engineering",
        "CEO",
        "COO",
        "VP Operations"
    ]

    # ==========================================
    # Research Configuration
    # ==========================================
    # Platforms to search for company information
    RESEARCH_PLATFORMS: List[str] = [
        "linkedin",
        "crunchbase",
        "google",
        "glassdoor"
    ]

    # Enable/disable research features
    ENABLE_WEB_RESEARCH: bool = os.getenv("ENABLE_WEB_RESEARCH", "true").lower() == "true"
    ENABLE_TECH_STACK_DETECTION: bool = os.getenv("ENABLE_TECH_STACK_DETECTION", "false").lower() == "true"
    ENABLE_EMAIL_FINDING: bool = os.getenv("ENABLE_EMAIL_FINDING", "false").lower() == "true"

    # ==========================================
    # Industry Focus Configuration
    # ==========================================
    # Industries you want to target (leave empty for all)
    TARGET_INDUSTRIES: List[str] = os.getenv(
        "TARGET_INDUSTRIES",
        "technology,software,fintech,healthcare tech,saas,e-commerce"
    ).split(",") if os.getenv("TARGET_INDUSTRIES") else []

    # Company size range (number of employees)
    MIN_COMPANY_SIZE: int = int(os.getenv("MIN_COMPANY_SIZE", "20"))
    MAX_COMPANY_SIZE: int = int(os.getenv("MAX_COMPANY_SIZE", "500"))

    # ==========================================
    # Logging Configuration
    # ==========================================
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_TO_FILE: bool = os.getenv("LOG_TO_FILE", "true").lower() == "true"
    LOG_DIR: str = os.getenv("LOG_DIR", "logs")

    # ==========================================
    # Output Configuration
    # ==========================================
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "output/prospects")
    EXPORT_FORMAT: str = os.getenv("EXPORT_FORMAT", "csv")  # csv, json, both

    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration is present."""
        required_fields = [
            ("OPENAI_API_KEY", cls.OPENAI_API_KEY),
        ]

        # Optional but recommended
        recommended_fields = [
            ("PINECONE_API_KEY", cls.PINECONE_API_KEY),
            ("SUPABASE_URL", cls.SUPABASE_URL),
            ("SUPABASE_KEY", cls.SUPABASE_KEY),
        ]

        missing = []
        for name, value in required_fields:
            if not value:
                missing.append(name)

        if missing:
            raise ValueError(
                f"Missing required configuration: {', '.join(missing)}. "
                f"Please check your .env file."
            )

        # Warn about recommended fields
        missing_recommended = [
            name for name, value in recommended_fields if not value
        ]
        if missing_recommended:
            print(
                f"Warning: Missing recommended configuration: {', '.join(missing_recommended)}. "
                f"Some features may be limited."
            )

        return True

    @classmethod
    def get_research_config(cls) -> dict:
        """Get configuration for company research."""
        return {
            'enable_web_research': cls.ENABLE_WEB_RESEARCH,
            'enable_tech_stack': cls.ENABLE_TECH_STACK_DETECTION,
            'enable_email_finding': cls.ENABLE_EMAIL_FINDING,
            'platforms': cls.RESEARCH_PLATFORMS
        }

    @classmethod
    def get_scoring_config(cls) -> dict:
        """Get configuration for ML scoring."""
        return {
            'min_growth_score': cls.MIN_GROWTH_SCORE,
            'min_lead_score': cls.MIN_LEAD_SCORE,
            'min_opportunity_confidence': cls.MIN_OPPORTUNITY_CONFIDENCE,
            'weights': {
                'growth': cls.GROWTH_WEIGHT,
                'hiring': cls.HIRING_WEIGHT,
                'fit': cls.FIT_WEIGHT,
                'opportunity': cls.OPPORTUNITY_WEIGHT
            }
        }


# Validate on import (with error handling)
try:
    EnhancedConfig.validate()
except ValueError as e:
    print(f"Configuration Warning: {e}")
