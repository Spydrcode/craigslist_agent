# Complete Dashboard & Batch Prospecting Guide

## Overview

You now have a **complete web-based prospecting system** that can:
- ✅ Search multiple cities and job categories
- ✅ Manage hundreds of prospects in one place
- ✅ Generate personalized outreach automatically
- ✅ Track all interactions and status
- ✅ Export data for analytics

---

## 🚀 Quick Start

### Option 1: Web Dashboard (Recommended)

**Start the dashboard:**
```bash
python run_dashboard.py
```

**Open in browser:**
```
http://localhost:5000
```

### Option 2: Command Line (For Advanced Users)

**Run batch prospecting:**
```bash
python batch_prospecting.py
```

**Manage clients:**
```bash
python manage_clients.py
```

---

## 📊 Web Dashboard Features

### 1. View All Prospects

The dashboard automatically loads ALL prospects from:
- Single city searches (`output/prospects/`)
- Batch searches (`output/batch_results/`)

**Features:**
- Filter by city, category, priority, score
- Sort by score (highest first)
- See growth stage, number of jobs
- Click to view full details

### 2. Run New Searches

**From Dashboard:**
1. Use the search panel (left side)
2. Select city and category
3. Add optional keywords
4. Set max pages to scrape
5. Click "Search Jobs"

**This runs the full AI analysis:**
- Scrapes job postings
- Analyzes growth signals
- Matches to services
- Scores with ML
- Saves results automatically

### 3. Select Prospects

**To select a prospect:**
1. Click on any prospect card
2. Click "Select for Outreach"
3. Enter your details (name, company, title)
4. System automatically generates:
   - Personalized email
   - Call script with objection handling
   - LinkedIn connection message
   - LinkedIn direct message

**All content saved to:**
- `data/clients/selected_clients.json`
- `data/clients/outreach_content.json`
- `output/outreach/CompanyName_outreach.txt`

### 4. Track Interactions

**After contacting a prospect:**
1. Open prospect details
2. Click "Log Interaction"
3. Select type: email_sent, call_made, meeting_scheduled, etc.
4. Select outcome: responded, no_response, interested, etc.
5. Add notes

**All tracked in:**
- `data/clients/interactions.json`

### 5. Export Data

**Export all prospects:**
- Click "Export to CSV"
- Opens in Excel
- Includes: scores, priority, growth, city, category, selected status

**Export analytics:**
- Click "Export Analytics"
- Full interaction history
- Conversion data
- Response rates

---

## 🎯 Batch Prospecting

### Interactive Mode

```bash
python batch_prospecting.py
```

**Prompts you for:**
1. **Cities** - Comma-separated or 'all'
   - Example: `sfbay,newyork,chicago`
   - Or: `all` for all 20 cities

2. **Categories** - Comma-separated or 'all'
   - Example: `sof,eng` (software and engineering)
   - Or: `all` for all categories

3. **Keywords** - Optional filters
   - Example: `AI,ML,Python`

4. **Pages** - How many pages per search
   - Default: 2 (about 240 jobs per city/category)

**Example Session:**
```
Enter city codes: sfbay,seattle,austin,boston
Enter category codes: sof
Enter keywords: AI,ML,startup
Pages per search: 2

Total searches: 4 (4 cities × 1 category)
Estimated time: 8 minutes

Proceed? (y/n): y

[Searches each city...]

BATCH COMPLETE
Total Prospects Found: 47
```

**Results saved to:**
- `output/batch_results/batch_prospects_TIMESTAMP.json`
- `output/batch_results/batch_stats_TIMESTAMP.json`

### Available Cities (20)

```
sfbay          - San Francisco Bay Area
newyork        - New York
losangeles     - Los Angeles
chicago        - Chicago
seattle        - Seattle
boston         - Boston
austin         - Austin
denver         - Denver
atlanta        - Atlanta
dallas         - Dallas
houston        - Houston
miami          - Miami
phoenix        - Phoenix
sandiego       - San Diego
portland       - Portland
philadelphia   - Philadelphia
washingtondc   - Washington DC
raleigh        - Raleigh
minneapolis    - Minneapolis
detroit        - Detroit
```

### Available Categories (10)

```
sof  - Software/QA/DBA
eng  - Engineering
web  - Web/HTML/Info Design
sad  - Systems/Networking
sls  - Sales/Business Development
mar  - Marketing/PR/Advertising
bus  - Business/Management
acc  - Accounting/Finance
sci  - Science/Biotech
edu  - Education/Teaching
```

---

## 📋 Complete Workflow

### Week 1: Batch Prospecting

**Monday Morning:**
```bash
python batch_prospecting.py
```
- Select 5 tech cities
- Software category
- 2 pages each
- Get 50-100 prospects in 10 minutes

### Week 1: Review & Select

**Monday Afternoon:**
```bash
python run_dashboard.py
```
Open http://localhost:5000

1. Filter by priority: URGENT and HIGH only
2. Sort by score (automatic)
3. Review top 20 prospects
4. Select best 10 for outreach
5. Generate all outreach content

### Week 1: Outreach (Tuesday-Friday)

**For each selected prospect:**
1. View outreach content in dashboard
2. Send personalized email
3. Log interaction
4. If no response in 48hrs, call using script
5. Log call outcome

### Week 2: Follow-up

**Track in dashboard:**
- View prospects by status
- See who responded
- Follow up with interested parties
- Schedule meetings
- Update status to "qualified" or "client"

### Monthly: Analytics

```bash
python run_dashboard.py
```
Click "Export Analytics"

**Analyze:**
- Which cities have best response rates?
- Which job categories convert best?
- What growth signals predict success?
- Average time to response?
- Conversion rate by priority tier?

---

## 🎨 Dashboard UI Guide

### Main Dashboard

```
┌─────────────────────────────────────────────────┐
│  🎯 Prospecting Dashboard                       │
├─────────────────────────────────────────────────┤
│                                                 │
│  Filters:                    Stats:             │
│  [City ▼]  [Category ▼]     Total: 127         │
│  [Priority ▼] [Score: 50+]  URGENT: 12         │
│  [ ] Selected Only          HIGH: 45           │
│                                                 │
│  [Run New Search]  [Batch Search]              │
│                                                 │
├─────────────────────────────────────────────────┤
│                                                 │
│  Prospect Cards:                                │
│  ┌────────────────────────────────────┐       │
│  │ TechCorp Solutions                 │       │
│  │ Score: 87.3  Priority: URGENT      │       │
│  │ Growth: RAPID_GROWTH (0.89)        │       │
│  │ 5 jobs in sfbay/sof                │       │
│  │                                    │       │
│  │ [View Details] [Select]            │       │
│  └────────────────────────────────────┘       │
│  ... more cards ...                            │
└─────────────────────────────────────────────────┘
```

### Prospect Details

```
┌─────────────────────────────────────────────────┐
│  TechCorp Solutions                             │
│  Score: 87.3/100  |  URGENT Priority            │
├─────────────────────────────────────────────────┤
│                                                 │
│  Company Info:                                  │
│  - Growth Stage: RAPID_GROWTH                   │
│  - Growth Score: 0.89                           │
│  - Jobs: 5 positions                            │
│  - Location: San Francisco                      │
│                                                 │
│  Service Opportunities:                         │
│  1. AI/ML Consulting (92% confidence)           │
│     Value: $75K-$200K                           │
│                                                 │
│  Generated Outreach:                            │
│  📧 Email   📞 Call Script   💼 LinkedIn        │
│                                                 │
│  Interactions:                                  │
│  - 2024-12-02: Email sent → No response yet    │
│                                                 │
│  [Select for Outreach]  [Log Interaction]       │
│  [Export Details]                               │
└─────────────────────────────────────────────────┘
```

---

## 📁 File Structure

After using the system, you'll have:

```
craigslist_agent/
├── output/
│   ├── prospects/
│   │   ├── prospects_20241202_*.json    ← Single searches
│   │   └── prospects_20241202_*.csv
│   └── batch_results/
│       ├── batch_prospects_*.json       ← Batch searches
│       └── batch_stats_*.json
│
├── data/
│   └── clients/
│       ├── prospects.json               ← All prospects ever found
│       ├── selected_clients.json        ← Prospects you selected
│       ├── interactions.json            ← All logged interactions
│       ├── outreach_content.json        ← Generated content
│       └── analytics_export.csv         ← Analytics data
│
└── output/outreach/
    └── CompanyName_outreach.txt         ← Formatted outreach
```

---

## 💡 Pro Tips

### Finding the Best Prospects

1. **Start with filters:**
   - Priority: URGENT or HIGH
   - Min Score: 70+
   - Growth Stage: RAPID_GROWTH

2. **Look for:**
   - Multiple job postings (3+)
   - Leadership positions hiring
   - Specific pain points mentioned
   - High service match confidence

3. **Prioritize:**
   - Companies hiring for multiple departments
   - Recent funding mentions
   - Urgent language in postings

### Optimizing Batch Searches

1. **Target tech hubs for software:**
   - sfbay, seattle, austin, boston, newyork

2. **Use specific keywords:**
   - Narrows results to relevant companies
   - Example: "AI,ML,startup" for ML consulting

3. **Adjust pages based on city:**
   - Big cities (sfbay, newyork): 3-5 pages
   - Medium cities (austin, denver): 2-3 pages
   - Smaller cities: 1-2 pages

### Improving Response Rates

**From your analytics, track:**
1. Which email subject lines get opened
2. Which industries respond best
3. Optimal follow-up timing
4. Most effective call scripts

**A/B test:**
- Different email tones (professional vs casual)
- Subject line styles (question vs statement)
- Call opening lines

---

## 🔧 Customization

### Change Your Services

Edit `agents/service_matcher_agent.py` lines 22-82 to add your specific services.

### Adjust Scoring Thresholds

Edit `run_prospecting_simple.py` or use dashboard:
```python
min_growth_score = 0.3  # Lower = more prospects
min_lead_score = 50.0   # Lower = more prospects
```

### Modify Outreach Tone

Edit `agents/outreach_agent.py` to change:
- Email templates
- Call script structure
- LinkedIn message style

---

## 📊 Analytics Queries

### In Excel (from CSV export):

**Response rate by city:**
```
=COUNTIFS(City,"sfbay",Status,"responded")/COUNTIF(City,"sfbay")
```

**Average score by priority:**
```
=AVERAGEIF(Priority,"URGENT",Score)
```

**Conversion rate:**
```
=COUNTIF(Status,"client")/COUNTA(Status)
```

---

## ❓ Troubleshooting

### Dashboard won't start

```bash
# Install Flask if missing
pip install flask

# Check port 5000 is free
# On Windows:
netstat -ano | findstr :5000
```

### No prospects found

- Lower `min_growth_score` to 0.2
- Lower `min_lead_score` to 30.0
- Try different city/category combination
- Increase `max_pages`

### Batch prospecting is slow

- Normal! Each search takes 2-3 minutes
- Run overnight for large batches
- Reduce number of cities/categories
- Reduce pages per search

### Outreach generation fails

- Check OpenAI API key in `.env`
- Check API credits
- Check internet connection
- Check `logs/prospecting.log` for details

---

## 🎯 Success Metrics

After your first month, you should have:

- [ ] 100+ prospects found
- [ ] 20+ prospects selected
- [ ] 20+ emails sent
- [ ] 10+ calls made
- [ ] 5+ meetings scheduled
- [ ] 1+ new clients

**If you hit these metrics, the system is working!**

---

## 🚀 Next Steps

1. **Run your first batch search**
   ```bash
   python batch_prospecting.py
   ```

2. **Start the dashboard**
   ```bash
   python run_dashboard.py
   ```

3. **Select your top 10 prospects**
   - Filter by priority and score
   - Generate outreach for each

4. **Start reaching out**
   - Send emails Monday-Wednesday mornings
   - Make calls Tuesday-Thursday afternoons
   - Log every interaction

5. **Review weekly**
   - What's working?
   - What needs adjustment?
   - Export and analyze data

---

**Questions? Check the logs in `logs/prospecting.log`**

**Ready to find clients? Run the dashboard now!** 🚀
