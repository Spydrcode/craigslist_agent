# System Audit & Cleanup Plan

## Current System Architecture

### **✅ ACTIVE FILES (Core System)**

#### **Main Entry Points**
1. `dashboard_with_agents.py` - **PRIMARY** Web dashboard with real-time agent tracking
2. `config.py` - Configuration management (gpt-4o-mini)
3. `models.py` - Core data models (RawJobPosting, ScraperConfig, etc.)
4. `models_enhanced.py` - Enhanced models (CompanyProfile, ProspectLead, GrowthSignals)

#### **Core Orchestrators**
1. `orchestrator_simple.py` - Base orchestrator (7-agent pipeline)
2. `orchestrator_observable.py` - **ACTIVE** Observable wrapper for real-time progress

#### **Active Agents** (agents/)
1. `scraper_agent.py` - Scrapes Craigslist (with quick_scan_only mode)
2. `parser_agent.py` - Parses jobs with AI
3. `growth_signal_analyzer.py` - Analyzes company growth
4. `company_research_agent.py` - Researches companies
5. `service_matcher_agent.py` - Matches services to pain points
6. `ml_scoring_agent.py` - Scores leads with ML
7. `outreach_agent.py` - Generates outreach emails
8. `client_agent.py` - OpenAI API wrapper
9. **`quick_filter_agent.py`** - NEW: Fast heuristic filtering (hiring velocity focus)
10. **`company_scorer.py`** - NEW: Intelligent company scoring (70% hiring velocity)

#### **Supporting Files**
1. `agent_progress.py` - Progress tracking for WebSocket
2. `client_manager.py` - Client/prospect management
3. `craigslist_discovery.py` - Auto-discovers cities & categories
4. `utils.py` - Utility functions (logging, extraction)

---

### **❌ DUPLICATE/UNUSED FILES (To Remove)**

#### **Duplicate Orchestrators**
- `orchestrator.py` - OLD version, superseded by orchestrator_simple.py
- `orchestrator_enhanced.py` - OLD version with DB dependencies we don't use
- `agents/orchestrator.py` - Duplicate in wrong location
- `agents/orchestrator_rag.py` - RAG features not implemented

#### **Duplicate Models**
- `config_enhanced.py` - Duplicate of config.py

#### **Duplicate Dashboards**
- `dashboard_app.py` - OLD dashboard without agents
- `run_dashboard.py` - OLD runner script

#### **Old Test Files**
- `test_scraper_bham.py` - One-time test, keep for debugging
- `test_connections.py` - OLD with DB dependencies
- `test_connections_simple.py` - OLD
- `test_rag_integration.py` - RAG not used
- `test_system.py` - Generic test

#### **Old Runner Scripts**
- `main.py` - OLD main entry
- `main_prospecting.py` - OLD prospecting entry
- `run_prospecting_simple.py` - OLD runner
- `batch_prospecting.py` - OLD batch runner

#### **Unused Agents** (agents/)
- `analyzer.py` - Functionality absorbed by other agents
- `database_agent.py` - We don't use DB (file-based only)
- `extractor.py` - Functionality in parser_agent
- `job_qualifier_agent.py` - Superseded by company_scorer
- `lead_analysis_agent.py` - Functionality distributed to other agents
- `rag_integration.py` - RAG not implemented
- `researcher.py` - Superseded by company_research_agent
- `scorer.py` - Superseded by ml_scoring_agent
- `storer.py` - Simple file I/O, not needed
- `vector_agent.py` - RAG/embeddings not used
- `writer.py` - Functionality in other agents

#### **Keep for Reference** (Unused but potentially useful)
- `manage_clients.py` - CLI tool for client management
- `setup.py` - Package setup

---

## **Active System Flow**

```
USER
  ↓
dashboard_with_agents.py (Flask + WebSocket)
  ↓
orchestrator_observable.py
  ↓
orchestrator_simple.py
  ↓
┌─────────────────────────────────────────┐
│ 7-AGENT PIPELINE                        │
├─────────────────────────────────────────┤
│ 1. scraper_agent → Quick scan ALL jobs │
│ 2. quick_filter_agent → Group by company, filter spam │
│ 3. company_scorer → Score by hiring velocity │
│ 4. parser_agent → AI parse top 30      │
│ 5. growth_signal_analyzer → Growth analysis │
│ 6. service_matcher_agent → Match services │
│ 7. ml_scoring_agent → Final scoring    │
└─────────────────────────────────────────┘
  ↓
Results saved to: output/prospects/
  ↓
Dashboard displays ranked companies
  ↓
USER selects companies
  ↓
outreach_agent → Generate email (on-demand)
```

---

## **Cleanup Actions**

### **Phase 1: Remove Duplicates**
```bash
# Remove duplicate orchestrators
rm orchestrator.py
rm orchestrator_enhanced.py
rm agents/orchestrator.py
rm agents/orchestrator_rag.py

# Remove duplicate config
rm config_enhanced.py

# Remove old dashboards
rm dashboard_app.py
rm run_dashboard.py

# Remove old runners
rm main.py
rm main_prospecting.py
rm run_prospecting_simple.py
rm batch_prospecting.py
```

### **Phase 2: Archive Unused Agents**
```bash
# Create archive directory
mkdir -p archive/unused_agents

# Move unused agents
mv agents/analyzer.py archive/unused_agents/
mv agents/database_agent.py archive/unused_agents/
mv agents/extractor.py archive/unused_agents/
mv agents/job_qualifier_agent.py archive/unused_agents/
mv agents/lead_analysis_agent.py archive/unused_agents/
mv agents/rag_integration.py archive/unused_agents/
mv agents/researcher.py archive/unused_agents/
mv agents/scorer.py archive/unused_agents/
mv agents/storer.py archive/unused_agents/
mv agents/vector_agent.py archive/unused_agents/
mv agents/writer.py archive/unused_agents/
```

### **Phase 3: Archive Old Tests**
```bash
mkdir -p archive/old_tests

mv test_connections.py archive/old_tests/
mv test_connections_simple.py archive/old_tests/
mv test_rag_integration.py archive/old_tests/
mv test_system.py archive/old_tests/
```

---

## **Final Clean Structure**

```
craigslist_agent/
├── dashboard_with_agents.py      # Main entry point
├── config.py                      # Configuration
├── models.py                      # Core models
├── models_enhanced.py             # Enhanced models
├── orchestrator_simple.py         # Base orchestrator
├── orchestrator_observable.py     # Observable wrapper
├── agent_progress.py              # Progress tracking
├── client_manager.py              # Client management
├── craigslist_discovery.py        # City/category discovery
├── utils.py                       # Utilities
│
├── agents/
│   ├── __init__.py
│   ├── scraper_agent.py           # Phase 1: Quick scan
│   ├── quick_filter_agent.py      # Phase 2: Filter & group
│   ├── company_scorer.py          # Phase 3: Score companies
│   ├── parser_agent.py            # Phase 4: AI parsing
│   ├── growth_signal_analyzer.py  # Phase 5: Growth analysis
│   ├── service_matcher_agent.py   # Phase 6: Service matching
│   ├── ml_scoring_agent.py        # Phase 7: ML scoring
│   ├── outreach_agent.py          # On-demand: Email generation
│   ├── company_research_agent.py  # On-demand: Deep research
│   └── client_agent.py            # OpenAI wrapper
│
├── dashboard/
│   └── templates/
│       └── dashboard_with_agents.html
│
├── output/
│   └── prospects/                 # Results saved here
│
├── data/
│   ├── clients/                   # Client data
│   └── craigslist_locations.json  # Cached cities
│
├── docs/
│   ├── HIRING_VELOCITY_HYPOTHESIS.md
│   ├── QUALIFICATION_CRITERIA.md
│   └── SYSTEM_AUDIT_AND_CLEANUP.md
│
├── archive/                       # Archived unused files
│   ├── unused_agents/
│   └── old_tests/
│
└── test_scraper_bham.py          # Keep for debugging
```

---

## **Professional Agentic Framework**

### **Architecture Principles**

1. **Single Responsibility**
   - Each agent does ONE thing well
   - No overlapping functionality

2. **Observable Pattern**
   - All agents report progress
   - WebSocket for real-time updates

3. **Hypothesis-Driven**
   - System optimized for hiring velocity
   - 70% weight on job count

4. **Two-Phase Processing**
   - Phase 1: Fast scan ALL data (5 sec)
   - Phase 2: Deep analysis on top 30 (2-3 min)

5. **Cost-Optimized**
   - gpt-4o-mini (99% cost savings)
   - Only analyze promising companies

6. **File-Based**
   - No database dependencies
   - Results saved to JSON/CSV
   - Easy to inspect and debug

---

## **✅ INTEGRATION COMPLETE: New Agents Connected**

~~The new agents (quick_filter_agent, company_scorer) are created but NOT integrated into the orchestrator yet.~~

### **✅ COMPLETED: Updated orchestrator_observable.py**

The two-phase workflow is now fully integrated:

```python
# PHASE 1: FAST (5-7 seconds)
# STAGE 1: Quick Scan (5 sec)
raw_jobs = scraper.scrape_listings()  # Get ALL jobs, no details

# STAGE 2: Filter & Group (1 sec)
from agents.quick_filter_agent import QuickFilterAgent
filter_agent = QuickFilterAgent()
promising_companies = filter_agent.filter_and_group_jobs(raw_jobs, min_company_jobs=3)

# STAGE 3: Score & Rank (1 sec)
from agents.company_scorer import CompanyScoringAgent
scorer = CompanyScoringAgent()
scored_companies = scorer.score_companies(promising_companies)

# Select Top 30 for Deep Analysis
top_companies = scorer.get_top_companies(scored_companies, top_n=30)

# PHASE 2: SELECTIVE (2-3 minutes)
# STAGE 4: Fetch Full Details & Parse with AI
# STAGE 5: Growth Analysis
# STAGE 6: Company Research (optional)
# STAGE 7: Service Matching
# STAGE 8: ML Scoring
# STAGE 9: Save Results
```

**Integration Status**: ✅ COMPLETE
**File Updated**: [orchestrator_observable.py](orchestrator_observable.py)
**Date**: 2025-12-03

---

## **Validation Checklist**

- [x] Remove duplicate files ✅
- [x] Archive unused agents ✅
- [x] Integrate quick_filter_agent into orchestrator ✅
- [x] Integrate company_scorer into orchestrator ✅
- [x] Update scraper to use quick_scan_only=True ✅
- [x] Update README.md with new system ✅
- [ ] Test full pipeline with real data ⏳ **NEXT STEP**
- [ ] Verify WebSocket progress updates work
- [ ] Verify results sorted by hiring velocity
- [ ] Document final API endpoints
- [ ] Optimize Phase 2 job detail fetching
