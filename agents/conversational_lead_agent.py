"""
Conversational Lead Analysis Agent using OpenAI Conversation State APIs.
Enables multi-turn analysis workflows with persistent context.
"""
from typing import Dict, Any, List, Optional
from agents.client_agent import ClientAgent
from utils import get_logger

logger = get_logger(__name__)


class ConversationalLeadAgent:
    """
    Agent for multi-turn lead analysis using OpenAI Conversation State APIs.
    
    Use Cases:
    - Deep dive analysis across multiple research phases
    - Iterative refinement of company profiles
    - Multi-step qualification workflows
    - Contextual follow-up questions
    """
    
    def __init__(self, client_agent: Optional[ClientAgent] = None, create_conversation: bool = False):
        """
        Initialize Conversational Lead Agent.
        
        Args:
            client_agent: ClientAgent instance (creates new if None)
            create_conversation: Automatically create a new conversation
        """
        self.client = client_agent or ClientAgent()
        
        if create_conversation:
            self.conversation_id = self.client.create_conversation()
        else:
            self.conversation_id = self.client.conversation_id
        
        logger.info(f"ConversationalLeadAgent initialized (conversation={self.conversation_id})")
    
    def start_company_analysis(self, company_name: str, initial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start a multi-turn company analysis conversation.
        
        Args:
            company_name: Company name
            initial_data: Initial data (job postings, website, etc.)
        
        Returns:
            Initial analysis with conversation context
        """
        logger.info(f"Starting conversational analysis for {company_name}")
        
        prompt = f"""You are analyzing {company_name} as a potential sales lead for Forecasta, 
a workforce analytics platform that helps companies optimize hiring and retention.

Initial Data:
- Company: {company_name}
- Job Postings: {initial_data.get('job_count', 0)} postings
- Industry: {initial_data.get('industry', 'Unknown')}
- Size: {initial_data.get('company_size', 'Unknown')} employees

Analyze this company and provide:
1. Initial qualification (TIER 1-5)
2. Key pain points identified
3. Follow-up questions we should research
4. Next steps for deeper analysis

Format as JSON."""
        
        messages = [
            {"role": "system", "content": "You are an expert sales analyst specializing in workforce analytics."},
            {"role": "user", "content": prompt}
        ]
        
        response = self.client._call_api(
            messages,
            temperature=0.3,
            max_tokens=1000,
            response_format={"type": "json_object"},
            store=True,
            use_conversation=True
        )
        
        import json
        analysis = json.loads(response)
        
        logger.info(f"Initial analysis complete. Response ID: {self.client.previous_response_id}")
        
        return {
            'company': company_name,
            'analysis': analysis,
            'conversation_id': self.conversation_id,
            'response_id': self.client.previous_response_id
        }
    
    def research_pain_point(self, pain_point: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Deep dive into a specific pain point using conversation context.
        
        Args:
            pain_point: Pain point to research
            context: Additional context (optional)
        
        Returns:
            Detailed pain point analysis
        """
        logger.info(f"Researching pain point: {pain_point}")
        
        prompt = f"""Based on our previous conversation about this company, 
let's deep dive into this pain point: {pain_point}

{f'Additional context: {context}' if context else ''}

Analyze:
1. How serious is this pain point? (1-10 severity)
2. Is Forecasta a good fit to solve this?
3. What specific features would help?
4. ROI estimate for solving this problem
5. Recommended talking points for sales pitch

Format as JSON."""
        
        messages = [{"role": "user", "content": prompt}]
        
        # This uses previous_response_id automatically for context
        response = self.client._call_api(
            messages,
            temperature=0.3,
            max_tokens=800,
            response_format={"type": "json_object"},
            store=True,
            use_conversation=True
        )
        
        import json
        return json.loads(response)
    
    def calculate_roi_in_context(self, company_size: int, avg_salary: float) -> Dict[str, Any]:
        """
        Calculate ROI with full conversation context about the company.
        
        Args:
            company_size: Number of employees
            avg_salary: Average employee salary
        
        Returns:
            Contextualized ROI calculation
        """
        logger.info("Calculating ROI with conversation context")
        
        prompt = f"""Based on everything we've discussed about this company, 
calculate a realistic ROI projection for Forecasta:

Company Size: {company_size} employees
Average Salary: ${avg_salary:,.0f}

Consider:
- Pain points identified earlier
- Industry benchmarks
- Growth signals
- Specific challenges

Provide:
1. Annual savings estimate
2. Implementation cost
3. ROI percentage
4. Payback period
5. Confidence level (based on our analysis)

Format as JSON with detailed reasoning."""
        
        messages = [{"role": "user", "content": prompt}]
        
        response = self.client._call_api(
            messages,
            temperature=0.2,
            max_tokens=1000,
            response_format={"type": "json_object"},
            store=True,
            use_conversation=True
        )
        
        import json
        return json.loads(response)
    
    def generate_outreach_email(self, contact_name: Optional[str] = None) -> str:
        """
        Generate personalized outreach email using full conversation context.
        
        Args:
            contact_name: Contact person's name (optional)
        
        Returns:
            Personalized email text
        """
        logger.info("Generating contextual outreach email")
        
        prompt = f"""Based on our entire analysis of this company, write a highly personalized 
cold outreach email for Forecasta.

{f'Recipient: {contact_name}' if contact_name else 'Use a generic greeting'}

The email should:
- Reference specific pain points we identified
- Mention their industry/growth signals
- Include ROI estimate from our calculation
- Feel personal, not templated
- Be concise (under 200 words)

Write the email (not JSON)."""
        
        messages = [{"role": "user", "content": prompt}]
        
        response = self.client._call_api(
            messages,
            temperature=0.7,  # Higher for creative writing
            max_tokens=500,
            store=True,
            use_conversation=True
        )
        
        return response
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the entire conversation and analysis.
        
        Returns:
            Conversation summary with key insights
        """
        logger.info("Generating conversation summary")
        
        prompt = """Summarize our entire conversation about this lead:

1. Company overview
2. Key findings
3. Qualification tier
4. Pain points identified
5. ROI projection
6. Recommended next steps

Format as JSON."""
        
        messages = [{"role": "user", "content": prompt}]
        
        response = self.client._call_api(
            messages,
            temperature=0.3,
            max_tokens=800,
            response_format={"type": "json_object"},
            store=True,
            use_conversation=True
        )
        
        import json
        summary = json.loads(response)
        
        # Add metadata
        summary['conversation_id'] = self.conversation_id
        summary['total_tokens_used'] = self.client.total_tokens_used
        summary['messages_in_history'] = len(self.client.conversation_history)
        
        return summary
    
    def ask_followup_question(self, question: str) -> str:
        """
        Ask a follow-up question about the lead using full context.
        
        Args:
            question: Question to ask
        
        Returns:
            Answer based on conversation context
        """
        logger.info(f"Follow-up question: {question}")
        
        messages = [{"role": "user", "content": question}]
        
        response = self.client._call_api(
            messages,
            temperature=0.5,
            max_tokens=600,
            store=True,
            use_conversation=True
        )
        
        return response
    
    def check_context_usage(self) -> Dict[str, Any]:
        """
        Check context window usage for this conversation.
        
        Returns:
            Context usage statistics
        """
        return self.client.estimate_context_usage(self.client.conversation_history)
    
    def export_conversation(self) -> Dict[str, Any]:
        """
        Export the full conversation for archival or review.
        
        Returns:
            Complete conversation data
        """
        return {
            'conversation_id': self.conversation_id,
            'messages': self.client.get_conversation_history(),
            'total_tokens': self.client.total_tokens_used,
            'model': self.client.model,
            'context_usage': self.check_context_usage()
        }


# Convenience function for quick multi-turn analysis
def analyze_lead_conversationally(
    company_name: str,
    initial_data: Dict[str, Any],
    research_pain_points: bool = True,
    calculate_roi: bool = True,
    generate_email: bool = False
) -> Dict[str, Any]:
    """
    Perform a complete multi-turn lead analysis workflow.
    
    Args:
        company_name: Company to analyze
        initial_data: Initial data about company
        research_pain_points: Deep dive into pain points
        calculate_roi: Calculate ROI with context
        generate_email: Generate outreach email
    
    Returns:
        Complete analysis results
    """
    agent = ConversationalLeadAgent(create_conversation=True)
    
    # Step 1: Initial analysis
    initial = agent.start_company_analysis(company_name, initial_data)
    results = {'initial_analysis': initial}
    
    # Step 2: Research top pain points
    if research_pain_points:
        pain_points = initial['analysis'].get('pain_points', [])
        if pain_points:
            top_pain_point = pain_points[0] if isinstance(pain_points, list) else pain_points
            pain_point_analysis = agent.research_pain_point(top_pain_point)
            results['pain_point_analysis'] = pain_point_analysis
    
    # Step 3: Calculate ROI with context
    if calculate_roi and 'company_size' in initial_data:
        roi = agent.calculate_roi_in_context(
            company_size=initial_data['company_size'],
            avg_salary=initial_data.get('avg_salary', 75000)
        )
        results['roi_calculation'] = roi
    
    # Step 4: Generate outreach email
    if generate_email:
        email = agent.generate_outreach_email()
        results['outreach_email'] = email
    
    # Summary
    summary = agent.get_conversation_summary()
    results['summary'] = summary
    
    logger.info(f"Conversational analysis complete. Total tokens: {agent.client.total_tokens_used}")
    
    return results
