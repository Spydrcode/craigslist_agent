"""
MCP Client for OpenAI Responses API

This module provides a client to interact with your MCP server through
OpenAI's Responses API, enabling programmatic ChatGPT access to your
lead database without relying on the ChatGPT interface.

The MCP server is automatically started when needed - no manual activation required!
"""

import os
from typing import Dict, List, Any, Optional
from openai import OpenAI
from utils.mcp_manager import MCPServerManager


class MCPClient:
    """
    Client for interacting with MCP server via OpenAI Responses API.
    
    This allows you to query your lead database programmatically using
    ChatGPT without needing the web interface.
    """
    
    def __init__(
        self,
        mcp_server_url: str = "http://localhost:8001/sse/",
        model: str = "gpt-4o",
        api_key: Optional[str] = None,
        auto_start_server: bool = True
    ):
        """
        Initialize MCP client.
        
        Args:
            mcp_server_url: URL of your MCP server
            model: OpenAI model to use
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            auto_start_server: Automatically start MCP server if not running
        """
        self.mcp_server_url = mcp_server_url
        self.model = model
        self.client = OpenAI(api_key=api_key)
        self.conversation_history: List[Dict[str, Any]] = []
        
        # Automatically ensure MCP server is running
        if auto_start_server:
            self.server_manager = MCPServerManager.get_instance()
            self.server_manager.ensure_running()
    
    def query(
        self,
        question: str,
        require_approval: str = "never",
        allowed_tools: Optional[List[str]] = None,
        previous_response_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Query your lead database via MCP server.
        
        Args:
            question: Natural language question about your leads
            require_approval: "never", "always", or custom config
            allowed_tools: List of allowed tool names (None = all)
            previous_response_id: For conversation chaining
        
        Returns:
            Response dictionary with answer and metadata
        """
        # Build MCP tool configuration
        mcp_tool = {
            "type": "mcp",
            "server_label": "craigslist_prospecting",
            "server_description": "Access to analyzed leads and job postings database",
            "server_url": self.mcp_server_url,
            "require_approval": require_approval,
        }
        
        # Add allowed tools if specified
        if allowed_tools:
            mcp_tool["allowed_tools"] = allowed_tools
        
        # Build request
        request_params = {
            "model": self.model,
            "tools": [mcp_tool],
            "input": question,
        }
        
        # Add previous response for conversation chaining
        if previous_response_id:
            request_params["previous_response_id"] = previous_response_id
        
        # Make API call
        response = self.client.responses.create(**request_params)
        
        # Extract results
        result = {
            "response_id": response.id,
            "answer": response.output_text,
            "status": response.status,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            "mcp_calls": [],
            "tool_list": None,
        }
        
        # Extract MCP tool calls and list_tools
        for item in response.output:
            if item.type == "mcp_call":
                result["mcp_calls"].append({
                    "tool_name": item.name,
                    "arguments": item.arguments,
                    "output": item.output,
                    "error": item.error,
                })
            elif item.type == "mcp_list_tools":
                result["tool_list"] = {
                    "server_label": item.server_label,
                    "tools": [t.name for t in item.tools],
                }
        
        # Save to conversation history
        self.conversation_history.append({
            "question": question,
            "response_id": response.id,
            "answer": response.output_text,
        })
        
        return result
    
    def search_leads(
        self,
        query: str,
        require_approval: str = "never"
    ) -> Dict[str, Any]:
        """
        Search for leads matching a query.
        
        Args:
            query: Search query (company, pain points, tech stack, etc.)
            require_approval: Approval setting for tool calls
        
        Returns:
            Response with matching leads
        """
        question = f"Search for leads matching: {query}"
        return self.query(
            question,
            require_approval=require_approval,
            allowed_tools=["search"]
        )
    
    def get_lead_details(
        self,
        lead_id: str,
        require_approval: str = "never"
    ) -> Dict[str, Any]:
        """
        Get complete details for a specific lead.
        
        Args:
            lead_id: Lead ID to fetch
            require_approval: Approval setting
        
        Returns:
            Response with full lead details
        """
        question = f"Get complete details for lead ID: {lead_id}"
        return self.query(
            question,
            require_approval=require_approval,
            allowed_tools=["fetch"]
        )
    
    def get_top_leads(
        self,
        limit: int = 10,
        require_approval: str = "never"
    ) -> Dict[str, Any]:
        """
        Get top scoring leads.
        
        Args:
            limit: Number of leads to return
            require_approval: Approval setting
        
        Returns:
            Response with top leads
        """
        question = f"Show me the top {limit} leads"
        return self.query(
            question,
            require_approval=require_approval,
            allowed_tools=["get_top_leads"]
        )
    
    def analyze_pattern(
        self,
        pattern_query: str,
        require_approval: str = "never"
    ) -> Dict[str, Any]:
        """
        Analyze patterns across leads.
        
        Args:
            pattern_query: What pattern to analyze (e.g., "common pain points")
            require_approval: Approval setting
        
        Returns:
            Response with pattern analysis
        """
        question = f"Analyze this pattern across my leads: {pattern_query}"
        return self.query(question, require_approval=require_approval)
    
    def conversation_query(
        self,
        question: str,
        require_approval: str = "never"
    ) -> Dict[str, Any]:
        """
        Continue a conversation with context from previous queries.
        
        Args:
            question: Follow-up question
            require_approval: Approval setting
        
        Returns:
            Response with context from conversation history
        """
        # Get previous response ID if available
        previous_id = None
        if self.conversation_history:
            previous_id = self.conversation_history[-1]["response_id"]
        
        return self.query(
            question,
            require_approval=require_approval,
            previous_response_id=previous_id
        )
    
    def clear_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []
    
    def get_conversation_summary(self) -> List[Dict[str, str]]:
        """
        Get summary of conversation history.
        
        Returns:
            List of questions and answers
        """
        return [
            {"question": h["question"], "answer": h["answer"]}
            for h in self.conversation_history
        ]


# Example usage
if __name__ == "__main__":
    import json
    
    # Initialize client
    client = MCPClient()
    
    print("="*70)
    print("MCP Client - Query Your Lead Database via OpenAI Responses API")
    print("="*70)
    
    # Example 1: Search for leads
    print("\n1. Searching for cloud migration leads...")
    result = client.search_leads("cloud migration")
    print(f"Answer: {result['answer']}")
    print(f"MCP calls made: {len(result['mcp_calls'])}")
    if result['mcp_calls']:
        print(f"Tools used: {[c['tool_name'] for c in result['mcp_calls']]}")
    
    # Example 2: Get top leads
    print("\n2. Getting top 5 leads...")
    result = client.get_top_leads(limit=5)
    print(f"Answer: {result['answer']}")
    
    # Example 3: Analyze patterns
    print("\n3. Analyzing common pain points...")
    result = client.analyze_pattern(
        "What are the most common pain points across all leads?"
    )
    print(f"Answer: {result['answer'][:300]}...")
    
    # Example 4: Conversational queries
    print("\n4. Conversational follow-up...")
    result = client.conversation_query(
        "Which of those leads have the highest scores?"
    )
    print(f"Answer: {result['answer'][:300]}...")
    
    # Example 5: Get conversation summary
    print("\n5. Conversation Summary:")
    summary = client.get_conversation_summary()
    for i, item in enumerate(summary, 1):
        print(f"\nQ{i}: {item['question']}")
        print(f"A{i}: {item['answer'][:200]}...")
    
    print("\n" + "="*70)
    print(f"Total tokens used: {result['usage']['total_tokens']}")
    print("="*70)
