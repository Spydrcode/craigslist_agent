"""
Example: Using the Lead Analysis Agent to qualify job posting leads for Forecasta.

This script demonstrates how to:
1. Analyze a job posting
2. Generate lead qualification scores
3. Create value propositions and call scripts
4. Save lead data for ML training
"""
import json
import os
from datetime import datetime
from agents import LeadAnalysisAgent, ClientAgent

# Sample job posting for testing
SAMPLE_POSTING = """
Commercial Roofer - 5+ Positions Available

ABC Roofing Solutions is a growing commercial roofing company serving the Bay Area 
for over 15 years. We're expanding our team and looking for experienced commercial 
roofers to join us.

Positions: 5-7 experienced roofers
Pay: $55,000-$75,000/year DOE + overtime
Benefits: Health insurance, 401k, paid time off

Requirements:
- 3+ years commercial roofing experience
- Own basic tools
- Valid driver's license
- Able to work at heights

We have a strong project pipeline for the next 6 months with several large contracts 
starting in spring. Looking to bring on crew before March rush.

About Us:
Family-owned business with 30 employees. We specialize in commercial flat roofing, 
re-roofing, and maintenance for schools, offices, and industrial buildings.

Contact: John Smith, Operations Manager
Phone: (555) 123-4567
Email: jobs@abcroofing.com
Website: www.abcroofing.com
"""


def main():
    """Run lead analysis example."""
    print("=" * 80)
    print("FORECASTA LEAD ANALYSIS AGENT - EXAMPLE")
    print("=" * 80)
    print()

    # Initialize the agent
    print("Initializing Lead Analysis Agent...")
    lead_agent = LeadAnalysisAgent()
    print("✓ Agent initialized\n")

    # Analyze the posting
    print("Analyzing job posting...")
    print("-" * 80)
    print(SAMPLE_POSTING[:200] + "...")
    print("-" * 80)
    print()

    # Run analysis (web search disabled for example)
    result = lead_agent.analyze_posting(
        posting_text=SAMPLE_POSTING,
        posting_url="https://sfbay.craigslist.org/sfc/trd/example123.html",
        enable_web_search=False  # Set to True to enable company research
    )

    # Display results
    print("\n" + "=" * 80)
    print("ANALYSIS RESULTS")
    print("=" * 80)
    print()

    # Company Information
    print("📊 COMPANY INFORMATION")
    print("-" * 80)
    company = result.get('company', {})
    print(f"Name: {company.get('name', 'N/A')}")
    print(f"Location: {company.get('location', 'N/A')}")
    print(f"Industry: {result.get('business_signals', {}).get('industry', 'N/A')}")
    print()

    # Lead Scoring
    print("🎯 LEAD SCORING")
    print("-" * 80)
    scoring = result.get('lead_scoring', {})
    print(f"Tier: {scoring.get('tier', 'N/A')} - {scoring.get('tier_label', 'N/A')}")
    print(f"Final Score: {scoring.get('final_score', 0)}/30")
    print(f"Recommendation: {scoring.get('recommendation', 'N/A')}")
    print()

    if scoring.get('disqualified', False):
        print(f"❌ DISQUALIFIED: {scoring.get('disqualification_reason', 'Unknown')}")
        print()
    else:
        print("Category Scores:")
        category_scores = scoring.get('category_scores', {})
        print(f"  • Company Scale: {category_scores.get('company_scale', 0)}/9")
        print(f"  • Forecasting Pain: {category_scores.get('forecasting_pain', 0)}/12")
        print(f"  • Accessibility: {category_scores.get('accessibility', 0)}/7")
        print(f"  • Data Quality: {category_scores.get('data_quality', 0)}/2")
        print()

        # Pain Points
        print("💡 FORECASTING NEEDS")
        print("-" * 80)
        needs = result.get('needs_analysis', {})
        print(f"Pain Severity: {needs.get('estimated_pain_severity', 'N/A')}")
        print(f"Forecast Horizon: {needs.get('forecast_horizon_recommended', 'N/A')}")
        print()

        pain_points = needs.get('primary_pain_points', [])
        if pain_points:
            print("Primary Pain Points:")
            for i, pain in enumerate(pain_points, 1):
                print(f"\n  {i}. {pain.get('pain_category', 'N/A')}")
                print(f"     Challenge: {pain.get('specific_challenge', 'N/A')}")
                print(f"     Solution: {pain.get('forecasta_solution', 'N/A')}")
        print()

        # Value Propositions
        print("💬 VALUE PROPOSITIONS")
        print("-" * 80)
        value_props = result.get('value_propositions', [])
        for i, vp in enumerate(value_props, 1):
            print(f"{i}. [{vp.get('version', 'N/A').upper()}]")
            print(f"   {vp.get('text', 'N/A')}")
            print()

        # Call Script Preview
        print("📞 CALL SCRIPT PREVIEW")
        print("-" * 80)
        call_script = result.get('call_script', {})
        print(f"Target Contact: {call_script.get('target_contact', 'N/A')}")
        print()

        main_script = call_script.get('main_script', {})
        print("Opening:")
        print(f'  "{main_script.get("introduction", "N/A")}"')
        print()
        print("Pattern Interrupt:")
        print(f'  "{main_script.get("pattern_interrupt", "N/A")}"')
        print()
        print("Key Question:")
        print(f'  "{main_script.get("diagnosis_question", "N/A")}"')
        print()

    # Generate Dashboard Summary
    print("\n" + "=" * 80)
    print("DASHBOARD SUMMARY")
    print("=" * 80)
    print()

    dashboard = lead_agent.generate_dashboard_summary(result)
    print(dashboard)

    # Save to file
    output_dir = "output/leads"
    os.makedirs(output_dir, exist_ok=True)

    lead_id = result.get('lead_id', 'unknown')
    company_name = result.get('company', {}).get('name', 'unknown')
    company_slug = company_name.lower().replace(' ', '_').replace('.', '')

    # Save JSON
    json_filename = f"lead_{company_slug}_{lead_id[:8]}.json"
    json_path = os.path.join(output_dir, json_filename)

    with open(json_path, 'w') as f:
        json.dump(result, f, indent=2)

    print("\n" + "=" * 80)
    print(f"✓ Lead data saved to: {json_path}")

    # Save markdown summary
    md_filename = f"lead_{company_slug}_{lead_id[:8]}_summary.md"
    md_path = os.path.join(output_dir, md_filename)

    with open(md_path, 'w') as f:
        f.write(dashboard)

    print(f"✓ Dashboard summary saved to: {md_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
