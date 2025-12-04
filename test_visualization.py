"""
Test script for OpenAI Visualization capabilities.
Demonstrates image generation and code interpreter for creating sales assets.
"""
from agents import VisualizationAgent, ClientAgent
from utils import get_logger

logger = get_logger(__name__)


def test_prospect_presentation():
    """Test creating a complete prospect presentation package."""
    print("\n" + "="*80)
    print("TEST: Creating Prospect Presentation Package")
    print("="*80)
    
    viz_agent = VisualizationAgent()
    
    # Create presentation for a tech company
    result = viz_agent.create_prospect_presentation(
        company_name="TechCorp Solutions",
        industry="Software Development",
        job_count=45,
        employee_count=500
    )
    
    print(f"\n✅ Created presentation for {result['company']}")
    print(f"📁 Output directory: {result['output_dir']}")
    print(f"🎨 Generated assets: {len(result['assets'])}")
    
    for asset_type, path in result['assets'].items():
        print(f"   - {asset_type}: {path}")
    
    return result


def test_hiring_pattern_visualization():
    """Test analyzing and visualizing hiring patterns."""
    print("\n" + "="*80)
    print("TEST: Hiring Pattern Visualization with Code Interpreter")
    print("="*80)
    
    viz_agent = VisualizationAgent()
    
    # Sample job posting data
    job_postings = [
        {
            "title": "Senior Software Engineer",
            "location": "San Francisco, CA",
            "posted_date": "2024-01-15",
            "company": "TechCorp"
        },
        {
            "title": "DevOps Engineer",
            "location": "San Francisco, CA",
            "posted_date": "2024-01-18",
            "company": "TechCorp"
        },
        {
            "title": "Product Manager",
            "location": "New York, NY",
            "posted_date": "2024-01-20",
            "company": "TechCorp"
        },
        {
            "title": "Data Scientist",
            "location": "San Francisco, CA",
            "posted_date": "2024-01-22",
            "company": "TechCorp"
        },
        {
            "title": "Frontend Developer",
            "location": "Remote",
            "posted_date": "2024-01-25",
            "company": "TechCorp"
        }
    ]
    
    dashboard_path = viz_agent.visualize_hiring_patterns(job_postings, "TechCorp Solutions")
    
    if dashboard_path:
        print(f"\n✅ Created hiring dashboard: {dashboard_path}")
    else:
        print("\n❌ Failed to create dashboard")
    
    return dashboard_path


def test_roi_calculator_visual():
    """Test creating visual ROI calculator."""
    print("\n" + "="*80)
    print("TEST: ROI Calculator Visualization")
    print("="*80)
    
    viz_agent = VisualizationAgent()
    
    # Calculate and visualize ROI for a mid-size company
    roi_path = viz_agent.create_roi_calculator_visual(
        company_size=250,
        avg_salary=75000,
        company_name="MidSize Inc"
    )
    
    if roi_path:
        print(f"\n✅ Created ROI calculator visual: {roi_path}")
    else:
        print("\n❌ Failed to create ROI visual")
    
    return roi_path


def test_company_comparison():
    """Test creating comparison charts."""
    print("\n" + "="*80)
    print("TEST: Company Comparison Chart")
    print("="*80)
    
    viz_agent = VisualizationAgent()
    
    # Compare two companies
    comparison_path = viz_agent.create_comparison_chart(
        company_a="TechCorp Solutions",
        jobs_a=45,
        company_b="StartupXYZ",
        jobs_b=12
    )
    
    if comparison_path:
        print(f"\n✅ Created comparison chart: {comparison_path}")
    else:
        print("\n❌ Failed to create comparison")
    
    return comparison_path


def test_individual_image_generation():
    """Test individual image generation capabilities."""
    print("\n" + "="*80)
    print("TEST: Individual Image Generation (DALL-E 3)")
    print("="*80)
    
    client = ClientAgent()
    
    # Test logo concept
    print("\n1. Generating company logo concept...")
    logo_result = client.generate_company_logo_concept(
        company_name="InnovateTech",
        industry="Artificial Intelligence"
    )
    print(f"   Logo URL: {logo_result.get('url', 'N/A')[:60]}...")
    
    # Test hiring trends
    print("\n2. Generating hiring trends visualization...")
    trends_result = client.generate_hiring_trend_visualization(
        company_name="GrowthCorp",
        job_count=78
    )
    print(f"   Trends URL: {trends_result.get('url', 'N/A')[:60]}...")
    
    # Test custom visualization
    print("\n3. Generating custom infographic...")
    custom_result = client.generate_image(
        prompt="""Create a professional sales funnel infographic.

Style: Modern business presentation
Colors: Blue gradient
Stages:
1. Lead Discovery (1000 companies)
2. Qualification (300 companies)  
3. Engagement (100 companies)
4. Proposal (30 companies)
5. Close (10 clients)

Include percentages and conversion rates""",
        size="1024x1792",
        quality="hd"
    )
    print(f"   Custom URL: {custom_result.get('url', 'N/A')[:60]}...")
    
    return {
        "logo": logo_result,
        "trends": trends_result,
        "custom": custom_result
    }


def test_code_interpreter_analytics():
    """Test code interpreter analytics capabilities."""
    print("\n" + "="*80)
    print("TEST: Code Interpreter Analytics")
    print("="*80)
    
    client = ClientAgent()
    
    # Sample job data for analysis
    job_data = [
        {"title": "Engineer", "location": "SF", "posted_date": "2024-01-01"},
        {"title": "Manager", "location": "NY", "posted_date": "2024-01-05"},
        {"title": "Designer", "location": "SF", "posted_date": "2024-01-10"},
        {"title": "Engineer", "location": "SF", "posted_date": "2024-01-15"},
        {"title": "Analyst", "location": "Remote", "posted_date": "2024-01-20"},
    ]
    
    print("\n1. Analyzing hiring data with Python...")
    analysis = client.analyze_hiring_data_with_code(job_data)
    if 'analysis' in analysis:
        print(f"   Analysis preview: {analysis['analysis'][:200]}...")
    else:
        print(f"   ❌ Error: {analysis.get('error', 'Unknown')}")
    
    print("\n2. Calculating ROI with Python...")
    roi = client.calculate_forecasta_roi(
        company_size=200,
        avg_salary=80000,
        turnover_rate=0.18
    )
    if 'roi_analysis' in roi:
        print(f"   ROI preview: {roi['roi_analysis'][:200]}...")
    else:
        print(f"   ❌ Error: {roi.get('error', 'Unknown')}")
    
    return {
        "hiring_analysis": analysis,
        "roi_calculation": roi
    }


def run_all_visualization_tests():
    """Run all visualization tests."""
    print("\n" + "🎨"*40)
    print("OPENAI VISUALIZATION AGENT TEST SUITE")
    print("🎨"*40)
    
    results = {}
    
    try:
        # Test 1: Full presentation package
        results['presentation'] = test_prospect_presentation()
        
        # Test 2: Hiring pattern dashboard
        results['hiring_patterns'] = test_hiring_pattern_visualization()
        
        # Test 3: ROI calculator
        results['roi_visual'] = test_roi_calculator_visual()
        
        # Test 4: Company comparison
        results['comparison'] = test_company_comparison()
        
        # Test 5: Individual image generation
        results['images'] = test_individual_image_generation()
        
        # Test 6: Code interpreter analytics
        results['analytics'] = test_code_interpreter_analytics()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS COMPLETED")
        print("="*80)
        print(f"\nGenerated assets saved to: output/visualizations/")
        print("\nVisual capabilities ready for:")
        print("  • Sales presentations")
        print("  • Prospect analysis reports")
        print("  • ROI calculators")
        print("  • Hiring trend dashboards")
        print("  • Company comparisons")
        print("  • Custom infographics")
        
    except Exception as e:
        logger.error(f"Test suite error: {e}", exc_info=True)
        print(f"\n❌ Test suite failed: {e}")
    
    return results


if __name__ == "__main__":
    run_all_visualization_tests()
