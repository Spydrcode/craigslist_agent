"""
Craigslist Prospecting MCP Server

This MCP server provides search and retrieval capabilities for analyzed leads
and job postings. Integrates with ChatGPT connectors and deep research.

Features:
- Search historical lead analysis
- Fetch complete lead profiles
- Query by company, pain points, tech stack
- Access job posting database
"""

import logging
import os
import json
from typing import Dict, List, Any
from pathlib import Path
from datetime import datetime

from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DATA_DIR = Path("data")
LEADS_DIR = DATA_DIR / "leads"
JOBS_DIR = DATA_DIR / "jobs"

# Ensure directories exist
LEADS_DIR.mkdir(parents=True, exist_ok=True)
JOBS_DIR.mkdir(parents=True, exist_ok=True)

server_instructions = """
This MCP server provides access to Craigslist prospecting data including:
- Analyzed lead profiles with qualification scores
- Job posting details and pain points
- Company growth signals and hiring velocity
- Service opportunities and ROI estimates

Use the search tool to find relevant leads and companies, then use fetch
to retrieve complete analysis with citations.
"""


def create_server():
    """Create and configure the MCP server with search and fetch tools."""

    mcp = FastMCP(name="Craigslist Prospecting MCP Server",
                  instructions=server_instructions)

    @mcp.tool()
    async def search(query: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for leads and job postings in the prospecting database.

        This tool searches through analyzed leads, companies, and job postings
        to find semantically relevant matches. Returns a list of search results
        with basic information. Use the fetch tool to get complete details.

        Args:
            query: Search query string. Can search by:
                - Company name
                - Pain points (e.g., "legacy system", "scaling issues")
                - Tech stack (e.g., "React", "AWS", "Kubernetes")
                - Job titles or requirements
                - Growth signals (e.g., "funded", "series A")

        Returns:
            Dictionary with 'results' key containing list of matching leads/jobs.
            Each result includes id, title, text snippet, and URL.
        """
        if not query or not query.strip():
            return {"results": []}

        logger.info(f"Searching prospecting data for query: '{query}'")

        results = []
        query_lower = query.lower()

        # Search lead files
        if LEADS_DIR.exists():
            for lead_file in LEADS_DIR.glob("*.json"):
                try:
                    with open(lead_file, 'r', encoding='utf-8') as f:
                        lead = json.load(f)

                    # Check if query matches lead data
                    searchable_text = json.dumps(lead).lower()
                    if query_lower in searchable_text:
                        # Create result entry
                        company_name = lead.get('company_name', 'Unknown Company')
                        lead_score = lead.get('lead_score', 0)
                        priority = lead.get('priority', 'UNKNOWN')
                        job_count = lead.get('job_count', 0)

                        # Extract snippet showing why it matched
                        snippet = f"Score: {lead_score}, Priority: {priority}, Jobs: {job_count}"

                        # Add pain points if available
                        pain_points = lead.get('pain_points', [])
                        if pain_points:
                            snippet += f"\nPain Points: {', '.join(pain_points[:3])}"

                        results.append({
                            "id": lead.get('lead_id', lead_file.stem),
                            "title": f"{company_name} - {priority} Lead",
                            "text": snippet,
                            "url": f"file:///{lead_file.absolute()}"
                        })

                except Exception as e:
                    logger.error(f"Error reading lead file {lead_file}: {e}")

        # Search job files
        if JOBS_DIR.exists():
            for job_file in JOBS_DIR.glob("*.json"):
                try:
                    with open(job_file, 'r', encoding='utf-8') as f:
                        job = json.load(f)

                    searchable_text = json.dumps(job).lower()
                    if query_lower in searchable_text:
                        title = job.get('title', 'Unknown Job')
                        company = job.get('company', 'Unknown Company')
                        location = job.get('location', 'Unknown')

                        snippet = f"{company} - {location}"
                        if 'description' in job:
                            desc = job['description'][:200]
                            snippet += f"\n{desc}..."

                        results.append({
                            "id": job.get('job_id', job_file.stem),
                            "title": f"{title} at {company}",
                            "text": snippet,
                            "url": job.get('url', f"file:///{job_file.absolute()}")
                        })

                except Exception as e:
                    logger.error(f"Error reading job file {job_file}: {e}")

        # Sort by relevance (simple: by score if available)
        results.sort(
            key=lambda x: float(x.get('text', '').split('Score: ')[1].split(',')[0])
            if 'Score: ' in x.get('text', '') else 0,
            reverse=True
        )

        # Limit results
        results = results[:20]

        logger.info(f"Search returned {len(results)} results")
        return {"results": results}

    @mcp.tool()
    async def fetch(id: str) -> Dict[str, Any]:
        """
        Retrieve complete lead or job posting details by ID.

        This tool fetches the full analysis for a lead or complete job posting
        details. Use this after finding relevant results with the search tool
        to get complete information for analysis and citations.

        Args:
            id: Lead ID or Job ID from search results

        Returns:
            Complete document with:
            - id: Unique identifier
            - title: Lead/job title
            - text: Full analysis or job description
            - url: Source URL or file path
            - metadata: Additional structured data

        Raises:
            ValueError: If the specified ID is not found
        """
        if not id:
            raise ValueError("Document ID is required")

        logger.info(f"Fetching content for ID: {id}")

        # Try to find lead file
        lead_file = LEADS_DIR / f"{id}.json"
        if lead_file.exists():
            with open(lead_file, 'r', encoding='utf-8') as f:
                lead = json.load(f)

            company_name = lead.get('company_name', 'Unknown Company')
            lead_score = lead.get('lead_score', 0)
            priority = lead.get('priority', 'UNKNOWN')

            # Build comprehensive text content
            text_parts = [
                f"Company: {company_name}",
                f"Lead Score: {lead_score}/100",
                f"Priority: {priority}",
                f"Job Count: {lead.get('job_count', 0)}",
                ""
            ]

            # Add pain points
            pain_points = lead.get('pain_points', [])
            if pain_points:
                text_parts.append("Pain Points:")
                for pp in pain_points:
                    text_parts.append(f"  - {pp}")
                text_parts.append("")

            # Add opportunities
            opportunities = lead.get('opportunities', [])
            if opportunities:
                text_parts.append("Service Opportunities:")
                for opp in opportunities:
                    service = opp.get('service', 'Unknown')
                    value = opp.get('estimated_value', 'Unknown')
                    text_parts.append(f"  - {service}: {value}")
                text_parts.append("")

            # Add growth stage
            growth_stage = lead.get('growth_stage', 'Unknown')
            text_parts.append(f"Growth Stage: {growth_stage}")

            # Add tech stack
            tech_stack = lead.get('tech_stack', [])
            if tech_stack:
                text_parts.append(f"Tech Stack: {', '.join(tech_stack)}")

            text_content = "\n".join(text_parts)

            return {
                "id": id,
                "title": f"{company_name} - Lead Analysis",
                "text": text_content,
                "url": lead.get('source_url', f"file:///{lead_file.absolute()}"),
                "metadata": {
                    "lead_score": lead_score,
                    "priority": priority,
                    "job_count": lead.get('job_count', 0),
                    "growth_stage": growth_stage,
                    "analyzed_date": lead.get('created_at', 'Unknown')
                }
            }

        # Try to find job file
        job_file = JOBS_DIR / f"{id}.json"
        if job_file.exists():
            with open(job_file, 'r', encoding='utf-8') as f:
                job = json.load(f)

            title = job.get('title', 'Unknown Job')
            company = job.get('company', 'Unknown Company')

            text_parts = [
                f"Title: {title}",
                f"Company: {company}",
                f"Location: {job.get('location', 'Unknown')}",
                f"Posted: {job.get('posted_date', 'Unknown')}",
                "",
                "Description:",
                job.get('description', 'No description available'),
                ""
            ]

            # Add requirements if available
            requirements = job.get('requirements', [])
            if requirements:
                text_parts.append("Requirements:")
                for req in requirements:
                    text_parts.append(f"  - {req}")

            text_content = "\n".join(text_parts)

            return {
                "id": id,
                "title": f"{title} at {company}",
                "text": text_content,
                "url": job.get('url', f"file:///{job_file.absolute()}"),
                "metadata": {
                    "company": company,
                    "location": job.get('location', 'Unknown'),
                    "posted_date": job.get('posted_date', 'Unknown'),
                    "scraped_date": job.get('scraped_at', 'Unknown')
                }
            }

        # Not found
        raise ValueError(f"No lead or job found with ID: {id}")

    @mcp.tool()
    async def get_top_leads(limit: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get the top-scoring leads from the database.

        Args:
            limit: Maximum number of leads to return (default: 10, max: 50)

        Returns:
            Dictionary with 'results' key containing top leads
        """
        limit = min(max(1, limit), 50)  # Clamp between 1 and 50

        logger.info(f"Fetching top {limit} leads")

        leads = []

        if LEADS_DIR.exists():
            for lead_file in LEADS_DIR.glob("*.json"):
                try:
                    with open(lead_file, 'r', encoding='utf-8') as f:
                        lead = json.load(f)
                        leads.append(lead)
                except Exception as e:
                    logger.error(f"Error reading lead file {lead_file}: {e}")

        # Sort by score
        leads.sort(key=lambda x: x.get('lead_score', 0), reverse=True)

        # Take top N
        top_leads = leads[:limit]

        results = []
        for lead in top_leads:
            company_name = lead.get('company_name', 'Unknown Company')
            lead_score = lead.get('lead_score', 0)
            priority = lead.get('priority', 'UNKNOWN')

            results.append({
                "id": lead.get('lead_id', 'unknown'),
                "title": f"{company_name} - {priority} ({lead_score})",
                "text": f"Score: {lead_score}, Jobs: {lead.get('job_count', 0)}",
                "url": lead.get('source_url', 'unknown')
            })

        logger.info(f"Returning {len(results)} top leads")
        return {"results": results}

    return mcp


def main():
    """Main function to start the MCP server."""
    logger.info("Starting Craigslist Prospecting MCP Server")
    logger.info(f"Data directory: {DATA_DIR.absolute()}")
    logger.info(f"Leads directory: {LEADS_DIR.absolute()}")
    logger.info(f"Jobs directory: {JOBS_DIR.absolute()}")

    # Create the MCP server
    server = create_server()

    # Configure and start the server
    logger.info("Starting MCP server on 0.0.0.0:8001")
    logger.info("Server will be accessible via SSE transport")
    logger.info("Server URL: http://localhost:8001/sse/")

    try:
        # Use FastMCP's built-in run method with SSE transport
        server.run(transport="sse", host="0.0.0.0", port=8001)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    main()
