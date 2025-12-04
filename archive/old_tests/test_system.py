"""Test script for the multi-agent lead qualification system."""

from agents.orchestrator import Orchestrator


def create_sample_posting():
    """Create a sample job posting for testing."""
    posting_html = """
    <html>
    <head><title>Restaurant Manager - Hiring Multiple Positions</title></head>
    <body>
    <section id="postingbody">
    <h2 class="postingtitle">Restaurant Manager - Seasonal Hiring</h2>
    <small>Scottsdale, AZ</small>

    <p><b>Company:</b> Desert Bistro Group</p>

    <p>Desert Bistro Group is expanding and looking to hire multiple Restaurant Manager positions
    for our busy season. We're a growing local restaurant group with 3 locations across the Phoenix area.</p>

    <p><b>Responsibilities:</b></p>
    <ul>
        <li>Manage daily operations and staff scheduling</li>
        <li>Forecast customer volume and plan staffing accordingly</li>
        <li>Ensure excellent customer service during peak seasons</li>
        <li>Manage inventory and ordering</li>
    </ul>

    <p><b>Requirements:</b></p>
    <ul>
        <li>3+ years restaurant management experience</li>
        <li>Strong leadership and team building skills</li>
        <li>Experience with high-volume operations</li>
    </ul>

    <p><b>Compensation & Benefits:</b></p>
    <ul>
        <li>$55,000 - $65,000 per year</li>
        <li>Health insurance</li>
        <li>401k</li>
        <li>Paid time off</li>
    </ul>

    <p>Contact: hiring@desertbistro.com or call (480) 555-1234</p>
    <p>Website: https://www.desertbistro.com</p>
    </section>
    <time datetime="2025-11-25T10:00:00">2025-11-25</time>
    </body>
    </html>
    """

    posting_url = "https://phoenix.craigslist.org/nph/fbh/d/restaurant-manager-seasonal/1234567890.html"

    return posting_html, posting_url


def test_individual_agents():
    """Test each agent individually."""
    print("=" * 80)
    print("TESTING INDIVIDUAL AGENTS")
    print("=" * 80)

    posting_html, posting_url = create_sample_posting()

    # Test Extractor
    print("\n1. Testing ExtractorAgent...")
    from agents.extractor import ExtractorAgent
    extractor = ExtractorAgent()
    extracted = extractor.extract(posting_html, posting_url)

    print(f"   Company: {extracted.get('company_name')}")
    print(f"   Job Title: {extracted.get('job_title')}")
    print(f"   Location: {extracted.get('location')}")
    print(f"   Salary: {extracted.get('salary')}")
    print(f"   Professionalism Score: {extracted.get('professionalism_score')}/10")
    print(f"   Red Flags: {extracted.get('red_flags')}")

    # Test Researcher
    print("\n2. Testing ResearcherAgent...")
    from agents.researcher import ResearcherAgent
    researcher = ResearcherAgent()
    researched = researcher.research(extracted)
    researched = researcher.validate_company(researched)

    print(f"   Company Verified: {researched.get('company_verified')}")
    print(f"   Is Local: {researched.get('is_local')}")
    print(f"   Is Valid Lead: {researched.get('is_valid_lead')}")

    # Test Scorer
    print("\n3. Testing ScorerAgent...")
    from agents.scorer import ScorerAgent
    scorer = ScorerAgent()
    scored = scorer.score(researched)

    print(f"   Score: {scored.get('score')}/30")
    print(f"   Tier: {scored.get('tier')}")
    print(f"   Score Breakdown:")
    for category, points in scored.get('score_breakdown', {}).items():
        print(f"     - {category}: {points}")

    # Test Analyzer
    print("\n4. Testing AnalyzerAgent...")
    from agents.analyzer import AnalyzerAgent
    analyzer = AnalyzerAgent()
    analyzed = analyzer.analyze(scored)

    print(f"   Pain Points: {len(analyzed.get('pain_points', []))}")
    for pain in analyzed.get('pain_points', []):
        print(f"     - {pain['category']}: {pain['description']}")

    print(f"   Forecast Opportunities: {len(analyzed.get('forecast_opportunities', []))}")
    for opp in analyzed.get('forecast_opportunities', []):
        print(f"     - {opp['what_to_predict']} ({opp['timeframe']})")

    # Test Writer
    print("\n5. Testing WriterAgent...")
    from agents.writer import WriterAgent
    writer = WriterAgent()
    written = writer.write(analyzed)

    print(f"   Value Proposition: {written.get('value_proposition')}")
    print(f"   Call Script Generated: {bool(written.get('call_script'))}")
    print(f"   Email Template Generated: {bool(written.get('email_template'))}")

    # Test Storer
    print("\n6. Testing StorerAgent...")
    from agents.storer import StorerAgent
    storer = StorerAgent()
    stored = storer.store(written)

    print(f"   Lead ID: {stored.get('lead_id')}")
    print(f"   Storage Path: {stored.get('storage_path')}")
    print(f"   Storage Status: {stored.get('storage_status')}")

    print("\n" + "=" * 80)
    print("INDIVIDUAL AGENT TESTS COMPLETE")
    print("=" * 80)


def test_full_pipeline():
    """Test the complete orchestrated pipeline."""
    print("\n\n")
    print("=" * 80)
    print("TESTING FULL PIPELINE")
    print("=" * 80)

    posting_html, posting_url = create_sample_posting()

    # Initialize orchestrator
    orchestrator = Orchestrator(data_dir="data/leads")

    # Process posting
    print("\nProcessing posting through full pipeline...")
    result = orchestrator.process_posting(posting_html, posting_url)

    # Display results
    print("\n" + "-" * 80)
    print("PIPELINE RESULTS")
    print("-" * 80)

    print(f"\nLead ID: {result.get('lead_id')}")
    print(f"Company: {result.get('company_name')}")
    print(f"Job Title: {result.get('job_title')}")
    print(f"Location: {result.get('location')}")
    print(f"Industry: {result.get('company_industry')}")

    print(f"\nSCORING:")
    print(f"  Score: {result.get('score')}/30")
    print(f"  Tier: {result.get('tier')}")
    print(f"  Disqualified: {result.get('disqualified')}")

    print(f"\nSTATUS TRACKING:")
    print(f"  Extraction: {result.get('extraction_status')}")
    print(f"  Research: {result.get('research_status')}")
    print(f"  Scoring: {result.get('scoring_status')}")
    print(f"  Analysis: {result.get('analysis_status')}")
    print(f"  Writing: {result.get('writing_status')}")
    print(f"  Storage: {result.get('storage_status')}")

    if result.get('value_proposition'):
        print(f"\nVALUE PROPOSITION:")
        print(f"  {result.get('value_proposition')}")

    if result.get('call_script'):
        print(f"\nCALL SCRIPT PREVIEW:")
        script = result.get('call_script')
        print(f"  Intro: {script.get('intro', 'N/A')}")
        print(f"  Pattern Interrupt: {script.get('pattern_interrupt', 'N/A')}")

    print("\n" + "=" * 80)
    print("FULL PIPELINE TEST COMPLETE")
    print("=" * 80)


def test_analytics():
    """Test analytics functionality."""
    print("\n\n")
    print("=" * 80)
    print("TESTING ANALYTICS")
    print("=" * 80)

    orchestrator = Orchestrator(data_dir="data/leads")

    analytics = orchestrator.get_analytics()

    print(f"\nTotal Leads: {analytics.get('total_leads')}")
    print(f"Average Score: {analytics.get('avg_score')}")
    print(f"Disqualified Count: {analytics.get('disqualified_count')}")

    print(f"\nLeads by Tier:")
    for tier, count in analytics.get('by_tier', {}).items():
        tier_labels = {1: "Hot", 2: "Warm", 3: "Medium", 4: "Cold", 5: "Disqualified"}
        print(f"  Tier {tier} ({tier_labels.get(tier, 'Unknown')}): {count}")

    print(f"\nLeads by Status:")
    for status, count in analytics.get('by_status', {}).items():
        print(f"  {status}: {count}")

    print(f"\nLeads by Industry:")
    for industry, count in analytics.get('by_industry', {}).items():
        print(f"  {industry}: {count}")

    print("\n" + "=" * 80)
    print("ANALYTICS TEST COMPLETE")
    print("=" * 80)


def test_bulk_operations():
    """Test bulk operations."""
    print("\n\n")
    print("=" * 80)
    print("TESTING BULK OPERATIONS")
    print("=" * 80)

    orchestrator = Orchestrator(data_dir="data/leads")

    # Get all leads
    leads = orchestrator.get_all_leads()

    if not leads:
        print("\nNo leads found. Run test_full_pipeline() first.")
        return

    lead_ids = [lead.get('lead_id') for lead in leads[:3]]  # Get first 3

    print(f"\nTesting with {len(lead_ids)} leads...")

    # Test bulk script generation
    print("\n1. Generating bulk scripts...")
    scripts = orchestrator.generate_bulk_scripts(lead_ids)
    print(f"   Generated scripts for {len(scripts)} leads")

    # Test bulk email generation
    print("\n2. Generating bulk emails...")
    emails = orchestrator.generate_bulk_emails(lead_ids)
    print(f"   Generated emails for {len(emails)} leads")

    # Test CSV export
    print("\n3. Exporting to CSV...")
    csv_data = orchestrator.export_leads_csv(lead_ids)
    lines = csv_data.split('\n')
    print(f"   CSV has {len(lines)} lines (including header)")

    print("\n" + "=" * 80)
    print("BULK OPERATIONS TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    print("\n")
    print("#" * 80)
    print("FORECASTA LEAD QUALIFICATION SYSTEM - TEST SUITE")
    print("#" * 80)

    # Run all tests
    test_individual_agents()
    test_full_pipeline()
    test_analytics()
    test_bulk_operations()

    print("\n\n")
    print("#" * 80)
    print("ALL TESTS COMPLETE!")
    print("#" * 80)
    print("\nNext steps:")
    print("1. Run 'python dashboard/backend.py' to start the API server")
    print("2. Open http://localhost:5000 in your browser to access the dashboard")
    print("3. Check data/leads/ directory for stored lead files")
    print("\n")
