"""
Deep Research Agent for Company Intelligence

Uses OpenAI's o3-deep-research and o4-mini-deep-research models to conduct
comprehensive research on companies, market trends, and lead qualification.

Key capabilities:
- Multi-source research (web + MCP + vector stores)
- Analyst-level reports with citations
- Company background and competitive analysis
- Market trends and industry insights
"""

import os
import json
import time
from typing import Dict, List, Any, Optional
from openai import OpenAI
from datetime import datetime


class DeepResearchAgent:
    """
    Agent for conducting deep research on companies and markets.
    
    Uses o3-deep-research or o4-mini-deep-research models with:
    - Web search for public information
    - MCP server for internal lead database
    - File search over vector stores (optional)
    - Code interpreter for analysis (optional)
    """
    
    def __init__(
        self,
        model: str = "o4-mini-deep-research",
        mcp_server_url: Optional[str] = None,
        vector_store_ids: Optional[List[str]] = None,
        timeout: int = 3600,
        api_key: Optional[str] = None
    ):
        """
        Initialize Deep Research Agent.
        
        Args:
            model: "o3-deep-research" or "o4-mini-deep-research"
            mcp_server_url: URL of your MCP server (for internal data)
            vector_store_ids: List of vector store IDs (for file search)
            timeout: Request timeout in seconds (default: 1 hour)
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
        """
        self.model = model
        self.mcp_server_url = mcp_server_url or "http://localhost:8001/sse/"
        self.vector_store_ids = vector_store_ids or []
        self.client = OpenAI(timeout=timeout, api_key=api_key)
        
        # Validate model
        valid_models = ["o3-deep-research", "o4-mini-deep-research"]
        if model not in valid_models:
            raise ValueError(f"Model must be one of: {valid_models}")
    
    def research_company(
        self,
        company_name: str,
        research_focus: Optional[str] = None,
        background: bool = True,
        use_internal_data: bool = True,
        use_code_interpreter: bool = False
    ) -> Dict[str, Any]:
        """
        Conduct deep research on a specific company.
        
        Args:
            company_name: Company to research
            research_focus: Specific focus (e.g., "financial health", "tech stack")
            background: Run in background mode (recommended)
            use_internal_data: Include MCP server for internal lead data
            use_code_interpreter: Enable code interpreter for analysis
        
        Returns:
            Research report with citations and metadata
        """
        # Build research prompt
        prompt = self._build_company_research_prompt(
            company_name,
            research_focus
        )
        
        # Build tools configuration
        tools = self._build_tools_config(
            use_internal_data=use_internal_data,
            use_code_interpreter=use_code_interpreter
        )
        
        # Execute research
        print(f"\n🔍 Starting deep research on: {company_name}")
        print(f"📊 Model: {self.model}")
        print(f"⏱️  Background mode: {background}")
        
        response = self.client.responses.create(
            model=self.model,
            input=prompt,
            background=background,
            tools=tools
        )
        
        # Extract results
        result = self._extract_research_results(response, company_name)
        
        print(f"✅ Research complete!")
        print(f"📄 Report length: {len(result['report'])} characters")
        print(f"🔗 Sources: {len(result['sources'])}")
        
        return result
    
    def research_market_trends(
        self,
        industry: str,
        time_period: str = "last 12 months",
        focus_areas: Optional[List[str]] = None,
        background: bool = True
    ) -> Dict[str, Any]:
        """
        Research market trends in a specific industry.
        
        Args:
            industry: Industry to research (e.g., "fintech", "healthtech")
            time_period: Time period to analyze
            focus_areas: Specific focus areas (e.g., ["hiring trends", "funding"])
            background: Run in background mode
        
        Returns:
            Market research report
        """
        prompt = self._build_market_trends_prompt(
            industry,
            time_period,
            focus_areas
        )
        
        tools = self._build_tools_config(
            use_internal_data=False,  # Public data only
            use_code_interpreter=True  # For trend analysis
        )
        
        print(f"\n🔍 Researching {industry} market trends...")
        
        response = self.client.responses.create(
            model=self.model,
            input=prompt,
            background=background,
            tools=tools
        )
        
        result = self._extract_research_results(response, f"{industry}_trends")
        
        print(f"✅ Market research complete!")
        
        return result
    
    def qualify_lead(
        self,
        company_name: str,
        lead_data: Dict[str, Any],
        qualification_criteria: Optional[List[str]] = None,
        background: bool = True
    ) -> Dict[str, Any]:
        """
        Deep research to qualify a lead.
        
        Combines internal data (from MCP) with public research to
        determine if this is a qualified prospect.
        
        Args:
            company_name: Company to qualify
            lead_data: Internal lead data (hiring velocity, pain points, etc.)
            qualification_criteria: Criteria for qualification
            background: Run in background mode
        
        Returns:
            Qualification report with recommendation
        """
        prompt = self._build_lead_qualification_prompt(
            company_name,
            lead_data,
            qualification_criteria
        )
        
        tools = self._build_tools_config(
            use_internal_data=True,  # Use MCP for historical data
            use_code_interpreter=True  # For scoring analysis
        )
        
        print(f"\n🔍 Deep qualifying lead: {company_name}")
        
        response = self.client.responses.create(
            model=self.model,
            input=prompt,
            background=background,
            tools=tools
        )
        
        result = self._extract_research_results(response, f"{company_name}_qualification")
        
        # Add qualification metadata
        result['lead_data'] = lead_data
        result['qualification_criteria'] = qualification_criteria
        
        print(f"✅ Lead qualification complete!")
        
        return result
    
    def competitive_analysis(
        self,
        target_company: str,
        competitors: List[str],
        comparison_dimensions: Optional[List[str]] = None,
        background: bool = True
    ) -> Dict[str, Any]:
        """
        Compare target company against competitors.
        
        Args:
            target_company: Company to analyze
            competitors: List of competitor names
            comparison_dimensions: What to compare (e.g., ["tech stack", "funding"])
            background: Run in background mode
        
        Returns:
            Competitive analysis report
        """
        prompt = self._build_competitive_analysis_prompt(
            target_company,
            competitors,
            comparison_dimensions
        )
        
        tools = self._build_tools_config(
            use_internal_data=True,
            use_code_interpreter=True
        )
        
        print(f"\n🔍 Competitive analysis: {target_company} vs {len(competitors)} competitors")
        
        response = self.client.responses.create(
            model=self.model,
            input=prompt,
            background=background,
            tools=tools
        )
        
        result = self._extract_research_results(response, f"{target_company}_competitive")
        
        print(f"✅ Competitive analysis complete!")
        
        return result
    
    def batch_research_leads(
        self,
        lead_ids: List[str],
        research_type: str = "qualification",
        webhook_url: Optional[str] = None
    ) -> List[str]:
        """
        Batch research multiple leads in background.
        
        Args:
            lead_ids: List of lead IDs to research
            research_type: Type of research ("qualification", "company_intel")
            webhook_url: Webhook to notify on completion
        
        Returns:
            List of response IDs for tracking
        """
        response_ids = []
        
        print(f"\n🔍 Starting batch research of {len(lead_ids)} leads...")
        
        for lead_id in lead_ids:
            # Get lead data from MCP
            prompt = f"Research lead {lead_id} for {research_type}"
            
            tools = self._build_tools_config(use_internal_data=True)
            
            response = self.client.responses.create(
                model=self.model,
                input=prompt,
                background=True,
                tools=tools,
                metadata={
                    "lead_id": lead_id,
                    "research_type": research_type,
                    "webhook_url": webhook_url
                }
            )
            
            response_ids.append(response.id)
            print(f"✓ Queued research for {lead_id}: {response.id}")
        
        print(f"✅ All {len(lead_ids)} research tasks queued!")
        if webhook_url:
            print(f"📡 Webhook will be called: {webhook_url}")
        
        return response_ids
    
    def _build_company_research_prompt(
        self,
        company_name: str,
        research_focus: Optional[str]
    ) -> str:
        """Build detailed research prompt for company analysis."""
        prompt = f"""
Research {company_name} in depth, providing an analyst-level report.

REQUIRED SECTIONS:
1. **Company Overview**
   - Business model and products/services
   - Founded date, headquarters, size
   - Leadership team and key executives
   
2. **Financial Health**
   - Revenue (if public)
   - Funding rounds and investors
   - Recent financial news or indicators
   
3. **Growth Signals**
   - Hiring velocity (job postings, team growth)
   - Market expansion and new products
   - Customer growth and testimonials
   
4. **Technology Stack**
   - Known technologies and platforms
   - Infrastructure and cloud providers
   - Engineering team signals
   
5. **Pain Points and Challenges**
   - Technical debt indicators
   - Scaling challenges
   - Migration or modernization needs
   
6. **Competitive Position**
   - Main competitors
   - Market differentiation
   - Industry trends affecting them

"""
        
        if research_focus:
            prompt += f"\nSPECIAL FOCUS: {research_focus}\n"
        
        prompt += """
REQUIREMENTS:
- Include specific figures, dates, and measurable outcomes
- Prioritize recent information (last 12 months)
- Include inline citations for all claims
- Use tables for structured data (funding rounds, tech stack, etc.)
- Flag any uncertain or conflicting information
- Provide URLs for all sources

FORMAT:
- Use headers (##) for main sections
- Use bullet points for lists
- Include a summary table at the top
- Add citations inline: [source name](url)
"""
        
        return prompt
    
    def _build_market_trends_prompt(
        self,
        industry: str,
        time_period: str,
        focus_areas: Optional[List[str]]
    ) -> str:
        """Build prompt for market trend research."""
        prompt = f"""
Research market trends in the {industry} industry over the {time_period}.

REQUIRED ANALYSIS:
1. **Market Size and Growth**
   - Current market size and projections
   - Growth rate and drivers
   
2. **Key Players**
   - Leading companies and market share
   - Recent M&A activity
   - Notable startups and funding
   
3. **Technology Trends**
   - Emerging technologies being adopted
   - Platform shifts and migrations
   - Infrastructure trends
   
4. **Hiring and Talent Trends**
   - Job posting volume trends
   - Most in-demand roles
   - Skills and tech stack shifts
   
5. **Challenges and Opportunities**
   - Common pain points across industry
   - Regulatory or market changes
   - Emerging opportunities
"""
        
        if focus_areas:
            prompt += f"\nPRIORITY FOCUS AREAS:\n"
            for area in focus_areas:
                prompt += f"- {area}\n"
        
        prompt += """
REQUIREMENTS:
- Include specific statistics and data points
- Show trends over time (use code interpreter if helpful)
- Include inline citations
- Create comparison tables where relevant
- Highlight actionable insights
"""
        
        return prompt
    
    def _build_lead_qualification_prompt(
        self,
        company_name: str,
        lead_data: Dict[str, Any],
        qualification_criteria: Optional[List[str]]
    ) -> str:
        """Build prompt for lead qualification research."""
        # Extract key data
        hiring_velocity = lead_data.get('job_count', 0)
        pain_points = lead_data.get('pain_points', [])
        score = lead_data.get('score', 0)
        
        prompt = f"""
Qualify {company_name} as a potential B2B prospect for software services.

INTERNAL DATA SUMMARY:
- Hiring Velocity: {hiring_velocity} job postings
- Current Score: {score}/100
- Known Pain Points: {', '.join(pain_points[:3]) if pain_points else 'Unknown'}

RESEARCH REQUIRED:
1. **Company Validation**
   - Verify company exists and is legitimate
   - Confirm size and growth stage
   - Validate hiring activity
   
2. **Budget and Authority**
   - Financial health and funding
   - Decision-maker identification
   - Budget signals (funding, revenue)
   
3. **Need Validation**
   - Confirm pain points from public sources
   - Identify additional technical challenges
   - Urgency indicators
   
4. **Fit Assessment**
   - Technology stack compatibility
   - Project scope indicators
   - Service opportunity areas
   
5. **Risk Factors**
   - Recent layoffs or downsizing
   - Financial distress signals
   - Competitive landscape issues
"""
        
        if qualification_criteria:
            prompt += f"\nQUALIFICATION CRITERIA:\n"
            for criterion in qualification_criteria:
                prompt += f"- {criterion}\n"
        
        prompt += """
DELIVERABLE:
Provide a clear QUALIFIED or NOT QUALIFIED recommendation with:
- Confidence level (High/Medium/Low)
- Key supporting evidence
- Recommended next steps
- Talking points for outreach
"""
        
        return prompt
    
    def _build_competitive_analysis_prompt(
        self,
        target_company: str,
        competitors: List[str],
        comparison_dimensions: Optional[List[str]]
    ) -> str:
        """Build prompt for competitive analysis."""
        prompt = f"""
Conduct competitive analysis of {target_company} against competitors: {', '.join(competitors)}.

COMPARISON DIMENSIONS:
"""
        
        if comparison_dimensions:
            for dim in comparison_dimensions:
                prompt += f"- {dim}\n"
        else:
            prompt += """
- Company size and funding
- Technology stack
- Product offerings
- Market positioning
- Customer base
- Hiring trends
"""
        
        prompt += """
DELIVERABLE:
1. **Comparison Table**
   Create a comprehensive table comparing all companies across dimensions
   
2. **Strengths and Weaknesses**
   For each company, identify 3 key strengths and 3 weaknesses
   
3. **Market Positioning**
   Where does each company sit in the market?
   
4. **Opportunity Analysis**
   For the target company, what opportunities exist based on competitor gaps?

REQUIREMENTS:
- Include specific data points and metrics
- Use inline citations
- Create structured tables
- Highlight key differentiators
"""
        
        return prompt
    
    def _build_tools_config(
        self,
        use_internal_data: bool = True,
        use_code_interpreter: bool = False
    ) -> List[Dict[str, Any]]:
        """Build tools configuration for research request."""
        tools = []
        
        # Always include web search
        tools.append({"type": "web_search_preview"})
        
        # Add MCP server if requested and available
        if use_internal_data and self.mcp_server_url:
            tools.append({
                "type": "mcp",
                "server_label": "lead_database",
                "server_url": self.mcp_server_url,
                "require_approval": "never"  # Required for deep research
            })
        
        # Add file search if vector stores available
        if self.vector_store_ids:
            tools.append({
                "type": "file_search",
                "vector_store_ids": self.vector_store_ids
            })
        
        # Add code interpreter if requested
        if use_code_interpreter:
            tools.append({
                "type": "code_interpreter",
                "container": {"type": "auto"}
            })
        
        return tools
    
    def _extract_research_results(
        self,
        response,
        research_subject: str
    ) -> Dict[str, Any]:
        """Extract and structure research results from API response."""
        # Extract the main report text
        report = response.output_text
        
        # Extract sources/citations
        sources = []
        annotations = []
        
        for item in response.output:
            # Extract message annotations (citations)
            if item.type == "message":
                for content in item.content:
                    if hasattr(content, 'annotations'):
                        for annotation in content.annotations:
                            sources.append({
                                "url": annotation.url,
                                "title": annotation.title,
                                "start_index": annotation.start_index,
                                "end_index": annotation.end_index
                            })
                            annotations.append(annotation)
        
        # Count tool calls by type
        tool_usage = {
            "web_search": 0,
            "mcp_call": 0,
            "code_interpreter": 0,
            "file_search": 0
        }
        
        for item in response.output:
            if item.type == "web_search_call":
                tool_usage["web_search"] += 1
            elif item.type == "mcp_call":
                tool_usage["mcp_call"] += 1
            elif item.type == "code_interpreter_call":
                tool_usage["code_interpreter"] += 1
            elif item.type == "file_search_call":
                tool_usage["file_search"] += 1
        
        return {
            "response_id": response.id,
            "subject": research_subject,
            "report": report,
            "sources": sources,
            "annotations": annotations,
            "tool_usage": tool_usage,
            "status": response.status,
            "created_at": datetime.now().isoformat(),
            "metadata": {
                "model": self.model,
                "source_count": len(sources),
                "report_length": len(report)
            }
        }
    
    def save_research_report(
        self,
        result: Dict[str, Any],
        output_dir: str = "output/research"
    ):
        """
        Save research report to file.
        
        Args:
            result: Research result from research methods
            output_dir: Directory to save reports
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename
        subject = result['subject'].replace(' ', '_').replace('/', '_')
        timestamp = int(time.time())
        filename = f"{output_dir}/{subject}_{timestamp}.json"
        
        # Save full result
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2)
        
        # Also save markdown report
        md_filename = filename.replace('.json', '.md')
        with open(md_filename, 'w') as f:
            f.write(f"# Research Report: {result['subject']}\n\n")
            f.write(f"**Generated:** {result['created_at']}\n")
            f.write(f"**Model:** {result['metadata']['model']}\n")
            f.write(f"**Sources:** {len(result['sources'])}\n\n")
            f.write("---\n\n")
            f.write(result['report'])
            f.write("\n\n---\n\n## Sources\n\n")
            for i, source in enumerate(result['sources'], 1):
                f.write(f"{i}. [{source['title']}]({source['url']})\n")
        
        print(f"✅ Report saved:")
        print(f"   JSON: {filename}")
        print(f"   Markdown: {md_filename}")


# Example usage
if __name__ == "__main__":
    import sys
    
    # Initialize agent
    agent = DeepResearchAgent(
        model="o4-mini-deep-research",  # Cheaper, faster
        mcp_server_url="http://localhost:8001/sse/"
    )
    
    print("="*70)
    print("DEEP RESEARCH AGENT - EXAMPLES")
    print("="*70)
    
    # Example 1: Company research
    print("\n1. Company Research Example")
    print("-"*70)
    result = agent.research_company(
        company_name="CloudTech Solutions",
        research_focus="Technical infrastructure and hiring needs",
        background=False  # Sync for demo
    )
    print(f"\nReport preview:")
    print(result['report'][:500] + "...")
    
    # Example 2: Lead qualification
    print("\n2. Lead Qualification Example")
    print("-"*70)
    lead_data = {
        "job_count": 15,
        "score": 92,
        "pain_points": ["cloud migration", "DevOps automation"],
        "tech_stack": ["Python", "AWS", "Kubernetes"]
    }
    result = agent.qualify_lead(
        company_name="FinanceAI Corp",
        lead_data=lead_data,
        qualification_criteria=[
            "Budget > $50K",
            "Tech stack compatible",
            "Active hiring"
        ],
        background=False
    )
    print(f"\nQualification preview:")
    print(result['report'][:500] + "...")
    
    print("\n" + "="*70)
    print("Examples complete! Check output/research/ for full reports")
    print("="*70)
