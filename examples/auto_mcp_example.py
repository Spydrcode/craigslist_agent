"""
Automatic MCP Server Example

This demonstrates how the MCP server automatically starts when needed.
No manual activation required!
"""

from mcp_client import MCPClient
from utils.mcp_manager import MCPServerManager, with_mcp_server


def example_1_auto_start():
    """
    Example 1: Automatic server start with MCPClient
    
    The server automatically starts when you create an MCPClient instance.
    """
    print("="*70)
    print("EXAMPLE 1: Automatic Server Start")
    print("="*70)
    print("\nCreating MCPClient (server will auto-start)...")
    
    # Server automatically starts here!
    client = MCPClient()
    
    print("✓ Client ready - server is running automatically\n")
    
    # Use the client normally
    result = client.search_leads("cloud migration")
    print(f"Result: {result['answer'][:200]}...\n")
    
    print("Done! Server keeps running for other clients to use.")
    print("It will auto-stop when your program exits.\n")


def example_2_context_manager():
    """
    Example 2: Context manager for explicit control
    
    If you want the server to stop after your work, use a context manager.
    """
    print("="*70)
    print("EXAMPLE 2: Context Manager (Explicit Control)")
    print("="*70)
    print("\nStarting MCP server with context manager...")
    
    # Server starts here
    with MCPServerManager() as server:
        print("✓ Server running in context\n")
        
        # Use MCP client
        client = MCPClient(auto_start_server=False)  # Server already running
        result = client.get_top_leads(limit=5)
        print(f"Result: {result['answer'][:200]}...\n")
        
        print("Exiting context...")
    
    # Server automatically stopped here
    print("✓ Server stopped automatically\n")


@with_mcp_server
def example_3_decorator():
    """
    Example 3: Decorator for automatic server management
    
    Use the @with_mcp_server decorator for functions that need the server.
    """
    print("="*70)
    print("EXAMPLE 3: Decorator (Most Convenient)")
    print("="*70)
    print("\n@with_mcp_server decorator handles everything!\n")
    
    # Server is already running thanks to decorator
    client = MCPClient(auto_start_server=False)
    result = client.query("Show me companies hiring for DevOps with score > 80")
    print(f"Result: {result['answer'][:200]}...\n")
    
    return result


def example_4_workflow_integration():
    """
    Example 4: Integration into your prospecting workflow
    
    Shows how to use in a real workflow without worrying about server management.
    """
    print("="*70)
    print("EXAMPLE 4: Real Workflow Integration")
    print("="*70)
    
    # Just use MCPClient - server auto-starts!
    client = MCPClient()
    
    print("\n1. Finding high-value leads...")
    high_value = client.query(
        "Find leads with hiring_velocity > 10 and score > 85, "
        "show company name and pain points"
    )
    print(f"✓ Found: {high_value['answer'][:150]}...\n")
    
    print("2. Analyzing tech stack patterns...")
    tech_patterns = client.query(
        "What are the most common technologies in our top 10 leads?"
    )
    print(f"✓ Analysis: {tech_patterns['answer'][:150]}...\n")
    
    print("3. Getting contact information...")
    contacts = client.query(
        "Show me contact details for the top 3 scoring leads"
    )
    print(f"✓ Contacts: {contacts['answer'][:150]}...\n")
    
    print("Done! Server stays running for next workflow.")


def example_5_multiple_clients():
    """
    Example 5: Multiple clients share the same server
    
    Only one server instance runs, even with multiple clients.
    """
    print("="*70)
    print("EXAMPLE 5: Multiple Clients, One Server")
    print("="*70)
    
    print("\nCreating first client...")
    client1 = MCPClient()
    print("✓ Client 1 ready (server auto-started)\n")
    
    print("Creating second client...")
    client2 = MCPClient()
    print("✓ Client 2 ready (using same server)\n")
    
    print("Creating third client...")
    client3 = MCPClient()
    print("✓ Client 3 ready (still same server)\n")
    
    # All clients can query independently
    result1 = client1.search_leads("kubernetes")
    result2 = client2.search_leads("terraform")
    result3 = client3.get_top_leads(3)
    
    print("All clients working with single server instance!")
    print("Server automatically stops when program exits.\n")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("AUTOMATIC MCP SERVER MANAGEMENT EXAMPLES")
    print("="*70)
    print("\nNo need to manually start/stop the MCP server!")
    print("It handles everything automatically.\n")
    
    # Run examples
    try:
        example_1_auto_start()
        input("\nPress Enter to continue to Example 2...")
        
        example_2_context_manager()
        input("\nPress Enter to continue to Example 3...")
        
        example_3_decorator()
        input("\nPress Enter to continue to Example 4...")
        
        example_4_workflow_integration()
        input("\nPress Enter to continue to Example 5...")
        
        example_5_multiple_clients()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*70)
    print("✅ Examples complete!")
    print("="*70)
    print("\nThe MCP server will automatically stop when this program exits.")
    print("No cleanup needed - it's all handled for you!\n")
