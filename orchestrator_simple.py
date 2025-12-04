"""
Simplified Orchestrator for Company Prospecting
Works without Pinecone or Supabase - saves results to files only.
"""
import uuid
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict
from pathlib import Path

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

logger = get_logger(__name__)


class SimpleProspectingOrchestrator:
    """
    Simplified orchestrator that works without database dependencies.
    Saves all results to JSON/CSV files.
    """

    def __init__(
        self,
        use_ai_parsing: bool = True,
        use_company_research: bool = True,
        output_dir: str = "output/prospects"
    ):
        """
        Initialize the orchestrator.

        Args:
            use_ai_parsing: Use AI for parsing job descriptions
            use_company_research: Perform company research
            output_dir: Directory to save results
        """
        logger.info("Initializing SimpleProspectingOrchestrator")

        self.use_ai_parsing = use_ai_parsing
        self.use_company_research = use_company_research
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize agents
        self.client_agent = ClientAgent() if use_ai_parsing else None
        self.parser_agent = ParserAgent(self.client_agent)
        self.growth_analyzer = GrowthSignalAnalyzerAgent()
        self.company_researcher = CompanyResearchAgent(self.client_agent)
        self.service_matcher = ServiceMatcherAgent(self.client_agent)
        self.ml_scorer = MLScoringAgent()

        logger.info("SimpleProspectingOrchestrator initialized successfully")

    def find_prospects(
        self,
        city: str = "sfbay",
        category: str = "sof",
        keywords: Optional[List[str]] = None,
        max_pages: int = 5,
        min_growth_score: float = 0.2,
        min_lead_score: float = 30.0
    ) -> Dict[str, Any]:
        """
        Find and qualify prospects.

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
        logger.info("STARTING PROSPECTING WORKFLOW")
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
            # Stage 1: Scrape
            logger.info("\nSTAGE 1: SCRAPING JOB POSTINGS")
            raw_jobs = self._scrape_jobs(city, category, keywords, max_pages)
            stats['jobs_scraped'] = len(raw_jobs)

            if not raw_jobs:
                return self._create_result(False, "No jobs found", stats)

            # Stage 2: Parse
            logger.info("\nSTAGE 2: PARSING JOB DATA")
            enhanced_jobs = self._parse_jobs(raw_jobs)

            # Stage 3: Group and analyze
            logger.info("\nSTAGE 3: ANALYZING GROWTH SIGNALS")
            company_groups = self._group_by_company(enhanced_jobs)
            stats['companies_identified'] = len(company_groups)

            growth_analysis = self._analyze_growth_signals(company_groups)

            # Filter by growth score
            promising_companies = {
                company: data for company, data in growth_analysis.items()
                if data['growth_signals'].growth_score >= min_growth_score
            }

            logger.info(
                f"Found {len(promising_companies)} companies with growth score >= {min_growth_score}"
            )

            # Stage 4: Research
            logger.info("\nSTAGE 4: RESEARCHING COMPANIES")
            prospects = self._research_companies(promising_companies)
            stats['companies_researched'] = len(prospects)

            # Stage 5: Identify opportunities
            logger.info("\nSTAGE 5: IDENTIFYING OPPORTUNITIES")
            prospects = self._identify_opportunities(prospects)
            stats['total_opportunities'] = sum(
                len(p.service_opportunities) for p in prospects
            )

            # Stage 6: Score
            logger.info("\nSTAGE 6: SCORING LEADS")
            prospects = self.ml_scorer.batch_score_leads(prospects)

            # Filter by score
            qualified_prospects = [
                p for p in prospects
                if p.lead_score >= min_lead_score
            ]
            stats['qualified_prospects'] = len(qualified_prospects)
            stats['high_priority_prospects'] = len([
                p for p in qualified_prospects
                if p.priority_tier in ['URGENT', 'HIGH']
            ])

            # Stage 7: Generate outreach plans
            logger.info("\nSTAGE 7: GENERATING OUTREACH PLANS")
            for prospect in qualified_prospects:
                self._generate_outreach_plan(prospect)

            # Stage 8: Save results
            logger.info("\nSTAGE 8: SAVING RESULTS")
            self._save_results(qualified_prospects, stats)

            # Complete
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            stats['duration_seconds'] = duration

            logger.info("\n" + "=" * 80)
            logger.info("PROSPECTING COMPLETE")
            logger.info("=" * 80)

            return {
                'success': True,
                'prospects': qualified_prospects,
                'stats': stats
            }

        except Exception as e:
            logger.error(f"Prospecting failed: {e}", exc_info=True)
            return self._create_result(False, str(e), stats)

    def _scrape_jobs(self, city, category, keywords, max_pages):
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
        logger.info(f"Scraped {len(raw_jobs)} jobs")
        return raw_jobs

    def _parse_jobs(self, raw_jobs):
        """Parse jobs with AI."""
        enhanced_jobs = []

        for raw_job in raw_jobs:
            parsed = self.parser_agent.parse_jobs([raw_job], use_ai=self.use_ai_parsing)[0]

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

            # Extract company name
            enhanced_job.company_name = self._extract_company_name(parsed.title, parsed.description)
            enhanced_jobs.append(enhanced_job)

        return enhanced_jobs

    def _extract_company_name(self, title: str, description: str) -> Optional[str]:
        """Extract company name from job posting."""
        # Simple extraction - can be enhanced
        import re

        # Look for "Company: XYZ" pattern
        match = re.search(r'company[:\s]+([a-zA-Z0-9\s&\.]+)', description.lower())
        if match:
            return match.group(1).strip().title()

        # If not found, return None (will group as "Unknown")
        return None

    def _group_by_company(self, jobs):
        """Group jobs by company."""
        groups = defaultdict(list)
        for job in jobs:
            company = job.company_name or "Unknown Company"
            groups[company].append(job)
        return dict(groups)

    def _analyze_growth_signals(self, company_groups):
        """Analyze growth for each company."""
        analysis = {}
        for company, postings in company_groups.items():
            growth_signals = self.growth_analyzer.analyze_multiple_postings(
                postings, company
            )
            analysis[company] = {
                'postings': postings,
                'growth_signals': growth_signals
            }
        return analysis

    def _research_companies(self, company_data):
        """Research companies."""
        prospects = []

        for company_name, data in company_data.items():
            postings = data['postings']
            growth_signals = data['growth_signals']

            profile = CompanyProfile(
                name=company_name,
                location=postings[0].location if postings else None,
                growth_signals=growth_signals
            )

            # Research if enabled
            if self.use_company_research:
                query = ResearchQuery(
                    company_name=company_name,
                    location=profile.location
                )
                profile = self.company_researcher.research_company(query)
                profile.growth_signals = growth_signals

            prospect = ProspectLead(
                lead_id=str(uuid.uuid4()),
                company_profile=profile,
                job_postings=postings
            )

            prospects.append(prospect)

        return prospects

    def _identify_opportunities(self, prospects):
        """Identify service opportunities."""
        for prospect in prospects:
            opportunities = self.service_matcher.identify_opportunities(prospect)
            prospect.service_opportunities = opportunities

            if opportunities:
                prospect.total_opportunity_score = sum(
                    opp.confidence_score for opp in opportunities
                ) / len(opportunities)

        return prospects

    def _generate_outreach_plan(self, prospect):
        """Generate outreach plan."""
        if not prospect.service_opportunities:
            return

        top_opp = prospect.service_opportunities[0]

        talking_points = [
            f"Noticed you're hiring for {len(prospect.job_postings)} positions",
            f"Your focus on {top_opp.service_type} aligns with our expertise",
        ]

        if prospect.company_profile.growth_signals:
            gs = prospect.company_profile.growth_signals
            if gs.expansion_mentioned:
                talking_points.append("Your expansion creates unique challenges we can solve")

        prospect.key_talking_points = talking_points
        prospect.decision_maker_target = "CTO or VP Engineering"
        prospect.recommended_approach = (
            f"Direct outreach. Urgency: {top_opp.urgency.value.upper()}. "
            f"Lead with {top_opp.service_type} expertise."
        )

    def _save_results(self, prospects, stats):
        """Save results to files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save full JSON
        json_file = self.output_dir / f"prospects_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(
                [self._prospect_to_dict(p) for p in prospects],
                f,
                indent=2,
                default=str
            )
        logger.info(f"Saved JSON: {json_file}")

        # Save CSV
        csv_file = self.output_dir / f"prospects_{timestamp}.csv"
        self._save_csv(prospects, csv_file)
        logger.info(f"Saved CSV: {csv_file}")

        # Save stats
        stats_file = self.output_dir / f"stats_{timestamp}.json"
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        logger.info(f"Saved stats: {stats_file}")

    def _prospect_to_dict(self, prospect):
        """Convert prospect to dictionary."""
        return {
            'lead_id': prospect.lead_id,
            'company_name': prospect.company_profile.name,
            'lead_score': prospect.lead_score,
            'priority': prospect.priority_tier,
            'location': prospect.company_profile.location,
            'job_count': len(prospect.job_postings),
            'growth_stage': prospect.company_profile.growth_signals.growth_stage.value if prospect.company_profile.growth_signals else 'unknown',
            'growth_score': prospect.company_profile.growth_signals.growth_score if prospect.company_profile.growth_signals else 0,
            'opportunities': [
                {
                    'service': opp.service_type,
                    'confidence': opp.confidence_score,
                    'value': opp.estimated_value,
                    'reasoning': opp.reasoning
                }
                for opp in prospect.service_opportunities
            ],
            'talking_points': prospect.key_talking_points,
            'decision_maker': prospect.decision_maker_target,
            'approach': prospect.recommended_approach
        }

    def _save_csv(self, prospects, filepath):
        """Save prospects to CSV."""
        import csv

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Company', 'Lead Score', 'Priority', 'Jobs', 'Growth Stage',
                'Top Opportunity', 'Value', 'Approach', 'Location'
            ])

            for p in prospects:
                top_opp = p.service_opportunities[0] if p.service_opportunities else None
                writer.writerow([
                    p.company_profile.name,
                    f"{p.lead_score:.1f}",
                    p.priority_tier,
                    len(p.job_postings),
                    p.company_profile.growth_signals.growth_stage.value if p.company_profile.growth_signals else 'unknown',
                    top_opp.service_type if top_opp else 'None',
                    top_opp.estimated_value if top_opp else 'N/A',
                    p.recommended_approach or 'TBD',
                    p.company_profile.location or 'Unknown'
                ])

    def _create_result(self, success, error, stats):
        """Create result dictionary."""
        result = {'success': success, 'stats': stats}
        if error:
            result['error'] = error
        return result
