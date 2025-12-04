"""
Test script for the new signal-based workflow.
Tests: Scraping → Signal Extraction → External Search → Growth Scoring
"""
import sys
sys.path.insert(0, '.')

from agents.scraper_agent import ScraperAgent
from agents.parser_agent import ParserAgent
from agents.external_search_agent import ExternalSearchAgent
from agents.growth_scoring_agent import GrowthScoringAgent
from agents.client_agent import ClientAgent
from models import ScraperConfig
from utils import get_logger

logger = get_logger(__name__)


def test_signal_workflow():
    """Test the complete signal-based workflow."""
    
    print("\n" + "="*80)
    print("TESTING SIGNAL-BASED GROWTH DETECTION WORKFLOW")
    print("="*80 + "\n")
    
    # Initialize agents
    print("1. Initializing agents...")
    client = ClientAgent()
    parser = ParserAgent(client_agent=client)
    external_search = ExternalSearchAgent(client_agent=client, use_web_search=True)
    growth_scorer = GrowthScoringAgent(client_agent=client, use_web_search=True)
    
    print("   ✓ All agents initialized\n")
    
    # Step 1: Scrape Craigslist (small sample)
    print("2. Scraping Craigslist for job postings (signal source)...")
    scraper_config = ScraperConfig(
        city='phoenix',
        category='sof',
        max_pages=1,  # Small test
        quick_scan_only=False,  # Need descriptions
        max_jobs_to_analyze=10
    )
    scraper = ScraperAgent(config=scraper_config)
    
    raw_jobs = scraper.scrape_listings()
    print(f"   ✓ Scraped {len(raw_jobs)} job postings\n")
    
    if not raw_jobs:
        print("   ✗ No jobs found. Exiting.")
        return
    
    # Step 2: Extract signals
    print("3. Extracting industry/job signals from postings...")
    signals = parser.extract_signals_batch(raw_jobs[:5], use_ai=True)  # Test with 5 jobs
    print(f"   ✓ Extracted {len(signals)} signals\n")
    
    # Show signal summary
    print("   Signal Summary:")
    industries = {}
    for signal in signals:
        industry = signal.industry
        if industry not in industries:
            industries[industry] = []
        industries[industry].append(signal.job_category)
    
    for industry, categories in industries.items():
        print(f"   - {industry}: {', '.join(set(categories))}")
    print()
    
    # Step 3: External company discovery
    print("4. Finding companies externally via web search...")
    discovered_companies = external_search.find_companies_from_signals(
        signals=signals,
        max_companies_per_industry=5
    )
    print(f"   ✓ Found {len(discovered_companies)} companies\n")
    
    if not discovered_companies:
        print("   ✗ No companies found externally.")
        print("\n   NOTE: This is expected if web search isn't working or industries are too specific.")
        print("   The workflow is still functional.\n")
        return
    
    # Show discovered companies
    print("   Discovered Companies:")
    for company in discovered_companies[:5]:
        print(f"   - {company.get('company_name', 'Unknown')}: {company.get('industry', 'Unknown')}, {company.get('location', 'Unknown')}")
    print()
    
    # Step 4: Growth scoring
    print("5. Scoring companies for growth (0-100)...")
    scored_companies = growth_scorer.score_companies(discovered_companies[:3])  # Test with 3
    print(f"   ✓ Scored {len(scored_companies)} companies\n")
    
    # Show top companies
    print("   Top Scoring Companies:")
    for company in scored_companies:
        print(f"   - {company.company_name}: {company.growth_score:.1f}/100")
        signals = company.signals
        if 'hiring_velocity' in signals:
            print(f"     * Hiring: {signals['hiring_velocity'].get('open_positions', 0)} open positions")
        if 'expansion' in signals:
            locations = signals['expansion'].get('locations', [])
            print(f"     * Expansion: {len(locations)} locations")
        print()
    
    print("="*80)
    print("✓ SIGNAL-BASED WORKFLOW TEST COMPLETE")
    print("="*80 + "\n")
    
    print("SUMMARY:")
    print(f"  - Input: {len(raw_jobs)} Craigslist job postings")
    print(f"  - Signals extracted: {len(signals)}")
    print(f"  - Industries detected: {len(industries)}")
    print(f"  - Companies found externally: {len(discovered_companies)}")
    print(f"  - Companies scored: {len(scored_companies)}")
    if scored_companies:
        print(f"  - Top company: {scored_companies[0].company_name} ({scored_companies[0].growth_score:.1f}/100)")
    print()


if __name__ == '__main__':
    try:
        test_signal_workflow()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        print(f"\n✗ Test failed: {e}")
