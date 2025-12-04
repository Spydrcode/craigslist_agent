# Dashboard API Documentation

## Overview

The Forecasta Lead Analysis Dashboard provides a comprehensive REST API that integrates all agents and the RAG framework.

**Base URL:** `http://localhost:3000`

---

## Lead Analysis Endpoints

### GET /api/leads

Get all leads with optional filters.

**Query Parameters:**

- `tier` - Filter by tier (TIER 1-5)
- `status` - Filter by status (new, contacted, etc.)
- `industry` - Filter by industry

**Response:**

```json
{
  "leads": [...],
  "count": 25
}
```

### GET /api/stats

Get lead statistics.

**Response:**

```json
{
  "total": 25,
  "tier_1": 5,
  "tier_2": 8,
  "avg_score": 15.2,
  "by_industry": {...},
  "by_status": {...}
}
```

### POST /api/analyze

Analyze a new job posting.

**Body:**

```json
{
  "posting_text": "Job description...",
  "posting_url": "https://..."
}
```

**Response:**

```json
{
  "success": true,
  "lead": {...},
  "summary": "markdown summary"
}
```

### POST /api/lead/<lead_id>/update

Update lead status or add notes.

**Body:**

```json
{
  "status": "contacted",
  "notes": "Called, left voicemail"
}
```

---

## Scraper Agent Endpoints

### POST /api/scrape

Scrape jobs from Craigslist.

**Body:**

```json
{
  "city": "sfbay",
  "category": "sof",
  "keywords": ["python", "engineer"],
  "max_pages": 3
}
```

**Response:**

```json
{
  "success": true,
  "jobs_found": 45,
  "jobs": [
    {
      "title": "Senior Python Engineer",
      "url": "https://...",
      "location": "San Francisco",
      "posted_date": "2025-11-29T..."
    }
  ]
}
```

**City Codes:** sfbay, newyork, losangeles, chicago, etc.
**Category Codes:** sof (software), eng (engineering), etc.

---

## Parser Agent Endpoints

### POST /api/parse

Parse a job posting with AI.

**Body:**

```json
{
  "job_text": "Full job description...",
  "title": "Software Engineer",
  "url": "https://...",
  "location": "Remote"
}
```

**Response:**

```json
{
  "success": true,
  "parsed_job": {
    "title": "Software Engineer",
    "skills": ["Python", "AWS", "Docker"],
    "pain_points": ["Scaling issues", "Legacy system"],
    "salary_min": 100000,
    "salary_max": 150000,
    "is_remote": true,
    "is_hybrid": false
  }
}
```

---

## Vector Search Endpoints

### POST /api/vector/search

Search jobs using semantic similarity.

**Body:**

```json
{
  "query": "experienced Python developer with cloud skills",
  "top_k": 5
}
```

**Response:**

```json
{
  "success": true,
  "results": [
    {
      "job_id": "abc123",
      "title": "Senior Python Engineer",
      "score": 0.95,
      "metadata": {...}
    }
  ]
}
```

---

## Database Query Endpoints

### POST /api/database/search

Search jobs in Supabase database.

**Body:**

```json
{
  "keywords": ["python", "remote"],
  "location": "San Francisco",
  "min_salary": 100000,
  "is_remote": true,
  "limit": 10
}
```

**Response:**

```json
{
  "success": true,
  "count": 7,
  "jobs": [
    {
      "title": "Python Developer",
      "company": "Tech Corp",
      "location": "San Francisco",
      "salary_min": 120000,
      "salary_max": 160000,
      "skills": ["Python", "Django", "PostgreSQL"]
    }
  ]
}
```

### GET /api/database/stats

Get database statistics.

**Response:**

```json
{
  "success": true,
  "stats": {
    "total_jobs": 1500,
    "jobs_this_week": 45,
    "avg_salary": 125000,
    "top_skills": ["Python", "JavaScript", "AWS"],
    "top_locations": ["San Francisco", "New York", "Remote"]
  }
}
```

---

## RAG Integration Endpoints

### POST /api/rag/query

Ask questions using RAG (Retrieval Augmented Generation).

**Body:**

```json
{
  "question": "What are the most in-demand skills for software engineers in the Bay Area?"
}
```

**Response:**

```json
{
  "success": true,
  "question": "What are the most in-demand skills...",
  "answer": "Based on recent job postings, the most in-demand skills are..."
}
```

**Note:** RAG endpoints only available if RAG integration is installed.

---

## Pipeline Endpoints

### POST /api/pipeline/run

Run the full scraping and analysis pipeline.

**Body:**

```json
{
  "city": "sfbay",
  "category": "sof",
  "keywords": ["python", "senior"],
  "max_pages": 2
}
```

**Response:**

```json
{
  "success": true,
  "jobs_scraped": 40,
  "jobs_parsed": 40,
  "jobs_stored": 38,
  "summary": {
    "vector_stored": 38,
    "database_stored": 38
  }
}
```

### POST /api/pipeline/analyze-and-qualify

Run scraping + lead qualification pipeline (end-to-end).

**Body:**

```json
{
  "city": "sfbay",
  "category": "sof",
  "keywords": ["forecasting", "analytics"],
  "max_pages": 3
}
```

**Response:**

```json
{
  "success": true,
  "jobs_scraped": 50,
  "qualified_leads": 8,
  "leads": [
    {
      "company": "ABC Analytics",
      "tier": "TIER 1",
      "score": 24
    },
    {
      "company": "Data Insights Inc",
      "tier": "TIER 2",
      "score": 17
    }
  ]
}
```

**This endpoint:**

1. Scrapes jobs from Craigslist
2. Analyzes each as potential Forecasta lead
3. Saves TIER 1-2 leads to dashboard
4. Returns qualified leads summary

---

## System Endpoints

### GET /api/agents/status

Check which agents are available.

**Response:**

```json
{
  "lead_analysis_agent": true,
  "scraper_agent": true,
  "parser_agent": true,
  "vector_agent": true,
  "database_agent": true,
  "orchestrator": true,
  "rag_integration": true,
  "rag_available": true
}
```

### GET /api/industries

Get list of all industries from leads.

**Response:**

```json
["Construction/Trades", "Trucking/Logistics", "Manufacturing", ...]
```

### GET /api/export/csv

Export all leads to CSV file.

**Response:** CSV file download

---

## Error Responses

All endpoints return errors in this format:

```json
{
  "error": "Description of error"
}
```

**HTTP Status Codes:**

- `200` - Success
- `400` - Bad request (missing parameters)
- `404` - Not found
- `500` - Server error
- `503` - Service unavailable (e.g., RAG not installed)

---

## Examples Using cURL

### Analyze a Job Posting

```bash
curl -X POST http://localhost:3000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "posting_text": "We are seeking a Project Manager for our construction company...",
    "posting_url": "https://craigslist.org/123"
  }'
```

### Scrape Jobs

```bash
curl -X POST http://localhost:3000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "city": "sfbay",
    "category": "sof",
    "keywords": ["python"],
    "max_pages": 1
  }'
```

### Vector Search

```bash
curl -X POST http://localhost:3000/api/vector/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "remote python developer",
    "top_k": 5
  }'
```

### Run Full Pipeline

```bash
curl -X POST http://localhost:3000/api/pipeline/analyze-and-qualify \
  -H "Content-Type: application/json" \
  -d '{
    "city": "sfbay",
    "category": "trd",
    "keywords": ["roofing", "construction"],
    "max_pages": 2
  }'
```

---

## Python Examples

### Using requests library

```python
import requests

# Analyze posting
response = requests.post(
    'http://localhost:3000/api/analyze',
    json={
        'posting_text': 'Job description...',
        'posting_url': 'https://...'
    }
)
result = response.json()
print(f"Tier: {result['lead']['lead_scoring']['tier']}")

# Scrape and qualify
response = requests.post(
    'http://localhost:3000/api/pipeline/analyze-and-qualify',
    json={
        'city': 'sfbay',
        'category': 'trd',
        'keywords': ['construction'],
        'max_pages': 2
    }
)
result = response.json()
print(f"Found {result['qualified_leads']} qualified leads")
```

---

## Integration Notes

**All agents are initialized lazily** - they only load when first needed, reducing startup time.

**RAG integration is optional** - if RAG agents aren't available, those endpoints return 503.

**Vector and Database agents** require Pinecone and Supabase credentials in `.env`.

**Pipeline endpoints** combine multiple agents for end-to-end workflows.

---

## Rate Limits

No rate limits currently enforced, but consider:

- Craigslist scraping: Be respectful, use delays
- OpenAI API: Monitor token usage
- Pinecone: Check plan limits
- Supabase: Monitor database usage

---

## Extending the API

To add new endpoints, edit `dashboard/leads_app.py`:

```python
@app.route('/api/your-endpoint', methods=['POST'])
def your_endpoint():
    # Your code here
    return jsonify({'success': True})
```
