# Quick Start Guide: Intelligent Company Prospecting

Get up and running with intelligent prospecting in 10 minutes.

## Step 1: Install Dependencies (2 minutes)

```bash
# Install enhanced dependencies
pip install -r requirements_enhanced.txt
```

## Step 2: Configure API Keys (3 minutes)

Create a `.env` file with at minimum:

```env
# REQUIRED
OPENAI_API_KEY=sk-your-openai-key-here

# RECOMMENDED (but optional for testing)
PINECONE_API_KEY=your-pinecone-key
PINECONE_ENVIRONMENT=us-east-1
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-key
```

**Getting API Keys**:
- OpenAI: https://platform.openai.com/api-keys
- Pinecone: https://app.pinecone.io (free tier available)
- Supabase: https://supabase.com (free tier available)

## Step 3: Run Your First Prospecting Search (5 minutes)

```bash
# Find tech companies in San Francisco Bay Area
python main_prospecting.py prospect --city sfbay --category sof --pages 3
```

This will:
1. Scrape ~60-90 tech job postings from Craigslist
2. Analyze growth signals for each company
3. Score and prioritize prospects
4. Export results to CSV and JSON

## Expected Output

```
================================================================================
PROSPECTING RESULTS
================================================================================

📊 Statistics:
   Jobs Scraped: 73
   Companies Identified: 21
   Companies Researched: 8
   Qualified Prospects: 5
   High Priority: 2
   Total Opportunities: 11

================================================================================
TOP PROSPECTS
================================================================================

1. TechStartup Inc
   Score: 82.5/100 | Priority: HIGH
   Location: San Francisco, CA
   Jobs: 4
   Growth: scaling (score: 0.75)
   Top Opportunity: Data Engineering
   Confidence: 87%
   Value: $50K-$150K
   Approach: Direct outreach to CTO or Head of Engineering...

✅ Exported to: output/prospects/prospects_20240115_143022.csv
✅ Detailed data: output/prospects/prospects_20240115_143022.json
```

## Step 4: Review Results

Open the CSV file in Excel or Google Sheets:

```
Company | Lead Score | Priority | Job Count | Growth Stage | Top Opportunity | Value
--------|-----------|----------|-----------|--------------|----------------|--------
TechStartup Inc | 82.5 | HIGH | 4 | scaling | Data Engineering | $50K-$150K
DataCorp | 75.3 | HIGH | 3 | rapid_growth | AI/ML Consulting | $75K-$200K
...
```

## Step 5: Analyze Specific Prospects

```bash
# Deep dive into a specific prospect
python main_prospecting.py analyze --file output/prospects/prospects_20240115_143022.json
```

This shows detailed analysis including:
- Growth signals and evidence
- Service opportunities with reasoning
- Outreach plan and talking points
- Decision maker targets

## Customization

### Find AI/ML Companies

```bash
python main_prospecting.py prospect --city sfbay --category sof \
    --keywords "machine learning" "AI" "data science" --pages 5
```

### Adjust Quality Thresholds

```bash
# Only show high-quality leads
python main_prospecting.py prospect --city sfbay --category sof \
    --min-growth 0.5 --min-score 70
```

### Search Multiple Cities

```bash
# San Francisco
python main_prospecting.py prospect --city sfbay --category sof --pages 3

# Seattle
python main_prospecting.py prospect --city seattle --category sof --pages 3

# New York
python main_prospecting.py prospect --city newyork --category sof --pages 3
```

## Common Issues

### "Configuration Error: Missing OPENAI_API_KEY"

**Solution**: Add your OpenAI API key to `.env`:
```env
OPENAI_API_KEY=sk-your-key-here
```

### "No qualified prospects found"

**Solutions**:
1. Lower thresholds: `--min-growth 0.2 --min-score 30`
2. Increase pages: `--pages 10`
3. Remove keyword filters
4. Try different city/category

### Slow Performance

**Solutions**:
1. Reduce pages: `--pages 2`
2. Disable company research temporarily by setting `ENABLE_WEB_RESEARCH=false` in `.env`
3. Use `gpt-3.5-turbo` instead of `gpt-4` (faster, cheaper, slightly less accurate)

## Next Steps

### 1. Customize Service Offerings

Edit [config_enhanced.py](config_enhanced.py#L87) to match your services:

```python
SERVICE_OFFERINGS: List[str] = [
    "Your Service 1",
    "Your Service 2",
    # Add your services
]
```

### 2. Set Up Enhanced Research

Add optional API keys to `.env` for better company research:

```env
GOOGLE_API_KEY=your-google-api-key
CRUNCHBASE_API_KEY=your-crunchbase-key
HUNTER_API_KEY=your-hunter-key
```

### 3. Automate with Cron/Scheduler

Run weekly to catch new opportunities:

```bash
# Linux/Mac crontab
0 9 * * 1 /path/to/venv/bin/python /path/to/main_prospecting.py prospect --city sfbay --category sof

# Windows Task Scheduler
schtasks /create /tn "ProspectingWeekly" /tr "python C:\path\to\main_prospecting.py prospect --city sfbay --category sof" /sc weekly /d MON /st 09:00
```

### 4. Integrate with CRM

Export CSV to:
- HubSpot (import as contacts/companies)
- Salesforce (import as leads)
- Pipedrive (import as deals)
- Google Sheets (for team collaboration)

### 5. Track Conversions

Use the database to track:
- Which prospects you contacted
- Response rates
- Conversion to clients
- Optimize scoring based on actual results

## Tips for Best Results

1. **Start Narrow**: Target specific niches first (e.g., "AI startups in fintech")
2. **Quality over Quantity**: Better to have 5 high-quality prospects than 50 mediocre ones
3. **Act Fast**: High urgency companies need quick response
4. **Personalize**: Use the talking points and evidence in your outreach
5. **Track Results**: Record which signals predict successful conversions

## Support

- **Documentation**: See [README_ENHANCED.md](README_ENHANCED.md)
- **Configuration**: See [config_enhanced.py](config_enhanced.py)
- **Examples**: See [examples/](examples/) directory

## Success Metrics

After your first run, you should have:
- ✅ 5-15 qualified prospects
- ✅ Detailed intelligence on each company
- ✅ Specific service opportunities identified
- ✅ Outreach plans with talking points
- ✅ Prioritized list for immediate action

**Time to First Outreach**: Under 30 minutes from starting the tool to sending your first personalized email!

---

**Ready to find companies that actually need your services? Run your first prospecting search now!**

```bash
python main_prospecting.py prospect --city sfbay --category sof --pages 3
```
