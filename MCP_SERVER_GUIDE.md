# MCP Server Guide - ChatGPT Integration

## Overview

The **Model Context Protocol (MCP) Server** enables ChatGPT and other AI assistants to search and retrieve data from your Craigslist prospecting system. This creates a powerful knowledge base of analyzed leads accessible directly in ChatGPT.

## What is MCP?

Model Context Protocol (MCP) is an open protocol that's becoming the industry standard for extending AI models with additional tools and knowledge. Your MCP server exposes your prospecting data through a standardized interface that ChatGPT can query.

## Benefits

### 🔍 ChatGPT Integration

- Query your lead database directly from ChatGPT
- Access historical analysis and insights
- Research companies using your accumulated data

### 🧠 Deep Research

- Use ChatGPT's deep research feature with your lead data
- Combine your proprietary data with web research
- Generate comprehensive prospect reports

### 📊 Knowledge Base

- Build searchable database of analyzed leads over time
- Track company evolution and hiring patterns
- Find similar companies and patterns

### 🔌 API Access

- Standardized protocol for accessing your data
- Works with ChatGPT, Claude, and other MCP clients
- Easy integration with external tools

---

## Features

### 1. Search Tool

**Find leads and job postings matching your query**

Search by:

- Company name
- Pain points ("legacy system", "scaling issues")
- Tech stack ("React", "AWS", "Kubernetes")
- Job titles or requirements
- Growth signals ("funded", "series A")

Returns up to 20 ranked results with snippets.

### 2. Fetch Tool

**Retrieve complete lead analysis or job details**

Returns full information including:

- Lead score and priority
- Complete pain point analysis
- Service opportunities and ROI
- Growth stage and hiring velocity
- Tech stack and requirements
- Original job postings

### 3. Get Top Leads Tool

**Quick access to highest-scoring prospects**

Returns top N leads sorted by score with:

- Company names and scores
- Priority levels
- Job counts
- Quick summary

---

## Installation

### 1. Install Dependencies

```bash
pip install fastmcp
```

Or install from requirements.txt (already updated):

```bash
pip install -r requirements.txt
```

### 2. Verify Data Structure

The MCP server expects this directory structure:

```
craigslist_agent/
├── data/
│   ├── leads/          # Lead analysis JSON files
│   │   ├── lead-001.json
│   │   ├── lead-002.json
│   │   └── ...
│   └── jobs/           # Job posting JSON files
│       ├── job-001.json
│       ├── job-002.json
│       └── ...
├── mcp_server.py       # MCP server (just created)
└── requirements.txt
```

The directories will be created automatically if they don't exist.

---

## Running the Server

### Local Development

Start the MCP server:

```bash
python mcp_server.py
```

Server runs on: `http://localhost:8001/sse/`

You'll see:

```
Starting Craigslist Prospecting MCP Server
Data directory: C:\Users\...\craigslist_agent\data
Leads directory: C:\Users\...\craigslist_agent\data\leads
Jobs directory: C:\Users\...\craigslist_agent\data\jobs
Starting MCP server on 0.0.0.0:8001
Server will be accessible via SSE transport
Server URL: http://localhost:8001/sse/
```

### Production Deployment

For production, deploy to a cloud platform:

**Replit:**

1. Import your code to Replit
2. Set up secrets (if needed)
3. Get public URL: `https://[your-repl].replit.dev/sse/`

**Render/Heroku:**

1. Deploy Python app
2. Expose port 8001
3. Get public URL

**Self-hosted:**

1. Run on server with public IP
2. Configure reverse proxy (nginx)
3. Add SSL certificate

---

## Data Format

### Lead JSON Format

```json
{
  "lead_id": "lead-001",
  "company_name": "TechCorp",
  "lead_score": 85.0,
  "priority": "HOT",
  "job_count": 12,
  "pain_points": [
    "Legacy system migration needed",
    "Scaling infrastructure challenges",
    "DevOps automation required"
  ],
  "opportunities": [
    {
      "service": "Cloud Migration",
      "estimated_value": "$75K-150K",
      "confidence": "high"
    }
  ],
  "growth_stage": "SCALING",
  "tech_stack": ["React", "AWS", "Kubernetes"],
  "source_url": "https://craigslist.org/...",
  "created_at": "2024-01-15T10:30:00"
}
```

### Job JSON Format

```json
{
  "job_id": "job-001",
  "title": "Senior Software Engineer",
  "company": "TechCorp",
  "location": "San Francisco, CA",
  "description": "Full job description...",
  "requirements": ["5+ years Python", "React experience", "AWS cloud"],
  "url": "https://craigslist.org/job/...",
  "posted_date": "2024-01-15",
  "scraped_at": "2024-01-15T10:00:00"
}
```

---

## Integration with Your Pipeline

### Saving Lead Data for MCP

Update your orchestrator to save lead data:

```python
from pathlib import Path
import json
from datetime import datetime

DATA_DIR = Path("data")
LEADS_DIR = DATA_DIR / "leads"
LEADS_DIR.mkdir(parents=True, exist_ok=True)

def save_lead_for_mcp(lead_analysis):
    """Save lead analysis for MCP server access"""
    lead_id = lead_analysis.get('lead_id')
    lead_file = LEADS_DIR / f"{lead_id}.json"

    with open(lead_file, 'w', encoding='utf-8') as f:
        json.dump(lead_analysis, f, indent=2)

    print(f"Saved lead to MCP database: {lead_id}")

# In your orchestrator workflow:
for lead in analyzed_leads:
    save_lead_for_mcp(lead)
```

### Saving Job Data for MCP

```python
JOBS_DIR = DATA_DIR / "jobs"
JOBS_DIR.mkdir(parents=True, exist_ok=True)

def save_job_for_mcp(job_posting):
    """Save job posting for MCP server access"""
    job_id = job_posting.get('job_id')
    job_file = JOBS_DIR / f"{job_id}.json"

    with open(job_file, 'w', encoding='utf-8') as f:
        json.dump(job_posting, f, indent=2)

    print(f"Saved job to MCP database: {job_id}")

# After scraping:
for job in scraped_jobs:
    save_job_for_mcp(job)
```

---

## Connect to ChatGPT

### Option 1: Developer Mode (Full MCP Access)

1. In ChatGPT, go to **Settings → Connectors → Advanced → Developer mode**
2. Enable developer mode
3. Click "Add connector"
4. Enter your MCP server URL: `http://localhost:8001/sse/` (local) or your public URL
5. Configure tools: `search`, `fetch`, `get_top_leads`
6. Set approval: "Never" for read-only operations
7. Save connector

### Option 2: Via API (Deep Research)

Use the Responses API with your MCP server:

```python
import openai

response = openai.responses.create(
    model="o4-mini-deep-research",
    input=[
        {
            "role": "developer",
            "content": [
                {
                    "type": "input_text",
                    "text": "You are a B2B sales research assistant with access to analyzed leads."
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": "Find all leads with legacy system migration needs and score above 80"
                }
            ]
        }
    ],
    reasoning={"summary": "auto"},
    tools=[
        {
            "type": "mcp",
            "server_label": "prospecting",
            "server_url": "http://localhost:8001/sse/",
            "allowed_tools": ["search", "fetch", "get_top_leads"],
            "require_approval": "never"
        }
    ]
)
```

---

## Usage Examples

### Example 1: Find High-Value Leads

**In ChatGPT:**

```
Find all leads with cloud migration needs and scores above 75
```

ChatGPT will:

1. Use `search` tool: "cloud migration score > 75"
2. Get matching leads
3. Use `fetch` tool to get full details
4. Summarize findings with company names, scores, opportunities

### Example 2: Research Similar Companies

**In ChatGPT:**

```
Show me companies similar to TechCorp that are scaling and have DevOps pain points
```

ChatGPT will:

1. Use `search` tool: "scaling DevOps"
2. Filter results similar to TechCorp
3. Use `fetch` to get complete profiles
4. Present comparison

### Example 3: Quick Top Leads

**In ChatGPT:**

```
What are my top 10 hottest leads right now?
```

ChatGPT will:

1. Use `get_top_leads` tool with limit=10
2. Display top prospects with scores
3. Highlight key opportunities

### Example 4: Deep Research on Industry

**Using Deep Research in ChatGPT:**

```
Research trends in hiring for fintech companies in my lead database. What are common pain points and which services should I prioritize?
```

ChatGPT will:

1. Use `search` to find fintech leads
2. Use `fetch` to get full analysis
3. Analyze patterns across companies
4. Generate comprehensive report with recommendations

---

## Advanced Features

### Custom Tool: Get Top Leads

```python
@mcp.tool()
async def get_top_leads(limit: int = 10) -> Dict[str, List[Dict[str, Any]]]:
    """Get the top-scoring leads from the database."""
    # Implementation in mcp_server.py
```

**Usage in ChatGPT:**

```
Get my top 20 leads
```

### Filtering and Sorting

The search tool automatically:

- Ranks results by lead score
- Returns most relevant matches first
- Limits to top 20 results
- Includes context snippets

### Metadata Access

The fetch tool returns structured metadata:

```json
{
  "metadata": {
    "lead_score": 85,
    "priority": "HOT",
    "job_count": 12,
    "growth_stage": "SCALING",
    "analyzed_date": "2024-01-15"
  }
}
```

---

## Security and Best Practices

### Data Privacy

⚠️ **Important**: MCP servers expose your data to AI models

- Only expose data you're comfortable sharing
- Don't include sensitive customer information
- Review data before saving to MCP directories

### Access Control

For production:

1. **Use OAuth** for authentication
2. **Implement rate limiting** to prevent abuse
3. **Add API keys** for server access
4. **Log all queries** for audit trail

### Prompt Injection Protection

Be aware that attackers could try prompt injection:

- Review ChatGPT's requests in logs
- Don't expose write actions without approval
- Monitor for suspicious queries
- Keep server updated

### Data Management

Best practices:

- **Archive old leads** periodically
- **Clean up test data** before production
- **Backup lead database** regularly
- **Version control** your data format

---

## Monitoring and Debugging

### Check Server Logs

The server logs all operations:

```
INFO:__main__:Searching prospecting data for query: 'cloud migration'
INFO:__main__:Search returned 15 results
INFO:__main__:Fetching content for ID: lead-123
```

### Test Locally

Test the MCP server manually:

```python
# test_mcp_server.py
import asyncio
from mcp_server import create_server

async def test():
    server = create_server()

    # Test search
    results = await server.tools['search']("cloud migration")
    print(f"Search results: {results}")

    # Test fetch
    if results['results']:
        lead_id = results['results'][0]['id']
        lead = await server.tools['fetch'](lead_id)
        print(f"Lead details: {lead}")

asyncio.run(test())
```

### Monitor Data Directory

Check what data is available:

```bash
# Count leads
dir data\leads | Measure-Object

# Count jobs
dir data\jobs | Measure-Object

# View recent leads
Get-ChildItem data\leads -Filter *.json | Sort-Object LastWriteTime -Descending | Select-Object -First 5
```

---

## Integration with Existing Features

### Combine with Batch API

```python
# Process jobs in batch, save results for MCP
from agents import process_jobs_batch

batch = process_jobs_batch(jobs, task_type='analyze')
results = agent.parse_results(agent.download_results(batch['batch_id']))

# Save to MCP database
for result in results:
    save_lead_for_mcp(result)
```

### Combine with Conversation State

```python
from agents import ConversationalLeadAgent

# Get lead from MCP
lead = fetch_from_mcp(lead_id)

# Interactive conversation
conv_agent = ConversationalLeadAgent()
analysis = conv_agent.analyze_lead_conversationally(lead)

# Save enhanced analysis back to MCP
save_lead_for_mcp(analysis)
```

### Dashboard Integration

Add MCP status to dashboard:

```python
@app.route('/api/mcp/status')
def mcp_status():
    lead_count = len(list(LEADS_DIR.glob("*.json")))
    job_count = len(list(JOBS_DIR.glob("*.json")))

    return jsonify({
        'mcp_server': 'http://localhost:8001/sse/',
        'leads_available': lead_count,
        'jobs_available': job_count,
        'status': 'running'
    })
```

---

## Troubleshooting

### Server won't start

**Issue**: Port 8001 already in use

**Solution:**

```python
# Change port in mcp_server.py
server.run(transport="sse", host="0.0.0.0", port=8002)
```

### No results found

**Issue**: Search returns empty results

**Check:**

1. Are files in `data/leads/` and `data/jobs/`?
2. Are JSON files valid?
3. Does query match content?

```bash
# Verify files exist
dir data\leads\*.json
dir data\jobs\*.json

# Check file content
Get-Content data\leads\lead-001.json | ConvertFrom-Json
```

### ChatGPT can't connect

**Issue**: ChatGPT connector fails

**Solutions:**

1. Verify server is running: `http://localhost:8001/sse/`
2. Check firewall allows port 8001
3. For production, use HTTPS with valid certificate
4. Ensure URL ends with `/sse/`

### Data not updating

**Issue**: New leads don't appear in search

**Solution**: Restart MCP server after adding new data files

---

## Cost and Performance

### Free to Run

MCP server costs:

- **Server**: Free (self-hosted)
- **API calls**: None (direct file access)
- **Storage**: Minimal (JSON files)

### Performance

- **Search**: ~50-100ms for 1000 leads
- **Fetch**: ~10ms per lead
- **Memory**: ~10MB per 1000 leads

### Scaling

For large datasets (10,000+ leads):

1. **Add database** (SQLite, PostgreSQL)
2. **Index fields** for faster search
3. **Cache results** for common queries
4. **Paginate** search results

---

## Next Steps

1. **Start the server**: `python mcp_server.py`
2. **Add test data**: Save a few lead analyses
3. **Connect ChatGPT**: Add connector in settings
4. **Test queries**: Try searching your leads
5. **Integrate pipeline**: Auto-save new leads
6. **Monitor usage**: Check logs and usage patterns

---

## Resources

- **MCP Documentation**: https://modelcontextprotocol.io/
- **FastMCP**: https://github.com/jlowin/fastmcp
- **OpenAI Connectors**: https://platform.openai.com/docs/guides/deep-research
- **Server Code**: `mcp_server.py`

---

**Summary:** Your MCP server turns your Craigslist prospecting system into a searchable knowledge base accessible from ChatGPT and other AI assistants. Perfect for research, pattern finding, and leveraging historical lead data! 🚀
