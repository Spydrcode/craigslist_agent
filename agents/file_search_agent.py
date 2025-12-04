"""
File Search Agent using OpenAI's File Search capability.
Enables searching through previously analyzed leads and company knowledge base.
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
from agents.client_agent import ClientAgent
from utils import get_logger

logger = get_logger(__name__)


class FileSearchAgent:
    """
    Agent for searching through lead files using OpenAI's file search.
    Enables finding similar companies, past interactions, and insights from previous analyses.
    """
    
    def __init__(self, client_agent: Optional[ClientAgent] = None, leads_dir: str = "output/leads"):
        """
        Initialize the File Search Agent.
        
        Args:
            client_agent: ClientAgent instance for AI calls
            leads_dir: Directory containing lead JSON files
        """
        self.client = client_agent or ClientAgent()
        self.leads_dir = Path(leads_dir)
        self.leads_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"FileSearchAgent initialized (leads_dir={leads_dir})")
    
    def search_similar_companies(self, company_name: str, industry: str = None, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Find similar companies we've analyzed before.
        
        Args:
            company_name: Name of company to find similar matches for
            industry: Optional industry filter
            max_results: Maximum number of results to return
            
        Returns:
            List of similar company profiles from past analyses
        """
        logger.info(f"Searching for companies similar to: {company_name}")
        
        # Load all lead files
        lead_files = list(self.leads_dir.glob("lead_*.json"))
        logger.info(f"Found {len(lead_files)} lead files to search")
        
        if not lead_files:
            logger.warning("No lead files found to search")
            return []
        
        # Build search context from all leads
        leads_context = []
        for lead_file in lead_files[:100]:  # Limit to 100 most recent
            try:
                with open(lead_file, 'r') as f:
                    lead_data = json.load(f)
                    leads_context.append({
                        'company': lead_data.get('company', {}).get('name', 'Unknown'),
                        'industry': lead_data.get('company', {}).get('industry', ''),
                        'tier': lead_data.get('lead_scoring', {}).get('tier', ''),
                        'score': lead_data.get('lead_scoring', {}).get('final_score', 0),
                        'pain_points': lead_data.get('needs_analysis', {}).get('primary_pain_points', [])[:3],
                        'file': str(lead_file)
                    })
            except Exception as e:
                logger.error(f"Error reading {lead_file}: {e}")
        
        if not leads_context:
            return []
        
        # Use OpenAI to find similar companies
        try:
            # Build file search prompt
            context_text = "\n".join([
                f"- {lead['company']} ({lead['industry']}): {lead['tier']} - Score {lead['score']}/30"
                for lead in leads_context
            ])
            
            messages = [
                {
                    "role": "system",
                    "content": "You are a sales intelligence assistant. Find similar companies based on industry, size, and pain points."
                },
                {
                    "role": "user",
                    "content": f"""From this list of previously analyzed companies, find the {max_results} most similar to: {company_name} ({industry or 'unknown industry'})

Previous Companies:
{context_text}

Return ONLY the company names, one per line, in order of similarity."""
                }
            ]
            
            response = self.client._call_api(
                messages=messages,
                temperature=0.3,
                max_tokens=500
            )
            
            # Parse response and match to full lead data
            similar_names = [name.strip() for name in response.strip().split('\n') if name.strip()]
            
            similar_leads = []
            for name in similar_names[:max_results]:
                # Find matching lead
                for lead in leads_context:
                    if name.lower() in lead['company'].lower() or lead['company'].lower() in name.lower():
                        similar_leads.append(lead)
                        break
            
            logger.info(f"Found {len(similar_leads)} similar companies")
            return similar_leads
            
        except Exception as e:
            logger.error(f"Similar company search failed: {e}")
            return []
    
    def search_by_pain_point(self, pain_point: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Find companies with specific pain points.
        
        Args:
            pain_point: Pain point to search for (e.g., "seasonal hiring", "turnover")
            max_results: Maximum number of results
            
        Returns:
            List of companies with matching pain points
        """
        logger.info(f"Searching for companies with pain point: {pain_point}")
        
        lead_files = list(self.leads_dir.glob("lead_*.json"))
        matching_companies = []
        
        for lead_file in lead_files:
            try:
                with open(lead_file, 'r') as f:
                    lead_data = json.load(f)
                    
                    # Check if pain point mentioned
                    pain_points = lead_data.get('needs_analysis', {}).get('primary_pain_points', [])
                    pain_points_text = ' '.join(pain_points).lower()
                    
                    if pain_point.lower() in pain_points_text:
                        matching_companies.append({
                            'company': lead_data.get('company', {}).get('name', 'Unknown'),
                            'tier': lead_data.get('lead_scoring', {}).get('tier', ''),
                            'pain_points': pain_points,
                            'file': str(lead_file)
                        })
                        
                        if len(matching_companies) >= max_results:
                            break
                            
            except Exception as e:
                logger.error(f"Error searching {lead_file}: {e}")
        
        logger.info(f"Found {len(matching_companies)} companies with matching pain points")
        return matching_companies
    
    def get_company_history(self, company_name: str) -> Optional[Dict[str, Any]]:
        """
        Get full history of interactions with a specific company.
        
        Args:
            company_name: Name of company to look up
            
        Returns:
            Complete lead data if found, None otherwise
        """
        logger.info(f"Looking up history for: {company_name}")
        
        lead_files = list(self.leads_dir.glob("lead_*.json"))
        
        for lead_file in lead_files:
            try:
                with open(lead_file, 'r') as f:
                    lead_data = json.load(f)
                    
                    stored_name = lead_data.get('company', {}).get('name', '').lower()
                    if company_name.lower() in stored_name or stored_name in company_name.lower():
                        logger.info(f"Found history for {company_name}")
                        return lead_data
                        
            except Exception as e:
                logger.error(f"Error reading {lead_file}: {e}")
        
        logger.info(f"No history found for {company_name}")
        return None
