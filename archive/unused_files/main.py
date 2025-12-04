"""
Main entry point for the Craigslist Job Scraper and Analyzer.
Provides a command-line interface for running the pipeline.
"""
import argparse
import json
import sys
from typing import Optional, List

from config import Config
from orchestrator import Orchestrator
from utils import setup_logger

# Set up main logger
logger = setup_logger(__name__, log_file='logs/main.log')


def run_scrape(
    city: str = "sfbay",
    category: str = "sof",
    keywords: Optional[List[str]] = None,
    max_pages: int = 3,
    criteria: Optional[dict] = None
):
    """
    Run the scraping pipeline.

    Args:
        city: Craigslist city code
        category: Job category code
        keywords: Search keywords
        max_pages: Maximum pages to scrape
        criteria: Relevance scoring criteria
    """
    logger.info("Initializing scraping job")

    try:
        # Initialize orchestrator
        orchestrator = Orchestrator(
            use_ai_parsing=True,
            use_vector_storage=True,
            use_database_storage=True
        )

        # Run pipeline
        result = orchestrator.run_pipeline(
            city=city,
            category=category,
            keywords=keywords,
            max_pages=max_pages,
            criteria=criteria
        )

        if result['success']:
            print("\n" + "=" * 60)
            print("SCRAPING COMPLETED SUCCESSFULLY")
            print("=" * 60)
            print(f"\nStatistics:")
            for key, value in result['stats'].items():
                print(f"  {key}: {value}")

            # Show top jobs if relevance scores available
            if 'jobs' in result and criteria:
                jobs = result['jobs']
                jobs_sorted = sorted(
                    jobs,
                    key=lambda x: x.relevance_score or 0,
                    reverse=True
                )[:10]

                print("\n" + "=" * 60)
                print("TOP 10 RELEVANT JOBS")
                print("=" * 60)

                for i, job in enumerate(jobs_sorted, 1):
                    print(f"\n{i}. {job.title}")
                    print(f"   URL: {job.url}")
                    print(f"   Location: {job.location}")
                    print(f"   Remote: {job.is_remote}")
                    if job.relevance_score:
                        print(f"   Relevance: {job.relevance_score:.2f}")
                    if job.skills:
                        print(f"   Skills: {', '.join(job.skills[:5])}")

        else:
            print(f"\nScraping failed: {result.get('error')}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Scraping failed: {e}", exc_info=True)
        print(f"\nError: {e}")
        sys.exit(1)


def search_jobs(query: str, limit: int = 20):
    """Search for jobs using semantic search."""
    logger.info(f"Searching for: {query}")

    try:
        orchestrator = Orchestrator()

        results = orchestrator.search_jobs(
            query=query,
            top_k=limit,
            use_semantic_search=True
        )

        print("\n" + "=" * 60)
        print(f"SEARCH RESULTS FOR: {query}")
        print("=" * 60)

        if not results:
            print("\nNo results found.")
            return

        for i, result in enumerate(results, 1):
            metadata = result.get('metadata', {})
            score = result.get('score', 0)

            print(f"\n{i}. {metadata.get('title', 'Unknown')}")
            print(f"   Match Score: {score:.2f}")
            print(f"   Location: {metadata.get('location', 'N/A')}")
            print(f"   Remote: {metadata.get('is_remote', False)}")

            if metadata.get('skills'):
                skills = metadata['skills'][:5]
                print(f"   Skills: {', '.join(skills)}")

    except Exception as e:
        logger.error(f"Search failed: {e}", exc_info=True)
        print(f"\nError: {e}")
        sys.exit(1)


def analyze_market(city: str = "sfbay", category: str = "sof"):
    """Analyze the job market."""
    logger.info(f"Analyzing market for {city}/{category}")

    try:
        orchestrator = Orchestrator()

        analysis = orchestrator.analyze_job_market(city, category)

        print("\n" + "=" * 60)
        print(f"JOB MARKET ANALYSIS: {city.upper()}/{category.upper()}")
        print("=" * 60)

        if 'error' in analysis:
            print(f"\nError: {analysis['error']}")
            return

        print(f"\nTotal Jobs: {analysis.get('total_jobs', 0)}")
        print(f"Remote Jobs: {analysis.get('remote_jobs', 0)}")
        print(f"Hybrid Jobs: {analysis.get('hybrid_jobs', 0)}")
        print(f"Onsite Jobs: {analysis.get('onsite_jobs', 0)}")

        if 'avg_salary' in analysis:
            print(f"\nAverage Salary: ${analysis['avg_salary']:,.0f}")
            print(f"Salary Range: ${analysis['min_salary']:,.0f} - ${analysis['max_salary']:,.0f}")

        if 'top_skills' in analysis:
            print("\nTop 10 In-Demand Skills:")
            for skill, count in analysis['top_skills'][:10]:
                print(f"  {skill}: {count}")

        if 'common_pain_points' in analysis:
            print("\nCommon Pain Points:")
            for pain, count in analysis['common_pain_points'][:5]:
                print(f"  - {pain}")

    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        print(f"\nError: {e}")
        sys.exit(1)


def schedule_scrape(
    city: str = "sfbay",
    category: str = "sof",
    hour: int = 9,
    minute: int = 0
):
    """Schedule a daily scraping job."""
    logger.info(f"Setting up scheduled scrape for {city}/{category}")

    try:
        orchestrator = Orchestrator()

        orchestrator.schedule_daily_scrape(
            city=city,
            category=category,
            hour=hour,
            minute=minute
        )

        orchestrator.start_scheduler()

        print("\n" + "=" * 60)
        print("SCHEDULER STARTED")
        print("=" * 60)
        print(f"\nDaily scrape scheduled for {hour:02d}:{minute:02d}")
        print(f"City: {city}")
        print(f"Category: {category}")
        print("\nPress Ctrl+C to stop the scheduler")

        # Keep running
        import time
        while True:
            time.sleep(60)

    except KeyboardInterrupt:
        print("\n\nStopping scheduler...")
        orchestrator.stop_scheduler()
        print("Scheduler stopped.")

    except Exception as e:
        logger.error(f"Scheduler failed: {e}", exc_info=True)
        print(f"\nError: {e}")
        sys.exit(1)


def export_jobs(output_file: str):
    """Export jobs to CSV."""
    logger.info(f"Exporting jobs to {output_file}")

    try:
        orchestrator = Orchestrator()

        success = orchestrator.export_jobs_to_csv(output_file)

        if success:
            print(f"\nJobs exported successfully to {output_file}")
        else:
            print("\nExport failed")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Export failed: {e}", exc_info=True)
        print(f"\nError: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Craigslist Job Scraper and Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape software jobs in San Francisco Bay Area
  python main.py scrape --city sfbay --category sof --pages 5

  # Scrape with keywords
  python main.py scrape --city sfbay --category sof --keywords python django --pages 3

  # Search for jobs
  python main.py search "python developer with django experience"

  # Analyze job market
  python main.py analyze --city sfbay --category sof

  # Schedule daily scraping at 9 AM
  python main.py schedule --city sfbay --category sof --hour 9

  # Export jobs to CSV
  python main.py export --output jobs.csv
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Scrape job postings')
    scrape_parser.add_argument('--city', default='sfbay', help='Craigslist city code')
    scrape_parser.add_argument('--category', default='sof', help='Job category code')
    scrape_parser.add_argument('--keywords', nargs='+', help='Search keywords')
    scrape_parser.add_argument('--pages', type=int, default=3, help='Max pages to scrape')
    scrape_parser.add_argument('--criteria', help='JSON criteria for relevance scoring')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search for jobs')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--limit', type=int, default=20, help='Number of results')

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze job market')
    analyze_parser.add_argument('--city', default='sfbay', help='City to analyze')
    analyze_parser.add_argument('--category', default='sof', help='Category to analyze')

    # Schedule command
    schedule_parser = subparsers.add_parser('schedule', help='Schedule daily scraping')
    schedule_parser.add_argument('--city', default='sfbay', help='City to scrape')
    schedule_parser.add_argument('--category', default='sof', help='Category to scrape')
    schedule_parser.add_argument('--hour', type=int, default=9, help='Hour to run (0-23)')
    schedule_parser.add_argument('--minute', type=int, default=0, help='Minute to run (0-59)')

    # Export command
    export_parser = subparsers.add_parser('export', help='Export jobs to CSV')
    export_parser.add_argument('--output', default='jobs.csv', help='Output CSV file')

    args = parser.parse_args()

    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        print(f"\nConfiguration Error: {e}")
        print("\nPlease ensure all required environment variables are set in .env")
        sys.exit(1)

    # Execute command
    if args.command == 'scrape':
        criteria = None
        if args.criteria:
            try:
                criteria = json.loads(args.criteria)
            except json.JSONDecodeError:
                print("Invalid JSON for criteria")
                sys.exit(1)

        run_scrape(
            city=args.city,
            category=args.category,
            keywords=args.keywords,
            max_pages=args.pages,
            criteria=criteria
        )

    elif args.command == 'search':
        search_jobs(args.query, args.limit)

    elif args.command == 'analyze':
        analyze_market(args.city, args.category)

    elif args.command == 'schedule':
        schedule_scrape(args.city, args.category, args.hour, args.minute)

    elif args.command == 'export':
        export_jobs(args.output)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
