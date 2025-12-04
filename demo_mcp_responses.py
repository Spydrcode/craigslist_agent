"""
Quick Demo: MCP + Responses API Integration

This script demonstrates how to use the MCPClient to query your lead database
using OpenAI's Responses API with MCP tools.

✨ NEW: MCP server automatically starts when needed - no manual activation!
"""

import os
from dotenv import load_dotenv
from mcp_client import MCPClient

# Load environment variables
load_dotenv()

def main():
    print("="*70)
    print("MCP + RESPONSES API DEMO")
    print("="*70)
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in .env file!")
        return
    
    print("✓ OpenAI API key loaded")
    
    # Initialize MCP client (server auto-starts!)
    print("\n📡 Initializing MCP client (server will auto-start if needed)...")
    try:
        client = MCPClient()  # Server automatically starts here!
        print("✓ MCP client ready (server auto-started)")
    except Exception as e:
        print(f"❌ Failed to initialize MCP client: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Example 1: Search for leads
    print("\n" + "="*70)
    print("EXAMPLE 1: Search for cloud migration leads")
    print("="*70)
    
    try:
        result = client.search_leads("cloud migration")
        print(f"\n📊 Answer:\n{result['answer']}")
        
        if result.get('tools_used'):
            print(f"\n🔧 Tools used: {', '.join(result['tools_used'])}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 2: Get top leads
    print("\n" + "="*70)
    print("EXAMPLE 2: Get top scoring leads")
    print("="*70)
    
    try:
        result = client.get_top_leads(limit=5)
        print(f"\n📊 Answer:\n{result['answer']}")
        
        if result.get('tools_used'):
            print(f"\n🔧 Tools used: {', '.join(result['tools_used'])}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 3: Fetch specific lead
    print("\n" + "="*70)
    print("EXAMPLE 3: Fetch detailed lead information")
    print("="*70)
    
    try:
        result = client.fetch_lead("lead_12345")
        print(f"\n📊 Answer:\n{result['answer']}")
        
        if result.get('tools_used'):
            print(f"\n🔧 Tools used: {', '.join(result['tools_used'])}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 4: Custom query combining multiple tools
    print("\n" + "="*70)
    print("EXAMPLE 4: Complex query using multiple tools")
    print("="*70)
    
    try:
        result = client.query(
            "Find companies hiring for DevOps roles with scores above 80, "
            "then show me detailed information about the top 3 results"
        )
        print(f"\n📊 Answer:\n{result['answer']}")
        
        if result.get('tools_used'):
            print(f"\n🔧 Tools used: {', '.join(result['tools_used'])}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*70)
    print("✅ Demo complete!")
    print("="*70)
    print("\n💡 Next steps:")
    print("1. Check RESPONSES_API_GUIDE.md for detailed documentation")
    print("2. Review mcp_client.py to see the implementation")
    print("3. Integrate MCPClient into your prospecting workflow")
    print("4. Try the conversation state features for multi-turn analysis")


if __name__ == "__main__":
    main()
