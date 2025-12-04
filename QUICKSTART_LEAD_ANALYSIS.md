# Quick Start: Lead Analysis System

## Run the Example

```powershell
# Navigate to project
cd C:\Users\dusti\git\craigslist_agent

# Set Python path
$env:PYTHONPATH="C:\Users\dusti\git\craigslist_agent"

# Run example
python examples/lead_analysis.py
```

## Use in Your Code

```python
from agents import LeadAnalysisAgent

# Initialize agent
agent = LeadAnalysisAgent()

# Analyze a job posting
result = agent.analyze_posting(
    posting_text=your_job_posting_text,
    posting_url="https://craigslist.org/posting/123",
    enable_web_search=False  # True when web search ready
)

# Check tier
tier = result['lead_scoring']['tier']
score = result['lead_scoring']['final_score']

print(f"{tier}: {score}/30")

# Generate dashboard
summary = agent.generate_dashboard_summary(result)
print(summary)

# Save to file
import json
with open(f"lead_{result['lead_id']}.json", 'w') as f:
    json.dump(result, f, indent=2)
```

## Key Result Fields

```python
# Lead quality
result['lead_scoring']['tier']           # "TIER 1" through "TIER 5"
result['lead_scoring']['final_score']    # 0-30 points
result['lead_scoring']['recommendation'] # "PURSUE", "MONITOR", "REJECT"

# Company info
result['company']['name']
result['company']['location']
result['company']['contact']

# Pain points
result['needs_analysis']['primary_pain_points']
result['needs_analysis']['estimated_pain_severity']

# Value props
result['value_propositions'][0]['text']

# Call script
result['call_script']['main_script']['diagnosis_question']
result['call_script']['target_contact']

# ML features
result['ml_features']
```

## Filter for TIER 1-2 Leads

```python
if result['lead_scoring']['tier'] in ['TIER 1', 'TIER 2']:
    # High-quality lead - pursue immediately
    contact = result['call_script']['target_contact']
    phone = result['company']['contact']['phone']
    value_prop = result['value_propositions'][0]['text']

    print(f"CALL: {contact} at {phone}")
    print(f"SAY: {value_prop}")
```

## Customize Scoring

Edit `agents/lead_analysis_agent.py`:

```python
def _score_forecasting_pain(self, signals: Dict) -> int:
    score = 0

    # Adjust point values
    if 'seasonal' in business_model:
        score += 5  # Change this value

    return min(score, 12)
```

## Add Industry Pain Points

Edit `prompts/system_prompt.py`:

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

## Output Files

After running, check:

- `output/leads/lead_[company]_[id].json` - Full data
- `output/leads/lead_[company]_[id]_summary.md` - Dashboard

## Tier Meanings

- **TIER 1 (20-30 pts)**: TOP PRIORITY - Call immediately
- **TIER 2 (15-19 pts)**: QUALIFIED LEAD - Add to pipeline
- **TIER 3 (10-14 pts)**: MONITOR - Watch for changes
- **TIER 4 (5-9 pts)**: LOW PRIORITY - Deprioritize
- **TIER 5 (0-4 pts)**: REJECT - Skip

## Troubleshooting

**"Module not found"**

```powershell
$env:PYTHONPATH="C:\Users\dusti\git\craigslist_agent"
```

**Low scores for good leads**

- Check if AI extracted data correctly in Step 1
- Adjust scoring weights if needed
- Enable web search for Step 2

**Generic value propositions**

- Add more industry examples in `prompts/system_prompt.py`

## Next Steps

1. Test with real Craigslist data
2. Implement web search (Step 2)
3. Integrate with your CRM
4. Build automated outreach

See `LEAD_ANALYSIS_README.md` for full documentation.
