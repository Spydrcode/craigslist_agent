# Automatic MCP Server Management - Quick Reference

## 🎯 No More Manual Server Management!

The MCP server now starts **automatically** when you create an `MCPClient`. No need to remember to activate/deactivate it!

## Three Ways to Use It

### 1️⃣ Automatic Start (Recommended - Simplest!)

```python
from mcp_client import MCPClient

# Server automatically starts here!
client = MCPClient()

# Use it normally
result = client.search_leads("cloud migration")
print(result['answer'])

# Server stays running for other clients
# Auto-stops when your program exits
```

**Best for:** Normal usage, workflows, scripts

---

### 2️⃣ Context Manager (Explicit Control)

```python
from utils.mcp_manager import MCPServerManager
from mcp_client import MCPClient

# Server starts when entering context
with MCPServerManager() as server:
    client = MCPClient(auto_start_server=False)
    result = client.search_leads("kubernetes")
    print(result['answer'])
# Server automatically stops when exiting context
```

**Best for:** When you want the server to stop immediately after your work

---

### 3️⃣ Decorator (Most Convenient for Functions)

```python
from utils.mcp_manager import with_mcp_server
from mcp_client import MCPClient

@with_mcp_server
def analyze_leads():
    # Server is already running!
    client = MCPClient(auto_start_server=False)
    return client.get_top_leads(10)

result = analyze_leads()  # Server auto-starts and auto-stops
```

**Best for:** Wrapping functions that need MCP server

---

## Real-World Workflow Example

```python
from mcp_client import MCPClient

def daily_prospecting_workflow():
    """Your daily workflow - server auto-manages itself!"""

    # Just create the client - server auto-starts!
    client = MCPClient()

    # 1. Find high-value leads
    high_value = client.query(
        "Find leads with score > 85 and hiring_velocity > 10"
    )

    # 2. Analyze patterns
    patterns = client.query(
        "What tech stacks are most common in top 10 leads?"
    )

    # 3. Get contact info
    contacts = client.query(
        "Show contact details for top 5 scoring leads"
    )

    return {
        'high_value': high_value,
        'patterns': patterns,
        'contacts': contacts
    }

    # Server auto-stops when program exits
    # No cleanup needed!

if __name__ == "__main__":
    results = daily_prospecting_workflow()
    print(results)
```

---

## Multiple Clients Share One Server

```python
# Create multiple clients - they all share the same server instance
client1 = MCPClient()  # Starts server
client2 = MCPClient()  # Uses existing server
client3 = MCPClient()  # Uses existing server

# All work independently
result1 = client1.search_leads("terraform")
result2 = client2.search_leads("kubernetes")
result3 = client3.get_top_leads(5)

# Server auto-stops when program exits
```

---

## Manual Control (If Needed)

```python
from utils.mcp_manager import MCPServerManager

# Get singleton manager instance
manager = MCPServerManager.get_instance()

# Start server manually
manager.start()

# Check if running
if manager.is_running():
    print("Server is running!")

# Stop server manually
manager.stop()
```

---

## How It Works

1. **Auto-Start**: When you create `MCPClient()`, it checks if the MCP server is running
2. **Singleton Pattern**: Only one server instance runs, even with multiple clients
3. **Background Process**: Server runs as a subprocess, doesn't block your code
4. **Auto-Cleanup**: Server automatically stops when your program exits (via `atexit`)
5. **Smart Detection**: Detects if server is already running (e.g., from another script)

---

## Migration from Manual Management

### Before (Manual):

```python
# Terminal 1: Start server manually
# > python mcp_server.py

# Terminal 2: Run your code
from mcp_client import MCPClient
client = MCPClient()
result = client.search_leads("cloud")

# Remember to stop server in Terminal 1 (Ctrl+C)
```

### After (Automatic):

```python
# Just one terminal - everything automatic!
from mcp_client import MCPClient
client = MCPClient()  # Server auto-starts
result = client.search_leads("cloud")
# Server auto-stops when done
```

---

## Configuration Options

```python
# Disable auto-start if you're managing the server yourself
client = MCPClient(auto_start_server=False)

# Use different port
from utils.mcp_manager import MCPServerManager
manager = MCPServerManager(port=8002)
manager.ensure_running()
```

---

## Examples to Try

Run these examples to see auto-management in action:

```bash
# Comprehensive examples
python examples/auto_mcp_example.py

# Updated demo (now with auto-start)
python demo_mcp_responses.py

# Test the manager directly
python utils/mcp_manager.py
```

---

## Troubleshooting

**Q: Server won't start?**

- Check if port 8001 is already in use
- Verify `mcp_server.py` exists in project root
- Check that `fastmcp` is installed: `pip install fastmcp`

**Q: Multiple servers running?**

- The manager uses singleton pattern to prevent this
- Each program instance gets one server
- Multiple programs can't share (need different ports)

**Q: Server not stopping?**

- Should auto-stop via `atexit` handler
- If stuck, manually kill: `taskkill /F /IM python.exe` (Windows)
- Or use Task Manager to find and kill the python process

**Q: Want to disable auto-start?**

```python
client = MCPClient(auto_start_server=False)
```

---

## Benefits

✅ **No Mental Overhead**: Don't remember to start/stop server  
✅ **Fewer Errors**: No "server not running" failures  
✅ **Cleaner Code**: No server management boilerplate  
✅ **Faster Development**: Just focus on your queries  
✅ **Production Ready**: Works in scripts, cron jobs, services

---

## See Also

- **Full Examples**: `examples/auto_mcp_example.py`
- **Implementation**: `utils/mcp_manager.py`
- **Integration**: `mcp_client.py`
- **Documentation**: `RESPONSES_API_GUIDE.md`
