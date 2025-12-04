"""
Quick Test Script for MCP + Responses API

This script tests the complete MCP integration using OpenAI's Responses API.
Run this to verify everything is working before integrating into your workflow.
"""

import os
import sys
from mcp_client import MCPClient


def check_prerequisites():
    """Check if all prerequisites are met."""
    print("="*70)
    print("CHECKING PREREQUISITES")
    print("="*70)
    
    checks = {
        "OpenAI API Key": os.getenv("OPENAI_API_KEY") is not None,
        "MCP Server Running": False,  # Will check via API call
    }
    
    for check, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"{status} {check}")
    
    if not checks["OpenAI API Key"]:
        print("\n❌ OPENAI_API_KEY not found!")
        print("Set it in .env file or environment variable")
        return False
    
    return True


def test_mcp_server_connection():
    """Test connection to MCP server."""
    print("\n" + "="*70)
    print("TEST 1: MCP Server Connection")
    print("="*70)
    
    try:
        # Try to initialize client (will fail if server not running)
        client = MCPClient()
        
        # Make a simple query to list tools
        result = client.query(
            "List the available tools",
            allowed_tools=[]  # Just list, don't call
        )
        
        if result['tool_list']:
            print("✓ MCP server connection successful!")
            print(f"✓ Available tools: {result['tool_list']['tools']}")
            return True
        else:
            print("✗ MCP server did not return tool list")
            return False
            
    except Exception as e:
        print(f"✗ Failed to connect to MCP server: {e}")
        print("\n💡 Make sure MCP server is running:")
        print("   python mcp_server.py")
        return False


def test_search_functionality():
    """Test search tool."""
    print("\n" + "="*70)
    print("TEST 2: Search Functionality")
    print("="*70)
    
    try:
        client = MCPClient()
        result = client.search_leads("cloud migration")
        
        print(f"✓ Search successful!")
        print(f"✓ Tokens used: {result['usage']['total_tokens']}")
        print(f"✓ Tools called: {[c['tool_name'] for c in result['mcp_calls']]}")
        print(f"\nAnswer preview:")
        print(result['answer'][:300] + "...")
        
        return True
        
    except Exception as e:
        print(f"✗ Search failed: {e}")
        return False


def test_get_top_leads():
    """Test get_top_leads tool."""
    print("\n" + "="*70)
    print("TEST 3: Get Top Leads")
    print("="*70)
    
    try:
        client = MCPClient()
        result = client.get_top_leads(limit=5)
        
        print(f"✓ Get top leads successful!")
        print(f"✓ Tokens used: {result['usage']['total_tokens']}")
        print(f"✓ Tools called: {[c['tool_name'] for c in result['mcp_calls']]}")
        print(f"\nAnswer preview:")
        print(result['answer'][:300] + "...")
        
        return True
        
    except Exception as e:
        print(f"✗ Get top leads failed: {e}")
        return False


def test_pattern_analysis():
    """Test pattern analysis."""
    print("\n" + "="*70)
    print("TEST 4: Pattern Analysis")
    print("="*70)
    
    try:
        client = MCPClient()
        result = client.analyze_pattern(
            "What are the most common pain points?"
        )
        
        print(f"✓ Pattern analysis successful!")
        print(f"✓ Tokens used: {result['usage']['total_tokens']}")
        print(f"✓ Tools called: {[c['tool_name'] for c in result['mcp_calls']]}")
        print(f"\nAnswer preview:")
        print(result['answer'][:300] + "...")
        
        return True
        
    except Exception as e:
        print(f"✗ Pattern analysis failed: {e}")
        return False


def test_conversation_chaining():
    """Test conversation chaining."""
    print("\n" + "="*70)
    print("TEST 5: Conversation Chaining")
    print("="*70)
    
    try:
        client = MCPClient()
        
        # First query
        print("\nQuery 1: Initial question")
        result1 = client.conversation_query("What are my top 3 leads?")
        print(f"✓ Response ID: {result1['response_id']}")
        print(f"✓ Tokens: {result1['usage']['total_tokens']}")
        
        # Follow-up query (should use context)
        print("\nQuery 2: Follow-up (with context chaining)")
        result2 = client.conversation_query("Which of those have the highest scores?")
        print(f"✓ Response ID: {result2['response_id']}")
        print(f"✓ Tokens: {result2['usage']['total_tokens']}")
        
        # Get conversation summary
        summary = client.get_conversation_summary()
        print(f"\n✓ Conversation tracking working!")
        print(f"✓ Total turns: {len(summary)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Conversation chaining failed: {e}")
        return False


def test_approval_workflow():
    """Test approval workflow."""
    print("\n" + "="*70)
    print("TEST 6: Approval Workflow")
    print("="*70)
    
    try:
        client = MCPClient()
        
        # Test with approvals disabled (should work immediately)
        print("\nTesting with require_approval='never'")
        result = client.query(
            "Search for cloud leads",
            require_approval="never"
        )
        
        if result['status'] == 'completed':
            print("✓ No approval workflow successful!")
            print(f"✓ Tools called immediately: {[c['tool_name'] for c in result['mcp_calls']]}")
        else:
            print(f"✗ Unexpected status: {result['status']}")
            return False
        
        # Note: Testing with require_approval='always' requires handling approval responses
        # which is more complex and better tested in integration tests
        
        return True
        
    except Exception as e:
        print(f"✗ Approval workflow failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("MCP + RESPONSES API TEST SUITE")
    print("="*80)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met!")
        print("\n📝 Setup instructions:")
        print("1. Set OPENAI_API_KEY in .env or environment")
        print("2. Start MCP server: python mcp_server.py")
        print("3. Create sample data: python test_mcp_server.py")
        sys.exit(1)
    
    # Run tests
    tests = [
        ("MCP Server Connection", test_mcp_server_connection),
        ("Search Functionality", test_search_functionality),
        ("Get Top Leads", test_get_top_leads),
        ("Pattern Analysis", test_pattern_analysis),
        ("Conversation Chaining", test_conversation_chaining),
        ("Approval Workflow", test_approval_workflow),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nYou're ready to use MCP + Responses API!")
        print("\nNext steps:")
        print("1. Run examples: python examples/integrated_workflow.py")
        print("2. Integrate into dashboard")
        print("3. Build custom queries for your workflow")
    else:
        print("\n⚠️  Some tests failed")
        print("Check the error messages above for details")
    
    print("="*80)


if __name__ == "__main__":
    main()
