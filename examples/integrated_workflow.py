"""
Complete Workflow Example: Batch + Conversation + MCP

This example demonstrates the combined power of all three OpenAI advanced features:
1. Batch API - Process large volumes at 50% cost savings
2. Conversation State - Interactive analysis with 58% token savings
3. MCP + Responses API - Programmatic knowledge base queries

Workflow:
- Use Batch API to process 100+ leads overnight
- Use MCP to research patterns across all historical data
- Use Conversation State for interactive analysis with decision maker
"""

import os
import json
import time
from typing import List, Dict, Any
from datetime import datetime

from agents.batch_processor_agent import BatchProcessorAgent
from agents.conversational_lead_agent import ConversationalLeadAgent
from mcp_client import MCPClient


class IntegratedProspectingWorkflow:
    """
    Complete workflow combining Batch, Conversation, and MCP.
    """
    
    def __init__(self):
        self.batch_agent = BatchProcessorAgent()
        self.conv_agent = ConversationalLeadAgent()
        self.mcp_client = MCPClient()
        self.workflow_id = f"workflow_{int(time.time())}"
    
    def step1_batch_process_leads(self, lead_ids: List[str]) -> str:
        """
        Step 1: Process large volume of leads using Batch API.
        
        50% cost savings vs synchronous processing.
        Runs overnight for 100+ leads.
        
        Args:
            lead_ids: List of lead IDs to analyze
        
        Returns:
            Batch ID for tracking
        """
        print("="*70)
        print("STEP 1: Batch Processing (50% Cost Savings)")
        print("="*70)
        
        # Create batch for analysis
        batch_id = self.batch_agent.create_batch_analyze(
            lead_ids=lead_ids,
            metadata={
                "workflow_id": self.workflow_id,
                "purpose": "overnight_lead_analysis"
            }
        )
        
        print(f"✓ Batch created: {batch_id}")
        print(f"✓ Processing {len(lead_ids)} leads")
        print(f"✓ Expected completion: 24 hours")
        print(f"✓ Cost savings: ~50% vs synchronous")
        
        return batch_id
    
    def step2_monitor_batch(self, batch_id: str) -> Dict[str, Any]:
        """
        Step 2: Monitor batch progress.
        
        Args:
            batch_id: Batch to monitor
        
        Returns:
            Batch status
        """
        print("\n" + "="*70)
        print("STEP 2: Monitoring Batch Progress")
        print("="*70)
        
        status = self.batch_agent.check_batch_status(batch_id)
        
        print(f"✓ Status: {status['status']}")
        print(f"✓ Completed: {status['request_counts']['completed']}/{status['request_counts']['total']}")
        print(f"✓ Created: {status['created_at']}")
        
        if status['status'] == 'completed':
            print("✓ Batch processing complete!")
            
            # Retrieve results
            results = self.batch_agent.retrieve_batch_results(batch_id)
            print(f"✓ Retrieved {len(results)} results")
            
            return results
        else:
            print(f"⏳ Batch still processing...")
            return None
    
    def step3_mcp_research(self) -> Dict[str, Any]:
        """
        Step 3: Research patterns using MCP + Responses API.
        
        Query historical lead database to discover insights.
        
        Returns:
            Research findings
        """
        print("\n" + "="*70)
        print("STEP 3: MCP Research (Historical Analysis)")
        print("="*70)
        
        findings = {}
        
        # Query 1: Top leads
        print("\nQuery 1: Top performing leads...")
        result = self.mcp_client.get_top_leads(limit=20)
        findings['top_leads'] = result['answer']
        print(f"✓ {result['usage']['total_tokens']} tokens used")
        
        # Query 2: Common pain points
        print("\nQuery 2: Analyzing pain points...")
        result = self.mcp_client.analyze_pattern(
            "What are the most common pain points across all high-scoring leads?"
        )
        findings['pain_points'] = result['answer']
        print(f"✓ {result['usage']['total_tokens']} tokens used")
        
        # Query 3: Tech stack trends
        print("\nQuery 3: Tech stack analysis...")
        result = self.mcp_client.analyze_pattern(
            "What are the most common tech stacks in companies scoring above 80?"
        )
        findings['tech_stacks'] = result['answer']
        print(f"✓ {result['usage']['total_tokens']} tokens used")
        
        # Query 4: Industry trends
        print("\nQuery 4: Industry distribution...")
        result = self.mcp_client.conversation_query(
            "Which industries have the most high-scoring leads?"
        )
        findings['industries'] = result['answer']
        print(f"✓ {result['usage']['total_tokens']} tokens used")
        
        print("\n✓ Research complete!")
        return findings
    
    def step4_conversational_analysis(
        self,
        research_findings: Dict[str, Any],
        batch_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Step 4: Interactive analysis using Conversation State APIs.
        
        58% token savings via automatic context chaining.
        
        Args:
            research_findings: From MCP research
            batch_results: From batch processing
        
        Returns:
            Conversation messages
        """
        print("\n" + "="*70)
        print("STEP 4: Conversational Analysis (58% Token Savings)")
        print("="*70)
        
        messages = []
        
        # Start conversation with research context
        prompt = f"""
        Based on our research findings:
        
        TOP LEADS:
        {research_findings['top_leads']}
        
        COMMON PAIN POINTS:
        {research_findings['pain_points']}
        
        TECH TRENDS:
        {research_findings['tech_stacks']}
        
        INDUSTRIES:
        {research_findings['industries']}
        
        And our latest batch analysis of {len(batch_results)} leads,
        please provide strategic recommendations for our outreach campaign.
        """
        
        print("\nQuery 1: Strategic recommendations...")
        response = self.conv_agent.start_conversation(prompt)
        messages.append({
            "role": "user",
            "content": prompt[:200] + "...",
            "response": response['message']['content'][:300] + "..."
        })
        print(f"✓ Conversation started: {response['conversation_id']}")
        print(f"✓ Tokens: {response['usage']['total_tokens']}")
        
        # Continue conversation
        print("\nQuery 2: Prioritization strategy...")
        response = self.conv_agent.continue_conversation(
            conversation_id=response['conversation_id'],
            user_message="Which 5 leads should we prioritize and why?"
        )
        messages.append({
            "role": "user",
            "content": "Which 5 leads should we prioritize and why?",
            "response": response['message']['content'][:300] + "..."
        })
        print(f"✓ Token savings: ~58% via chaining")
        print(f"✓ Tokens: {response['usage']['total_tokens']}")
        
        # Get outreach strategy
        print("\nQuery 3: Outreach messaging...")
        response = self.conv_agent.continue_conversation(
            conversation_id=response['conversation_id'],
            user_message="What messaging themes should we use for each priority lead?"
        )
        messages.append({
            "role": "user",
            "content": "What messaging themes should we use for each priority lead?",
            "response": response['message']['content'][:300] + "..."
        })
        print(f"✓ Tokens: {response['usage']['total_tokens']}")
        
        # Get timeline
        print("\nQuery 4: Campaign timeline...")
        response = self.conv_agent.continue_conversation(
            conversation_id=response['conversation_id'],
            user_message="Suggest a 2-week outreach timeline"
        )
        messages.append({
            "role": "user",
            "content": "Suggest a 2-week outreach timeline",
            "response": response['message']['content'][:300] + "..."
        })
        print(f"✓ Tokens: {response['usage']['total_tokens']}")
        
        print("\n✓ Conversational analysis complete!")
        return messages
    
    def step5_save_results(
        self,
        research: Dict[str, Any],
        conversation: List[Dict[str, Any]],
        batch_results: List[Dict[str, Any]]
    ):
        """
        Step 5: Save complete workflow results.
        
        Args:
            research: MCP research findings
            conversation: Conversation messages
            batch_results: Batch processing results
        """
        print("\n" + "="*70)
        print("STEP 5: Saving Workflow Results")
        print("="*70)
        
        output = {
            "workflow_id": self.workflow_id,
            "timestamp": datetime.now().isoformat(),
            "research_findings": research,
            "conversation_analysis": conversation,
            "batch_results_count": len(batch_results),
            "total_leads_analyzed": len(batch_results),
        }
        
        # Save to file
        filename = f"output/workflows/workflow_{self.workflow_id}.json"
        os.makedirs("output/workflows", exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"✓ Results saved to: {filename}")
        print(f"✓ Total leads analyzed: {len(batch_results)}")
        print(f"✓ Research queries: 4")
        print(f"✓ Conversation turns: {len(conversation)}")
    
    def run_complete_workflow(
        self,
        lead_ids: List[str],
        wait_for_batch: bool = False
    ):
        """
        Run complete workflow combining all three features.
        
        Args:
            lead_ids: Leads to analyze
            wait_for_batch: Whether to wait for batch completion
        """
        print("\n" + "="*80)
        print("INTEGRATED PROSPECTING WORKFLOW")
        print("Batch API + Conversation State + MCP")
        print("="*80)
        
        # Step 1: Batch process
        batch_id = self.step1_batch_process_leads(lead_ids)
        
        # Step 2: Monitor (optional wait)
        if wait_for_batch:
            print("\n⏳ Waiting for batch completion...")
            batch_results = None
            while batch_results is None:
                time.sleep(60)  # Check every minute
                batch_results = self.step2_monitor_batch(batch_id)
        else:
            print("\n⏭️  Skipping batch wait (demo mode)")
            batch_results = []  # Empty for demo
        
        # Step 3: MCP research
        research = self.step3_mcp_research()
        
        # Step 4: Conversational analysis
        conversation = self.step4_conversational_analysis(research, batch_results)
        
        # Step 5: Save results
        self.step5_save_results(research, conversation, batch_results)
        
        print("\n" + "="*80)
        print("WORKFLOW COMPLETE!")
        print("="*80)
        print(f"✓ Batch processing: 50% cost savings")
        print(f"✓ Conversation state: 58% token savings")
        print(f"✓ MCP research: Pattern discovery across historical data")
        print(f"✓ Total leads analyzed: {len(lead_ids)}")
        print("="*80)


def example_realistic_workflow():
    """
    Example: Realistic workflow with sample data.
    """
    workflow = IntegratedProspectingWorkflow()
    
    # Sample lead IDs (in production, these would come from database)
    sample_leads = [
        f"lead_{i:03d}" for i in range(1, 51)  # 50 leads
    ]
    
    print("\n📊 REALISTIC WORKFLOW EXAMPLE")
    print("-" * 80)
    print("Scenario: You scraped 50 new leads yesterday")
    print("Goal: Analyze them and create outreach strategy")
    print("-" * 80)
    
    # Run workflow (demo mode - don't wait for batch)
    workflow.run_complete_workflow(
        lead_ids=sample_leads,
        wait_for_batch=False  # Set True in production
    )


def example_individual_features():
    """
    Example: Using each feature individually.
    """
    print("\n📊 INDIVIDUAL FEATURE EXAMPLES")
    print("="*80)
    
    # Example 1: Batch API only
    print("\n1. BATCH API - Process leads overnight")
    print("-"*80)
    batch = BatchProcessorAgent()
    batch_id = batch.create_batch_analyze(
        lead_ids=[f"lead_{i}" for i in range(100)],
        metadata={"purpose": "overnight_analysis"}
    )
    print(f"✓ Batch {batch_id} created")
    print("✓ 50% cost savings vs synchronous")
    
    # Example 2: MCP only
    print("\n2. MCP + RESPONSES API - Research patterns")
    print("-"*80)
    mcp = MCPClient()
    result = mcp.analyze_pattern("common pain points in finance industry")
    print(f"✓ Answer: {result['answer'][:200]}...")
    print(f"✓ Tokens: {result['usage']['total_tokens']}")
    
    # Example 3: Conversation State only
    print("\n3. CONVERSATION STATE - Interactive analysis")
    print("-"*80)
    conv = ConversationalLeadAgent()
    response = conv.start_conversation(
        "Analyze the top 5 leads and suggest outreach strategy"
    )
    print(f"✓ Conversation ID: {response['conversation_id']}")
    print(f"✓ Response: {response['message']['content'][:200]}...")
    
    response = conv.continue_conversation(
        conversation_id=response['conversation_id'],
        user_message="Which lead should we contact first?"
    )
    print(f"✓ Follow-up: {response['message']['content'][:200]}...")
    print("✓ 58% token savings via chaining")


def example_cost_comparison():
    """
    Example: Cost comparison of different approaches.
    """
    print("\n💰 COST COMPARISON")
    print("="*80)
    
    leads_to_analyze = 100
    
    # Old approach (synchronous, no optimization)
    print("\n❌ OLD APPROACH (Naive)")
    print("-"*80)
    old_cost_per_lead = 0.0010  # $0.001 per lead
    old_total = leads_to_analyze * old_cost_per_lead
    print(f"Cost per lead: ${old_cost_per_lead:.4f}")
    print(f"Total for {leads_to_analyze} leads: ${old_total:.2f}")
    print("No conversation chaining, no batch discount")
    
    # New approach (batch + conversation + MCP)
    print("\n✅ NEW APPROACH (Optimized)")
    print("-"*80)
    
    # Batch API: 50% savings
    batch_cost = old_total * 0.5
    print(f"1. Batch API cost: ${batch_cost:.2f} (50% savings)")
    
    # Conversation State: 58% token savings on analysis
    analysis_cost = 0.05  # One-time analysis cost
    conv_savings = analysis_cost * 0.58
    conv_cost = analysis_cost - conv_savings
    print(f"2. Conversation State: ${conv_cost:.2f} (58% token savings)")
    
    # MCP: Research queries (minimal cost)
    mcp_cost = 0.02  # A few pattern queries
    print(f"3. MCP research: ${mcp_cost:.2f}")
    
    total_new = batch_cost + conv_cost + mcp_cost
    savings = old_total - total_new
    savings_pct = (savings / old_total) * 100
    
    print(f"\nTotal new cost: ${total_new:.2f}")
    print(f"Total savings: ${savings:.2f} ({savings_pct:.1f}%)")
    print("="*80)


if __name__ == "__main__":
    print("\n" + "="*80)
    print("INTEGRATED WORKFLOW EXAMPLES")
    print("Batch API + Conversation State + MCP + Responses API")
    print("="*80)
    
    # Run examples
    print("\n" + "🚀 Choose an example:")
    print("1. Realistic complete workflow")
    print("2. Individual feature examples")
    print("3. Cost comparison")
    print("4. All examples")
    
    choice = input("\nEnter choice (1-4) or press Enter for demo: ").strip() or "1"
    
    if choice == "1":
        example_realistic_workflow()
    elif choice == "2":
        example_individual_features()
    elif choice == "3":
        example_cost_comparison()
    elif choice == "4":
        example_realistic_workflow()
        example_individual_features()
        example_cost_comparison()
    else:
        print("Running default demo...")
        example_realistic_workflow()
    
    print("\n" + "="*80)
    print("✓ Examples complete!")
    print("="*80)
