"""
Hybrid Orchestrator: Real-time + Batch Processing

Two modes:
1. Real-time: Interactive dashboard searches (gpt-4o-mini, immediate results)
2. Batch: Overnight bulk processing (gpt-4o-mini batch API, 50% savings)
"""
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from orchestrator_simple import SimpleProspectingOrchestrator
from agents.batch_processor_agent import BatchProcessorAgent
from utils import get_logger

logger = get_logger(__name__)


class HybridProspectingOrchestrator:
    """
    Orchestrator that supports both real-time and batch processing modes.

    Real-time Mode:
      - User clicks "Search" in dashboard
      - Uses gpt-4o-mini (real-time API)
      - Results in 10-15 minutes
      - Cost: ~$0.10 per 400 jobs

    Batch Mode:
      - Schedule nightly jobs for multiple cities
      - Uses gpt-4o-mini (Batch API)
      - Results in 24 hours
      - Cost: ~$0.05 per 400 jobs (50% discount)
    """

    def __init__(
        self,
        use_ai_parsing: bool = True,
        use_company_research: bool = True,
        output_dir: str = "output/prospects",
        batch_output_dir: str = "output/batch_results"
    ):
        """
        Initialize hybrid orchestrator.

        Args:
            use_ai_parsing: Use AI for parsing
            use_company_research: Research companies
            output_dir: Real-time results directory
            batch_output_dir: Batch results directory
        """
        # Real-time orchestrator (uses gpt-4o-mini by default)
        self.realtime_orchestrator = SimpleProspectingOrchestrator(
            use_ai_parsing=use_ai_parsing,
            use_company_research=use_company_research,
            output_dir=output_dir
        )

        # Batch processor
        self.batch_processor = BatchProcessorAgent(output_dir=batch_output_dir)

        self.batch_output_dir = Path(batch_output_dir)
        self.batch_output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("HybridProspectingOrchestrator initialized")

    def find_prospects_realtime(
        self,
        city: str = "phoenix",
        category: str = "sof",
        keywords: Optional[List[str]] = None,
        max_pages: int = 2,
        min_growth_score: float = 0.2,
        min_lead_score: float = 30.0
    ) -> Dict[str, Any]:
        """
        Real-time prospect finding (immediate results).

        Use this when:
        - User clicks "Search" in dashboard
        - Need results immediately
        - Processing 1-2 cities

        Args:
            city: Craigslist city code
            category: Job category
            keywords: Search keywords
            max_pages: Pages to scrape
            min_growth_score: Minimum growth score (lowered to 0.2 for testing)
            min_lead_score: Minimum lead score (lowered to 30 for testing)

        Returns:
            Results with prospects and stats
        """
        logger.info(f"Starting REAL-TIME search: {city}/{category}")

        return self.realtime_orchestrator.find_prospects(
            city=city,
            category=category,
            keywords=keywords,
            max_pages=max_pages,
            min_growth_score=min_growth_score,
            min_lead_score=min_lead_score
        )

    def schedule_batch_job(
        self,
        cities: List[str],
        category: str = "sof",
        keywords: Optional[List[str]] = None,
        max_pages: int = 2,
        job_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Schedule batch job for multiple cities (50% cost savings).

        Use this when:
        - Want to scan entire country overnight
        - Processing 10+ cities
        - Don't need immediate results
        - Want to save 50% on API costs

        Args:
            cities: List of city codes to process
            category: Job category
            keywords: Search keywords
            max_pages: Pages per city
            job_name: Optional job name

        Returns:
            Batch job information with batch_id
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        job_name = job_name or f"batch_prospects_{timestamp}"

        logger.info(f"Scheduling BATCH JOB: {len(cities)} cities")
        logger.info(f"Cities: {', '.join(cities)}")

        # 1. Scrape all cities (no AI yet, just collect raw data)
        all_jobs = []
        for city in cities:
            logger.info(f"Scraping {city}...")
            from models import ScraperConfig
            from agents.scraper_agent import ScraperAgent

            config = ScraperConfig(
                city=city,
                category=category,
                keywords=keywords,
                max_pages=max_pages,
                quick_scan_only=True  # Fast scraping
            )

            scraper = ScraperAgent(config)
            jobs = scraper.scrape_listings()

            # Add city metadata
            for job in jobs:
                all_jobs.append({
                    'city': city,
                    'title': job.title,
                    'url': job.url,
                    'location': job.location,
                    'posted_date': job.posted_date,
                    'description': job.description or job.title
                })

        logger.info(f"Scraped {len(all_jobs)} total jobs from {len(cities)} cities")

        # 2. Create batch input file for parsing
        batch_file = self.batch_processor.create_batch_input_file(
            job_postings=all_jobs,
            task_type="parse",
            model="gpt-4o-mini"  # Cheapest, best quality
        )

        # 3. Submit to OpenAI Batch API
        batch_info = self.batch_processor.submit_batch(
            input_file=batch_file,
            description=f"Parse jobs from {len(cities)} cities"
        )

        # 4. Save job metadata
        job_metadata = {
            'job_name': job_name,
            'batch_id': batch_info['batch_id'],
            'cities': cities,
            'category': category,
            'keywords': keywords,
            'total_jobs': len(all_jobs),
            'submitted_at': timestamp,
            'status': 'submitted'
        }

        metadata_file = self.batch_output_dir / f"{job_name}_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(job_metadata, f, indent=2)

        logger.info(f"Batch job submitted: {batch_info['batch_id']}")
        logger.info(f"Estimated completion: 24 hours")
        logger.info(f"Estimated cost: ${len(all_jobs) * 0.0001:.2f} (50% discount)")

        return job_metadata

    def check_batch_status(self, batch_id: str) -> Dict[str, Any]:
        """
        Check status of batch job.

        Args:
            batch_id: Batch ID from schedule_batch_job

        Returns:
            Status information
        """
        return self.batch_processor.check_batch_status(batch_id)

    def get_batch_results(self, batch_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve completed batch results.

        Args:
            batch_id: Batch ID from schedule_batch_job

        Returns:
            List of parsed prospects
        """
        return self.batch_processor.get_batch_results(batch_id)

    def list_batch_jobs(self) -> List[Dict[str, Any]]:
        """
        List all batch jobs (active and completed).

        Returns:
            List of batch job metadata
        """
        jobs = []
        for metadata_file in self.batch_output_dir.glob("*_metadata.json"):
            with open(metadata_file) as f:
                jobs.append(json.load(f))

        return sorted(jobs, key=lambda x: x['submitted_at'], reverse=True)
