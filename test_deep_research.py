"""
Test Deep Research Agent

This script tests the DeepResearchAgent with various research scenarios.
"""

import os
from agents.deep_research_agent import DeepResearchAgent


def test_company_research():
    """Test basic company research."""
    print("\n" + "="*80)
    print("TEST 1: Company Research")
    print("="*80)
    
    agent = DeepResearchAgent(
        model="o4-mini-deep-research",
        mcp_server_url="http://localhost:8001/sse/"
    )
    
    result = agent.research_company(
        company_name="Stripe",
        research_focus="Payment infrastructure and developer tools",
        background=False,  # Synchronous for testing
        use_internal_data=False  # Public data only
    )
    
    print(f"\n✅ Research complete!")
    print(f"📄 Report length: {len(result['report'])} chars")
    print(f"🔗 Sources: {len(result['sources'])}")
    print(f"🔧 Tools used: {result['tool_usage']}")
    
    print(f"\n📊 REPORT PREVIEW:")
    print("-"*80)
    print(result['report'][:1000] + "...\n")
    
    # Save report
    agent.save_research_report(result)
    
    return result


def test_lead_qualification():
    """Test lead qualification research."""
    print("\n" + "="*80)
    print("TEST 2: Lead Qualification")
    print("="*80)
    
    agent = DeepResearchAgent(
        model="o4-mini-deep-research",
        mcp_server_url="http://localhost:8001/sse/"
    )
    
    # Sample lead data
    lead_data = {
        "company_name": "Notion",
        "job_count": 12,
        "score": 88,
        "pain_points": ["scaling infrastructure", "performance optimization"],
        "tech_stack": ["React", "TypeScript", "PostgreSQL"],
        "industry": "productivity software"
    }
    
    result = agent.qualify_lead(
        company_name=lead_data['company_name'],
        lead_data=lead_data,
        qualification_criteria=[
            "Company has $50K+ budget",
            "Active hiring indicates growth",
            "Tech stack shows infrastructure needs",
            "No recent layoffs or downsizing"
        ],
        background=False
    )
    
    print(f"\n✅ Qualification complete!")
    print(f"📄 Report length: {len(result['report'])} chars")
    print(f"🔗 Sources: {len(result['sources'])}")
    
    print(f"\n📊 QUALIFICATION PREVIEW:")
    print("-"*80)
    print(result['report'][:1000] + "...\n")
    
    # Save report
    agent.save_research_report(result)
    
    return result


def test_market_trends():
    """Test market trend research."""
    print("\n" + "="*80)
    print("TEST 3: Market Trends Research")
    print("="*80)
    
    agent = DeepResearchAgent(
        model="o4-mini-deep-research"
    )
    
    result = agent.research_market_trends(
        industry="AI/ML",
        time_period="last 6 months",
        focus_areas=[
            "hiring trends",
            "funding activity",
            "emerging technologies"
        ],
        background=False
    )
    
    print(f"\n✅ Market research complete!")
    print(f"📄 Report length: {len(result['report'])} chars")
    print(f"🔗 Sources: {len(result['sources'])}")
    
    print(f"\n📊 MARKET TRENDS PREVIEW:")
    print("-"*80)
    print(result['report'][:1000] + "...\n")
    
    # Save report
    agent.save_research_report(result)
    
    return result


def test_competitive_analysis():
    """Test competitive analysis."""
    print("\n" + "="*80)
    print("TEST 4: Competitive Analysis")
    print("="*80)
    
    agent = DeepResearchAgent(
        model="o4-mini-deep-research"
    )
    
    result = agent.competitive_analysis(
        target_company="Vercel",
        competitors=["Netlify", "Cloudflare Pages", "AWS Amplify"],
        comparison_dimensions=[
            "pricing",
            "features",
            "developer experience",
            "performance"
        ],
        background=False
    )
    
    print(f"\n✅ Competitive analysis complete!")
    print(f"📄 Report length: {len(result['report'])} chars")
    print(f"🔗 Sources: {len(result['sources'])}")
    
    print(f"\n📊 COMPETITIVE ANALYSIS PREVIEW:")
    print("-"*80)
    print(result['report'][:1000] + "...\n")
    
    # Save report
    agent.save_research_report(result)
    
    return result


def test_with_internal_data():
    """Test research using internal MCP data."""
    print("\n" + "="*80)
    print("TEST 5: Research with Internal Lead Data")
    print("="*80)
    
    # Check if MCP server is running
    print("⚠️  Note: This test requires MCP server running")
    print("    Start it with: python mcp_server.py")
    
    proceed = input("\nIs MCP server running? (y/n): ").strip().lower()
    if proceed != 'y':
        print("Skipping internal data test")
        return None
    
    agent = DeepResearchAgent(
        model="o4-mini-deep-research",
        mcp_server_url="http://localhost:8001/sse/"
    )
    
    # This will use both web search AND internal MCP data
    result = agent.research_company(
        company_name="CloudTech Solutions",  # From sample data
        research_focus="Validate hiring velocity and pain points",
        background=False,
        use_internal_data=True,  # Use MCP server
        use_code_interpreter=False
    )
    
    print(f"\n✅ Research with internal data complete!")
    print(f"📄 Report length: {len(result['report'])} chars")
    print(f"🔗 Sources: {len(result['sources'])}")
    print(f"🔧 Tools used: {result['tool_usage']}")
    
    print(f"\n📊 COMBINED RESEARCH PREVIEW:")
    print("-"*80)
    print(result['report'][:1000] + "...\n")
    
    # Save report
    agent.save_research_report(result)
    
    return result


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("DEEP RESEARCH AGENT - TEST SUITE")
    print("="*80)
    print("\nThis will make API calls to OpenAI's deep research models.")
    print("Costs vary but typically $0.50-$5 per research task.")
    print("\nTests will run synchronously (not background) for demonstration.")
    
    proceed = input("\nProceed with tests? (y/n): ").strip().lower()
    if proceed != 'y':
        print("Tests cancelled")
        return
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n❌ OPENAI_API_KEY not found!")
        print("Set it in .env or environment variable")
        return
    
    results = {}
    
    # Run tests
    try:
        # Test 1: Basic company research
        results['company_research'] = test_company_research()
        
        # Test 2: Lead qualification
        results['lead_qualification'] = test_lead_qualification()
        
        # Test 3: Market trends
        results['market_trends'] = test_market_trends()
        
        # Test 4: Competitive analysis
        results['competitive_analysis'] = test_competitive_analysis()
        
        # Test 5: With internal data (optional)
        results['internal_data'] = test_with_internal_data()
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, result in results.items():
        if result:
            status = "✅ PASS"
            sources = len(result.get('sources', []))
            print(f"{status}: {test_name} ({sources} sources)")
        else:
            print(f"⏭️  SKIP: {test_name}")
    
    print("\n📁 Reports saved to: output/research/")
    print("="*80)


if __name__ == "__main__":
    main()
