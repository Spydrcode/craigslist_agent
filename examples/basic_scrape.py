"""
Example: Basic job scraping workflow.
Demonstrates scraping jobs from Craigslist without AI features.
"""
import sys
sys.path.append('..')

from agents import ScraperAgent
from models import ScraperConfig
from utils import setup_logger

# Setup logging
logger = setup_logger(__name__)


def main():
    """Run a basic scrape."""
    logger.info("Starting basic scrape example")

    # Configure scraper
    config = ScraperConfig(
        city="sfbay",  # San Francisco Bay Area
        category="sof",  # Software jobs
        keywords=["python", "django"],
        max_pages=2,
        delay_min=2,
        delay_max=4
    )

    # Initialize scraper
    scraper = ScraperAgent(config)

    # Test connection
    if not scraper.test_connection():
        logger.error("Connection test failed")
        return

    # Scrape listings
    logger.info("Scraping job listings...")
    jobs = scraper.scrape_listings()

    logger.info(f"Scraped {len(jobs)} jobs")

    # Display results
    print("\n" + "=" * 80)
    print("SCRAPED JOBS")
    print("=" * 80)

    for i, job in enumerate(jobs[:5], 1):  # Show first 5
        print(f"\n{i}. {job.title}")
        print(f"   URL: {job.url}")
        print(f"   Location: {job.location}")
        print(f"   Posted: {job.posted_date}")
        print(f"   Description: {job.description[:200]}...")

    print(f"\n\nTotal jobs scraped: {len(jobs)}")


if __name__ == "__main__":
    main()
