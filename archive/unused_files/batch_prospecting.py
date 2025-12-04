"""
Batch Prospecting Script
Run prospecting across multiple cities and job categories.
"""
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from orchestrator_simple import SimpleProspectingOrchestrator
from utils import get_logger

logger = get_logger(__name__)

# Common Craigslist Cities
CITIES = {
    'sfbay': 'San Francisco Bay Area',
    'newyork': 'New York',
    'losangeles': 'Los Angeles',
    'chicago': 'Chicago',
    'seattle': 'Seattle',
    'boston': 'Boston',
    'austin': 'Austin',
    'denver': 'Denver',
    'atlanta': 'Atlanta',
    'dallas': 'Dallas',
    'houston': 'Houston',
    'miami': 'Miami',
    'phoenix': 'Phoenix',
    'sandiego': 'San Diego',
    'portland': 'Portland',
    'philadelphia': 'Philadelphia',
    'washingtondc': 'Washington DC',
    'raleigh': 'Raleigh',
    'minneapolis': 'Minneapolis',
    'detroit': 'Detroit'
}

# Common Job Categories
CATEGORIES = {
    'sof': 'Software/QA/DBA',
    'eng': 'Engineering',
    'web': 'Web/HTML/Info Design',
    'sad': 'Systems/Networking',
    'sls': 'Sales/Business Development',
    'mar': 'Marketing/PR/Advertising',
    'bus': 'Business/Management',
    'acc': 'Accounting/Finance',
    'sci': 'Science/Biotech',
    'edu': 'Education/Teaching'
}


class BatchProspector:
    """Run prospecting across multiple cities and categories."""

    def __init__(self):
        """Initialize batch prospector."""
        self.orchestrator = SimpleProspectingOrchestrator()
        self.results_dir = Path("output/batch_results")
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def run_batch(
        self,
        cities: List[str],
        categories: List[str],
        keywords: List[str] = None,
        max_pages: int = 2,
        min_growth_score: float = 0.3,
        min_lead_score: float = 50.0
    ) -> Dict:
        """
        Run prospecting for multiple cities and categories.

        Args:
            cities: List of city codes (e.g., ['sfbay', 'newyork'])
            categories: List of category codes (e.g., ['sof', 'eng'])
            keywords: Optional keywords to filter
            max_pages: Pages to scrape per city/category
            min_growth_score: Minimum growth score filter
            min_lead_score: Minimum lead score filter

        Returns:
            Summary of all results
        """
        print("="*80)
        print("BATCH PROSPECTING")
        print("="*80)
        print(f"\nCities: {', '.join([CITIES.get(c, c) for c in cities])}")
        print(f"Categories: {', '.join([CATEGORIES.get(c, c) for c in categories])}")
        if keywords:
            print(f"Keywords: {', '.join(keywords)}")
        print(f"Pages per search: {max_pages}")
        print(f"Filters: growth >= {min_growth_score}, score >= {min_lead_score}")
        print()

        all_prospects = []
        batch_stats = {
            'start_time': datetime.utcnow().isoformat(),
            'cities': cities,
            'categories': categories,
            'total_searches': len(cities) * len(categories),
            'completed_searches': 0,
            'total_jobs': 0,
            'total_prospects': 0,
            'searches': []
        }

        search_num = 0
        total_searches = len(cities) * len(categories)

        for city in cities:
            for category in categories:
                search_num += 1

                print(f"[{search_num}/{total_searches}] Searching {CITIES.get(city, city)} - {CATEGORIES.get(category, category)}...")

                try:
                    result = self.orchestrator.find_prospects(
                        city=city,
                        category=category,
                        keywords=keywords,
                        max_pages=max_pages,
                        min_growth_score=min_growth_score,
                        min_lead_score=min_lead_score
                    )

                    if result['success']:
                        prospects = result['prospects']

                        # Tag each prospect with source
                        for prospect in prospects:
                            prospect_dict = prospect.dict()
                            prospect_dict['source_city'] = city
                            prospect_dict['source_category'] = category
                            all_prospects.append(prospect_dict)

                        search_result = {
                            'city': city,
                            'category': category,
                            'jobs_scraped': result['stats']['jobs_scraped'],
                            'prospects_found': len(prospects),
                            'success': True
                        }

                        batch_stats['total_jobs'] += result['stats']['jobs_scraped']
                        batch_stats['total_prospects'] += len(prospects)
                        batch_stats['completed_searches'] += 1

                        print(f"  Found {len(prospects)} prospects from {result['stats']['jobs_scraped']} jobs")

                    else:
                        search_result = {
                            'city': city,
                            'category': category,
                            'error': result.get('error', 'Unknown error'),
                            'success': False
                        }
                        print(f"  ERROR: {result.get('error')}")

                    batch_stats['searches'].append(search_result)

                except Exception as e:
                    logger.error(f"Search failed for {city}/{category}: {e}", exc_info=True)
                    search_result = {
                        'city': city,
                        'category': category,
                        'error': str(e),
                        'success': False
                    }
                    batch_stats['searches'].append(search_result)
                    print(f"  ERROR: {e}")

                print()

        # Save results
        batch_stats['end_time'] = datetime.utcnow().isoformat()
        batch_stats['total_unique_prospects'] = len(all_prospects)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Save all prospects
        prospects_file = self.results_dir / f"batch_prospects_{timestamp}.json"
        with open(prospects_file, 'w') as f:
            json.dump(all_prospects, f, indent=2, default=str)

        # Save batch stats
        stats_file = self.results_dir / f"batch_stats_{timestamp}.json"
        with open(stats_file, 'w') as f:
            json.dump(batch_stats, f, indent=2, default=str)

        # Print summary
        print("="*80)
        print("BATCH COMPLETE")
        print("="*80)
        print(f"\nTotal Searches: {batch_stats['completed_searches']}/{batch_stats['total_searches']}")
        print(f"Total Jobs Scraped: {batch_stats['total_jobs']}")
        print(f"Total Prospects Found: {batch_stats['total_prospects']}")
        print(f"\nResults saved to:")
        print(f"  - {prospects_file}")
        print(f"  - {stats_file}")
        print()

        return {
            'success': True,
            'prospects': all_prospects,
            'stats': batch_stats,
            'files': {
                'prospects': str(prospects_file),
                'stats': str(stats_file)
            }
        }


def main():
    """Interactive batch prospecting."""
    print("\n" + "="*80)
    print("BATCH PROSPECTING TOOL")
    print("="*80)

    # Show available cities
    print("\nAvailable Cities:")
    for i, (code, name) in enumerate(list(CITIES.items())[:10], 1):
        print(f"  {code:<15} - {name}")
    print(f"  ... and {len(CITIES) - 10} more")

    # Show available categories
    print("\nAvailable Categories:")
    for code, name in CATEGORIES.items():
        print(f"  {code:<10} - {name}")

    print("\n" + "-"*80)
    print("\nQuick Examples:")
    print("  1. Tech hubs: sfbay,seattle,newyork")
    print("  2. All tech cities: sfbay,seattle,austin,boston,newyork")
    print("  3. Major markets: newyork,losangeles,chicago")
    print()

    # Get user input
    cities_input = input("Enter city codes (comma-separated, or 'all' for all): ").strip()
    if cities_input.lower() == 'all':
        selected_cities = list(CITIES.keys())
    else:
        selected_cities = [c.strip() for c in cities_input.split(',')]

    categories_input = input("Enter category codes (comma-separated, or 'sof' for software): ").strip()
    if not categories_input:
        selected_categories = ['sof']
    elif categories_input.lower() == 'all':
        selected_categories = list(CATEGORIES.keys())
    else:
        selected_categories = [c.strip() for c in categories_input.split(',')]

    keywords_input = input("Enter keywords (comma-separated, optional): ").strip()
    keywords = [k.strip() for k in keywords_input.split(',')] if keywords_input else None

    pages_input = input("Pages per search (default: 2): ").strip()
    max_pages = int(pages_input) if pages_input else 2

    # Confirm
    print("\n" + "="*80)
    print("CONFIRMATION")
    print("="*80)
    print(f"Cities: {len(selected_cities)} ({', '.join(selected_cities[:5])}{', ...' if len(selected_cities) > 5 else ''})")
    print(f"Categories: {len(selected_categories)} ({', '.join(selected_categories)})")
    print(f"Keywords: {keywords if keywords else 'None'}")
    print(f"Pages per search: {max_pages}")
    print(f"Total searches: {len(selected_cities) * len(selected_categories)}")
    print(f"Estimated time: {len(selected_cities) * len(selected_categories) * 2} minutes")
    print()

    confirm = input("Proceed? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return

    # Run batch
    prospector = BatchProspector()
    result = prospector.run_batch(
        cities=selected_cities,
        categories=selected_categories,
        keywords=keywords,
        max_pages=max_pages
    )

    if result['success']:
        print("\nBatch prospecting complete!")
        print(f"Found {len(result['prospects'])} total prospects")
        print("\nRun the dashboard to view and manage your prospects:")
        print("  python dashboard_app.py")


if __name__ == "__main__":
    main()
