"""
Orchestrator for coordinating the entire job scraping and analysis pipeline.
Manages workflow between Scraper, Parser, Vector, and Database agents.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from config import Config
from utils import get_logger, deduplicate_jobs
from models import ScraperConfig, RawJobPosting, ParsedJobPosting
from agents import (
    ClientAgent,
    ScraperAgent,
    ParserAgent,
    VectorAgent,
    DatabaseAgent
)

logger = get_logger(__name__)


class Orchestrator:
    """
    Central orchestrator for the job scraping and analysis pipeline.
    Coordinates all agents and manages the complete workflow.
    """

    def __init__(
        self,
        use_ai_parsing: bool = True,
        use_vector_storage: bool = True,
        use_database_storage: bool = True
    ):
        """
        Initialize the Orchestrator.

        Args:
            use_ai_parsing: Whether to use AI for parsing (vs basic extraction)
            use_vector_storage: Whether to store embeddings in Pinecone
            use_database_storage: Whether to store data in Supabase
        """
        logger.info("Initializing Orchestrator")

        # Configuration
        self.use_ai_parsing = use_ai_parsing
        self.use_vector_storage = use_vector_storage
        self.use_database_storage = use_database_storage

        # Initialize agents
        self.client_agent = ClientAgent() if use_ai_parsing else None
        self.parser_agent = ParserAgent(self.client_agent)

        if use_vector_storage:
            self.vector_agent = VectorAgent(self.client_agent)
        else:
            self.vector_agent = None

        if use_database_storage:
            self.database_agent = DatabaseAgent()
        else:
            self.database_agent = None

        # Scheduler for periodic runs
        self.scheduler = BackgroundScheduler()

        logger.info("Orchestrator initialized successfully")

    def run_pipeline(
        self,
        city: str = "sfbay",
        category: str = "sof",
        keywords: Optional[List[str]] = None,
        max_pages: int = 3,
        criteria: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run the complete scraping and analysis pipeline.

        Args:
            city: Craigslist city code
            category: Job category code
            keywords: Optional search keywords
            max_pages: Maximum pages to scrape
            criteria: Optional criteria for relevance scoring

        Returns:
            Dictionary with pipeline results and statistics
        """
        logger.info(
            f"Starting pipeline for {city}/{category} "
            f"(keywords: {keywords}, max_pages: {max_pages})"
        )

        # Track scrape run in database
        run_id = None
        if self.database_agent:
            run_id = self.database_agent.create_scrape_run(
                city, category, keywords
            )

        try:
            # Stage 1: Scraping
            logger.info("=" * 60)
            logger.info("STAGE 1: SCRAPING")
            logger.info("=" * 60)

            scraper_config = ScraperConfig(
                city=city,
                category=category,
                keywords=keywords,
                max_pages=max_pages
            )

            scraper_agent = ScraperAgent(scraper_config)
            raw_jobs = scraper_agent.scrape_listings()

            logger.info(f"Scraped {len(raw_jobs)} raw jobs")

            if not raw_jobs:
                logger.warning("No jobs found, stopping pipeline")
                if run_id:
                    self.database_agent.complete_scrape_run(
                        run_id, 0, 0, 0, "No jobs found"
                    )
                return {
                    'success': False,
                    'error': 'No jobs found',
                    'stats': {}
                }

            # Store raw jobs if database enabled
            if self.database_agent:
                logger.info("Storing raw jobs in database")
                self.database_agent.insert_raw_jobs(raw_jobs)

            # Stage 2: Parsing
            logger.info("=" * 60)
            logger.info("STAGE 2: PARSING")
            logger.info("=" * 60)

            parsed_jobs = self.parser_agent.parse_jobs(
                raw_jobs,
                use_ai=self.use_ai_parsing
            )

            logger.info(f"Parsed {len(parsed_jobs)} jobs")

            # Deduplicate
            parsed_jobs = deduplicate_jobs(parsed_jobs)
            logger.info(f"After deduplication: {len(parsed_jobs)} jobs")

            # Enrich with relevance scores if criteria provided
            if criteria and self.use_ai_parsing:
                logger.info("Scoring job relevance")
                for job in parsed_jobs:
                    try:
                        score = self.parser_agent.score_job_relevance(
                            job, criteria
                        )
                        job.relevance_score = score
                    except Exception as e:
                        logger.error(f"Failed to score job {job.url}: {e}")

            # Stage 3: Vector Storage
            vector_count = 0
            if self.vector_agent:
                logger.info("=" * 60)
                logger.info("STAGE 3: VECTOR STORAGE")
                logger.info("=" * 60)

                vector_count = self.vector_agent.upsert_jobs(parsed_jobs)
                logger.info(f"Stored {vector_count} embeddings in Pinecone")

            # Stage 4: Database Storage
            db_count = 0
            if self.database_agent:
                logger.info("=" * 60)
                logger.info("STAGE 4: DATABASE STORAGE")
                logger.info("=" * 60)

                db_count = self.database_agent.insert_parsed_jobs(parsed_jobs)
                logger.info(f"Stored {db_count} jobs in Supabase")

                # Mark raw jobs as processed
                for job in parsed_jobs:
                    self.database_agent.mark_raw_job_processed(job.url)

            # Complete scrape run
            if run_id:
                self.database_agent.complete_scrape_run(
                    run_id,
                    jobs_found=len(raw_jobs),
                    jobs_parsed=len(parsed_jobs),
                    jobs_stored=db_count
                )

            # Pipeline summary
            logger.info("=" * 60)
            logger.info("PIPELINE COMPLETE")
            logger.info("=" * 60)

            stats = {
                'jobs_scraped': len(raw_jobs),
                'jobs_parsed': len(parsed_jobs),
                'embeddings_stored': vector_count,
                'database_records': db_count,
            }

            if criteria:
                # Calculate average relevance
                scores = [j.relevance_score for j in parsed_jobs if j.relevance_score]
                if scores:
                    stats['avg_relevance'] = sum(scores) / len(scores)
                    stats['high_relevance_count'] = len([s for s in scores if s >= 0.7])

            logger.info(f"Stats: {stats}")

            return {
                'success': True,
                'stats': stats,
                'jobs': parsed_jobs
            }

        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)

            if run_id:
                self.database_agent.complete_scrape_run(
                    run_id, 0, 0, 0, str(e)
                )

            return {
                'success': False,
                'error': str(e),
                'stats': {}
            }

    def search_jobs(
        self,
        query: str,
        top_k: int = 20,
        use_semantic_search: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search for jobs using semantic or text search.

        Args:
            query: Search query
            top_k: Number of results to return
            use_semantic_search: Use vector search vs text search

        Returns:
            List of matching jobs
        """
        logger.info(f"Searching for jobs: '{query}'")

        if use_semantic_search and self.vector_agent:
            # Use semantic search
            from models import SearchQuery

            search_query = SearchQuery(
                query_text=query,
                top_k=top_k,
                min_score=0.6
            )

            results = self.vector_agent.search_similar_jobs(search_query)

            logger.info(f"Found {len(results)} jobs via semantic search")
            return results

        elif self.database_agent:
            # Use text search
            results = self.database_agent.search_jobs(query, limit=top_k)

            logger.info(f"Found {len(results)} jobs via text search")
            return results

        else:
            logger.warning("No search capability available")
            return []

    def get_job_recommendations(
        self,
        job_id: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get job recommendations similar to a given job.

        Args:
            job_id: Reference job ID
            top_k: Number of recommendations

        Returns:
            List of similar jobs
        """
        if not self.vector_agent:
            logger.warning("Vector agent not available for recommendations")
            return []

        logger.info(f"Getting recommendations for job: {job_id}")

        similar_jobs = self.vector_agent.find_similar_to_job(
            job_id,
            top_k=top_k
        )

        logger.info(f"Found {len(similar_jobs)} similar jobs")
        return similar_jobs

    def schedule_daily_scrape(
        self,
        city: str = "sfbay",
        category: str = "sof",
        keywords: Optional[List[str]] = None,
        hour: int = 9,
        minute: int = 0
    ):
        """
        Schedule a daily scraping job.

        Args:
            city: Craigslist city code
            category: Job category code
            keywords: Optional search keywords
            hour: Hour to run (0-23)
            minute: Minute to run (0-59)
        """
        logger.info(
            f"Scheduling daily scrape for {city}/{category} "
            f"at {hour:02d}:{minute:02d}"
        )

        def job():
            logger.info("Running scheduled scrape")
            self.run_pipeline(
                city=city,
                category=category,
                keywords=keywords,
                max_pages=5
            )

        # Add job to scheduler
        self.scheduler.add_job(
            job,
            trigger=CronTrigger(hour=hour, minute=minute),
            id=f"daily_scrape_{city}_{category}",
            replace_existing=True
        )

        logger.info("Scheduled job added")

    def start_scheduler(self):
        """Start the background scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")

    def stop_scheduler(self):
        """Stop the background scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")

    def get_scheduled_jobs(self) -> List[str]:
        """Get list of scheduled job IDs."""
        return [job.id for job in self.scheduler.get_jobs()]

    def analyze_job_market(
        self,
        city: str = "sfbay",
        category: str = "sof"
    ) -> Dict[str, Any]:
        """
        Analyze the job market with aggregated statistics.

        Args:
            city: City to analyze
            category: Category to analyze

        Returns:
            Dictionary with market analysis
        """
        if not self.database_agent:
            logger.warning("Database agent required for market analysis")
            return {}

        logger.info(f"Analyzing job market for {city}/{category}")

        try:
            # Get jobs from database
            jobs = self.database_agent.get_jobs_by_criteria(
                category=category,
                limit=500
            )

            if not jobs:
                return {'error': 'No jobs found'}

            # Analyze
            analysis = {
                'total_jobs': len(jobs),
                'remote_jobs': len([j for j in jobs if j.get('is_remote')]),
                'hybrid_jobs': len([j for j in jobs if j.get('is_hybrid')]),
                'onsite_jobs': len([j for j in jobs if j.get('is_onsite')]),
            }

            # Salary statistics
            salaries = [
                (j.get('salary_min', 0) + j.get('salary_max', 0)) / 2
                for j in jobs
                if j.get('salary_min') and j.get('salary_max')
            ]

            if salaries:
                analysis['avg_salary'] = sum(salaries) / len(salaries)
                analysis['min_salary'] = min(salaries)
                analysis['max_salary'] = max(salaries)

            # Top skills
            all_skills = []
            for job in jobs:
                if job.get('skills'):
                    all_skills.extend(job['skills'])

            from collections import Counter
            skill_counts = Counter(all_skills)
            analysis['top_skills'] = skill_counts.most_common(20)

            # Common pain points
            all_pain_points = []
            for job in jobs:
                if job.get('pain_points'):
                    all_pain_points.extend(job['pain_points'])

            pain_point_counts = Counter(all_pain_points)
            analysis['common_pain_points'] = pain_point_counts.most_common(10)

            logger.info("Market analysis complete")
            return analysis

        except Exception as e:
            logger.error(f"Market analysis failed: {e}")
            return {'error': str(e)}

    def export_jobs_to_csv(
        self,
        output_file: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Export jobs to CSV file.

        Args:
            output_file: Output CSV file path
            filters: Optional filters for jobs

        Returns:
            True if successful
        """
        if not self.database_agent:
            logger.warning("Database agent required for export")
            return False

        try:
            import pandas as pd

            logger.info(f"Exporting jobs to {output_file}")

            # Get jobs
            if filters:
                jobs = self.database_agent.get_jobs_by_criteria(**filters)
            else:
                jobs = self.database_agent.get_recent_jobs(limit=1000)

            # Convert to DataFrame
            df = pd.DataFrame(jobs)

            # Export
            df.to_csv(output_file, index=False)

            logger.info(f"Exported {len(jobs)} jobs to {output_file}")
            return True

        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False
