# 🚀 Quick Start: Lead Analysis Dashboard

## Start the Dashboard (Choose One)

### Method 1: Double-click Batch File

```
Double-click: run_dashboard.bat
```

### Method 2: PowerShell Script

```powershell
.\run_dashboard.ps1
```

### Method 3: Manual Command

```powershell
cd C:\Users\dusti\git\craigslist_agent
$env:PYTHONPATH="C:\Users\dusti\git\craigslist_agent"
python dashboard/leads_app.py
```

## Access the Dashboard

Open your browser and go to:

```
http://localhost:3000
```

## What You'll See

### 📊 Statistics Cards (Top)

- **Total Leads** - All leads in system
- **Tier 1** - Top priority leads (green)
- **Tier 2** - Qualified leads (blue)
- **Average Score** - Mean score across all leads

### 🔧 Filter Controls (Middle)

- **Filter by Tier** - Show only specific tiers
- **Filter by Status** - New, contacted, meeting scheduled, etc.
- **Filter by Industry** - Focus on specific industries
- **🔄 Refresh** - Reload data
- **➕ Analyze New Posting** - Process new job posting
- **📥 Export CSV** - Download all leads

### 📋 Lead Cards (Bottom)

Each card shows:

- Company name and location
- Tier badge and score
- Contact info (phone, email, website)
- Pain points
- Value proposition
- Opening question for calls
- Action buttons

## Common Tasks

### 1️⃣ View High-Priority Leads

1. Select "Tier 1 - Top Priority" from tier filter
2. See only leads scoring 20-30 points
3. Click "View Full Details" for complete info

### 2️⃣ Analyze New Job Posting

1. Click "➕ Analyze New Posting"
2. Paste job posting text
3. (Optional) Add URL
4. Click "🔍 Analyze"
5. Lead appears instantly in dashboard

### 3️⃣ Update Lead Status

1. Find lead card
2. Use status dropdown
3. Select: Contacted, Meeting Scheduled, Customer, or Lost
4. Dashboard updates automatically

### 4️⃣ Add Notes

1. Click "📝 Add Note" on any lead
2. Enter your note
3. Note saved with timestamp

### 5️⃣ Export to CSV

1. Click "📥 Export CSV"
2. File downloads automatically
3. Import to your CRM (Salesforce, HubSpot, etc.)

## Test the Dashboard

If you don't have any leads yet:

```powershell
# Generate a sample lead
python examples/lead_analysis.py

# Then refresh the dashboard
```

## Understanding Tiers

- 🟢 **TIER 1** (20-30 pts) - Call TODAY
- 🔵 **TIER 2** (15-19 pts) - Add to pipeline
- 🟡 **TIER 3** (10-14 pts) - Monitor
- 🔴 **TIER 4** (5-9 pts) - Low priority
- ⚫ **TIER 5** (0-4 pts) - Reject

## Keyboard Shortcuts

- **F5** - Refresh page
- **Ctrl+F** - Search (use browser search)
- **Ctrl+C** - Stop server (in terminal)

## Troubleshooting

**Dashboard won't start?**

```powershell
# Check if port 3000 is in use
Get-NetTCPConnection -LocalPort 3000

# If needed, change port in dashboard/leads_app.py
```

**No leads showing?**

```powershell
# Generate test lead
python examples/lead_analysis.py

# Check leads directory
ls output/leads/
```

**Changes not appearing?**

- Click "🔄 Refresh" button
- Or reload browser (F5)

## Next Steps

1. ✅ Generate leads using `examples/lead_analysis.py`
2. ✅ View them in dashboard at localhost:3000
3. ✅ Filter to TIER 1-2 leads
4. ✅ Update statuses as you contact
5. ✅ Export to CSV for CRM import

## Full Documentation

- **Dashboard Guide**: `dashboard/DASHBOARD_README.md`
- **Lead Analysis**: `LEAD_ANALYSIS_README.md`
- **Quick Reference**: `QUICKSTART_LEAD_ANALYSIS.md`

---

**Dashboard is now running at http://localhost:3000** 🎉
