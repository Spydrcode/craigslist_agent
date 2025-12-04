# Quick Start Guide - Forecasta Lead Qualification System

Get up and running with the multi-agent lead qualification system in 5 minutes.

---
**NEW SYSTEM**: This quick start covers the new multi-agent lead qualification system. For the original scraper, see the sections below.

---

## Forecasta Lead Qualification System

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Tests

```bash
python test_system.py
```

This creates sample data and tests all 6 agents plus the orchestrator.

### 3. Start Dashboard

```bash
python dashboard/backend.py
```

Open browser to: `http://localhost:5000`

### 4. Use the Dashboard

- **Search Panel**: Set location, date range, industries
- **Analytics**: View tier distribution, status funnel, industry breakdown
- **Lead Table**: Sort, filter, select leads
- **Bulk Actions**: Generate scripts, emails, or export CSV
- **Lead Details**: Click any lead to see full profile with call script

### Quick API Usage

```python
from agents.orchestrator import Orchestrator

orchestrator = Orchestrator(data_dir="data/leads")

# Process a posting
result = orchestrator.process_posting(html, url)

# Get tier 1 leads
hot_leads = orchestrator.get_all_leads(filters={"tier": 1})

# Analytics
stats = orchestrator.get_analytics()
```

For detailed documentation, see [README_MULTI_AGENT.md](README_MULTI_AGENT.md)

---

## Original Craigslist Job Scraper

Get up and running with the Craigslist Job Scraper in 5 minutes.

## Prerequisites

- Python 3.10+
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))
- Pinecone account ([sign up here](https://www.pinecone.io/))
- Supabase project ([create one here](https://supabase.com/))

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Configure Environment

```bash
# Run the setup wizard
python setup.py
```

Or manually:

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
# Required:
# - OPENAI_API_KEY
# - PINECONE_API_KEY
# - PINECONE_ENVIRONMENT
# - SUPABASE_URL
# - SUPABASE_KEY
```

## 3. Set Up Supabase Database

1. Go to your Supabase project
2. Navigate to SQL Editor
3. Copy contents of `database_schema.sql`
4. Paste and run in SQL Editor

This creates all necessary tables and indexes.

## 4. Run Your First Scrape

```bash
# Scrape 1 page of software jobs in SF Bay Area
python main.py scrape --city sfbay --category sof --pages 1
```

This will:
- Scrape job listings from Craigslist
- Parse them with AI (extract skills, pain points)
- Store embeddings in Pinecone
- Save to Supabase database

## 5. Launch the Dashboard

```bash
streamlit run dashboard/app.py
```

Open http://localhost:8501 in your browser.

## Common Commands

### Scrape with Keywords

```bash
python main.py scrape --city sfbay --category sof --keywords python django --pages 3
```

### Search Jobs

```bash
python main.py search "senior python developer with ML experience"
```

### Analyze Market

```bash
python main.py analyze --city sfbay --category sof
```

### Export to CSV

```bash
python main.py export --output jobs.csv
```

## City and Category Codes

### Popular Cities
- `sfbay` - San Francisco Bay Area
- `newyork` - New York
- `losangeles` - Los Angeles
- `seattle` - Seattle
- `chicago` - Chicago
- `boston` - Boston
- `austin` - Austin

### Job Categories
- `sof` - Software/IT/Tech
- `eng` - Engineering
- `sls` - Sales
- `acc` - Accounting/Finance
- `mar` - Marketing/Advertising
- `sad` - Systems/Networking

Find more codes at: https://craigslist.org

## Examples

Check the `examples/` directory:

```bash
# Basic scraping
python examples/basic_scrape.py

# AI-powered parsing
python examples/ai_parsing.py

# Complete pipeline
python examples/full_pipeline.py
```

## Troubleshooting

### "Configuration Error"
→ Make sure all API keys are set in `.env`

### "Connection failed"
→ Verify your API keys are correct

### "No jobs found"
→ Try different keywords or increase `--pages`

### "Rate limited"
→ Increase delays in `.env`:
```env
SCRAPING_DELAY_MIN=3
SCRAPING_DELAY_MAX=6
```

## Next Steps

1. **Read the full README.md** for detailed documentation
2. **Customize parsing** by modifying `agents/parser_agent.py`
3. **Set up scheduled scraping** with `python main.py schedule`
4. **Explore the API** by importing modules in your own scripts

## Getting Help

- Check README.md for full documentation
- Review example scripts in `examples/`
- Open an issue on GitHub

---

Happy scraping! 🚀
