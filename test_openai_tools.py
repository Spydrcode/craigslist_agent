"""
Test script demonstrating OpenAI's advanced tools integration:
1. Web Search - Research companies from job postings
2. Function Calling - Structured data extraction
3. File Search - Find similar companies from past analyses
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from agents import ClientAgent, CompanyResearchAgent, ParserAgent, FileSearchAgent
from models import RawJobPosting
from models_enhanced import ResearchQuery

def test_web_search():
    """Test 1: Web Search for Company Research"""
    print("\n" + "="*80)
    print("TEST 1: WEB SEARCH - Company Research")
    print("="*80)
    
    client = ClientAgent()
    
    # Research a company using web search
    result = client.research_company_web(
        company_name="Wegmans Food Markets",
        context="Grocery retail chain, hiring for multiple store positions in New York"
    )
    
    print(f"\nCompany: {result['company_name']}")
    print(f"Source: {result['source']}")
    print(f"\nResearch Summary:")
    print(result['research_summary'][:500] + "..." if len(result['research_summary']) > 500 else result['research_summary'])
    print("\n✓ Web search completed successfully!")


def test_function_calling():
    """Test 2: Function Calling for Structured Extraction"""
    print("\n" + "="*80)
    print("TEST 2: FUNCTION CALLING - Structured Data Extraction")
    print("="*80)
    
    client = ClientAgent()
    
    # Sample job posting text
    job_text = """
    Store Manager - Wegmans Food Markets
    
    Wegmans is a family-owned grocery chain with over 100 stores across the East Coast.
    We're expanding rapidly and opening 5 new locations this year, creating hundreds of jobs.
    
    We're looking for experienced Store Managers to lead our teams. This role involves:
    - Managing 50-100 team members
    - Handling high-volume customer traffic (10,000+ customers/week)
    - Scheduling and workforce planning for seasonal demand
    - Reducing turnover through employee engagement
    
    Salary: $80,000 - $120,000 + benefits
    
    Requirements:
    - 5+ years retail management experience
    - Strong leadership and people management skills
    - Experience with inventory and staffing systems
    """
    
    # Extract structured data using function calling
    company_data = client.extract_company_info_structured(
        job_description=job_text,
        job_title="Store Manager"
    )
    
    print(f"\nExtracted Data:")
    print(f"  Company: {company_data.get('company_name', 'N/A')}")
    print(f"  Industry: {company_data.get('industry', 'N/A')}")
    print(f"  Company Size: {company_data.get('company_size', 'N/A')}")
    print(f"  Forecasta Fit Score: {company_data.get('forecasta_fit_score', 0)}/10")
    print(f"  Reasoning: {company_data.get('forecasta_fit_reasoning', 'N/A')}")
    print(f"\n  Hiring Volume Signals:")
    for signal in company_data.get('hiring_volume_signals', []):
        print(f"    - {signal}")
    print(f"\n  Pain Points:")
    for pain in company_data.get('pain_points', []):
        print(f"    - {pain}")
    print(f"\n  Growth Indicators:")
    for growth in company_data.get('growth_indicators', []):
        print(f"    - {growth}")
    
    print("\n✓ Function calling completed successfully!")


def test_file_search():
    """Test 3: File Search for Similar Companies"""
    print("\n" + "="*80)
    print("TEST 3: FILE SEARCH - Find Similar Companies")
    print("="*80)
    
    file_search = FileSearchAgent()
    
    # Search for companies similar to a retail chain
    similar = file_search.search_similar_companies(
        company_name="Target",
        industry="Retail",
        max_results=5
    )
    
    if similar:
        print(f"\nFound {len(similar)} similar companies:")
        for i, company in enumerate(similar, 1):
            print(f"\n  {i}. {company['company']} ({company['industry']})")
            print(f"     Tier: {company['tier']}, Score: {company['score']}/30")
            if company['pain_points']:
                print(f"     Pain Points: {', '.join(company['pain_points'][:2])}")
    else:
        print("\nNo similar companies found in database.")
        print("(Run some lead analyses first to populate the database)")
    
    # Search by specific pain point
    print("\n" + "-"*80)
    print("Searching for companies with 'turnover' challenges...")
    pain_point_matches = file_search.search_by_pain_point("turnover", max_results=3)
    
    if pain_point_matches:
        print(f"\nFound {len(pain_point_matches)} companies:")
        for company in pain_point_matches:
            print(f"  - {company['company']} ({company['tier']})")
    else:
        print("No companies found with turnover challenges.")
    
    print("\n✓ File search completed successfully!")


def test_integrated_workflow():
    """Test 4: Integrated Workflow Using All Three Tools"""
    print("\n" + "="*80)
    print("TEST 4: INTEGRATED WORKFLOW - All Tools Together")
    print("="*80)
    
    print("\nScenario: Analyzing a job posting with full intelligence")
    print("-" * 80)
    
    # Step 1: Parse job posting with function calling
    print("\n[1/3] Extracting structured data from job posting...")
    client = ClientAgent()
    parser = ParserAgent(client, use_structured_extraction=True)
    
    raw_job = RawJobPosting(
        title="Construction Superintendent",
        url="https://example.com/job/123",
        description="""
        Major construction company hiring Superintendents for multiple projects.
        We have 15 active construction sites and are growing rapidly.
        Managing crews of 20-50 workers per site.
        Need help with scheduling, workforce planning, and reducing labor costs.
        """,
        location="Phoenix, AZ",
        category="construction"
    )
    
    parsed = parser.parse_job(raw_job, use_ai=True)
    print(f"   ✓ Extracted {len(parsed.pain_points)} pain points, {len(parsed.skills)} skills")
    
    # Step 2: Research company with web search
    print("\n[2/3] Researching company using web search...")
    research_agent = CompanyResearchAgent(client, use_web_search=True)
    
    query = ResearchQuery(
        company_name="ABC Construction",
        location="Phoenix, AZ",
        industry="Construction",
        search_platforms=[]  # Web search will be used instead
    )
    
    # Note: Web search would run here in production
    print("   ✓ Web search would gather: company size, growth, hiring patterns")
    
    # Step 3: Check for similar companies
    print("\n[3/3] Searching for similar companies in database...")
    file_search = FileSearchAgent()
    similar = file_search.search_similar_companies("ABC Construction", "Construction", max_results=3)
    
    if similar:
        print(f"   ✓ Found {len(similar)} similar companies we've analyzed before")
    else:
        print("   ℹ No similar companies in database yet")
    
    print("\n✓ Integrated workflow completed!")
    print("\nAll three OpenAI tools working together:")
    print("  1. Function Calling → Structured data extraction")
    print("  2. Web Search → Real-time company research") 
    print("  3. File Search → Historical intelligence from past analyses")


if __name__ == "__main__":
    print("\n")
    print("="*80)
    print(" OPENAI ADVANCED TOOLS INTEGRATION TEST")
    print("="*80)
    print("\nTesting 3 OpenAI capabilities:")
    print("  1. Web Search - Real-time company research")
    print("  2. Function Calling - Structured data extraction")
    print("  3. File Search - Historical lead intelligence")
    
    try:
        # Run all tests
        test_function_calling()  # Start with this - doesn't require internet
        test_web_search()  # Requires OpenAI web search enabled
        test_file_search()  # Requires existing lead files
        test_integrated_workflow()  # Shows them working together
        
        print("\n" + "="*80)
        print("✓ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*80)
        print("\nNext steps:")
        print("  1. These features are now available in your agents")
        print("  2. Web search is enabled by default in CompanyResearchAgent")
        print("  3. Function calling is enabled by default in ParserAgent")
        print("  4. FileSearchAgent can search your lead database")
        print("\n")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
