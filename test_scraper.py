"""Quick test of scraper agent"""
from agents.scraper_agent import ScraperAgent
from models import ScraperConfig

# Test scraping Phoenix software jobs
config = ScraperConfig(
    city='phoenix',
    category='sof',
    max_pages=1,
    quick_scan_only=True  # Don't fetch full details for testing
)

scraper = ScraperAgent(config)
jobs = scraper.scrape_listings()

print(f"\n===SCRAPER TEST RESULTS===")
print(f"Found {len(jobs)} jobs")
for job in jobs:
    print(f"  - {job.title} ({job.location})")
    print(f"    URL: {job.url}")
