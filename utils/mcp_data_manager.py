"""
MCP Server Integration Helper

This module provides utilities to save lead and job data in the format
expected by the MCP server for ChatGPT integration.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


class MCPDataManager:
    """Manages data persistence for MCP server access."""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize MCP data manager.
        
        Args:
            data_dir: Root directory for data storage
        """
        self.data_dir = Path(data_dir)
        self.leads_dir = self.data_dir / "leads"
        self.jobs_dir = self.data_dir / "jobs"
        
        # Create directories if they don't exist
        self.leads_dir.mkdir(parents=True, exist_ok=True)
        self.jobs_dir.mkdir(parents=True, exist_ok=True)
    
    def save_lead(self, lead_data: Dict[str, Any]) -> str:
        """
        Save lead analysis for MCP server access.
        
        Args:
            lead_data: Dictionary containing lead analysis
                Required fields: lead_id
                Recommended fields: company_name, lead_score, priority,
                                  job_count, pain_points, opportunities,
                                  growth_stage, tech_stack
        
        Returns:
            Path to saved lead file
        """
        lead_id = lead_data.get('lead_id')
        if not lead_id:
            raise ValueError("lead_id is required in lead_data")
        
        # Add timestamp if not present
        if 'created_at' not in lead_data:
            lead_data['created_at'] = datetime.now().isoformat()
        
        lead_file = self.leads_dir / f"{lead_id}.json"
        
        with open(lead_file, 'w', encoding='utf-8') as f:
            json.dump(lead_data, f, indent=2, ensure_ascii=False)
        
        return str(lead_file)
    
    def save_job(self, job_data: Dict[str, Any]) -> str:
        """
        Save job posting for MCP server access.
        
        Args:
            job_data: Dictionary containing job posting details
                Required fields: job_id
                Recommended fields: title, company, location, description,
                                  requirements, url, posted_date
        
        Returns:
            Path to saved job file
        """
        job_id = job_data.get('job_id')
        if not job_id:
            raise ValueError("job_id is required in job_data")
        
        # Add timestamp if not present
        if 'scraped_at' not in job_data:
            job_data['scraped_at'] = datetime.now().isoformat()
        
        job_file = self.jobs_dir / f"{job_id}.json"
        
        with open(job_file, 'w', encoding='utf-8') as f:
            json.dump(job_data, f, indent=2, ensure_ascii=False)
        
        return str(job_file)
    
    def save_leads_bulk(self, leads: list) -> int:
        """
        Save multiple leads in bulk.
        
        Args:
            leads: List of lead dictionaries
        
        Returns:
            Number of leads saved
        """
        count = 0
        for lead in leads:
            try:
                self.save_lead(lead)
                count += 1
            except Exception as e:
                print(f"Error saving lead {lead.get('lead_id', 'unknown')}: {e}")
        
        return count
    
    def save_jobs_bulk(self, jobs: list) -> int:
        """
        Save multiple jobs in bulk.
        
        Args:
            jobs: List of job dictionaries
        
        Returns:
            Number of jobs saved
        """
        count = 0
        for job in jobs:
            try:
                self.save_job(job)
                count += 1
            except Exception as e:
                print(f"Error saving job {job.get('job_id', 'unknown')}: {e}")
        
        return count
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about stored data.
        
        Returns:
            Dictionary with counts and info
        """
        lead_files = list(self.leads_dir.glob("*.json"))
        job_files = list(self.jobs_dir.glob("*.json"))
        
        return {
            'leads_count': len(lead_files),
            'jobs_count': len(job_files),
            'leads_dir': str(self.leads_dir.absolute()),
            'jobs_dir': str(self.jobs_dir.absolute()),
            'total_size_mb': sum(f.stat().st_size for f in lead_files + job_files) / 1024 / 1024
        }


# Example usage
if __name__ == "__main__":
    # Initialize manager
    mcp = MCPDataManager()
    
    # Example lead data
    lead_example = {
        'lead_id': 'lead-example-001',
        'company_name': 'Example TechCorp',
        'lead_score': 85.0,
        'priority': 'HOT',
        'job_count': 12,
        'pain_points': [
            'Legacy system migration',
            'Scaling infrastructure',
            'DevOps automation'
        ],
        'opportunities': [
            {
                'service': 'Cloud Migration',
                'estimated_value': '$75K-150K',
                'confidence': 'high'
            }
        ],
        'growth_stage': 'SCALING',
        'tech_stack': ['React', 'AWS', 'Kubernetes'],
        'source_url': 'https://craigslist.org/example'
    }
    
    # Example job data
    job_example = {
        'job_id': 'job-example-001',
        'title': 'Senior Software Engineer',
        'company': 'Example TechCorp',
        'location': 'San Francisco, CA',
        'description': 'We are looking for an experienced software engineer...',
        'requirements': [
            '5+ years Python',
            'React experience',
            'AWS cloud'
        ],
        'url': 'https://craigslist.org/job/example',
        'posted_date': '2024-01-15'
    }
    
    # Save examples
    lead_path = mcp.save_lead(lead_example)
    job_path = mcp.save_job(job_example)
    
    print(f"Saved lead to: {lead_path}")
    print(f"Saved job to: {job_path}")
    
    # Get stats
    stats = mcp.get_stats()
    print(f"\nMCP Data Stats:")
    print(f"  Leads: {stats['leads_count']}")
    print(f"  Jobs: {stats['jobs_count']}")
    print(f"  Total size: {stats['total_size_mb']:.2f} MB")
