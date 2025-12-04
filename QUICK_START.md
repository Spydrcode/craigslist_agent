# Quick Start Guide

## Your Complete Prospecting System is Ready!

You now have THREE ways to find and manage hundreds of prospects:

---

## 🌐 Option 1: Web Dashboard (RECOMMENDED)

**Best for:** Managing hundreds of prospects, running searches, tracking everything

```bash
python run_dashboard.py
```

Then open: **http://localhost:5000**

### What you can do:
- ✅ View ALL prospects from all searches in one place
- ✅ Filter by city, category, priority, score
- ✅ Run new searches (single or batch)
- ✅ Select prospects → generates email + call script + LinkedIn
- ✅ Track all interactions and status
- ✅ Export to CSV for Excel analysis

---

## 📦 Option 2: Batch Prospecting

**Best for:** Searching multiple cities at once overnight

```bash
python batch_prospecting.py
```

### Example: Search 5 Tech Hubs
```
Cities: sfbay,seattle,austin,boston,newyork
Category: sof (software)
Keywords: AI,ML,startup
Pages: 2

→ Finds 50-100 qualified prospects in 10 minutes
```

### Available Cities (20):
sfbay, newyork, losangeles, chicago, seattle, boston, austin, denver, atlanta, dallas, houston, miami, phoenix, sandiego, portland, philadelphia, washingtondc, raleigh, minneapolis, detroit

### Categories:
- `sof` - Software/Tech
- `eng` - Engineering
- `bus` - Business/Management
- `sls` - Sales
- `mar` - Marketing
- And 5 more...

---

## 🖥️ Option 3: Command Line

**Best for:** Quick single searches, managing clients

### Find Prospects (Single City):
```bash
python run_prospecting_simple.py
```

### Manage Clients:
```bash
python manage_clients.py
```

---

## 🎯 Your Weekly Workflow

### Monday: Prospect
```bash
python batch_prospecting.py
# Search 5 cities → Get 50-100 prospects
```

### Monday PM: Select
```bash
python run_dashboard.py
# Filter → Select top 10 → Generate outreach
```

### Tuesday-Friday: Outreach
- Send 2-3 emails per day
- Make 2-3 calls per day
- Log all interactions in dashboard

### Weekly: Review
- Check response rates
- See who's interested
- Follow up with hot leads

### Monthly: Analytics
- Export CSV from dashboard
- Analyze what's working
- Adjust strategy

---

## 📊 What You'll See in Dashboard

```
┌────────────────────────────────────────┐
│  Prospecting Dashboard                 │
├────────────────────────────────────────┤
│  Total Prospects: 127                  │
│  URGENT: 12  |  HIGH: 45  | MEDIUM: 58 │
│                                        │
│  Filters:                              │
│  City: [All ▼]    Category: [All ▼]   │
│  Priority: [URGENT ▼]  Score: [70+]   │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │ TechCorp Solutions               │ │
│  │ Score: 87.3 | URGENT | sfbay    │ │
│  │ Growth: RAPID_GROWTH (0.89)     │ │
│  │ 5 jobs • AI/ML opportunity      │ │
│  │ [View] [Select]                 │ │
│  └──────────────────────────────────┘ │
│  ... more prospects ...               │
└────────────────────────────────────────┘
```

---

## ⚡ Quick Commands

```bash
# Start dashboard
python run_dashboard.py

# Batch search multiple cities
python batch_prospecting.py

# Quick single search
python run_prospecting_simple.py

# Manage selected clients
python manage_clients.py
```

---

## 📁 Where Your Data Lives

```
output/
├── prospects/           ← Single searches
└── batch_results/       ← Batch searches

data/clients/
├── selected_clients.json     ← Who you're pursuing
├── interactions.json         ← All logged calls/emails
├── outreach_content.json     ← Generated emails/scripts
└── analytics_export.csv      ← Export for Excel
```

---

## 💡 Pro Tips

### Finding Best Prospects
1. Filter: Priority = URGENT, Score ≥ 70
2. Look for: Multiple jobs (3+), RAPID_GROWTH stage
3. Select: Companies with specific pain points mentioned

### Best Response Rates
- Email subject lines mentioning their specific hiring
- Calls: 10-11am or 4-5pm
- Follow up in 48 hours if no response

### Batch Search Strategy
- **Tech companies:** sfbay, seattle, austin, boston
- **Keywords:** Be specific (e.g., "AI,ML,Python")
- **Pages:** 2-3 for big cities, 1-2 for smaller

---

## ✅ First Week Checklist

- [ ] Run batch prospecting (5 cities)
- [ ] Start dashboard (http://localhost:5000)
- [ ] Select top 10 prospects
- [ ] Generate outreach for all 10
- [ ] Send 5 emails
- [ ] Make 3 calls
- [ ] Log all interactions
- [ ] Schedule 1+ meeting

**If you complete this, you're crushing it!** 🚀

---

## 🆘 Need Help?

**Dashboard won't start?**
```bash
pip install flask
python run_dashboard.py
```

**No prospects found?**
- Lower the score threshold to 30
- Try different city/category
- Increase pages to 5

**Slow prospecting?**
- Normal! AI analysis takes time
- Run batch overnight
- Each city takes 2-3 minutes

---

## 🚀 Ready to Start?

### 1. Run your first batch search:
```bash
python batch_prospecting.py
```
Enter: `sfbay,seattle,austin` for cities
Enter: `sof` for category
Hit enter for defaults

### 2. Start the dashboard:
```bash
python run_dashboard.py
```
Open: http://localhost:5000

### 3. Select and reach out!
- Filter to URGENT priority
- Select top 5
- Copy generated email
- Send and log interaction

**That's it! You're now systematically finding companies that need you.** 🎯

---

For detailed instructions, see:
- [DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md) - Complete dashboard manual
- [CLIENT_MANAGEMENT_GUIDE.md](CLIENT_MANAGEMENT_GUIDE.md) - Client management
- [COMPLETE_SYSTEM_GUIDE.md](COMPLETE_SYSTEM_GUIDE.md) - Full system docs
