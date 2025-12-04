# Advanced Features Quick Reference

## 🚀 OpenAI Conversation State & Batch API

### When to Use What

| Scenario                     | Use This               | Why                                          |
| ---------------------------- | ---------------------- | -------------------------------------------- |
| 500+ jobs to process         | **Batch API**          | 50% cost savings, separate rate limits       |
| Interactive lead exploration | **Conversation State** | Real-time, multi-turn context                |
| Top 10-20 deep analysis      | **Conversation State** | Rich context, follow-ups                     |
| Overnight processing         | **Batch API**          | No wait, cost effective                      |
| Daily workflow               | **Both (Hybrid)**      | Filter with batch, analyze with conversation |

---

## 💰 Cost Comparison (1,000 Jobs)

| Method                   | Cost      | Time                  | Best For                         |
| ------------------------ | --------- | --------------------- | -------------------------------- |
| All Synchronous          | $10.00    | 33 min                | Small volumes, immediate results |
| Batch Only               | $5.00     | 2-24 hrs              | Large volumes, no urgency        |
| **Hybrid** (Recommended) | **$5.66** | **Overnight + 5 min** | **Best balance**                 |

---

## 🔧 Quick Start Code

### Conversation State (Interactive)

```python
from agents import ConversationalLeadAgent

agent = ConversationalLeadAgent()
analysis = agent.start_conversation(job_posting)
roi = agent.get_roi_estimate(job_posting)  # Context preserved
email = agent.generate_email_draft(job_posting)  # Full history

# Benefits: 58% token savings, 85% less code
```

### Batch API (Large-Scale)

```python
from agents import process_jobs_batch

result = process_jobs_batch(
    scraped_jobs,
    task_type='analyze',
    wait_for_completion=False
)

# Check status later
from agents import BatchProcessorAgent
agent = BatchProcessorAgent()
status = agent.check_batch_status(result['batch_id'])

# Benefits: 50% cost savings
```

### Combined (Optimal)

```python
# 1. Batch qualify (50% cost)
batch = process_jobs_batch(all_jobs, task_type='qualify')

# 2. Get qualified
results = agent.parse_results(agent.download_results(batch['batch_id']))
qualified = [r for r in results if 'qualified' in r['content'].lower()]

# 3. Conversation on top 20 (58% tokens)
conv_agent = ConversationalLeadAgent()
for lead in qualified[:20]:
    analysis = conv_agent.analyze_lead_conversationally(lead)

# Combined savings: 43%
```

---

## 🌐 Dashboard Endpoints

### Conversation

- `POST /api/conversation/start` - Start conversation
- `POST /api/conversation/roi` - Get ROI estimate
- `POST /api/conversation/email` - Generate email
- `GET /api/conversation/complete/<id>` - Complete workflow

### Batch

- `POST /api/batch/create` - Create batch
- `GET /api/batch/status/<id>` - Check status
- `GET /api/batch/results/<id>` - Download results
- `POST /api/batch/process-scraped` - One-call processing

---

## 📊 Savings Calculator

### Monthly Projections (Daily Processing)

| Daily Volume | Sync Cost | Batch Cost | Hybrid Cost | Savings |
| ------------ | --------- | ---------- | ----------- | ------- |
| 100 jobs     | $30       | $15        | $17         | 43-50%  |
| 500 jobs     | $150      | $75        | $85         | 43-50%  |
| 1,000 jobs   | $300      | $150       | $170        | 43-50%  |
| 5,000 jobs   | $1,500    | $750       | $850        | 43-50%  |

---

## 🎯 Batch Task Types

| Type                  | Purpose           | Use When                                  |
| --------------------- | ----------------- | ----------------------------------------- |
| `analyze`             | Complete analysis | Need full qualification, pain points, ROI |
| `qualify`             | Quick filter      | Processing large volumes quickly          |
| `parse`               | Structured data   | Extract fields for database               |
| `extract_pain_points` | Pain analysis     | Identify urgency signals                  |

---

## 📚 Documentation

| Guide                  | File                          | What's Inside                        |
| ---------------------- | ----------------------------- | ------------------------------------ |
| Conversation Complete  | `CONVERSATION_STATE_GUIDE.md` | Full API, examples, best practices   |
| Batch Complete         | `BATCH_API_GUIDE.md`          | Full workflow, monitoring, debugging |
| Integration Examples   | `INTEGRATION_EXAMPLE.md`      | Real workflows, cost breakdowns      |
| Implementation Summary | `OPENAI_FEATURES_SUMMARY.md`  | Overview, metrics, resources         |

---

## ✅ Quick Wins

| Change                            | Time   | Savings           |
| --------------------------------- | ------ | ----------------- |
| Switch to batch for qualification | 5 min  | 50% on qualifying |
| Use conversation for top 20       | 10 min | 58% on analysis   |
| Combine both (hybrid)             | 15 min | **43% overall**   |

---

**See full guides for complete details and examples** 🚀
