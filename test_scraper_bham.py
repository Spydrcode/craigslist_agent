"""Quick test to see if bham scraping works"""
from agents.scraper_agent import ScraperAgent
from models import ScraperConfig
from utils import get_logger

logger = get_logger(__name__)

# Test scraping bham with limited jobs
config = ScraperConfig(
    city='bham',
    category='jjj',  # all jobs
    max_pages=1,
    max_jobs=5  # Only fetch 5 jobs
)

scraper = ScraperAgent(config=config)

print("Starting scrape test...")
try:
    jobs = scraper.scrape_listings()
    print(f"\nSuccess! Scraped {len(jobs)} jobs")
    for job in jobs[:3]:
        print(f"  - {job.title}")
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
