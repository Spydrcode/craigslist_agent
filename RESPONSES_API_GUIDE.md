# MCP with OpenAI Responses API Guide

**Updated approach using OpenAI's Responses API instead of ChatGPT interface**

## Overview

This guide shows how to connect your MCP server to OpenAI's **Responses API** for programmatic access to your lead database. This is the new recommended approach as ChatGPT's interface MCP support is being updated.

### Why Responses API?

✅ **Programmatic Control** - Full API-based access, no UI dependency  
✅ **Production Ready** - Rate limits, monitoring, logging built-in  
✅ **Approval Management** - Fine-grained control over tool calls  
✅ **Conversation State** - Integrates with your existing conversation features  
✅ **Cost Effective** - Pay only for tokens used, no per-call fees

## Quick Start

### 1. Start Your MCP Server

```bash
# First, create sample data
python test_mcp_server.py

# Start the MCP server
python mcp_server.py
```

Your MCP server will be running at `http://localhost:8001/sse/`

### 2. Use the MCP Client

```python
from mcp_client import MCPClient

# Initialize client
client = MCPClient(
    mcp_server_url="http://localhost:8001/sse/",
    model="gpt-4o"
)

# Search for leads
result = client.search_leads("cloud migration")
print(result['answer'])

# Get top leads
result = client.get_top_leads(limit=10)
print(result['answer'])

# Analyze patterns
result = client.analyze_pattern(
    "What are the most common tech stacks in high-scoring leads?"
)
print(result['answer'])

# Conversational follow-up
result = client.conversation_query(
    "Which of those companies are hiring the most?"
)
print(result['answer'])
```

## How It Works

### Architecture

```
Your Application
    ↓
MCPClient (Python)
    ↓
OpenAI Responses API (gpt-4o)
    ↓
Your MCP Server (localhost:8001)
    ↓
Lead Database (data/leads/*.json)
```

### Request Flow

1. **You call** `client.query("Find cloud migration leads")`
2. **MCPClient builds** Responses API request with MCP tool config
3. **OpenAI Responses API** connects to your MCP server at `http://localhost:8001/sse/`
4. **MCP server lists tools** (search, fetch, get_top_leads)
5. **GPT-4o decides** which tools to call based on your question
6. **MCP server executes** tool calls and returns data
7. **GPT-4o synthesizes** answer from tool outputs
8. **MCPClient returns** structured response with answer and metadata

## Configuration Options

### Approval Settings

Control which tool calls require approval:

```python
# Never require approval (fastest)
result = client.query(
    "Find leads",
    require_approval="never"
)

# Always require approval (most secure)
result = client.query(
    "Find leads",
    require_approval="always"
)

# Selective approval (recommended)
result = client.query(
    "Find leads",
    require_approval={
        "never": {
            "tool_names": ["search", "get_top_leads"]  # Read-only
        }
        # fetch requires approval (detailed data)
    }
)
```

### Allowed Tools

Restrict which tools can be used:

```python
# Only allow search
result = client.query(
    "Find leads",
    allowed_tools=["search"]
)

# Allow search and top leads
result = client.query(
    "Show best leads",
    allowed_tools=["search", "get_top_leads"]
)

# All tools (default)
result = client.query("Analyze leads")
```

### Conversation Chaining

Use `previous_response_id` for multi-turn conversations:

```python
# First query
result1 = client.query("What are my top leads?")

# Follow-up with context
result2 = client.query(
    "Which of those have cloud pain points?",
    previous_response_id=result1['response_id']
)

# Or use conversation_query (automatic chaining)
result1 = client.conversation_query("What are my top leads?")
result2 = client.conversation_query("Which have cloud pain points?")
```

## API Reference

### MCPClient

#### `__init__(mcp_server_url, model, api_key)`

Initialize the MCP client.

**Parameters:**

- `mcp_server_url` (str): URL of your MCP server (default: "http://localhost:8001/sse/")
- `model` (str): OpenAI model to use (default: "gpt-4o")
- `api_key` (str, optional): OpenAI API key (or set `OPENAI_API_KEY` env var)

#### `query(question, require_approval, allowed_tools, previous_response_id)`

General-purpose query to your lead database.

**Parameters:**

- `question` (str): Natural language question
- `require_approval` (str): "never", "always", or config dict
- `allowed_tools` (List[str], optional): List of tool names to allow
- `previous_response_id` (str, optional): For conversation chaining

**Returns:**

```python
{
    "response_id": "resp_abc123...",
    "answer": "Here are the top leads...",
    "status": "completed",
    "usage": {
        "input_tokens": 1234,
        "output_tokens": 567,
        "total_tokens": 1801
    },
    "mcp_calls": [
        {
            "tool_name": "search",
            "arguments": "{\"query\":\"cloud migration\"}",
            "output": "[{\"id\":\"lead_001\"...}]",
            "error": null
        }
    ],
    "tool_list": {
        "server_label": "craigslist_prospecting",
        "tools": ["search", "fetch", "get_top_leads"]
    }
}
```

#### `search_leads(query, require_approval)`

Search for leads matching criteria.

**Parameters:**

- `query` (str): Search query (company, pain points, tech, etc.)
- `require_approval` (str): Approval setting

**Returns:** Same as `query()`

#### `get_lead_details(lead_id, require_approval)`

Get complete details for a specific lead.

**Parameters:**

- `lead_id` (str): Lead ID to fetch
- `require_approval` (str): Approval setting

**Returns:** Same as `query()`

#### `get_top_leads(limit, require_approval)`

Get top scoring leads.

**Parameters:**

- `limit` (int): Number of leads (1-50)
- `require_approval` (str): Approval setting

**Returns:** Same as `query()`

#### `analyze_pattern(pattern_query, require_approval)`

Analyze patterns across leads.

**Parameters:**

- `pattern_query` (str): What to analyze (e.g., "common pain points")
- `require_approval` (str): Approval setting

**Returns:** Same as `query()`

#### `conversation_query(question, require_approval)`

Continue conversation with automatic context chaining.

**Parameters:**

- `question` (str): Follow-up question
- `require_approval` (str): Approval setting

**Returns:** Same as `query()`

#### `clear_conversation()`

Clear conversation history.

#### `get_conversation_summary()`

Get summary of conversation.

**Returns:**

```python
[
    {
        "question": "What are my top leads?",
        "answer": "Your top leads are..."
    },
    {
        "question": "Which have cloud pain points?",
        "answer": "Of those leads, 3 have..."
    }
]
```

## Usage Examples

### Example 1: Find Specific Leads

```python
from mcp_client import MCPClient

client = MCPClient()

# Find leads with specific pain points
result = client.search_leads("cloud migration and DevOps")
print(result['answer'])

# Get details on a specific lead
result = client.get_lead_details("lead_cloudtech_001")
print(result['answer'])
```

### Example 2: Analysis Workflow

```python
# Get top leads
result = client.get_top_leads(limit=20)
print(f"Top leads: {result['answer']}")

# Analyze patterns
result = client.analyze_pattern(
    "What are the most common pain points in these top 20 leads?"
)
print(f"Common patterns: {result['answer']}")

# Filter by criteria
result = client.search_leads(
    "leads with scores above 85 and Python in tech stack"
)
print(f"Filtered leads: {result['answer']}")
```

### Example 3: Conversational Research

```python
# Start a research conversation
result = client.conversation_query(
    "Show me all leads in the finance industry"
)
print(result['answer'])

# Follow-up questions maintain context
result = client.conversation_query(
    "Which of those are hiring for data engineering?"
)
print(result['answer'])

result = client.conversation_query(
    "What are their biggest pain points?"
)
print(result['answer'])

# Get full conversation
summary = client.get_conversation_summary()
for i, item in enumerate(summary, 1):
    print(f"\nQ{i}: {item['question']}")
    print(f"A{i}: {item['answer']}")
```

### Example 4: Dashboard Integration

```python
from flask import Flask, request, jsonify
from mcp_client import MCPClient

app = Flask(__name__)
client = MCPClient()

@app.route('/api/mcp/query', methods=['POST'])
def mcp_query():
    """
    Query endpoint for dashboard.

    POST /api/mcp/query
    {
        "question": "Find cloud migration leads",
        "require_approval": "never"
    }
    """
    data = request.json
    result = client.query(
        question=data['question'],
        require_approval=data.get('require_approval', 'never')
    )
    return jsonify(result)

@app.route('/api/mcp/top-leads', methods=['GET'])
def get_top_leads():
    """Get top leads."""
    limit = request.args.get('limit', 10, type=int)
    result = client.get_top_leads(limit=limit)
    return jsonify(result)

@app.route('/api/mcp/conversation', methods=['POST'])
def conversation():
    """Conversational endpoint."""
    data = request.json
    result = client.conversation_query(data['question'])
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
```

### Example 5: Batch Analysis with Approval

```python
# Analyze leads with approval workflow
result = client.query(
    "Analyze all leads and identify which ones to contact first",
    require_approval="always"
)

# Check if approval needed
if result['status'] == 'requires_approval':
    print("Approval request:")
    print(f"Tool: {result['approval_request']['tool_name']}")
    print(f"Args: {result['approval_request']['arguments']}")

    # Manual approval
    approved = input("Approve? (y/n): ") == 'y'

    if approved:
        # Continue with approval
        result = client.client.responses.create(
            model=client.model,
            previous_response_id=result['response_id'],
            input=[{
                "type": "mcp_approval_response",
                "approve": True,
                "approval_request_id": result['approval_request']['id']
            }],
            tools=[{
                "type": "mcp",
                "server_url": client.mcp_server_url,
            }]
        )
        print(result.output_text)
```

## Integration with Existing Features

### With Conversation State APIs

```python
from mcp_client import MCPClient
from agents.conversational_lead_agent import ConversationalLeadAgent

# Use MCP for research, Conversation State for interactive analysis
mcp = MCPClient()
conv_agent = ConversationalLeadAgent()

# Research with MCP
research = mcp.analyze_pattern("common pain points in finance")

# Interactive analysis with Conversation State
response = conv_agent.analyze_with_context(
    prompt=f"Based on this research: {research['answer']}, "
           "create a targeted outreach strategy"
)
```

### With Batch API

```python
from mcp_client import MCPClient
from agents.batch_processor_agent import BatchProcessorAgent

mcp = MCPClient()
batch = BatchProcessorAgent()

# Use MCP to identify candidates for batch processing
candidates = mcp.query(
    "Find all leads created in the last 7 days that haven't been analyzed"
)

# Process them in batch
lead_ids = extract_lead_ids(candidates['answer'])
batch_id = batch.create_batch_analyze(lead_ids)

# Monitor with MCP insights
status = batch.check_batch_status(batch_id)
```

## Rate Limits

OpenAI Responses API rate limits for MCP tool:

| Tier     | RPM (Requests Per Minute) |
| -------- | ------------------------- |
| Tier 1   | 200                       |
| Tier 2-3 | 1000                      |
| Tier 4-5 | 2000                      |

**Tips:**

- Cache `mcp_list_tools` output to avoid re-listing tools
- Use conversation chaining to maintain context efficiently
- Batch related queries when possible
- Monitor usage via response metadata

## Cost Optimization

### Token Usage

You only pay for tokens used when:

1. Importing tool definitions (`mcp_list_tools`)
2. Making tool calls (`mcp_call`)
3. Model generating responses

**No additional fees per MCP call!**

### Best Practices

```python
# ✅ GOOD: Reuse tool list in context
result1 = client.query("Find leads")
tool_list_id = result1['tool_list']  # Save this

# Subsequent queries in same session use cached tool list
result2 = client.query(
    "Get details on lead_001",
    previous_response_id=result1['response_id']  # Includes tool list
)

# ✅ GOOD: Specific tool filtering
result = client.query(
    "Search leads",
    allowed_tools=["search"]  # Only import 1 tool
)

# ❌ AVOID: Re-listing tools every query
# Each query without context re-imports tools
result1 = client.query("Query 1")  # Lists tools
result2 = client.query("Query 2")  # Lists tools again (wasteful)
```

## Security and Best Practices

### 1. Approval Management

```python
# Read-only operations: no approval needed
client.query(
    "Search leads",
    require_approval={
        "never": {
            "tool_names": ["search", "get_top_leads"]
        }
    }
)

# Detailed data access: require approval
client.query(
    "Get full details",
    require_approval={
        "always": {
            "tool_names": ["fetch"]
        }
    }
)
```

### 2. Logging and Monitoring

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log all queries
result = client.query("Find leads")
logger.info(f"MCP Query: {result['usage']['total_tokens']} tokens")
logger.info(f"Tools used: {[c['tool_name'] for c in result['mcp_calls']]}")
```

### 3. Error Handling

```python
try:
    result = client.query("Find leads")
    if result['status'] != 'completed':
        print(f"Query incomplete: {result['status']}")

    # Check for tool errors
    for call in result['mcp_calls']:
        if call['error']:
            print(f"Tool error: {call['error']}")
except Exception as e:
    print(f"MCP client error: {e}")
```

### 4. Data Privacy

- Your MCP server runs locally (localhost:8001)
- Data sent to OpenAI only includes tool outputs
- Review tool outputs before disabling approvals
- Enable logging to audit data access
- Compatible with Zero Data Retention (30 days)

## Production Deployment

### Deploy MCP Server

```bash
# Option 1: Deploy to Replit/Render/Heroku
# Update server URL in client:
client = MCPClient(
    mcp_server_url="https://your-mcp-server.replit.app/sse/"
)

# Option 2: Self-hosted with HTTPS
# Use reverse proxy (nginx) for SSL termination
client = MCPClient(
    mcp_server_url="https://mcp.yourdomain.com/sse/"
)
```

### Environment Variables

```python
import os

client = MCPClient(
    mcp_server_url=os.getenv("MCP_SERVER_URL", "http://localhost:8001/sse/"),
    model=os.getenv("OPENAI_MODEL", "gpt-4o"),
    api_key=os.getenv("OPENAI_API_KEY")
)
```

### Health Checks

```python
def check_mcp_health():
    """Verify MCP server is accessible."""
    try:
        result = client.query(
            "List available tools",
            allowed_tools=[]  # Just list, don't call
        )
        return result['tool_list'] is not None
    except Exception as e:
        print(f"MCP server unhealthy: {e}")
        return False
```

## Troubleshooting

### MCP Server Connection Failed

```python
# Error: "Failed to connect to MCP server"

# Check 1: Is server running?
# Run: python mcp_server.py

# Check 2: Correct URL?
client = MCPClient(
    mcp_server_url="http://localhost:8001/sse/"  # Must end with /sse/
)

# Check 3: Firewall/network?
# Test: curl http://localhost:8001/sse/
```

### No Tool Calls Made

```python
# Issue: Query completes but no tools used

# Check 1: Are tools listed?
result = client.query("Find leads")
print(result['tool_list'])  # Should show tools

# Check 2: Is question clear enough?
# ❌ Vague: "Tell me about leads"
# ✅ Specific: "Search for leads with cloud migration pain points"

# Check 3: Are tools allowed?
result = client.query(
    "Find leads",
    allowed_tools=["search"]  # Make sure search is included
)
```

### High Token Usage

```python
# Issue: Queries using too many tokens

# Solution 1: Filter tools
result = client.query(
    "Search leads",
    allowed_tools=["search"]  # Only import needed tools
)

# Solution 2: Use conversation chaining
result1 = client.conversation_query("First query")
result2 = client.conversation_query("Follow-up")  # Reuses context

# Solution 3: Monitor usage
print(f"Tokens: {result['usage']['total_tokens']}")
```

## Next Steps

1. **Test Locally**

   ```bash
   python test_mcp_server.py  # Create sample data
   python mcp_server.py        # Start server
   python mcp_client.py        # Run examples
   ```

2. **Integrate with Dashboard**

   - Add MCP query endpoints
   - Build UI for conversational research
   - Display MCP insights alongside lead data

3. **Production Deployment**

   - Deploy MCP server to cloud
   - Add authentication (OAuth)
   - Set up monitoring and logging
   - Configure rate limiting

4. **Advanced Features**
   - Build custom tools for your workflow
   - Integrate with CRM via MCP
   - Create automated research agents
   - Add vector search for similarity matching

## Resources

- [OpenAI Responses API Docs](https://platform.openai.com/docs/api-reference/responses)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- Your existing guides:
  - `MCP_SERVER_GUIDE.md` - Original MCP server documentation
  - `CONVERSATION_STATE_GUIDE.md` - Conversation State APIs
  - `BATCH_API_GUIDE.md` - Batch processing

---

**This is the new recommended approach for MCP integration!** The Responses API provides full programmatic control without relying on ChatGPT's interface.
