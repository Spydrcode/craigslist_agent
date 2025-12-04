# Integration Example: Conversation State + Batch API

This guide demonstrates optimal workflows combining **Conversation State APIs** (interactive multi-turn analysis) with **Batch API** (large-scale async processing) for maximum efficiency and cost savings.

## Cost Comparison

### Naive Approach (All Synchronous)

```python
# Process 1,000 jobs synchronously
cost = 1000 * $0.01 = $10.00
time = 1000 * 2s = 33 minutes
```

### Optimized Approach (Batch + Conversation)

```python
# Batch qualify 1,000 → 100 qualified
batch_cost = 1000 * $0.005 = $5.00 (50% savings)

# Conversational analysis on 20 top prospects
conv_cost = 20 * $0.008 = $0.16 (58% token savings via chaining)

total_cost = $5.16
total_savings = $10.00 - $5.16 = $4.84 (48% savings)
```

---

## Workflow 1: Two-Tier Processing

**Use Case:** Daily scraping of 500-1,000 jobs, need to identify and analyze top prospects

### Step 1: Batch Qualification (Overnight)

```python
from agents import process_jobs_batch, BatchProcessorAgent

# Scrape all jobs (existing scraper)
from agents import scraper_agent
scrape_results = scraper_agent.scrape_all_pages(
    city='sfbay',
    category='software',
    max_pages=20
)

print(f"Scraped {len(scrape_results)} jobs")

# Submit batch qualification job (runs overnight, 50% cost)
batch_result = process_jobs_batch(
    scrape_results,
    task_type='qualify',  # Quick qualification filter
    wait_for_completion=False,  # Don't wait, check tomorrow
    model='gpt-4o-mini'
)

print(f"Batch submitted: {batch_result['batch_id']}")
print(f"Processing {batch_result['job_count']} jobs")
print("Check status tomorrow morning")

# Save batch ID for later
import json
with open('active_batches.json', 'a') as f:
    f.write(json.dumps({
        'batch_id': batch_result['batch_id'],
        'date': '2024-01-15',
        'job_count': batch_result['job_count'],
        'task_type': 'qualify'
    }) + '\n')
```

### Step 2: Review Results (Next Morning)

```python
from agents import BatchProcessorAgent

agent = BatchProcessorAgent()

# Load batch ID from yesterday
with open('active_batches.json') as f:
    batches = [json.loads(line) for line in f]
    yesterday_batch = batches[-1]  # Most recent

batch_id = yesterday_batch['batch_id']

# Check status
status = agent.check_batch_status(batch_id)
print(f"Status: {status['status']}")
print(f"Completed: {status['request_counts']['completed']}/{status['request_counts']['total']}")

# Download if completed
if status['status'] == 'completed':
    results_file = agent.download_results(batch_id)
    results = agent.parse_results(results_file)

    print(f"Total results: {len(results)}")
    print(f"Successful: {sum(1 for r in results if r['success'])}")
    print(f"Failed: {sum(1 for r in results if not r['success'])}")

    # Filter for qualified leads
    qualified_leads = []
    for result in results:
        if result['success']:
            content = result['content'].lower()
            if 'qualified' in content or 'high confidence' in content:
                qualified_leads.append({
                    'job_id': result['custom_id'],
                    'qualification': result['content'],
                    'original_job': scrape_results[int(result['custom_id'].split('-')[1])]
                })

    print(f"Qualified leads: {len(qualified_leads)}")

    # Save for interactive analysis
    with open('qualified_leads.json', 'w') as f:
        json.dump(qualified_leads, f, indent=2)
```

### Step 3: Interactive Conversational Analysis (Same Day)

```python
from agents import ConversationalLeadAgent

# Load qualified leads from batch processing
with open('qualified_leads.json') as f:
    qualified_leads = json.load(f)

# Sort by some criteria (job count, urgency keywords, etc.)
sorted_leads = sorted(
    qualified_leads,
    key=lambda x: x['original_job'].get('job_count', 1),
    reverse=True
)

# Interactive analysis on top 20 prospects
conv_agent = ConversationalLeadAgent()

top_prospects = []
for lead in sorted_leads[:20]:
    job = lead['original_job']

    print(f"\nAnalyzing: {job.get('title', 'Unknown')} - {job.get('company', 'Unknown')}")

    # Multi-turn conversational analysis (context preserved)
    conversation = conv_agent.start_conversation(job)

    # Get ROI estimate (uses conversation context)
    roi = conv_agent.get_roi_estimate(job)

    # Generate email draft (uses full conversation history)
    email = conv_agent.generate_email_draft(job)

    # Get summary
    summary = conv_agent.get_conversation_summary()

    top_prospects.append({
        'job': job,
        'analysis': conversation,
        'roi': roi,
        'email': email,
        'summary': summary,
        'conversation_id': conv_agent.client_agent.conversation_id
    })

    print(f"ROI: {roi.get('estimated_value', 'Unknown')}")
    print(f"Conversation ID: {conv_agent.client_agent.conversation_id}")

# Save for outreach
with open('top_prospects_analyzed.json', 'w') as f:
    json.dump(top_prospects, f, indent=2)

print(f"\nCompleted analysis of {len(top_prospects)} top prospects")
print(f"Batch cost: ~${len(scrape_results) * 0.005:.2f}")
print(f"Conversation cost: ~${len(top_prospects) * 0.008:.2f}")
print(f"Total: ~${(len(scrape_results) * 0.005 + len(top_prospects) * 0.008):.2f}")
```

### Summary - Workflow 1

**Input:** 800 scraped jobs  
**Batch Qualification:** 800 jobs → 75 qualified (Cost: $4.00)  
**Conversational Analysis:** 20 top prospects (Cost: $0.16)  
**Total Cost:** $4.16  
**Synchronous Equivalent:** $8.00  
**Savings:** $3.84 (48%)

---

## Workflow 2: Multi-Stage Batch Processing

**Use Case:** Large-scale weekly analysis with progressive filtering

### Stage 1: Quick Qualification (Batch)

```python
from agents import process_jobs_batch

# Weekly scrape: 5,000 jobs
weekly_jobs = scraper_agent.scrape_all_pages(
    city='sfbay',
    category='all',
    max_pages=100
)

# Stage 1: Quick qualification filter
stage1_batch = process_jobs_batch(
    weekly_jobs,
    task_type='qualify',
    wait_for_completion=False,
    model='gpt-4o-mini'
)

print(f"Stage 1 batch: {stage1_batch['batch_id']}")
print(f"Qualifying {len(weekly_jobs)} jobs...")
```

### Stage 2: Deep Analysis (Batch)

```python
# Wait for Stage 1 completion (or check next day)
agent = BatchProcessorAgent()
stage1_results = agent.parse_results(
    agent.download_results(stage1_batch['batch_id'])
)

# Filter to qualified only
qualified = []
for result in stage1_results:
    if result['success'] and 'qualified' in result['content'].lower():
        job_idx = int(result['custom_id'].split('-')[1])
        qualified.append(weekly_jobs[job_idx])

print(f"Qualified: {len(qualified)} from {len(weekly_jobs)}")

# Stage 2: Deep analysis on qualified subset
stage2_batch = process_jobs_batch(
    qualified,
    task_type='analyze',  # Full analysis
    wait_for_completion=False,
    model='gpt-4o-mini'
)

print(f"Stage 2 batch: {stage2_batch['batch_id']}")
print(f"Deep analyzing {len(qualified)} qualified jobs...")
```

### Stage 3: Interactive Follow-up (Conversation)

```python
# Wait for Stage 2 completion
stage2_results = agent.parse_results(
    agent.download_results(stage2_batch['batch_id'])
)

# Parse analysis results
analyzed_jobs = []
for result in stage2_results:
    if result['success']:
        job_idx = int(result['custom_id'].split('-')[1])
        analyzed_jobs.append({
            'job': qualified[job_idx],
            'analysis': result['content']
        })

# Sort by score/priority from analysis
# (assume analysis includes score)
sorted_analyzed = sorted(
    analyzed_jobs,
    key=lambda x: extract_score(x['analysis']),
    reverse=True
)

# Stage 3: Conversational deep-dive on top 30
conv_agent = ConversationalLeadAgent()

final_prospects = []
for analyzed in sorted_analyzed[:30]:
    job = analyzed['job']

    # Use conversation state for multi-turn analysis
    result = conv_agent.analyze_lead_conversationally(job)

    final_prospects.append({
        'job': job,
        'batch_analysis': analyzed['analysis'],
        'conversational_analysis': result,
        'conversation_id': conv_agent.client_agent.conversation_id
    })

print(f"Final prospects: {len(final_prospects)}")
```

### Summary - Workflow 2

**Input:** 5,000 weekly jobs  
**Stage 1 Batch:** 5,000 qualify → 600 qualified (Cost: $25.00)  
**Stage 2 Batch:** 600 analyze → 100 top (Cost: $3.00)  
**Stage 3 Conversation:** 30 deep-dive (Cost: $0.24)  
**Total Cost:** $28.24  
**Synchronous Equivalent:** ~$50.00  
**Savings:** $21.76 (44%)

---

## Workflow 3: Real-Time + Batch Hybrid

**Use Case:** Interactive exploration during day, batch processing at night

### Daytime: Interactive Exploration

```python
from agents import ConversationalLeadAgent

# User explores a specific company interactively
conv_agent = ConversationalLeadAgent()

# Start conversation about a specific lead
job = {'title': 'Senior Developer', 'company': 'TechCorp', ...}

# Interactive session (real-time)
analysis = conv_agent.start_conversation(job)
print(analysis)

# User asks follow-up
roi = conv_agent.get_roi_estimate(job)
print(roi)

# Generate email
email = conv_agent.generate_email_draft(job)
print(email)

# Get summary
summary = conv_agent.get_conversation_summary()
print(summary)
```

### Evening: Batch Process All

```python
# End of day: Batch process all scraped jobs for tomorrow
all_jobs = scraper_agent.scrape_all_pages(
    city='sfbay',
    category='software',
    max_pages=30
)

# Submit overnight batch
batch = process_jobs_batch(
    all_jobs,
    task_type='analyze',
    wait_for_completion=False,
    model='gpt-4o-mini'
)

print(f"Overnight batch: {batch['batch_id']}")
print("Results ready tomorrow morning")
```

### Next Morning: Review Batch Results

```python
# Check overnight batch
agent = BatchProcessorAgent()
results = agent.parse_results(
    agent.download_results(batch['batch_id'])
)

# Filter top prospects
top = [r for r in results if r['success']][:50]

# Interactive conversation on interesting leads
for result in top[:10]:
    job_idx = int(result['custom_id'].split('-')[1])
    job = all_jobs[job_idx]

    # Interactive follow-up
    conv_agent = ConversationalLeadAgent()
    deep_analysis = conv_agent.analyze_lead_conversationally(job)
    # ... continue conversation
```

---

## Dashboard Integration Example

Complete workflow via REST API:

### 1. Submit Batch via Dashboard

```bash
curl -X POST http://localhost:3000/api/batch/process-scraped \
  -H "Content-Type: application/json" \
  -d '{
    "scrape_results": [...],
    "task_type": "qualify"
  }'

# Response:
{
  "success": true,
  "batch_id": "batch_abc123",
  "job_count": 500,
  "task_type": "qualify",
  "message": "Processing 500 jobs in batch mode. Check status with batch_id."
}
```

### 2. Check Status

```bash
curl http://localhost:3000/api/batch/status/batch_abc123

# Response:
{
  "success": true,
  "status": {
    "id": "batch_abc123",
    "status": "in_progress",
    "request_counts": {
      "total": 500,
      "completed": 350,
      "failed": 2
    }
  }
}
```

### 3. Download Results

```bash
curl http://localhost:3000/api/batch/results/batch_abc123

# Response:
{
  "success": true,
  "batch_id": "batch_abc123",
  "total": 500,
  "successful": 498,
  "failed": 2,
  "results": [...]
}
```

### 4. Start Conversation on Top Lead

```bash
curl -X POST http://localhost:3000/api/conversation/start \
  -H "Content-Type: application/json" \
  -d '{
    "job_posting": {...}
  }'

# Response:
{
  "success": true,
  "conversation_id": "conv_xyz789",
  "analysis": "...",
  "tokens_used": 450
}
```

### 5. Continue Conversation

```bash
curl -X POST http://localhost:3000/api/conversation/roi \
  -H "Content-Type: application/json" \
  -d '{
    "job_posting": {...}
  }'

# Response:
{
  "success": true,
  "conversation_id": "conv_xyz789",
  "roi_estimate": {...},
  "previous_response_id": "resp_abc",
  "total_tokens_used": 780
}
```

---

## Cost Breakdown Example

### Scenario: 1,000 Jobs Scraped Daily

#### Option A: All Synchronous (Naive)

```
1,000 jobs × $0.01/job = $10.00/day
$10.00 × 30 days = $300/month
```

#### Option B: All Batch (Cost-Optimized)

```
1,000 jobs × $0.005/job = $5.00/day
$5.00 × 30 days = $150/month
Savings: $150/month (50%)
```

#### Option C: Hybrid (Batch + Conversation) - RECOMMENDED

```
Daily workflow:
- Batch qualify 1,000 jobs: $5.00
- Filter to 100 qualified
- Batch analyze 100: $0.50
- Filter to 20 top
- Conversational deep-dive 20: $0.16

Total: $5.66/day × 30 days = $169.80/month
Savings: $130.20/month (43%)
```

**Best Value:** Option C provides 43% savings while maintaining interactive analysis on top prospects.

---

## Best Practices

### 1. Use Batch for Volume, Conversation for Quality

- **Batch:** Large-scale filtering and qualification
- **Conversation:** Interactive analysis of top prospects

### 2. Progressive Filtering

```
5,000 jobs
  → Batch qualify → 600 qualified (12%)
  → Batch analyze → 100 top (2%)
  → Conversation → 20 deep-dive (0.4%)
```

### 3. Store Conversation IDs

```python
# Save conversation state for later retrieval
prospect_data = {
    'job': job,
    'conversation_id': conv_agent.client_agent.conversation_id,
    'batch_id': batch_id,
    'created': datetime.now().isoformat()
}

with open(f'prospects/{job_id}.json', 'w') as f:
    json.dump(prospect_data, f)
```

### 4. Monitor Costs

```python
# Track daily costs
daily_costs = {
    'batch_qualify': len(all_jobs) * 0.005,
    'batch_analyze': len(qualified) * 0.005,
    'conversations': len(top_prospects) * 0.008,
    'total': 0
}
daily_costs['total'] = sum(daily_costs.values())

print(f"Daily cost: ${daily_costs['total']:.2f}")
```

---

## Summary

### When to Use What

| Use Case                | Best Tool              | Why                                          |
| ----------------------- | ---------------------- | -------------------------------------------- |
| 500+ jobs to qualify    | **Batch API**          | 50% cost, separate rate limits               |
| Interactive exploration | **Conversation State** | Real-time, multi-turn context                |
| Top 10-20 deep analysis | **Conversation State** | Rich context, follow-up questions            |
| Overnight processing    | **Batch API**          | No wait time, cost effective                 |
| Daily workflow          | **Both (Hybrid)**      | Filter with batch, analyze with conversation |

### Recommended Workflow

1. **Morning:** Check overnight batch results
2. **Day:** Interactive conversation on top prospects
3. **Evening:** Submit new batch for overnight processing
4. **Repeat:** Continuous optimization and cost savings

### Expected Savings

- **Batch Only:** 50% cost reduction
- **Conversation Only:** 58% token savings via chaining
- **Combined (Hybrid):** 40-50% overall savings with better quality

---

For detailed documentation:

- [BATCH_API_GUIDE.md](BATCH_API_GUIDE.md) - Complete batch processing guide
- [CONVERSATION_STATE_GUIDE.md](CONVERSATION_STATE_GUIDE.md) - Conversation state documentation
- [README.md](README.md) - Main project documentation
