# System Architecture - Forecasta Lead Qualification

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CRAIGSLIST POSTINGS                             │
│                    (Job listings with company info)                     │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          ORCHESTRATOR                                    │
│                    (Coordinates Agent Workflow)                         │
└─────────────────────────────────────────────────────────────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        ▼                        ▼                        ▼
┌───────────────┐      ┌───────────────┐       ┌───────────────┐
│   AGENT 1     │──────▶│   AGENT 2     │───────▶│   AGENT 3     │
│  EXTRACTOR    │      │  RESEARCHER   │       │    SCORER     │
│               │      │               │       │               │
│ Parse HTML    │      │ Verify Co.    │       │ Calculate     │
│ Extract data  │      │ Find size     │       │ 0-30 score    │
│ Find keywords │      │ Identify DM   │       │ Assign tier   │
└───────────────┘      └───────────────┘       └───────┬───────┘
                                                        │
        ┌───────────────────────────────────────────────┘
        ▼                        ▼                        ▼
┌───────────────┐      ┌───────────────┐       ┌───────────────┐
│   AGENT 4     │◀─────│   AGENT 5     │◀──────│   AGENT 6     │
│   ANALYZER    │      │    WRITER     │       │    STORER     │
│               │      │               │       │               │
│ Find pain pts │      │ Value prop    │       │ Save JSON     │
│ Map forecasts │      │ Call script   │       │ Update CSV    │
│ Gen insights  │      │ Email template│       │ Analytics     │
└───────────────┘      └───────────────┘       └───────┬───────┘
                                                        │
                                                        ▼
                                               ┌────────────────┐
                                               │  DATA STORAGE  │
                                               │                │
                                               │ leads/*.json   │
                                               │ master.csv     │
                                               └───────┬────────┘
                                                       │
        ┌──────────────────────────────────────────────┼──────────┐
        ▼                                              ▼          ▼
┌───────────────┐                            ┌──────────────┐  ┌─────────┐
│  BACKEND API  │                            │  DASHBOARD   │  │  EXPORT │
│    (Flask)    │◀───────────────────────────│   (HTML/JS)  │  │  (CSV)  │
│               │                            │              │  │         │
│ REST Endpoints│                            │ Analytics    │  │ Reports │
│ /api/leads    │                            │ Lead Table   │  │         │
│ /api/analytics│                            │ Bulk Actions │  │         │
└───────────────┘                            └──────────────┘  └─────────┘
```

## Agent Workflow Detail

```
AGENT 1: EXTRACTOR
├─ Input: Raw HTML, URL
├─ Processing:
│  ├─ Parse company name
│  ├─ Extract job title, location, salary
│  ├─ Find contact info (email, phone, website)
│  ├─ Identify keywords (scale, forecasting, industry)
│  ├─ Detect red flags (MLM, chains, spam)
│  └─ Calculate professionalism (1-10)
└─ Output: Structured JSON
         │
         ▼
AGENT 2: RESEARCHER
├─ Input: Extracted data
├─ Processing:
│  ├─ Web search for company
│  ├─ Verify legitimacy
│  ├─ Find employee count
│  ├─ Identify industry
│  ├─ Search for decision makers
│  ├─ Check if local (Phoenix metro)
│  └─ Retry logic (3x)
└─ Output: Enhanced with company profile
         │
         ▼
AGENT 3: SCORER
├─ Input: Researched data
├─ Processing:
│  ├─ Company Scale (9 pts)
│  │  └─ Multiple positions, salary $50K+, manager roles, benefits
│  ├─ Forecasting Pain (12 pts)
│  │  └─ Seasonal, project-based, volume-driven, growth
│  ├─ Accessibility (7 pts)
│  │  └─ Local, <200 employees, decision maker found
│  ├─ Data Quality (2 pts)
│  │  └─ Professionalism 7-10
│  └─ Assign tier (1-5)
└─ Output: Score (0-30), Tier, Breakdown
         │
         ▼
AGENT 4: ANALYZER (Skip if score < 10)
├─ Input: Scored data
├─ Processing:
│  ├─ Identify pain points
│  │  └─ Seasonal, project uncertainty, volume, growth, bulk hiring
│  ├─ Map forecast opportunities by industry
│  │  └─ Retail: traffic, Hospitality: reservations, etc.
│  ├─ Generate insights
│  │  └─ Primary pain, best opportunity, talk track angle
│  └─ Create opening hook
└─ Output: Pain points, Opportunities, Insights
         │
         ▼
AGENT 5: WRITER (Skip if tier > 3)
├─ Input: Analyzed data
├─ Processing:
│  ├─ Value Proposition
│  │  └─ "Predict [X] [time] ahead so you [benefit] instead of [problem]"
│  ├─ Call Script
│  │  ├─ Intro (60-sec ask)
│  │  ├─ Pattern interrupt (reference posting)
│  │  ├─ Diagnosis question (pain point)
│  │  ├─ Value statement
│  │  ├─ Social proof
│  │  ├─ Meeting ask (specific times)
│  │  └─ Objection handling (3 types)
│  └─ Email Template
│     ├─ Subject line
│     ├─ Body with value prop
│     └─ 2 follow-up templates
└─ Output: Value prop, Call script, Emails
         │
         ▼
AGENT 6: STORER
├─ Input: Fully processed lead
├─ Processing:
│  ├─ Generate unique ID
│  ├─ Save JSON file (data/leads/lead_{id}.json)
│  ├─ Update master CSV
│  └─ Track timestamps
└─ Output: Lead ID, Storage paths, Status
```

## Scoring Algorithm Flow

```
START
  │
  ├─ Check Red Flags
  │  ├─ 2+ red flags? ────────────────┐
  │  ├─ Can't verify company? ────────┤
  │  ├─ National chain? ──────────────┤
  │  └─ MLM indicators? ──────────────┤
  │                                    ▼
  │                              DISQUALIFIED
  │                              Score: 0
  │                              Tier: 5
  │
  ├─ Calculate Points
  │
  ├─ COMPANY SCALE (max 9)
  │  ├─ Multiple positions? ────── +3
  │  ├─ Salary $50K+? ──────────── +2
  │  ├─ Manager/Director role? ─── +2
  │  └─ Benefits mentioned? ────── +2
  │
  ├─ FORECASTING PAIN (max 12)
  │  ├─ Seasonal business? ──────── +5
  │  ├─ Project-based work? ─────── +5
  │  ├─ Volume-driven ops? ──────── +4
  │  └─ Growth language? ────────── +3
  │
  ├─ ACCESSIBILITY (max 7)
  │  ├─ Local company? ──────────── +3
  │  ├─ < 200 employees? ────────── +2
  │  └─ Decision maker found? ───── +2
  │
  ├─ DATA QUALITY (max 2)
  │  └─ Professionalism 7-10? ───── +2
  │
  ├─ Sum Points (0-30)
  │
  └─ Assign Tier
     ├─ 20-30 pts ─────▶ TIER 1 (Hot)
     ├─ 15-19 pts ─────▶ TIER 2 (Warm)
     ├─ 10-14 pts ─────▶ TIER 3 (Medium)
     ├─ 5-9 pts ───────▶ TIER 4 (Cold)
     └─ 0-4 pts ───────▶ TIER 5 (Disqualified)
```

## Conditional Logic Flow

```
Posting
  │
  ▼
Extractor ────────────────────────┐
  │                               │
  ▼                               │
Researcher ───────────────────────┤
  │                               │
  ▼                               │
Scorer                            │
  │                               │
  ├─ Score < 10? ──YES──▶ Skip Analyzer
  │        │                      │
  │       NO                      │
  ▼        │                      │
Analyzer ◀─┘                      │
  │                               │
  ▼                               │
  ├─ Tier > 3? ──YES──▶ Skip Writer
  │        │                      │
  │       NO                      │
  ▼        │                      │
Writer ◀───┘                      │
  │                               │
  ▼                               │
Storer ◀──────────────────────────┘
  │
  ▼
Stored Lead
```

## Data Flow

```
INPUT: Craigslist Posting HTML
  │
  ├─ company_name: "Desert Bistro Group"
  ├─ job_title: "Restaurant Manager"
  ├─ salary: {min: 55000, max: 65000, period: "year"}
  ├─ location: "Scottsdale, AZ"
  └─ keywords: ["seasonal", "volume", "manager", "benefits"]
  │
  ▼ (After Research)
  │
  ├─ company_verified: true
  ├─ is_local: true
  ├─ company_size: null
  └─ is_valid_lead: true
  │
  ▼ (After Scoring)
  │
  ├─ score: 23
  ├─ tier: 1
  └─ score_breakdown: {
      company_scale: 6,
      forecasting_pain: 12,
      accessibility: 3,
      data_quality: 2
    }
  │
  ▼ (After Analysis)
  │
  ├─ pain_points: [
  │   {category: "seasonal_staffing", severity: "high"},
  │   {category: "volume_variability", severity: "high"},
  │   {category: "growth_planning", severity: "medium"}
  │  ]
  └─ forecast_opportunities: [
      {what: "staffing needs", timeframe: "4-6 weeks"}
    ]
  │
  ▼ (After Writing)
  │
  ├─ value_proposition: "Predict staffing needs 4-6 weeks..."
  ├─ call_script: {intro: "...", pattern_interrupt: "...", ...}
  └─ email_template: {subject: "...", body: "...", ...}
  │
  ▼ (After Storage)
  │
OUTPUT: Stored Lead
  ├─ lead_id: "desert_bistro_group_20251129_210616"
  ├─ storage_path: "data/leads/lead_desert_bistro_group_20251129_210616.json"
  └─ status: "new"
```

## API Architecture

```
                    ┌──────────────────┐
                    │   FRONTEND       │
                    │   (Browser)      │
                    └────────┬─────────┘
                             │
                    HTTP Requests (JSON)
                             │
                             ▼
                    ┌──────────────────┐
                    │   FLASK API      │
                    │   Port 5000      │
                    └────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ GET /api/    │    │ POST /api/   │    │ POST /api/   │
│ leads        │    │ leads/:id/   │    │ bulk/scripts │
│              │    │ update       │    │              │
│ Filter leads │    │ Update status│    │ Generate     │
│ by tier,     │    │ Add notes    │    │ call scripts │
│ status       │    │              │    │              │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                    │
       └───────────────────┼────────────────────┘
                           ▼
                  ┌─────────────────┐
                  │  ORCHESTRATOR   │
                  │                 │
                  │ get_all_leads() │
                  │ update_status() │
                  │ bulk_scripts()  │
                  └────────┬────────┘
                           ▼
                  ┌─────────────────┐
                  │  STORER AGENT   │
                  │                 │
                  │ Read/Write JSON │
                  │ Query CSV       │
                  └────────┬────────┘
                           ▼
                  ┌─────────────────┐
                  │  FILE SYSTEM    │
                  │                 │
                  │ data/leads/     │
                  │ *.json, *.csv   │
                  └─────────────────┘
```

## Dashboard Component Architecture

```
┌────────────────────────────────────────────────────────────┐
│                        DASHBOARD                           │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────────────────────────────────────────┐    │
│  │  SEARCH PANEL                                     │    │
│  │  [Location ▼] [Date Range ▼] [☑ Industries]     │    │
│  │  [SEARCH BUTTON]                                  │    │
│  └──────────────────────────────────────────────────┘    │
│                                                            │
│  ┌──────────────────────────────────────────────────┐    │
│  │  ANALYTICS                                        │    │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐   │    │
│  │  │ Total  │ │ Tier 1 │ │ Tier 2 │ │  Avg   │   │    │
│  │  │ Leads  │ │  Hot   │ │  Warm  │ │ Score  │   │    │
│  │  └────────┘ └────────┘ └────────┘ └────────┘   │    │
│  │  ┌────────┐ ┌────────┐ ┌────────┐              │    │
│  │  │ By Tier│ │By Status│ │By Ind. │              │    │
│  │  │ (Bar)  │ │(Donut)  │ │(Horiz) │              │    │
│  │  └────────┘ └────────┘ └────────┘              │    │
│  └──────────────────────────────────────────────────┘    │
│                                                            │
│  ┌──────────────────────────────────────────────────┐    │
│  │  FILTERS                                          │    │
│  │  [Tier ▼] [Status ▼] [Refresh]                  │    │
│  └──────────────────────────────────────────────────┘    │
│                                                            │
│  ┌──────────────────────────────────────────────────┐    │
│  │  LEAD TABLE                      Bulk Actions:    │    │
│  │  ☐ Company | Title | Tier | Status | [View]      │    │
│  │  ☐ ABC Corp | Manager | T1 | New | [View]        │    │
│  │  ☐ XYZ Inc  | Director| T2 | New | [View]        │    │
│  │  [Select All] [Scripts] [Emails] [Export CSV]    │    │
│  └──────────────────────────────────────────────────┘    │
│                                                            │
└────────────────────────────────────────────────────────────┘

                         │ Click View
                         ▼
┌────────────────────────────────────────────────────────────┐
│                    LEAD DETAIL MODAL                       │
├────────────────────────────────────────────────────────────┤
│  [X] Close                                                 │
│                                                            │
│  ┌──────────────────────────────────────────────────┐    │
│  │  COMPANY INFO                                     │    │
│  │  Company: ABC Corp    | Industry: Retail          │    │
│  │  Location: Phoenix    | Size: 150 employees       │    │
│  │  Score: 25/30         | Tier: 1 (Hot)             │    │
│  └──────────────────────────────────────────────────┘    │
│                                                            │
│  ┌──────────────────────────────────────────────────┐    │
│  │  VALUE PROPOSITION                                │    │
│  │  "Predict customer traffic 2-4 weeks ahead..."    │    │
│  └──────────────────────────────────────────────────┘    │
│                                                            │
│  ┌──────────────────────────────────────────────────┐    │
│  │  CALL SCRIPT                                      │    │
│  │  ► Intro: "Hi, this is..."                        │    │
│  │  ► Pattern Interrupt: "I noticed..."              │    │
│  │  ► Diagnosis: "What's your biggest..."            │    │
│  │  ► Value: "We help companies like..."             │    │
│  │  ► Meeting Ask: "15 minutes Thursday..."          │    │
│  └──────────────────────────────────────────────────┘    │
│                                                            │
│  ┌──────────────────────────────────────────────────┐    │
│  │  EMAIL TEMPLATE                                   │    │
│  │  Subject: "Seasonal staffing for ABC Corp"        │    │
│  │  Body: "Hi [Name], I noticed..."                  │    │
│  └──────────────────────────────────────────────────┘    │
│                                                            │
│  ┌──────────────────────────────────────────────────┐    │
│  │  UPDATE STATUS                                    │    │
│  │  Status: [Contacted ▼]                            │    │
│  │  Notes: [Left voicemail...]                       │    │
│  │  [SAVE]                                           │    │
│  └──────────────────────────────────────────────────┘    │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

## Technology Stack

```
┌──────────────────────────────────────────────────────────┐
│ LAYER               │ TECHNOLOGY                         │
├──────────────────────────────────────────────────────────┤
│ Frontend            │ HTML5, CSS3, JavaScript (ES6+)     │
│                     │ Chart.js for visualizations        │
├──────────────────────────────────────────────────────────┤
│ Backend API         │ Flask 3.0+                         │
│                     │ Flask-CORS for cross-origin        │
├──────────────────────────────────────────────────────────┤
│ Agents              │ Python 3.10+                       │
│                     │ Type hints (Dict, List, Optional)  │
├──────────────────────────────────────────────────────────┤
│ Data Storage        │ JSON files (structured leads)      │
│                     │ CSV (master index)                 │
├──────────────────────────────────────────────────────────┤
│ Web Scraping        │ BeautifulSoup4, Requests           │
│ (Future)            │ lxml parser                        │
├──────────────────────────────────────────────────────────┤
│ AI/ML               │ Anthropic Claude (future)          │
│ (Future)            │ OpenAI, Pinecone embeddings        │
└──────────────────────────────────────────────────────────┘
```

## Deployment Architecture (Future)

```
                    ┌──────────────────┐
                    │     USERS        │
                    │   (Browsers)     │
                    └────────┬─────────┘
                             │
                    HTTPS (SSL/TLS)
                             │
                             ▼
                    ┌──────────────────┐
                    │  VERCEL / HEROKU │
                    │  (Frontend Host) │
                    └────────┬─────────┘
                             │
                         REST API
                             │
                             ▼
                    ┌──────────────────┐
                    │ RAILWAY / RENDER │
                    │  (Backend API)   │
                    └────────┬─────────┘
                             │
                             ▼
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   S3 / GCS   │    │  PostgreSQL  │    │ Redis Cache  │
│ (File Store) │    │  (Lead Data) │    │ (Sessions)   │
└──────────────┘    └──────────────┘    └──────────────┘
```

---

**System Status**: ✅ FULLY OPERATIONAL

All components tested and verified working.
