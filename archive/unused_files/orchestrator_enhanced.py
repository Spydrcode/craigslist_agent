"""
Enhanced Orchestrator for Intelligent Company Prospecting
Coordinates all agents in an intelligent workflow to find companies that need your services.
"""
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict

from config import Config
from utils import get_logger
from models_enhanced import (
    JobPostingEnhanced,
    CompanyProfile,
    ProspectLead,
    ResearchQuery,
    GrowthSignals
)
from agents.scraper_agent import ScraperAgent
from agents.parser_agent import ParserAgent
from agents.client_agent import ClientAgent
from agents.growth_signal_analyzer import GrowthSignalAnalyzerAgent
from agents.company_research_agent import CompanyResearchAgent
from agents.service_matcher_agent import ServiceMatcherAgent
from agents.ml_scoring_agent import MLScoringAgent
from agents.database_agent import DatabaseAgent

logger = get_logger(__name__)


class IntelligentProspectingOrchestrator:
    """
    Enhanced orchestrator for intelligent company prospecting.

    This orchestrator implements a sophisticated workflow:
    1. Scrape job postings from Craigslist
    2. Parse and extract structured data
    3. Group postings by company
    4. Analyze growth signals
    5. Research companies across multiple platforms
    6. Identify service opportunities
    7. Score and prioritize leads using ML
    8. Generate actionable outreach plans
    """

    def __init__(
        self,
        use_ai_parsing: bool = True,
        use_company_research: bool = True,
        use_ml_scoring: bool = True,
        save_to_database: bool = True
    ):
        """
        Initialize the orchestrator.

        Args:
            use_ai_parsing: Use AI for parsing job descriptions
            use_company_research: Perform multi-platform company research
            use_ml_scoring: Use ML for lead scoring
            save_to_database: Save results to database
        """
        logger.info("Initializing IntelligentProspectingOrchestrator")

        self.use_ai_parsing = use_ai_parsing
        self.use_company_research = use_company_research
        self.use_ml_scoring = use_ml_scoring
        self.save_to_database = save_to_database

        # Initialize agents
        self.client_agent = ClientAgent() if use_ai_parsing else None
        self.parser_agent = ParserAgent(self.client_agent)
        self.growth_analyzer = GrowthSignalAnalyzerAgent()
        self.company_researcher = CompanyResearchAgent(self.client_agent)
        self.service_matcher = ServiceMatcherAgent(self.client_agent)
        self.ml_scorer = MLScoringAgent()
        self.database_agent = DatabaseAgent() if save_to_database else None

        logger.info("IntelligentProspectingOrchestrator initialized successfully")

    def find_prospects(
        self,
        city: str = "sfbay",
        category: str = "sof",
        keywords: Optional[List[str]] = None,
        max_pages: int = 5,
        min_growth_score: float = 0.3,
        min_lead_score: float = 40.0
    ) -> Dict[str, Any]:
        """
        Main workflow to find and qualify prospects.

        Args:
            city: Craigslist city code
            category: Job category code
            keywords: Search keywords
            max_pages: Maximum pages to scrape
            min_growth_score: Minimum growth score threshold (0-1)
            min_lead_score: Minimum lead score threshold (0-100)

        Returns:
            Dictionary with prospects and statistics
        """
        logger.info("=" * 80)
        logger.info("STARTING INTELLIGENT PROSPECTING WORKFLOW")
        logger.info("=" * 80)

        start_time = datetime.utcnow()
        stats = {
            'jobs_scraped': 0,
            'companies_identified': 0,
            'companies_researched': 0,
            'qualified_prospects': 0,
            'high_priority_prospects': 0,
            'total_opportunities': 0
        }

        try:
            # ==========================================
            # STAGE 1: Scrape Job Postings
            # ==========================================
            logger.info("\n" + "=" * 80)
            logger.info("STAGE 1: SCRAPING JOB POSTINGS")
            logger.info("=" * 80)

            raw_jobs = self._scrape_jobs(city, category, keywords, max_pages)
            stats['jobs_scraped'] = len(raw_jobs)

            if not raw_jobs:
                return self._create_result(False, "No jobs found", stats)

            # ==========================================
            # STAGE 2: Parse and Enhance Job Data
            # ==========================================
            logger.info("\n" + "=" * 80)
            logger.info("STAGE 2: PARSING AND ENHANCING JOB DATA")
            logger.info("=" * 80)

            enhanced_jobs = self._parse_jobs(raw_jobs)

            # ==========================================
            # STAGE 3: Group by Company and Analyze Growth
            # ==========================================
            logger.info("\n" + "=" * 80)
            logger.info("STAGE 3: GROUPING BY COMPANY & ANALYZING GROWTH")
            logger.info("=" * 80)

            company_groups = self._group_by_company(enhanced_jobs)
            stats['companies_identified'] = len(company_groups)

            growth_analysis = self._analyze_growth_signals(company_groups)

            # Filter companies by growth score
            promising_companies = {
                company: data for company, data in growth_analysis.items()
                if data['growth_signals'].growth_score >= min_growth_score
            }

            logger.info(
                f"Found {len(promising_companies)} companies with growth score >= {min_growth_score}"
            )

            # ==========================================
            # STAGE 4: Company Research
            # ==========================================
            logger.info("\n" + "=" * 80)
            logger.info("STAGE 4: RESEARCHING COMPANIES")
            logger.info("=" * 80)

            prospects = self._research_companies(promising_companies)
            stats['companies_researched'] = len(prospects)

            # ==========================================
            # STAGE 5: Identify Service Opportunities
            # ==========================================
            logger.info("\n" + "=" * 80)
            logger.info("STAGE 5: IDENTIFYING SERVICE OPPORTUNITIES")
            logger.info("=" * 80)

            prospects = self._identify_opportunities(prospects)
            stats['total_opportunities'] = sum(
                len(p.service_opportunities) for p in prospects
            )

            # ==========================================
            # STAGE 6: ML-Based Lead Scoring
            # ==========================================
            logger.info("\n" + "=" * 80)
            logger.info("STAGE 6: SCORING AND PRIORITIZING LEADS")
            logger.info("=" * 80)

            if self.use_ml_scoring:
                prospects = self.ml_scorer.batch_score_leads(prospects)
            else:
                # Simple scoring fallback
                for prospect in prospects:
                    prospect.lead_score = prospect.company_profile.growth_signals.growth_score * 100

            # Filter by minimum score
            qualified_prospects = [
                p for p in prospects
                if p.lead_score >= min_lead_score
            ]
            stats['qualified_prospects'] = len(qualified_prospects)
            stats['high_priority_prospects'] = len([
                p for p in qualified_prospects
                if p.priority_tier in ['URGENT', 'HIGH']
            ])

            # ==========================================
            # STAGE 7: Generate Outreach Plans
            # ==========================================
            logger.info("\n" + "=" * 80)
            logger.info("STAGE 7: GENERATING OUTREACH PLANS")
            logger.info("=" * 80)

            for prospect in qualified_prospects:
                self._generate_outreach_plan(prospect)

            # ==========================================
            # STAGE 8: Save Results
            # ==========================================
            if self.save_to_database and qualified_prospects:
                logger.info("\n" + "=" * 80)
                logger.info("STAGE 8: SAVING RESULTS")
                logger.info("=" * 80)
                self._save_prospects(qualified_prospects)

            # ==========================================
            # PIPELINE COMPLETE
            # ==========================================
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            stats['duration_seconds'] = duration

            logger.info("\n" + "=" * 80)
            logger.info("PROSPECTING WORKFLOW COMPLETE")
            logger.info("=" * 80)
            logger.info(f"Duration: {duration:.1f} seconds")
            logger.info(f"Qualified Prospects: {stats['qualified_prospects']}")
            logger.info(f"High Priority: {stats['high_priority_prospects']}")

            return {
                'success': True,
                'prospects': qualified_prospects,
                'stats': stats
            }

        except Exception as e:
            logger.error(f"Prospecting workflow failed: {e}", exc_info=True)
            return self._create_result(False, str(e), stats)

    def _scrape_jobs(
        self,
        city: str,
        category: str,
        keywords: Optional[List[str]],
        max_pages: int
    ) -> List:
        """Scrape job postings."""
        from models import ScraperConfig

        config = ScraperConfig(
            city=city,
            category=category,
            keywords=keywords,
            max_pages=max_pages
        )

        scraper = ScraperAgent(config)
        raw_jobs = scraper.scrape_listings()

        logger.info(f"Scraped {len(raw_jobs)} job postings")
        return raw_jobs

    def _parse_jobs(self, raw_jobs: List) -> List[JobPostingEnhanced]:
        """Parse raw jobs into enhanced format."""
        enhanced_jobs = []

        for raw_job in raw_jobs:
            # Parse using existing parser
            parsed = self.parser_agent.parse_jobs([raw_job], use_ai=self.use_ai_parsing)[0]

            # Convert to enhanced model
            enhanced_job = JobPostingEnhanced(
                title=parsed.title,
                url=parsed.url,
                description=parsed.description,
                location=parsed.location,
                posted_date=parsed.posted_date,
                skills_required=parsed.skills,
                pain_points=parsed.pain_points,
                salary_min=parsed.salary_min,
                salary_max=parsed.salary_max,
                salary_text=parsed.salary_text,
                is_remote=parsed.is_remote,
                is_hybrid=parsed.is_hybrid,
                is_onsite=parsed.is_onsite
            )

            # Extract company name from title or description
            enhanced_job.company_name = self._extract_company_name(raw_job)

            # Identify growth indicators in posting
            enhanced_job.growth_indicators = self._extract_growth_indicators(enhanced_job)

            enhanced_jobs.append(enhanced_job)

        logger.info(f"Parsed {len(enhanced_jobs)} jobs with AI enhancement")
        return enhanced_jobs

    def _group_by_company(
        self,
        jobs: List[JobPostingEnhanced]
    ) -> Dict[str, List[JobPostingEnhanced]]:
        """Group job postings by company."""
        groups = defaultdict(list)

        for job in jobs:
            company_name = job.company_name or "Unknown Company"
            groups[company_name].append(job)

        logger.info(f"Grouped jobs into {len(groups)} companies")
        return dict(groups)

    def _analyze_growth_signals(
        self,
        company_groups: Dict[str, List[JobPostingEnhanced]]
    ) -> Dict[str, Dict[str, Any]]:
        """Analyze growth signals for each company."""
        analysis = {}

        for company_name, postings in company_groups.items():
            growth_signals = self.growth_analyzer.analyze_multiple_postings(
                postings,
                company_name
            )

            analysis[company_name] = {
                'postings': postings,
                'growth_signals': growth_signals
            }

            logger.debug(
                f"{company_name}: growth_score={growth_signals.growth_score:.2f}, "
                f"stage={growth_signals.growth_stage.value}"
            )

        return analysis

    def _research_companies(
        self,
        company_data: Dict[str, Dict[str, Any]]
    ) -> List[ProspectLead]:
        """Research companies to build comprehensive profiles."""
        prospects = []

        for company_name, data in company_data.items():
            postings = data['postings']
            growth_signals = data['growth_signals']

            # Create base profile
            profile = CompanyProfile(
                name=company_name,
                location=postings[0].location if postings else None,
                growth_signals=growth_signals
            )

            # Perform multi-platform research if enabled
            if self.use_company_research:
                query = ResearchQuery(
                    company_name=company_name,
                    location=profile.location
                )
                profile = self.company_researcher.research_company(query)
                profile.growth_signals = growth_signals

            # Create prospect lead
            prospect = ProspectLead(
                lead_id=str(uuid.uuid4()),
                company_profile=profile,
                job_postings=postings
            )

            prospects.append(prospect)

        logger.info(f"Researched {len(prospects)} companies")
        return prospects

    def _identify_opportunities(
        self,
        prospects: List[ProspectLead]
    ) -> List[ProspectLead]:
        """Identify service opportunities for prospects."""
        for prospect in prospects:
            opportunities = self.service_matcher.identify_opportunities(prospect)
            prospect.service_opportunities = opportunities

            # Calculate total opportunity score
            if opportunities:
                prospect.total_opportunity_score = sum(
                    opp.confidence_score for opp in opportunities
                ) / len(opportunities)

        return prospects

    def _generate_outreach_plan(self, prospect: ProspectLead):
        """Generate outreach plan for a prospect."""
        if not prospect.service_opportunities:
            return

        top_opportunity = prospect.service_opportunities[0]

        # Generate talking points
        talking_points = [
            f"Noticed you're hiring for {len(prospect.job_postings)} positions",
            f"Your focus on {top_opportunity.service_type} aligns with our expertise",
        ]

        if prospect.company_profile.growth_signals:
            gs = prospect.company_profile.growth_signals
            if gs.expansion_mentioned:
                talking_points.append("Your company's expansion creates unique challenges we can help solve")

        prospect.key_talking_points = talking_points

        # Determine decision maker target
        if any('director' in p.title.lower() or 'vp' in p.title.lower() for p in prospect.job_postings):
            prospect.decision_maker_target = "VP/Director of Engineering or Operations"
        else:
            prospect.decision_maker_target = "CTO or Head of Engineering"

        # Recommended approach
        urgency = top_opportunity.urgency.value
        prospect.recommended_approach = (
            f"Direct outreach to {prospect.decision_maker_target}. "
            f"Urgency: {urgency.upper()}. "
            f"Lead with {top_opportunity.service_type} expertise."
        )

    def _save_prospects(self, prospects: List[ProspectLead]):
        """Save prospects to database."""
        if not self.database_agent:
            return

        try:
            # Implementation depends on database schema
            # For now, just log
            logger.info(f"Saved {len(prospects)} prospects to database")
        except Exception as e:
            logger.error(f"Error saving prospects: {e}")

    def _extract_company_name(self, raw_job: Any) -> Optional[str]:
        """Extract company name from job posting."""
        # Simple extraction - enhance based on your scraping logic
        # This is a placeholder
        return None

    def _extract_growth_indicators(self, job: JobPostingEnhanced) -> List[str]:
        """Extract growth indicators from job posting."""
        indicators = []
        text = f"{job.title} {job.description}".lower()

        growth_keywords = [
            'expanding', 'growth', 'scaling', 'new location',
            'rapid growth', 'funded', 'series'
        ]

        for keyword in growth_keywords:
            if keyword in text:
                indicators.append(keyword)

        return indicators

    def _create_result(
        self,
        success: bool,
        error: Optional[str],
        stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create standardized result dictionary."""
        result = {
            'success': success,
            'stats': stats
        }
        if error:
            result['error'] = error
        return result

    def export_prospects_to_csv(
        self,
        prospects: List[ProspectLead],
        output_file: str
    ):
        """Export prospects to CSV for easy review."""
        import pandas as pd

        data = []
        for prospect in prospects:
            data.append({
                'Company': prospect.company_profile.name,
                'Lead Score': f"{prospect.lead_score:.1f}",
                'Priority': prospect.priority_tier,
                'Job Count': len(prospect.job_postings),
                'Growth Stage': prospect.company_profile.growth_signals.growth_stage.value if prospect.company_profile.growth_signals else 'unknown',
                'Top Opportunity': prospect.service_opportunities[0].service_type if prospect.service_opportunities else 'None',
                'Opportunity Value': prospect.service_opportunities[0].estimated_value if prospect.service_opportunities else 'N/A',
                'Decision Maker': prospect.decision_maker_target or 'TBD',
                'Location': prospect.company_profile.location,
                'Approach': prospect.recommended_approach or 'TBD'
            })

        df = pd.DataFrame(data)
        df.to_csv(output_file, index=False)
        logger.info(f"Exported {len(prospects)} prospects to {output_file}")
