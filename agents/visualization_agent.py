"""
Visualization Agent using OpenAI's Image Generation and Code Interpreter.
Creates visual assets for presentations, reports, and dashboards.
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
import requests
from agents.client_agent import ClientAgent
from utils import get_logger

logger = get_logger(__name__)


class VisualizationAgent:
    """
    Agent for creating visualizations and graphics for sales presentations.
    Uses DALL-E for image generation and Code Interpreter for data visualizations.
    """
    
    def __init__(self, client_agent: Optional[ClientAgent] = None, output_dir: str = "output/visualizations"):
        """
        Initialize the Visualization Agent.
        
        Args:
            client_agent: ClientAgent instance for AI calls
            output_dir: Directory to save generated images
        """
        self.client = client_agent or ClientAgent()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"VisualizationAgent initialized (output_dir={output_dir})")
    
    def create_prospect_presentation(self, company_name: str, industry: str, job_count: int, 
                                    employee_count: int = None) -> Dict[str, Any]:
        """
        Create a complete visual package for a prospect presentation.
        
        Args:
            company_name: Name of the prospect company
            industry: Company's industry
            job_count: Number of jobs they've posted
            employee_count: Estimated employee count
            
        Returns:
            Dictionary with paths to all generated assets
        """
        logger.info(f"Creating presentation package for {company_name}")
        
        assets = {}
        
        # 1. Company logo concept
        logger.info("Generating logo concept...")
        logo_result = self.client.generate_company_logo_concept(company_name, industry)
        if 'url' in logo_result:
            logo_path = self._download_image(logo_result['url'], f"{company_name}_logo.png")
            assets['logo'] = logo_path
        
        # 2. Hiring trend visualization
        logger.info("Generating hiring trends chart...")
        trend_result = self.client.generate_hiring_trend_visualization(company_name, job_count)
        if 'url' in trend_result:
            trend_path = self._download_image(trend_result['url'], f"{company_name}_hiring_trends.png")
            assets['hiring_trends'] = trend_path
        
        # 3. If we have employee count, generate ROI visualization
        if employee_count:
            logger.info("Generating ROI projection...")
            roi_prompt = f"""Create a professional infographic showing ROI projection for {company_name}.

Style: Clean, modern business infographic
Colors: Blue and green gradient
Include:
- Company name: {company_name}
- Employee count: {employee_count:,}
- Key metrics: Reduce turnover 15-20%, Optimize staffing 5-10%
- Projected savings: ${employee_count * 50 * 12:,}/year
- ROI: 300-500%
- Payback: 3-6 months

Make it visually appealing for a sales presentation."""
            
            roi_result = self.client.generate_image(roi_prompt, size="1792x1024", quality="hd")
            if 'url' in roi_result:
                roi_path = self._download_image(roi_result['url'], f"{company_name}_roi.png")
                assets['roi_projection'] = roi_path
        
        logger.info(f"Created {len(assets)} visual assets for {company_name}")
        return {
            "company": company_name,
            "assets": assets,
            "output_dir": str(self.output_dir)
        }
    
    def visualize_hiring_patterns(self, job_postings: List[Dict[str, Any]], company_name: str) -> str:
        """
        Analyze and visualize hiring patterns using Code Interpreter.
        
        Args:
            job_postings: List of job posting data
            company_name: Name of the company
            
        Returns:
            Path to generated visualization
        """
        logger.info(f"Visualizing hiring patterns for {company_name} ({len(job_postings)} jobs)")
        
        # Analyze with Code Interpreter
        analysis = self.client.analyze_hiring_data_with_code(job_postings)
        
        if 'error' in analysis:
            logger.error(f"Analysis failed: {analysis['error']}")
            return None
        
        # Generate visualization based on analysis
        prompt = f"""Create a data visualization dashboard for {company_name}'s hiring patterns.

Based on this analysis:
{analysis['analysis'][:500]}

Create a professional dashboard showing:
- Hiring velocity timeline
- Geographic distribution map
- Role distribution pie chart
- Growth indicators

Style: Modern business analytics dashboard
Colors: Blue, green, and gray
Include data labels and legends"""
        
        viz_result = self.client.generate_image(prompt, size="1792x1024", quality="hd")
        
        if 'url' in viz_result:
            return self._download_image(viz_result['url'], f"{company_name}_hiring_dashboard.png")
        
        return None
    
    def create_roi_calculator_visual(self, company_size: int, avg_salary: float, company_name: str = "Prospect") -> str:
        """
        Generate a visual ROI calculator result.
        
        Args:
            company_size: Number of employees
            avg_salary: Average salary
            company_name: Company name
            
        Returns:
            Path to generated ROI visual
        """
        logger.info(f"Creating ROI calculator visual for {company_name}")
        
        # Calculate ROI with Code Interpreter
        roi_data = self.client.calculate_forecasta_roi(company_size, avg_salary)
        
        if 'error' in roi_data:
            logger.error(f"ROI calculation failed: {roi_data['error']}")
            return None
        
        # Generate visual representation
        prompt = f"""Create a professional ROI calculator results infographic for {company_name}.

Based on calculations:
- Company Size: {company_size:,} employees
- Average Salary: ${avg_salary:,.0f}

Show results from this analysis:
{roi_data['roi_analysis'][:600]}

Style: Professional business infographic
Layout: Vertical flow showing inputs → calculations → results
Colors: Corporate blue and green
Include: Dollar amounts, percentages, timeline graphics
Make it persuasive for sales presentations"""
        
        roi_visual = self.client.generate_image(prompt, size="1024x1792", quality="hd")
        
        if 'url' in roi_visual:
            return self._download_image(roi_visual['url'], f"{company_name}_roi_calculator.png")
        
        return None
    
    def _download_image(self, url: str, filename: str) -> str:
        """
        Download an image from URL and save locally.
        
        Args:
            url: Image URL
            filename: Filename to save as
            
        Returns:
            Path to saved image
        """
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            filepath = self.output_dir / filename
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded image: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to download image: {e}")
            return None
    
    def create_comparison_chart(self, company_a: str, jobs_a: int, company_b: str, jobs_b: int) -> str:
        """
        Create a comparison chart between two companies.
        
        Args:
            company_a: First company name
            jobs_a: First company job count
            company_b: Second company name  
            jobs_b: Second company job count
            
        Returns:
            Path to comparison chart
        """
        logger.info(f"Creating comparison: {company_a} vs {company_b}")
        
        prompt = f"""Create a professional business comparison chart.

Comparing:
- {company_a}: {jobs_a} job postings
- {company_b}: {jobs_b} job postings

Style: Side-by-side bar chart
Colors: Blue for {company_a}, Green for {company_b}
Include: Company names, job counts, percentage difference
Professional business presentation style"""
        
        chart_result = self.client.generate_image(prompt, size="1792x1024", quality="hd")
        
        if 'url' in chart_result:
            filename = f"comparison_{company_a}_vs_{company_b}.png".replace(" ", "_")
            return self._download_image(chart_result['url'], filename)
        
        return None
