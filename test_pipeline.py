"""Test the full orchestrator pipeline"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from orchestrator_simple import SimpleProspectingOrchestrator

# Initialize orchestrator
orchestrator = SimpleProspectingOrchestrator(
    use_ai_parsing=True,
    use_company_research=True,
    output_dir="output/test_prospects"
)

# Run pipeline
print("\n" + "="*80)
print("TESTING FULL PIPELINE")
print("="*80)

result = orchestrator.find_prospects(
    city='phoenix',
    category='sof',
    max_pages=1,
    min_growth_score=0.3,
    min_lead_score=30.0  # Lower threshold for testing
)

print("\n" + "="*80)
print("PIPELINE RESULTS")
print("="*80)
print(f"Success: {result['success']}")
print(f"Stats: {result.get('stats', {})}")

if result.get('prospects'):
    print(f"\nFound {len(result['prospects'])} prospects:")
    for p in result['prospects']:
        print(f"\n  Company: {p.company_profile.name}")
        print(f"  Lead Score: {p.lead_score}")
        print(f"  Growth Score: {p.company_profile.growth_signals.growth_score if p.company_profile.growth_signals else 'N/A'}")
        print(f"  Job Count: {len(p.job_postings)}")
        print(f"  Opportunities: {len(p.service_opportunities) if p.service_opportunities else 0}")
        if p.service_opportunities:
            for opp in p.service_opportunities[:2]:
                print(f"    - {opp.service_type}: {opp.pain_point}")
else:
    print(f"\n❌ ERROR: {result.get('error')}")
