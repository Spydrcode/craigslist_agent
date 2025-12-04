# Batch API Guide - 50% Cost Savings for Large-Scale Processing

## Overview

The OpenAI Batch API enables asynchronous processing of large volumes of job postings at **50% lower cost** compared to synchronous API calls. Perfect for analyzing hundreds or thousands of job postings scraped from Craigslist.

## Key Benefits

### 💰 Cost Savings

- **50% discount** on all batch requests
- Example: Analyzing 1,000 jobs
  - Synchronous API: ~$10.00
  - Batch API: ~$5.00
  - **Savings: $5.00** (50%)

### ⚡ Higher Rate Limits

- Separate rate limit pool from synchronous requests
- Process thousands of jobs without hitting standard rate limits
- No delays or throttling for batch requests

### 📦 Scalability

- Process up to **50,000 requests** per batch
- Maximum file size: **200MB**
- Ideal for overnight batch processing

### ⏰ Completion Window

- Results available within **24 hours**
- Typically completes much faster (2-4 hours for most batches)
- Perfect for non-time-sensitive analysis

## When to Use Batch API vs Synchronous API

### Use Batch API When:

- ✅ Analyzing **hundreds or thousands** of job postings
- ✅ Results **not needed immediately** (can wait hours)
- ✅ Want to **maximize cost efficiency**
- ✅ Processing **overnight batches**
- ✅ Approaching **rate limits** with sync calls

### Use Synchronous API When:

- ⚡ Need **immediate results** (real-time analysis)
- ⚡ Processing **small volumes** (<50 jobs)
- ⚡ Interactive workflows (e.g., conversational analysis)
- ⚡ User is **waiting** for response

## Supported Task Types

The BatchProcessorAgent supports 4 task types:

### 1. Complete Analysis (`analyze`)

Deep analysis of job postings including qualification, pain points, and ROI.

**Use Case:** Comprehensive overnight analysis of all scraped jobs

### 2. Quick Qualification (`qualify`)

Fast qualification to determine if job is a good fit.

**Use Case:** Filter thousands of jobs to find best prospects

### 3. Pain Point Extraction (`extract_pain_points`)

Extract key pain points and urgency signals.

**Use Case:** Identify jobs with urgent needs and high motivation

### 4. Structured Parsing (`parse`)

Parse job posting into structured fields (title, company, salary, etc.).

**Use Case:** Extract data for database storage or further processing

## Quick Start Examples

### Example 1: Batch Process Scraped Jobs

```python
from agents import process_jobs_batch

# After scraping jobs from Craigslist
scrape_results = scraper_agent.scrape_all_pages("software")

# Process all jobs in batch mode (50% cost savings)
result = process_jobs_batch(
    scrape_results,
    task_type='analyze',
    wait_for_completion=False,  # Don't wait (check status later)
    model='gpt-4o-mini'
)

print(f"Batch ID: {result['batch_id']}")
print(f"Processing {result['job_count']} jobs")
print("Check back in 2-4 hours for results")
```

### Example 2: Manual Workflow with Full Control

```python
from agents import BatchProcessorAgent

agent = BatchProcessorAgent()

# Step 1: Create batch input file
input_file = agent.create_batch_input_file(
    jobs=scrape_results,
    task_type='qualify',  # Quick qualification
    model='gpt-4o-mini'
)

# Step 2: Upload file
file_id = agent.upload_batch_file(input_file)

# Step 3: Create batch
batch_id = agent.create_batch(
    file_id,
    description="Qualify 500 software engineer jobs"
)

# Step 4: Check status (run periodically)
status = agent.check_batch_status(batch_id)
print(f"Status: {status['status']}")
print(f"Progress: {status.get('request_counts', {})}")

# Step 5: Download results when completed
if status['status'] == 'completed':
    results_file = agent.download_results(batch_id)
    results = agent.parse_results(results_file)

    print(f"Processed: {len(results)} jobs")
    for result in results[:5]:  # First 5
        print(f"Job {result['custom_id']}: {result['content'][:100]}...")
```

### Example 3: Wait for Completion (Blocking)

```python
from agents import BatchProcessorAgent

agent = BatchProcessorAgent()

# Create and submit batch
input_file = agent.create_batch_input_file(jobs, 'analyze')
file_id = agent.upload_batch_file(input_file)
batch_id = agent.create_batch(file_id)

# Wait for completion (checks every 5 minutes)
final_status = agent.wait_for_batch(
    batch_id,
    check_interval=300,  # 5 minutes
    timeout=86400  # 24 hours
)

if final_status['status'] == 'completed':
    results = agent.parse_results(
        agent.download_results(batch_id)
    )
    print(f"Successfully processed {len(results)} jobs!")
```

## Dashboard API Endpoints

### 1. Create Batch Job

**POST** `/api/batch/create`

```json
{
    "jobs": [...],  // Array of job objects from scraper
    "task_type": "analyze",  // analyze, qualify, parse, extract_pain_points
    "model": "gpt-4o-mini"  // optional
}
```

**Response:**

```json
{
  "success": true,
  "batch_id": "batch_abc123",
  "file_id": "file_xyz789",
  "job_count": 500,
  "task_type": "analyze",
  "model": "gpt-4o-mini",
  "message": "Batch created. Results available within 24 hours."
}
```

### 2. Check Batch Status

**GET** `/api/batch/status/<batch_id>`

**Response:**

```json
{
  "success": true,
  "status": {
    "id": "batch_abc123",
    "status": "in_progress",
    "request_counts": {
      "total": 500,
      "completed": 350,
      "failed": 2
    },
    "created_at": 1234567890,
    "completed_at": null
  }
}
```

Possible statuses:

- `validating` - Checking input file
- `in_progress` - Processing requests
- `finalizing` - Compiling results
- `completed` - Ready to download
- `failed` - Processing error
- `expired` - Not completed within 24h
- `cancelled` - Manually cancelled

### 3. Download Results

**GET** `/api/batch/results/<batch_id>`

**Response:**

```json
{
    "success": true,
    "batch_id": "batch_abc123",
    "results_file": "batch_results_abc123.jsonl",
    "total": 500,
    "successful": 498,
    "failed": 2,
    "results": [
        {
            "custom_id": "job-0",
            "success": true,
            "content": "Analysis result...",
            "error": null
        },
        ...
    ]
}
```

### 4. Cancel Batch

**POST** `/api/batch/cancel/<batch_id>`

**Response:**

```json
{
  "success": true,
  "batch_id": "batch_abc123",
  "status": "cancelling"
}
```

Note: Cancellation can take up to 10 minutes. Already completed requests will still be charged.

### 5. List Recent Batches

**GET** `/api/batch/list?limit=20`

**Response:**

```json
{
    "success": true,
    "batches": [
        {
            "id": "batch_abc123",
            "status": "completed",
            "created_at": 1234567890,
            "request_counts": {"total": 500, "completed": 500, "failed": 0}
        },
        ...
    ],
    "count": 20
}
```

### 6. Process Scraped Jobs (One-Call Convenience)

**POST** `/api/batch/process-scraped`

```json
{
    "scrape_results": [...],  // Results from /api/scrape
    "task_type": "analyze"
}
```

**Response:**

```json
{
  "success": true,
  "batch_id": "batch_abc123",
  "job_count": 500,
  "task_type": "analyze",
  "message": "Processing 500 jobs in batch mode. Check status with batch_id."
}
```

## Integration with Conversation State

Combine batch processing with conversation state for powerful workflows:

### Workflow 1: Batch + Conversation

1. **Overnight:** Batch process 1,000 jobs (50% cost savings)
2. **Morning:** Review top 50 qualified leads
3. **Interactive:** Use conversational analysis on top prospects

```python
# Step 1: Batch process overnight (50% cost)
result = process_jobs_batch(all_jobs, task_type='qualify')
batch_id = result['batch_id']

# Step 2: Next day, get results
results = agent.parse_results(agent.download_results(batch_id))

# Step 3: Filter top leads
top_leads = [r for r in results if 'high confidence' in r['content'].lower()]

# Step 4: Conversational analysis on top leads (full context)
from agents import ConversationalLeadAgent

conv_agent = ConversationalLeadAgent()
for lead in top_leads[:10]:  # Top 10 only
    # Multi-turn conversation with context preservation
    analysis = conv_agent.analyze_lead_conversationally(lead)
    roi = conv_agent.get_roi_estimate(lead)
    email = conv_agent.generate_email_draft(lead)
```

### Workflow 2: Two-Stage Processing

1. **Stage 1 (Batch):** Quick qualify 5,000 jobs → 500 qualified
2. **Stage 2 (Batch):** Deep analyze 500 qualified → 50 top prospects
3. **Stage 3 (Conversational):** Interactive follow-up on 50

```python
# Stage 1: Quick qualification (batch)
qualify_batch = process_jobs_batch(
    all_5000_jobs,
    task_type='qualify',
    wait_for_completion=False
)

# ... wait for completion ...

# Stage 2: Deep analysis of qualified (batch)
qualified_jobs = [r for r in results if r['qualified']]
analysis_batch = process_jobs_batch(
    qualified_jobs,
    task_type='analyze',
    wait_for_completion=False
)

# ... wait for completion ...

# Stage 3: Conversational on top prospects (sync)
top_prospects = sorted(analysis_results, key=lambda x: x['score'])[:50]
for prospect in top_prospects:
    conversation = conv_agent.start_conversation(prospect)
    # Interactive multi-turn analysis
```

## Cost Optimization Strategies

### Strategy 1: Batch Everything Overnight

- **Scenario:** Scrape 1,000+ jobs daily
- **Approach:** Batch process all jobs overnight
- **Savings:** 50% on all processing ($500/mo → $250/mo)

### Strategy 2: Hybrid Approach

- **Scenario:** Mix of urgent and non-urgent jobs
- **Approach:**
  - Sync: High-priority jobs needing immediate response (~10%)
  - Batch: Bulk analysis overnight (~90%)
- **Savings:** ~45% overall

### Strategy 3: Two-Tier Processing

- **Scenario:** Need to filter large volumes
- **Approach:**
  1. Batch qualify all jobs (cheap, fast filtering)
  2. Sync/conversation on qualified subset (interactive)
- **Savings:** 40-50% with better targeting

## File Format Details

### Input File (.jsonl)

Each line is a JSON object:

```json
{"custom_id": "job-0", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "gpt-4o-mini", "messages": [...]}}
{"custom_id": "job-1", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "gpt-4o-mini", "messages": [...]}}
...
```

- `custom_id`: Your identifier for mapping results (e.g., "job-0", "job-123")
- `method`: Always "POST"
- `url`: Always "/v1/chat/completions"
- `body`: Standard Chat Completions API parameters

### Output File (.jsonl)

Each line contains response for corresponding input:

```json
{"id": "batch_req_abc", "custom_id": "job-0", "response": {"status_code": 200, "body": {"choices": [...]}}, "error": null}
{"id": "batch_req_def", "custom_id": "job-1", "response": {"status_code": 200, "body": {"choices": [...]}}, "error": null}
...
```

The `parse_results()` method automatically handles this format.

## Monitoring and Debugging

### Check Progress

```python
status = agent.check_batch_status(batch_id)
counts = status.get('request_counts', {})
print(f"Progress: {counts['completed']}/{counts['total']}")
print(f"Failed: {counts.get('failed', 0)}")
```

### Handle Errors

```python
results = agent.parse_results(results_file)

# Check for failures
failed = [r for r in results if not r['success']]
if failed:
    print(f"Failed requests: {len(failed)}")
    for fail in failed:
        print(f"Job {fail['custom_id']}: {fail['error']}")

# Process successful results
successful = [r for r in results if r['success']]
print(f"Successfully processed: {len(successful)}")
```

### Cancel if Needed

```python
# Cancel within 10 minutes of creation for full refund
if something_wrong:
    agent.cancel_batch(batch_id)
    print("Batch cancelled")
```

## Best Practices

### 1. Use Descriptive Custom IDs

```python
# Good: Contains job info
custom_id = f"job-{job['id']}-{job['title'][:20]}"

# Bad: Generic numbering
custom_id = f"request-{i}"
```

### 2. Add Metadata Descriptions

```python
batch_id = agent.create_batch(
    file_id,
    description=f"Analyze {len(jobs)} {category} jobs from {date}"
)
```

### 3. Store Batch IDs

```python
import json

batch_info = {
    'batch_id': batch_id,
    'created': datetime.now().isoformat(),
    'job_count': len(jobs),
    'task_type': task_type
}

with open('active_batches.json', 'a') as f:
    f.write(json.dumps(batch_info) + '\n')
```

### 4. Validate Before Processing

```python
# Check job format before creating batch
for job in jobs:
    assert 'description' in job, "Missing description"
    assert 'title' in job, "Missing title"
```

### 5. Handle Large Batches

```python
# Split very large sets into multiple batches
BATCH_SIZE = 10000

for i in range(0, len(all_jobs), BATCH_SIZE):
    batch_jobs = all_jobs[i:i+BATCH_SIZE]
    batch_id = process_jobs_batch(
        batch_jobs,
        task_type='analyze',
        wait_for_completion=False
    )
    print(f"Created batch {i//BATCH_SIZE + 1}: {batch_id}")
```

## Common Issues and Solutions

### Issue: "Invalid JSONL format"

**Solution:** Ensure each line is valid JSON:

```python
import json

# Validate before uploading
with open(input_file) as f:
    for i, line in enumerate(f):
        try:
            json.loads(line)
        except json.JSONDecodeError as e:
            print(f"Line {i}: Invalid JSON - {e}")
```

### Issue: Batch expires before completion

**Solution:** Process smaller batches or increase check frequency:

```python
# Monitor actively for large batches
agent.wait_for_batch(batch_id, check_interval=300)  # Check every 5 min
```

### Issue: High failure rate in results

**Solution:** Check error messages and adjust prompts:

```python
failed = [r for r in results if not r['success']]
error_types = {}
for fail in failed:
    error_msg = fail['error']['message']
    error_types[error_msg] = error_types.get(error_msg, 0) + 1

print("Error breakdown:", error_types)
```

## Testing

See `test_batch_api.py` for comprehensive examples:

```bash
# Run all batch API tests
python test_batch_api.py

# Test specific scenario
python -c "from test_batch_api import test_batch_cost_comparison; test_batch_cost_comparison()"
```

## Next Steps

1. **Try the examples** in this guide
2. **Review test_batch_api.py** for working code
3. **Integrate with your scraping workflow**
4. **Monitor costs** and compare with synchronous processing
5. **Combine with Conversation State** for optimal workflows

## Support and Resources

- [OpenAI Batch API Documentation](https://platform.openai.com/docs/guides/batch)
- [Cost Calculator](https://openai.com/pricing)
- Test Suite: `test_batch_api.py`
- Agent Implementation: `agents/batch_processor_agent.py`
- Dashboard Endpoints: `dashboard/leads_app.py` (lines 1633-1800)

---

**Remember:** Batch API = 50% cost savings for the same quality results. Perfect for analyzing hundreds or thousands of Craigslist job postings overnight! 🚀
