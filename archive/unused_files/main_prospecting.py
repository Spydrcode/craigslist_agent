"""
Main entry point for intelligent company prospecting system.
Finds companies in growth/hiring stages and identifies service opportunities.
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List

from config_enhanced import EnhancedConfig
from orchestrator_enhanced import IntelligentProspectingOrchestrator
from utils import setup_logger

# Set up logger
logger = setup_logger(__name__, log_file='logs/prospecting.log')


def run_prospecting(
    city: str = "sfbay",
    category: str = "sof",
    keywords: Optional[List[str]] = None,
    max_pages: int = 5,
    min_growth_score: float = 0.3,
    min_lead_score: float = 40.0,
    export: bool = True
):
    """
    Run the intelligent prospecting workflow.

    Args:
        city: Craigslist city code
        category: Job category code
        keywords: Search keywords
        max_pages: Maximum pages to scrape
        min_growth_score: Minimum growth score (0-1)
        min_lead_score: Minimum lead score (0-100)
        export: Export results to CSV
    """
    print("\n" + "=" * 80)
    print("INTELLIGENT COMPANY PROSPECTING SYSTEM")
    print("=" * 80)
    print(f"\nTarget: {city}/{category}")
    print(f"Keywords: {keywords or 'None'}")
    print(f"Filters: Growth >= {min_growth_score}, Lead Score >= {min_lead_score}")
    print("\n" + "=" * 80 + "\n")

    try:
        # Initialize orchestrator
        orchestrator = IntelligentProspectingOrchestrator(
            use_ai_parsing=True,
            use_company_research=EnhancedConfig.ENABLE_WEB_RESEARCH,
            use_ml_scoring=True,
            save_to_database=True
        )

        # Run prospecting workflow
        result = orchestrator.find_prospects(
            city=city,
            category=category,
            keywords=keywords,
            max_pages=max_pages,
            min_growth_score=min_growth_score,
            min_lead_score=min_lead_score
        )

        if not result['success']:
            print(f"\n❌ Prospecting failed: {result.get('error')}")
            sys.exit(1)

        # Display results
        prospects = result.get('prospects', [])
        stats = result['stats']

        print("\n" + "=" * 80)
        print("PROSPECTING RESULTS")
        print("=" * 80)
        print(f"\n📊 Statistics:")
        print(f"   Jobs Scraped: {stats['jobs_scraped']}")
        print(f"   Companies Identified: {stats['companies_identified']}")
        print(f"   Companies Researched: {stats['companies_researched']}")
        print(f"   Qualified Prospects: {stats['qualified_prospects']}")
        print(f"   High Priority: {stats['high_priority_prospects']}")
        print(f"   Total Opportunities: {stats['total_opportunities']}")
        print(f"   Duration: {stats.get('duration_seconds', 0):.1f}s")

        if prospects:
            print("\n" + "=" * 80)
            print("TOP PROSPECTS")
            print("=" * 80)

            for i, prospect in enumerate(prospects[:10], 1):
                print(f"\n{i}. {prospect.company_profile.name}")
                print(f"   Score: {prospect.lead_score:.1f}/100 | Priority: {prospect.priority_tier}")
                print(f"   Location: {prospect.company_profile.location or 'Unknown'}")
                print(f"   Jobs: {len(prospect.job_postings)}")

                if prospect.company_profile.growth_signals:
                    gs = prospect.company_profile.growth_signals
                    print(f"   Growth: {gs.growth_stage.value} (score: {gs.growth_score:.2f})")
                    print(f"   Urgency: {gs.hiring_urgency.value}")

                if prospect.service_opportunities:
                    top_opp = prospect.service_opportunities[0]
                    print(f"   Top Opportunity: {top_opp.service_type}")
                    print(f"   Confidence: {top_opp.confidence_score:.0%}")
                    print(f"   Value: {top_opp.estimated_value}")

                if prospect.recommended_approach:
                    print(f"   Approach: {prospect.recommended_approach[:100]}...")

            # Export results
            if export:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_dir = Path(EnhancedConfig.OUTPUT_DIR)
                output_dir.mkdir(parents=True, exist_ok=True)

                # Export to CSV
                csv_file = output_dir / f"prospects_{timestamp}.csv"
                orchestrator.export_prospects_to_csv(prospects, str(csv_file))
                print(f"\n✅ Exported to: {csv_file}")

                # Export detailed JSON
                json_file = output_dir / f"prospects_{timestamp}.json"
                with open(json_file, 'w') as f:
                    json.dump(
                        [p.dict() for p in prospects],
                        f,
                        indent=2,
                        default=str
                    )
                print(f"✅ Detailed data: {json_file}")

        else:
            print("\n⚠️  No qualified prospects found.")
            print("Try:")
            print("  - Lowering the minimum scores")
            print("  - Expanding the search area")
            print("  - Using different keywords")

        print("\n" + "=" * 80 + "\n")

    except Exception as e:
        logger.error(f"Prospecting failed: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        sys.exit(1)


def analyze_prospect(prospect_file: str):
    """
    Analyze a specific prospect from saved JSON.

    Args:
        prospect_file: Path to prospect JSON file
    """
    try:
        with open(prospect_file, 'r') as f:
            data = json.load(f)

        # If it's a list, take the first
        if isinstance(data, list):
            data = data[0]

        print("\n" + "=" * 80)
        print("PROSPECT ANALYSIS")
        print("=" * 80)

        # Company info
        company = data.get('company_profile', {})
        print(f"\n🏢 Company: {company.get('name', 'Unknown')}")
        print(f"   Industry: {company.get('industry', 'Unknown')}")
        print(f"   Size: {company.get('size_range', 'Unknown')}")
        print(f"   Location: {company.get('location', 'Unknown')}")

        # Growth signals
        if 'growth_signals' in company:
            gs = company['growth_signals']
            print(f"\n📈 Growth Signals:")
            print(f"   Stage: {gs.get('growth_stage', 'unknown')}")
            print(f"   Score: {gs.get('growth_score', 0):.2f}")
            print(f"   Hiring Multiple: {gs.get('is_hiring_multiple', False)}")
            print(f"   Multiple Departments: {gs.get('multiple_departments', False)}")
            print(f"   Leadership Positions: {gs.get('leadership_positions', False)}")

        # Opportunities
        opportunities = data.get('service_opportunities', [])
        if opportunities:
            print(f"\n💼 Service Opportunities ({len(opportunities)}):")
            for opp in opportunities:
                print(f"\n   - {opp['service_type']}")
                print(f"     Confidence: {opp['confidence_score']:.0%}")
                print(f"     Value: {opp.get('estimated_value', 'N/A')}")
                print(f"     Reasoning: {opp.get('reasoning', 'N/A')}")

        # Outreach plan
        print(f"\n📞 Outreach Plan:")
        print(f"   Target: {data.get('decision_maker_target', 'TBD')}")
        print(f"   Approach: {data.get('recommended_approach', 'TBD')}")

        talking_points = data.get('key_talking_points', [])
        if talking_points:
            print(f"\n   Talking Points:")
            for point in talking_points:
                print(f"   - {point}")

        print("\n" + "=" * 80 + "\n")

    except Exception as e:
        print(f"Error analyzing prospect: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Intelligent Company Prospecting System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Find prospects in SF Bay Area tech jobs
  python main_prospecting.py prospect --city sfbay --category sof --pages 5

  # Focus on AI/ML companies
  python main_prospecting.py prospect --city sfbay --category sof --keywords "machine learning" "AI" --pages 3

  # Adjust qualification thresholds
  python main_prospecting.py prospect --city seattle --category sof --min-growth 0.4 --min-score 60

  # Analyze a saved prospect
  python main_prospecting.py analyze --file output/prospects/prospects_20240115_143022.json

City Codes:
  sfbay - San Francisco Bay Area
  seattle - Seattle
  newyork - New York
  losangeles - Los Angeles
  boston - Boston
  austin - Austin
  chicago - Chicago

Category Codes:
  sof - Software/Tech
  eng - Engineering
  sls - Sales
  sad - Systems/Networking
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Prospect command
    prospect_parser = subparsers.add_parser('prospect', help='Find and qualify prospects')
    prospect_parser.add_argument('--city', default='sfbay', help='Craigslist city code')
    prospect_parser.add_argument('--category', default='sof', help='Job category code')
    prospect_parser.add_argument('--keywords', nargs='+', help='Search keywords')
    prospect_parser.add_argument('--pages', type=int, default=5, help='Max pages to scrape')
    prospect_parser.add_argument('--min-growth', type=float, default=0.3, help='Min growth score (0-1)')
    prospect_parser.add_argument('--min-score', type=float, default=40.0, help='Min lead score (0-100)')
    prospect_parser.add_argument('--no-export', action='store_true', help='Skip exporting results')

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a saved prospect')
    analyze_parser.add_argument('--file', required=True, help='Prospect JSON file')

    args = parser.parse_args()

    # Validate configuration
    try:
        EnhancedConfig.validate()
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nPlease ensure all required environment variables are set in .env")
        print("See .env.example for reference")
        sys.exit(1)

    # Execute command
    if args.command == 'prospect':
        run_prospecting(
            city=args.city,
            category=args.category,
            keywords=args.keywords,
            max_pages=args.pages,
            min_growth_score=args.min_growth,
            min_lead_score=args.min_score,
            export=not args.no_export
        )

    elif args.command == 'analyze':
        analyze_prospect(args.file)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
