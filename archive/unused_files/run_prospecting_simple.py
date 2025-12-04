"""
Simple prospecting runner - no database required.
Finds companies that need your services and saves results to files.
"""
import sys
from orchestrator_simple import SimpleProspectingOrchestrator

print("\n" + "="*60)
print("INTELLIGENT COMPANY PROSPECTING")
print("="*60)
print("\nSearching for companies in growth/hiring stages...")
print("This will take 3-5 minutes.\n")

# Create orchestrator
orchestrator = SimpleProspectingOrchestrator(
    use_ai_parsing=True,
    use_company_research=False,  # Disable for faster testing
    output_dir="output/prospects"
)

# Run prospecting
result = orchestrator.find_prospects(
    city="sfbay",
    category="sof",
    keywords=None,
    max_pages=2,  # Start small for testing
    min_growth_score=0.3,
    min_lead_score=40.0
)

if not result['success']:
    print(f"\nERROR: {result.get('error')}")
    sys.exit(1)

# Display results
prospects = result.get('prospects', [])
stats = result['stats']

print("\n" + "="*60)
print("RESULTS")
print("="*60)

print(f"\nStatistics:")
print(f"  Jobs Scraped: {stats['jobs_scraped']}")
print(f"  Companies Identified: {stats['companies_identified']}")
print(f"  Qualified Prospects: {stats['qualified_prospects']}")
print(f"  High Priority: {stats['high_priority_prospects']}")
print(f"  Opportunities Found: {stats['total_opportunities']}")
print(f"  Duration: {stats.get('duration_seconds', 0):.1f}s")

if prospects:
    print(f"\n{'='*60}")
    print("TOP PROSPECTS")
    print("="*60)

    for i, prospect in enumerate(prospects[:5], 1):
        print(f"\n{i}. {prospect.company_profile.name}")
        print(f"   Score: {prospect.lead_score:.1f}/100")
        print(f"   Priority: {prospect.priority_tier}")
        print(f"   Jobs: {len(prospect.job_postings)}")

        if prospect.company_profile.growth_signals:
            gs = prospect.company_profile.growth_signals
            print(f"   Growth: {gs.growth_stage.value} (score: {gs.growth_score:.2f})")

        if prospect.service_opportunities:
            top_opp = prospect.service_opportunities[0]
            print(f"   Opportunity: {top_opp.service_type}")
            print(f"   Value: {top_opp.estimated_value}")

    print(f"\n{'='*60}")
    print("\nResults saved to:")
    print("  - output/prospects/prospects_TIMESTAMP.json")
    print("  - output/prospects/prospects_TIMESTAMP.csv")
else:
    print("\nNo qualified prospects found.")
    print("Try lowering --min-growth or --min-score")

print("\n" + "="*60 + "\n")
