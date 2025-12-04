# Signal-Based Growth Detection System

## Overview

This system has been **refactored from a direct lead generator into a signal-source growth detector**.

### What Changed

**BEFORE:**

- Scraped Craigslist → Extracted company names/contacts → Generated outreach leads

**NOW:**

- Scrapes Craigslist → Extracts industry signals → Finds companies externally → Scores growth

### Key Philosophy

Craigslist is now a **signal source**, not a lead source. We extract hiring patterns (industry, job type, urgency) and use those signals to find growing companies through external research.

---

## New Workflow

### Phase 1: Signal Extraction (1-2 min)

1. **Scrape Craigslist** - Collect job postings from target city/category
2. **Extract Signals** - Parse each posting for:
   - Industry classification
   - Job category
   - Location
   - Urgency level (high/medium/low)
   - Number of roles
   - Seniority level
   - Growth indicators
3. **Aggregate** - Group signals by industry + location

### Phase 2: External Discovery (2-3 min)

4. **Web Search** - For each industry/location:
   - Find companies operating in that sector
   - Check job boards (Indeed, LinkedIn, Glassdoor)
   - Identify active hiring companies
5. **Company List** - Build list of real companies (with websites)

### Phase 3: Growth Scoring (3-5 min)

6. **Score Each Company** (0-100):
   - **35%** Hiring Velocity - Open positions across job boards
   - **20%** Review Activity - Recent Glassdoor/Google reviews
   - **20%** Web Activity - Blog posts, news, press releases
   - **25%** Expansion - Multiple locations, funding, growth news
7. **Filter** - Return top-scoring companies (score >= 30)

---

## New Data Models

### `JobSignal`

Extracted from Craigslist posts (NO company contacts):

```python
{
    "job_url": "https://...",
    "job_title": "Senior Software Engineer",
    "industry": "Technology",
    "job_category": "Software Engineering",
    "location": "Phoenix, AZ",
    "urgency_level": "high",
    "num_roles": 3,
    "seniority_level": "senior",
    "growth_indicators": ["expanding team", "funded"],
    "required_skills": ["Python", "AWS", "Docker"],
    "is_remote": true
}
```

### `ExternalCompany`

Discovered via web search (NOT from Craigslist):

```python
{
    "company_name": "Acme Tech Corp",
    "website": "https://acme.tech",
    "industry": "Technology",
    "location": "Phoenix, AZ",
    "growth_score": 78.5,  # 0-100
    "signals": {
        "hiring_velocity": {
            "open_positions": 15,
            "job_boards": ["Indeed", "LinkedIn"],
            "departments": ["Engineering", "Sales"],
            "score": 30
        },
        "review_activity": {
            "recent_reviews": 8,
            "rating_trend": "improving",
            "average_rating": 4.2,
            "score": 16
        },
        "web_activity": {
            "recent_blog_posts": 5,
            "press_releases": 2,
            "content_frequency": "high",
            "score": 18
        },
        "expansion": {
            "locations": ["Phoenix", "Austin", "Denver"],
            "funding": "Series B",
            "expansion_news": ["Opened Austin office Q4 2024"],
            "score": 22
        }
    },
    "source": "external_search",
    "matched_signal_industries": ["Technology"]
}
```

---

## New Agents

### 1. `ParserAgent` (Enhanced)

**NEW METHOD:** `extract_job_signal(raw_job) -> JobSignal`

- Uses AI to classify industry, job category, urgency
- Extracts seniority level, number of roles
- Identifies growth indicators
- **Does NOT extract company names or contacts**

### 2. `ExternalSearchAgent` (New)

**Purpose:** Find companies based on industry signals

- Groups signals by industry + location
- Uses OpenAI web search to find companies in each sector
- Checks job boards for active hiring companies
- Returns list of company names + websites

### 3. `GrowthScoringAgent` (New)

**Purpose:** Score companies 0-100 for growth potential

- Researches each company via web search
- Checks hiring velocity across job boards
- Analyzes review activity and trends
- Monitors web/content activity
- Identifies expansion signals (funding, locations, news)
- Assigns weighted score

---

## Updated Orchestrator

`orchestrator_observable.py` now runs a 3-phase pipeline:

```python
# Phase 1: Signal Extraction
raw_jobs = scraper.scrape_listings()
signals = parser.extract_signals_batch(raw_jobs)

# Phase 2: External Discovery
discovered_companies = external_search.find_companies_from_signals(signals)

# Phase 3: Growth Scoring
scored_companies = growth_scorer.score_companies(discovered_companies)
top_companies = growth_scorer.get_top_companies(scored_companies, min_score=30)

return {
    'signals': signals,
    'companies': scored_companies,
    'top_companies': top_companies
}
```

---

## Dashboard Changes

The dashboard now displays:

1. **Signals Tab** - Industry/job signals extracted from Craigslist
2. **Companies Tab** - Externally discovered companies with growth scores
3. **Growth Details** - Detailed scoring breakdown for each company

**REMOVED:**

- Direct outreach generation
- Contact extraction
- Email/phone parsing

**Key difference:** Results are companies found via research, not scraped from posts.

---

## Vector Storage (Predictive)

`vector_agent.py` now stores signal timeseries:

```python
{
    "industry": "Technology",
    "location": "Phoenix",
    "date": "2025-12-04",
    "signal_count": 25,
    "urgency_high": 8,
    "seniority_senior": 12,
    "growth_indicators": ["funded", "expanding"]
}
```

**Use case:** Predict industry growth trends by analyzing signal patterns over time.

---

## Testing

Run the test script:

```bash
python test_signal_workflow.py
```

This will:

1. Scrape a small sample from Craigslist
2. Extract signals
3. Find companies externally
4. Score top companies
5. Display results

---

## API Endpoints (Updated)

### `/api/scrape` (Modified)

**Input:**

```json
{
  "city": "phoenix",
  "category": "sof",
  "max_pages": 2,
  "max_jobs": 50
}
```

**Output:**

```json
{
    "success": true,
    "signals": [...],      // JobSignal objects
    "companies": [...],    // ExternalCompany objects (all scored)
    "top_companies": [...], // High-growth companies (score >= 30)
    "stats": {
        "total_signals": 45,
        "industries_detected": 5,
        "companies_found": 12,
        "high_growth_companies": 8
    }
}
```

---

## Files Modified

### Core Models

- `models.py` - Added `JobSignal` and `ExternalCompany`

### New Agents

- `agents/external_search_agent.py` - NEW
- `agents/growth_scoring_agent.py` - NEW

### Modified Agents

- `agents/parser_agent.py` - Added `extract_job_signal()` method

### Orchestrator

- `orchestrator_observable.py` - Complete workflow refactor

### Dashboard

- `dashboard/leads_app.py` - Updated `/api/scrape` endpoint

### Tests

- `test_signal_workflow.py` - NEW test script

---

## Migration Notes

### What Still Works

- All existing utilities (`utils/`)
- Vector storage (repurposed for signals)
- OpenAI client agent
- Web search integration
- Existing scraper (for signal collection)

### What's Deprecated

- Direct company name extraction from Craigslist
- Contact/email parsing
- Outreach generation
- Lead-to-prospect conversion

### Backward Compatibility

- Old dashboard code paths preserved (may show empty results)
- Old models still exist (unused)
- No breaking changes to utility functions

---

## Next Steps

1. **Test with real data** - Run against multiple cities
2. **Tune scoring weights** - Adjust GrowthScoringAgent weights
3. **Add caching** - Cache external search results
4. **Industry prediction** - Build ML model from signal timeseries
5. **UI polish** - Update dashboard to better display growth scores

---

## Support

For questions or issues with the new workflow, check:

- `test_signal_workflow.py` - Working example
- Agent logs in `logs/` directory
- Signal results in `data/signals/`
