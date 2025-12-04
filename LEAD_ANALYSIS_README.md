# Lead Analysis System for Forecasta

This system implements an AI-powered 8-step workflow to analyze job postings and identify high-quality leads for Forecasta, a forecasting analytics service.

## Overview

The Lead Analysis Agent automatically:

1. **Extracts structured data** from job postings
2. **Researches companies** online (optional)
3. **Scores leads** using a 30-point qualification algorithm
4. **Identifies forecasting pain points** specific to each business
5. **Generates custom value propositions** in industry language
6. **Creates personalized cold call scripts**
7. **Stores data in ML-ready format**
8. **Outputs dashboard summaries** for sales teams

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up your OpenAI API key in .env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview
```

### Basic Usage

```python
from agents import LeadAnalysisAgent

# Initialize the agent
lead_agent = LeadAnalysisAgent()

# Analyze a job posting
result = lead_agent.analyze_posting(
    posting_text=job_posting_text,
    posting_url="https://craigslist.org/...",
    enable_web_search=False  # Set to True when web search is implemented
)

# Generate dashboard summary
summary = lead_agent.generate_dashboard_summary(result)
print(summary)

# Save lead data
import json
with open(f"lead_{result['lead_id']}.json", 'w') as f:
    json.dump(result, f, indent=2)
```

### Run Example

```bash
python examples/lead_analysis.py
```

## The 8-Step Workflow

### Step 1: Data Extraction & Structuring

Extracts:

- Company information (name, location, contact)
- Job details (title, salary, benefits)
- Business signals (industry, business model, growth indicators)
- Red flags (MLM, recruiting agencies, spam)
- Professionalism score (1-10)

### Step 2: Company Research (Optional)

When enabled, performs web searches to find:

- Official website
- Employee count estimates
- Decision makers (names, titles)
- LinkedIn company page
- Recent growth signals
- Online presence quality

**Note:** Web search integration is currently a placeholder. Implement using tools like SerpAPI, Google Custom Search, or other web search APIs.

### Step 3: Lead Scoring

30-point scoring algorithm across 4 categories:

**Company Scale (max 9 points)**

- Multiple positions posted: +3
- Salary $50K+: +2
- Manager/supervisor roles: +2
- Benefits mentioned: +2
- Employee count 20-200: +2

**Forecasting Pain Indicators (max 12 points)**

- Seasonal business: +5
- Project-based work: +5
- Volume-dependent operations: +4
- Growth language: +3
- Hiring 5+ positions: +3

**Accessibility (max 7 points)**

- Local/regional ownership: +3
- <200 employees: +2
- Decision maker identified: +2
- Direct employer (not agency): +1

**Data Quality (max 2 points)**

- Professionalism score 7-10: +2
- Professionalism score 5-6: +1

**Tier Assignment:**

- 20-30 points: TIER 1 - TOP PRIORITY
- 15-19 points: TIER 2 - QUALIFIED LEAD
- 10-14 points: TIER 3 - MONITOR
- 5-9 points: TIER 4 - LOW PRIORITY
- 0-4 points: TIER 5 - REJECT

**Automatic Disqualifiers:**

- 2+ red flags
- Company not verified as legitimate
- Recruiting agency posting
- National chain company
- MLM language

### Step 4: Needs Analysis

Identifies specific forecasting pain points by business type:

**Project-Based Businesses** (Construction, Restoration)

- Pain: Lumpy demand makes staffing difficult
- Solution: Pipeline-to-capacity forecasting

**Seasonal Businesses** (Landscaping, Roofing, HVAC)

- Pain: When to ramp up/down for peak seasons
- Solution: Multi-year pattern analysis + leading indicators

**Volume-Driven** (Manufacturing, Call Centers)

- Pain: Matching production to staffing
- Solution: Demand forecasting with 30-60 day horizon

**Trucking/Logistics**

- Pain: Driver capacity planning by lane
- Solution: Route volume forecasting

**High-Growth Companies**

- Pain: Scaling headcount without over-hiring
- Solution: Growth-adjusted capacity forecasting

### Step 5: Value Proposition Generation

Creates 2-3 custom value propositions using the formula:

> "[Action][specific pain] so you can [Quantified Outcome] instead of [Current Bad State]"

**Example for Construction:**

> "Turn your project pipeline into crew capacity forecasts so you know if you need 5 or 15 workers next quarter - not next week."

**Example for Trucking:**

> "Predict driver requirements by lane type 90 days out so you match capacity to contracts instead of paying deadhead miles or missing revenue."

### Step 6: Call Script Generation

Generates personalized cold call scripts with:

1. **Introduction** (5-10 seconds)
2. **Pattern Interrupt** (references their specific posting)
3. **Diagnosis Question** (about their #1 pain point)
4. **Value Statement** (if they confirm the pain)
5. **Meeting Ask** (specific time/format)
6. **Objection Handling** (4 common objections)

Scripts use conversational language, avoid jargon, and position Forecasta as a peer consultant, not a salesperson.

### Step 7: ML Feature Engineering

Encodes data for machine learning:

- Industry codes
- Business model codes
- Company size buckets
- Pain severity scores (0-1)
- Accessibility scores (0-1)
- Data quality scores (0-1)

### Step 8: Dashboard Summary

Generates markdown-formatted summary with:

- Quick stats (tier, score, priority)
- Company overview
- Why they need Forecasta
- Recommended approach
- Next actions checklist
- Research notes

## Output Format

### JSON Structure

```json
{
  "lead_id": "uuid",
  "version": "1.0",
  "created_timestamp": "ISO_datetime",
  "source": "craigslist",
  "company": { ... },
  "job": { ... },
  "business_signals": { ... },
  "red_flags": { ... },
  "company_research": { ... },
  "lead_scoring": { ... },
  "needs_analysis": { ... },
  "value_propositions": [ ... ],
  "call_script": { ... },
  "ml_features": { ... },
  "outcome_tracking": {
    "status": "new",
    "contact_attempts": 0,
    "conversion_probability": 0.75
  }
}
```

### Dashboard Summary (Markdown)

See `examples/lead_analysis.py` for sample output.

## Integration with Existing Pipeline

The Lead Analysis Agent can be integrated into your existing scraping pipeline:

```python
from orchestrator import Orchestrator
from agents import LeadAnalysisAgent

# In orchestrator.py
class Orchestrator:
    def __init__(self):
        # ... existing initialization ...
        self.lead_agent = LeadAnalysisAgent()

    def run_pipeline(self, ...):
        # ... existing scraping and parsing ...

        # Add lead analysis step
        for parsed_job in parsed_jobs:
            lead_analysis = self.lead_agent.analyze_posting(
                posting_text=parsed_job.description,
                posting_url=parsed_job.url
            )

            # Only process TIER 1-2 leads
            if lead_analysis['lead_scoring']['tier'] in ['TIER 1', 'TIER 2']:
                # Save to database
                # Generate call scripts
                # Alert sales team
                pass
```

## Customization

### Industry-Specific Pain Points

Add new industries in `prompts/system_prompt.py`:

```python
PAIN_POINTS_BY_INDUSTRY = {
    "your_industry": {
        "pain": "Specific challenge",
        "why": "Business impact",
        "current": "Current approach",
        "solution": "Forecasta solution"
    }
}
```

### Scoring Algorithm

Adjust weights in `agents/lead_analysis_agent.py`:

```python
def _score_forecasting_pain(self, signals: Dict) -> int:
    score = 0
    # Modify point values here
    if 'seasonal' in business_model:
        score += 5  # Adjust this value
    return min(score, 12)
```

### Value Proposition Templates

Add examples in `prompts/system_prompt.py`:

```python
VALUE_PROP_EXAMPLES = {
    "your_industry": "Your custom value prop template..."
}
```

## System Prompts

All AI prompts are centralized in `prompts/system_prompt.py`:

- `SYSTEM_PROMPT`: Overall agent identity
- `WORKFLOW_INSTRUCTIONS`: 8-step workflow
- `STEP_X_INSTRUCTIONS`: Instructions for each step
- `LEAD_SCORING_ALGORITHM`: Scoring rules
- `PAIN_POINTS_BY_INDUSTRY`: Industry-specific pain points
- `VALUE_PROP_EXAMPLES`: Value proposition templates
- `CALL_SCRIPT_TEMPLATE`: Call script structure

## Future Enhancements

### Web Search Integration

Implement `_step_2_company_research()` using:

- SerpAPI
- Google Custom Search API
- LinkedIn API
- Company data providers (Clearbit, ZoomInfo)

### CRM Integration

Export leads to:

- Salesforce
- HubSpot
- Pipedrive
- Custom CRM

### A/B Testing

Track which value propositions and call scripts convert best.

### Machine Learning

Train models on outcome data to:

- Improve lead scoring accuracy
- Predict conversion probability
- Optimize pain point identification
- Generate better value propositions

### Automated Follow-up

- Email sequence generation
- LinkedIn message templates
- Follow-up scheduling

## File Structure

```
craigslist_agent/
├── agents/
│   └── lead_analysis_agent.py    # Main lead analysis agent
├── prompts/
│   ├── __init__.py
│   └── system_prompt.py           # All AI prompts and templates
├── examples/
│   └── lead_analysis.py           # Example usage
└── output/
    └── leads/                     # Generated lead files
        ├── lead_*.json            # Structured data
        └── lead_*_summary.md      # Dashboard summaries
```

## Testing

```bash
# Run example with sample posting
python examples/lead_analysis.py

# Test with your own posting
python -c "
from agents import LeadAnalysisAgent
agent = LeadAnalysisAgent()
result = agent.analyze_posting('''
[paste your job posting here]
''')
print(agent.generate_dashboard_summary(result))
"
```

## Troubleshooting

### "No valid JSON found in response"

The AI response didn't contain parseable JSON. Check:

- OpenAI API key is valid
- Model has sufficient context window
- Posting text isn't corrupted

### Low lead scores for good prospects

Adjust scoring algorithm weights in `lead_analysis_agent.py`.

### Missing pain points

Add industry-specific pain points in `prompts/system_prompt.py`.

### Generic value propositions

Provide more examples in `VALUE_PROP_EXAMPLES`.

## License

See LICENSE file in repository root.

## Support

For issues or questions, please open an issue on GitHub.
