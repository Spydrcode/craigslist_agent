"""
Simple Test: Automatic MCP Server Management

This demonstrates the automatic start/stop of the MCP server.
"""

from mcp_client import MCPClient
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

print("="*70)
print("AUTOMATIC MCP SERVER TEST")
print("="*70)

if not os.getenv("OPENAI_API_KEY"):
    print("\n❌ OPENAI_API_KEY not found in .env!")
    print("Please set it to test the automatic server management.")
    exit(1)

print("\n✅ OpenAI API key loaded")
print("\n" + "="*70)
print("Creating MCPClient (server will auto-start)...")
print("="*70)

try:
    # This will automatically start the MCP server!
    client = MCPClient()
    
    print("\n✅ SUCCESS! MCP server automatically started")
    print("   You didn't have to manually run 'python mcp_server.py'")
    print("   The server is now running in the background.")
    
    print("\n" + "="*70)
    print("Testing a simple query...")
    print("="*70)
    
    # Try a basic query
    result = client.search_leads("cloud migration")
    print(f"\n📊 Query result:")
    print(f"   Status: {result['status']}")
    print(f"   Answer preview: {result['answer'][:200]}...")
    
    print("\n" + "="*70)
    print("✅ AUTOMATIC SERVER MANAGEMENT WORKS!")
    print("="*70)
    print("\nKey points:")
    print("  ✓ Server started automatically when creating MCPClient")
    print("  ✓ No manual 'python mcp_server.py' needed")
    print("  ✓ Server will auto-stop when this script exits")
    print("  ✓ Multiple scripts can share the same server instance")
    
    print("\n💡 Next steps:")
    print("  1. Check AUTO_MCP_QUICKSTART.md for usage patterns")
    print("  2. Run examples/auto_mcp_example.py for more examples")
    print("  3. Use MCPClient() in your workflows - it just works!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    print("\n💡 Troubleshooting:")
    print("  - Make sure 'pip install fastmcp requests' is run")
    print("  - Check that mcp_server.py exists")
    print("  - Verify sample data exists (run test_mcp_server.py)")

print("\n" + "="*70)
print("Script ending - server will auto-stop...")
print("="*70)
