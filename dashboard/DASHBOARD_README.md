# 🎯 Lead Analysis Dashboard

Interactive web-based dashboard for viewing, filtering, and managing Forecasta lead analysis results.

## Quick Start

### Option 1: PowerShell Script (Recommended)

```powershell
.\run_dashboard.ps1
```

### Option 2: Manual Start

```powershell
# Install Flask if needed
pip install flask

# Set Python path and run
$env:PYTHONPATH="C:\Users\dusti\git\craigslist_agent"
python dashboard/leads_app.py
```

The dashboard will start at **http://localhost:3000**

## Features

### 📊 Dashboard Overview

- **Real-time statistics** - Total leads, tier breakdown, average scores
- **Visual tier cards** - Color-coded for quick identification
- **Industry breakdown** - See distribution across industries
- **Status tracking** - Monitor contact attempts and outcomes

### 🔍 Filtering & Search

- **Filter by Tier** - Show only TIER 1/2 high-priority leads
- **Filter by Status** - New, contacted, meeting scheduled, customer, lost
- **Filter by Industry** - Focus on specific verticals
- **Instant updates** - Real-time filtering without page reload

### 📋 Lead Cards

Each lead displays:

- Company name, location, industry
- Tier badge and score (0-30 points)
- Contact information (phone, email, website)
- Scoring breakdown across 4 categories
- Key pain points
- Custom value proposition
- Recommended opening question
- Current status

### ⚡ Actions

- **View Full Details** - See complete JSON data
- **Update Status** - Mark as contacted, meeting scheduled, customer, lost
- **Add Notes** - Track interactions and observations
- **Analyze New Posting** - Process new job postings directly in the UI
- **Export to CSV** - Download all leads for CRM import

## API Endpoints

The dashboard provides a REST API:

### GET /api/leads

Get all leads with optional filters

```
?tier=TIER 1&status=new&industry=Construction/Trades
```

### GET /api/stats

Get dashboard statistics

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

### GET /api/lead/<lead_id>

Get single lead details

### POST /api/lead/<lead_id>/update

Update lead status/notes

```json
{
  "status": "contacted",
  "notes": "Called, left voicemail"
}
```

### POST /api/analyze

Analyze new job posting

```json
{
  "posting_text": "Job description here...",
  "posting_url": "https://..."
}
```

### GET /api/export/csv

Export all leads to CSV

## Using the Dashboard

### 1. View Leads

- Leads are displayed newest first
- Color-coded tier badges for quick identification
- Expand cards to see full details

### 2. Filter Leads

Use the filter dropdowns to:

- Show only high-priority leads (TIER 1-2)
- View contacted vs. new leads
- Focus on specific industries

### 3. Analyze New Posting

1. Click "➕ Analyze New Posting"
2. Paste job posting text
3. Optionally add URL
4. Click "🔍 Analyze"
5. Lead appears in dashboard immediately

### 4. Update Lead Status

As you contact leads:

- Use status dropdown to mark progress
- Add notes for each interaction
- Track outcome (customer/lost)

### 5. Export Data

Click "📥 Export CSV" to download all leads for:

- CRM import (Salesforce, HubSpot, etc.)
- Reporting and analysis
- Team sharing

## Tier Color Coding

- **🟢 TIER 1** (Green) - TOP PRIORITY - Contact immediately
- **🔵 TIER 2** (Blue) - QUALIFIED LEAD - Add to pipeline
- **🟡 TIER 3** (Yellow) - MONITOR - Watch for changes
- **🔴 TIER 4** (Red) - LOW PRIORITY - Deprioritize
- **⚫ TIER 5** (Gray) - REJECT - Skip

## Data Location

All lead data is stored in:

```
output/leads/
  ├── lead_company_abc123.json          (Full data)
  └── lead_company_abc123_summary.md    (Human-readable)
```

The dashboard reads from these JSON files in real-time.

## Integration with Analysis Agent

The dashboard automatically picks up new leads analyzed via:

```python
from agents import LeadAnalysisAgent

agent = LeadAnalysisAgent()
result = agent.analyze_posting(posting_text, posting_url)

# Lead automatically appears in dashboard
```

Or use the web UI to analyze directly!

## Customization

### Change Port

Edit `dashboard/leads_app.py`:

```python
app.run(host='0.0.0.0', port=3000, debug=True)  # Change 3000 to desired port
```

### Modify UI

Edit `dashboard/templates/leads_dashboard.html` to customize:

- Colors and styling
- Card layout
- Filter options
- Statistics displayed

### Add API Endpoints

Edit `dashboard/leads_app.py` to add new endpoints for:

- Email automation
- CRM integration
- Reporting
- Analytics

## Troubleshooting

### "Module not found" error

```powershell
$env:PYTHONPATH="C:\Users\dusti\git\craigslist_agent"
```

### Port already in use

Change port in `leads_app.py` or kill process:

```powershell
Get-NetTCPConnection -LocalPort 3000 | Select-Object -ExpandProperty OwningProcess | Stop-Process
```

### No leads showing

1. Run example to generate sample lead:
   ```powershell
   python examples/lead_analysis.py
   ```
2. Check `output/leads/` directory has JSON files

### Dashboard not updating

Click "🔄 Refresh" button or reload page

## Screenshots

### Dashboard Overview

- Stats cards showing tier distribution
- Filter controls for drilling down
- Lead cards with all key information

### Lead Card Detail

- Company contact information
- Scoring breakdown
- Pain points and value proposition
- Call script opening question
- Action buttons for status updates

### Analyze Modal

- Paste job posting text
- Instant analysis
- Results appear immediately

## Production Deployment

For production use:

1. **Use production WSGI server**:

   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:3000 dashboard.leads_app:app
   ```

2. **Add authentication** for security

3. **Set debug=False** in app.run()

4. **Use environment variables** for configuration

5. **Add logging** for monitoring

6. **Back up lead data** regularly

## Next Features (Roadmap)

- [ ] Batch status updates
- [ ] Email integration for direct outreach
- [ ] Calendar integration for scheduling
- [ ] Advanced analytics and charts
- [ ] Team collaboration features
- [ ] Auto-refresh without page reload
- [ ] Mobile-responsive improvements
- [ ] Dark mode toggle

## Support

For issues or questions, check:

- `LEAD_ANALYSIS_README.md` - Full documentation
- `QUICKSTART_LEAD_ANALYSIS.md` - Quick reference
- GitHub issues

---

Built with ❤️ for Forecasta • Powered by Flask & Python
