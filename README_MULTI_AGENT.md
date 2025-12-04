# Forecasta Lead Qualification System

A complete multi-agent system for processing and qualifying Craigslist job postings into sales leads.

## Architecture

### 6 Specialized Agents

1. **ExtractorAgent** - Parses job postings into structured JSON
   - Extracts company name, job title, salary, location, contact info
   - Identifies keywords and red flags
   - Calculates professionalism score (1-10)

2. **ResearcherAgent** - Performs web research on companies
   - Verifies company legitimacy
   - Finds employee count, industry, website
   - Identifies decision makers
   - Determines if local to Phoenix area

3. **ScorerAgent** - Calculates lead quality (0-30 points)
   - **Company Scale** (9 pts): Multiple positions, salary $50K+, manager roles, benefits
   - **Forecasting Pain** (12 pts): Seasonal, project-based, volume-driven, growth
   - **Accessibility** (7 pts): Local, <200 employees, decision maker found
   - **Data Quality** (2 pts): Professionalism score 7-10
   - **Assigns Tier**: 1 (Hot, 20-30pts) → 5 (Disqualified, 0-4pts)

4. **AnalyzerAgent** - Identifies forecasting pain points
   - Maps pain categories (seasonal, project uncertainty, volume variability, growth, bulk hiring)
   - Identifies forecast opportunities by industry
   - Generates strategic insights and opening hooks
   - Skipped if score < 10

5. **WriterAgent** - Generates sales collateral
   - Value proposition using formula: "Predict [X] [timeframe] ahead so you [benefit] instead of [problem]"
   - Structured call scripts with objection handling
   - Email templates with follow-ups
   - Skipped if tier > 3

6. **StorerAgent** - Persists data for ML and retrieval
   - Saves individual lead JSON files
   - Updates master CSV for quick filtering
   - Provides analytics aggregation

### Orchestrator

Coordinates workflow between agents:
```
ExtractorAgent → ResearcherAgent → ScorerAgent → AnalyzerAgent → WriterAgent → StorerAgent
```

**Features:**
- Error handling with 3x retry logic
- Conditional skipping (skip Analyzer if score < 10, skip Writer if tier > 3)
- State management and progress tracking
- Batch processing support

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Ensure directory structure exists
mkdir -p data/leads data/schemas dashboard/frontend
```

## Usage

### 1. Start Backend API

```bash
python dashboard/backend.py
```

Server runs at `http://localhost:5000`

### 2. Access Dashboard

Open browser to `http://localhost:5000`

### 3. Process Leads Programmatically

```python
from agents.orchestrator import Orchestrator

# Initialize
orchestrator = Orchestrator(data_dir="data/leads")

# Process single posting
result = orchestrator.process_posting(
    posting_html="<html>...</html>",
    posting_url="https://phoenix.craigslist.org/..."
)

# Process batch
results = orchestrator.process_batch([
    {"html": "...", "url": "..."},
    {"html": "...", "url": "..."}
])

# Retrieve leads
all_leads = orchestrator.get_all_leads()
tier_1_leads = orchestrator.get_all_leads(filters={"tier": 1})

# Get analytics
analytics = orchestrator.get_analytics()

# Update lead status
orchestrator.update_lead_status("lead_id", "contacted", "Left voicemail")

# Generate bulk scripts
scripts = orchestrator.generate_bulk_scripts(["lead_1", "lead_2"])

# Export to CSV
csv_data = orchestrator.export_leads_csv(["lead_1", "lead_2"])
```

## API Endpoints

### POST /api/search
Trigger Craigslist scraping (placeholder - integrate with ScraperAgent)

**Request:**
```json
{
  "location": "phoenix",
  "date_range": "7",
  "industries": ["retail", "hospitality"]
}
```

### GET /api/leads
Get filtered leads

**Query params:** `tier`, `status`, `industry`, `is_local`

### GET /api/leads/:id
Get full lead details

### POST /api/leads/:id/update
Update lead status and notes

**Request:**
```json
{
  "status": "contacted",
  "notes": "Left voicemail"
}
```

### POST /api/bulk/scripts
Generate call scripts for selected leads

**Request:**
```json
{
  "lead_ids": ["lead_1", "lead_2"]
}
```

### POST /api/bulk/emails
Generate email templates for selected leads

### POST /api/export/csv
Export leads to CSV

### GET /api/analytics
Get dashboard analytics (totals, by tier, by status, by industry)

## Dashboard Features

### 1. Search Parameters Panel
- Location dropdown (Phoenix metro areas)
- Date range picker (1, 3, 7, 30 days)
- Industry checkboxes
- Search button

### 2. Analytics Overview
- Total leads, Tier 1 count, Tier 2 count, Avg score
- Charts: Leads by tier (bar), by status (doughnut), by industry (horizontal bar)

### 3. Lead Table
- Sortable columns: Company, Job Title, Industry, Score, Tier, Status, Location
- Filterable by tier and status
- Checkboxes for bulk selection
- View button to see full details

### 4. Bulk Actions
- Select All
- Generate Scripts (for selected leads)
- Generate Emails (for selected leads)
- Export CSV (for selected leads)

### 5. Lead Detail Modal
- Full company information
- Value proposition
- Call script (structured sections)
- Email template
- Pain points analysis
- Status update form with notes

## Scoring Algorithm

### Disqualification Criteria
- 2+ red flags
- Can't verify company
- National chain
- MLM indicators

### Point Allocation (Max 30)

**Company Scale (9 points):**
- Multiple positions: +3
- Salary $50K+: +2
- Manager/director roles: +2
- Benefits mentioned: +2

**Forecasting Pain (12 points):**
- Seasonal business: +5
- Project-based work: +5
- Volume-driven operations: +4
- Growth language: +3

**Accessibility (7 points):**
- Local company: +3
- <200 employees: +2
- Decision maker found: +2

**Data Quality (2 points):**
- Professionalism 7-10: +2
- Professionalism 5-6: +1
- Professionalism <5: +0

### Tier Assignment
- **Tier 1 (Hot)**: 20-30 points
- **Tier 2 (Warm)**: 15-19 points
- **Tier 3 (Medium)**: 10-14 points
- **Tier 4 (Cold)**: 5-9 points
- **Tier 5 (Disqualified)**: 0-4 points

## Value Proposition Formula

```
Predict [specific thing] [timeframe] ahead so you [benefit] instead of [current problem]
```

**Examples:**
- "Predict customer traffic 2-4 weeks ahead so you optimize staffing levels instead of overstaffing during slow periods"
- "Predict project timelines 6-12 weeks ahead so you plan crew assignments instead of project delays"

## Call Script Structure

1. **Intro**: "Hi, this is [name] with Forecasta. Do you have 60 seconds?"
2. **Pattern Interrupt**: Reference their specific posting
3. **Diagnosis Question**: Ask about their #1 pain point
4. **Value Statement**: What Forecasta does in their language
5. **Social Proof**: Similar companies
6. **Meeting Ask**: "15 minutes Thursday at 10am or Friday afternoon?"
7. **Objection Handling**: Not interested, too busy, send info

## Data Schema

See [data/schemas/lead_schema.json](data/schemas/lead_schema.json) for complete schema.

## File Structure

```
craigslist_agent/
├── agents/
│   ├── __init__.py
│   ├── extractor.py
│   ├── researcher.py
│   ├── scorer.py
│   ├── analyzer.py
│   ├── writer.py
│   ├── storer.py
│   └── orchestrator.py
├── dashboard/
│   ├── backend.py
│   └── frontend/
│       ├── index.html
│       ├── app.js
│       └── styles.css
├── data/
│   ├── leads/
│   │   ├── lead_*.json
│   │   └── leads_master.csv
│   └── schemas/
│       └── lead_schema.json
├── requirements.txt
└── README_MULTI_AGENT.md
```

## Testing

### Test Single Agent

```python
from agents.extractor import ExtractorAgent

extractor = ExtractorAgent()
result = extractor.extract(posting_html, posting_url)
print(result)
```

### Test Full Pipeline

```python
from agents.orchestrator import Orchestrator

orchestrator = Orchestrator()
result = orchestrator.process_posting(posting_html, posting_url)

print(f"Lead ID: {result['lead_id']}")
print(f"Tier: {result['tier']}")
print(f"Score: {result['score']}")
print(f"Value Prop: {result.get('value_proposition')}")
```

### Test with Sample Data

Create a test posting HTML and run through the system to verify all agents execute correctly.

## Integration with Existing System

This multi-agent system is designed to integrate with your existing Craigslist scraper:

1. **ScraperAgent** → Extract postings → **ExtractorAgent** (new system starts here)
2. Use existing database/vector storage alongside StorerAgent
3. Dashboard can coexist with other interfaces

## Next Steps

1. **Integrate Web Search**: Add actual web search API (Anthropic web search, Serper, etc.) to ResearcherAgent
2. **Connect Scraper**: Link existing ScraperAgent to feed postings into orchestrator
3. **Add Authentication**: Secure dashboard with login
4. **ML Training**: Use stored data to train models for better scoring
5. **Email Integration**: Connect email sending for automated outreach
6. **CRM Sync**: Sync leads to Salesforce/HubSpot
7. **Webhook Notifications**: Alert when tier 1 leads are found

## License

MIT
