"""
End-to-End Example: Using All OpenAI Advanced Tools Together
Demonstrates a complete workflow from scraping → research → analysis → visualization
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents import (
    ScraperAgent,
    CompanyResearchAgent,
    LeadAnalysisAgent,
    VisualizationAgent,
    FileSearchAgent,
    ClientAgent
)
from utils import get_logger

logger = get_logger(__name__)


def example_complete_workflow():
    """
    Complete workflow demonstrating all OpenAI tools:
    1. Web Search - Research company
    2. Function Calling - Extract structured data
    3. File Search - Find similar companies
    4. Image Generation - Create presentation
    5. Code Interpreter - Analyze hiring patterns
    """
    print("\n" + "="*80)
    print("COMPLETE WORKFLOW: All OpenAI Tools")
    print("="*80)
    
    company_name = "TechCorp Solutions"
    
    # ========================================================================
    # STEP 1: Research Company (Web Search)
    # ========================================================================
    print("\n📡 STEP 1: Researching company with Web Search...")
    
    researcher = CompanyResearchAgent(use_web_search=True)
    profile = researcher.research_company(company_name)
    
    print(f"   Company: {profile.name}")
    print(f"   Industry: {profile.industry}")
    print(f"   Size: {profile.company_size} employees")
    print(f"   Location: {profile.location}")
    
    # ========================================================================
    # STEP 2: Extract Structured Data (Function Calling)
    # ========================================================================
    print("\n🔧 STEP 2: Extracting structured company data...")
    
    client = ClientAgent()
    
    # Create a text summary of company
    company_text = f"""
    {profile.name} is a {profile.industry} company based in {profile.location}.
    They have approximately {profile.company_size} employees.
    Recent growth signals: {', '.join(profile.growth_signals[:3])}
    """
    
    structured_data = client.extract_company_info_structured(company_text)
    
    print(f"   Validated Fields: {len(structured_data.get('company_data', {}))} fields extracted")
    print(f"   Confidence: {structured_data.get('confidence', 0):.1f}%")
    
    # ========================================================================
    # STEP 3: Find Similar Companies (File Search)
    # ========================================================================
    print("\n🔍 STEP 3: Finding similar companies in history...")
    
    file_agent = FileSearchAgent()
    similar_companies = file_agent.search_similar_companies(company_name, limit=3)
    
    print(f"   Found {len(similar_companies)} similar companies:")
    for comp in similar_companies:
        print(f"   - {comp.get('company', 'Unknown')}")
    
    # ========================================================================
    # STEP 4: Analyze Hiring Patterns (Code Interpreter)
    # ========================================================================
    print("\n📊 STEP 4: Analyzing hiring patterns with Code Interpreter...")
    
    # Sample job data
    job_postings = [
        {"title": "Senior Software Engineer", "location": "San Francisco, CA", "posted_date": "2024-01-15"},
        {"title": "DevOps Engineer", "location": "San Francisco, CA", "posted_date": "2024-01-18"},
        {"title": "Product Manager", "location": "New York, NY", "posted_date": "2024-01-20"},
        {"title": "Data Scientist", "location": "San Francisco, CA", "posted_date": "2024-01-22"},
        {"title": "Frontend Developer", "location": "Remote", "posted_date": "2024-01-25"},
    ]
    
    analysis = client.analyze_hiring_data_with_code(job_postings)
    
    if 'analysis' in analysis:
        print(f"   Analysis preview: {analysis['analysis'][:200]}...")
    else:
        print(f"   ❌ Analysis failed: {analysis.get('error', 'Unknown')}")
    
    # ========================================================================
    # STEP 5: Calculate ROI (Code Interpreter)
    # ========================================================================
    print("\n💰 STEP 5: Calculating Forecasta ROI...")
    
    roi = client.calculate_forecasta_roi(
        company_size=profile.company_size or 250,
        avg_salary=80000,
        turnover_rate=0.15
    )
    
    if 'roi_analysis' in roi:
        print(f"   ROI preview: {roi['roi_analysis'][:200]}...")
    else:
        print(f"   ❌ ROI calculation failed: {roi.get('error', 'Unknown')}")
    
    # ========================================================================
    # STEP 6: Create Visual Presentation (Image Generation)
    # ========================================================================
    print("\n🎨 STEP 6: Creating visual presentation with DALL-E 3...")
    
    viz = VisualizationAgent()
    
    presentation = viz.create_prospect_presentation(
        company_name=company_name,
        industry=profile.industry,
        job_count=len(job_postings),
        employee_count=profile.company_size or 250
    )
    
    print(f"   ✅ Created {len(presentation['assets'])} visual assets")
    for asset_type, path in presentation['assets'].items():
        print(f"      - {asset_type}: {path}")
    
    # ========================================================================
    # STEP 7: Create Hiring Dashboard (Image Generation + Code Interpreter)
    # ========================================================================
    print("\n📈 STEP 7: Creating hiring trends dashboard...")
    
    dashboard_path = viz.visualize_hiring_patterns(job_postings, company_name)
    
    if dashboard_path:
        print(f"   ✅ Dashboard created: {dashboard_path}")
    else:
        print("   ❌ Dashboard creation failed")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "="*80)
    print("✅ WORKFLOW COMPLETE")
    print("="*80)
    
    print("\nTools Used:")
    print("  ✅ Web Search - Company research")
    print("  ✅ Function Calling - Structured data extraction")
    print("  ✅ File Search - Similar company discovery")
    print("  ✅ Code Interpreter - Hiring analysis + ROI calculation")
    print("  ✅ Image Generation - Visual presentations")
    
    print(f"\nOutput:")
    print(f"  📁 Presentation assets: {presentation['output_dir']}")
    print(f"  📊 Dashboard: {dashboard_path if dashboard_path else 'N/A'}")
    
    print("\nNext Steps:")
    print("  1. Review visual assets in output/visualizations/")
    print("  2. Use presentation for sales pitch")
    print("  3. Track lead in CRM")
    print("  4. Schedule follow-up based on TIER score")


def example_quick_visualization():
    """Quick example: Just create visuals for a known company."""
    print("\n" + "="*80)
    print("QUICK EXAMPLE: Create Visuals for Known Company")
    print("="*80)
    
    viz = VisualizationAgent()
    
    # Create complete package
    package = viz.create_prospect_presentation(
        company_name="StartupXYZ",
        industry="SaaS",
        job_count=12,
        employee_count=45
    )
    
    print(f"\n✅ Created presentation for {package['company']}")
    print(f"📁 Assets: {len(package['assets'])}")
    for asset_type, path in package['assets'].items():
        print(f"   - {asset_type}")


def example_historical_intelligence():
    """Example: Use file search to find patterns."""
    print("\n" + "="*80)
    print("HISTORICAL INTELLIGENCE: Find Patterns in Past Leads")
    print("="*80)
    
    file_agent = FileSearchAgent()
    
    # Find companies with turnover issues
    print("\n🔍 Searching for companies with employee turnover challenges...")
    turnover_companies = file_agent.search_by_pain_point(
        pain_point="high employee turnover",
        limit=5
    )
    
    print(f"   Found {len(turnover_companies)} companies")
    for company in turnover_companies:
        print(f"   - {company.get('company', 'Unknown')}")
    
    # Find similar companies
    if turnover_companies:
        first_company = turnover_companies[0].get('company')
        print(f"\n🔍 Finding companies similar to {first_company}...")
        similar = file_agent.search_similar_companies(first_company, limit=3)
        
        print(f"   Found {len(similar)} similar companies")
        for comp in similar:
            print(f"   - {comp.get('company', 'Unknown')}")


def example_roi_calculator():
    """Example: Quick ROI calculator."""
    print("\n" + "="*80)
    print("ROI CALCULATOR: Calculate Forecasta Value Proposition")
    print("="*80)
    
    client = ClientAgent()
    viz = VisualizationAgent()
    
    companies = [
        {"name": "Small Corp", "size": 50, "salary": 65000},
        {"name": "Mid Corp", "size": 250, "salary": 75000},
        {"name": "Large Corp", "size": 1000, "salary": 85000},
    ]
    
    for company in companies:
        print(f"\n💰 Calculating ROI for {company['name']}...")
        
        # Calculate
        roi = client.calculate_forecasta_roi(
            company_size=company['size'],
            avg_salary=company['salary'],
            turnover_rate=0.18
        )
        
        if 'roi_analysis' in roi:
            print(f"   Analysis: {roi['roi_analysis'][:150]}...")
        
        # Visualize
        visual_path = viz.create_roi_calculator_visual(
            company_size=company['size'],
            avg_salary=company['salary'],
            company_name=company['name']
        )
        
        if visual_path:
            print(f"   ✅ Visual created: {visual_path}")


if __name__ == "__main__":
    print("\n" + "🚀"*40)
    print("END-TO-END OPENAI TOOLS EXAMPLES")
    print("🚀"*40)
    
    print("\nSelect example to run:")
    print("  1. Complete Workflow (all tools)")
    print("  2. Quick Visualization")
    print("  3. Historical Intelligence")
    print("  4. ROI Calculator")
    print("  5. Run All")
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    if choice == "1":
        example_complete_workflow()
    elif choice == "2":
        example_quick_visualization()
    elif choice == "3":
        example_historical_intelligence()
    elif choice == "4":
        example_roi_calculator()
    elif choice == "5":
        print("\n🚀 Running all examples...\n")
        example_complete_workflow()
        example_quick_visualization()
        example_historical_intelligence()
        example_roi_calculator()
    else:
        print("Invalid choice. Running complete workflow...")
        example_complete_workflow()
    
    print("\n" + "="*80)
    print("✅ EXAMPLES COMPLETE")
    print("="*80)
    print("\nCheck output/visualizations/ for generated assets")
