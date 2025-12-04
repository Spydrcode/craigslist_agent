"""
Example: AI-powered job parsing.
Demonstrates using the Parser Agent with GPT to extract insights.
"""
import sys
sys.path.append('..')

from agents import ScraperAgent, ParserAgent, ClientAgent
from models import ScraperConfig
from utils import setup_logger

# Setup logging
logger = setup_logger(__name__)


def main():
    """Run AI parsing example."""
    logger.info("Starting AI parsing example")

    # Configure scraper
    config = ScraperConfig(
        city="sfbay",
        category="sof",
        keywords=["machine learning"],
        max_pages=1,
    )

    # Initialize agents
    scraper = ScraperAgent(config)
    client = ClientAgent()
    parser = ParserAgent(client)

    # Scrape a few jobs
    logger.info("Scraping jobs...")
    raw_jobs = scraper.scrape_listings()

    if not raw_jobs:
        logger.error("No jobs found")
        return

    logger.info(f"Found {len(raw_jobs)} jobs")

    # Parse with AI
    logger.info("Parsing jobs with AI...")
    parsed_jobs = parser.parse_jobs(raw_jobs[:3], use_ai=True)  # Parse first 3

    # Display results
    print("\n" + "=" * 80)
    print("AI-PARSED JOBS WITH INSIGHTS")
    print("=" * 80)

    for i, job in enumerate(parsed_jobs, 1):
        print(f"\n{'=' * 80}")
        print(f"JOB {i}: {job.title}")
        print(f"{'=' * 80}")
        print(f"URL: {job.url}")
        print(f"Location: {job.location}")
        print(f"Remote: {job.is_remote} | Hybrid: {job.is_hybrid}")

        if job.salary_min and job.salary_max:
            print(f"Salary: ${job.salary_min:,.0f} - ${job.salary_max:,.0f}")

        print(f"\nSkills ({len(job.skills)}):")
        for skill in job.skills[:10]:
            print(f"  - {skill}")

        print(f"\nPain Points ({len(job.pain_points)}):")
        for pain in job.pain_points:
            print(f"  - {pain}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
