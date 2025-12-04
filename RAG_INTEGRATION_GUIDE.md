# RAG Integration Guide

## Overview

Your system now has **TWO orchestrators** you can use:

1. **Orchestrator** (Basic) - File-based storage only
2. **OrchestratorRAG** (Advanced) - File storage + Vector DB + Relational DB

## Current Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    EXISTING RAG FRAMEWORK                       │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ClientAgent          VectorAgent         DatabaseAgent        │
│  ├─ OpenAI GPT      ├─ Pinecone          ├─ Supabase          │
│  ├─ Embeddings      ├─ Semantic Search   ├─ PostgreSQL        │
│  └─ Job Analysis    └─ Vector Storage    └─ Full-Text Search  │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌────────────────────────────────────────────────────────────────┐
│                   RAG INTEGRATION LAYER [NEW]                   │
│                                                                 │
│  RAGIntegration                                                │
│  ├─ enhance_research_with_rag()                                │
│  ├─ store_lead_in_vector_db()                                  │
│  ├─ store_lead_in_relational_db()                              │
│  ├─ find_similar_leads()                                       │
│  └─ get_conversion_insights()                                  │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌────────────────────────────────────────────────────────────────┐
│              NEW LEAD QUALIFICATION SYSTEM                      │
│                                                                 │
│  OrchestratorRAG  (Extends base Orchestrator)                  │
│  ├─ All 6 agents (Extract, Research, Score, Analyze,          │
│  │               Write, Store)                                 │
│  ├─ RAG-enhanced research                                      │
│  ├─ Semantic search for leads                                  │
│  ├─ Historical context retrieval                               │
│  └─ ML-ready data pipeline                                     │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

## What Was Integrated

### ✅ New Components

1. **RAGIntegration** ([agents/rag_integration.py](agents/rag_integration.py))
   - Connects ClientAgent, VectorAgent, DatabaseAgent
   - Provides semantic search for similar companies
   - Stores leads in vector DB for RAG retrieval
   - Stores leads in relational DB for structured queries
   - Retrieves historical conversion insights

2. **OrchestratorRAG** ([agents/orchestrator_rag.py](agents/orchestrator_rag.py))
   - Extends base Orchestrator
   - Adds RAG capabilities throughout pipeline
   - Enables semantic search: "Find restaurant companies struggling with seasonal staffing"
   - Provides ML-ready data export

### 🔗 Integration Points

| Stage | Enhancement |
|-------|-------------|
| **Research** | Find similar companies before web search |
| **Analysis** | Retrieve conversion insights from historical leads |
| **Storage** | Store in vector DB (Pinecone) + relational DB (Supabase) + JSON files |
| **Retrieval** | Semantic search across all processed leads |

## Setup Instructions

### Option 1: Basic Mode (No RAG)

```python
from agents.orchestrator import Orchestrator

# File storage only
orchestrator = Orchestrator(data_dir="data/leads")

result = orchestrator.process_posting(html, url)
```

**Pros**: Simple, no external dependencies
**Cons**: No semantic search, no historical context

---

### Option 2: RAG Mode (Full Features)

#### Step 1: Configure APIs

Create/update `.env`:

```bash
# Required for RAG
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=lead-qualification
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=...
```

#### Step 2: Create Supabase Table

Run this SQL in Supabase SQL Editor:

```sql
-- Create qualified_leads table
CREATE TABLE qualified_leads (
    id BIGSERIAL PRIMARY KEY,
    lead_id TEXT UNIQUE NOT NULL,
    company_name TEXT,
    job_title TEXT,
    location TEXT,
    industry TEXT,
    tier INTEGER,
    score INTEGER,
    is_local BOOLEAN,
    posting_url TEXT,
    value_proposition TEXT,
    status TEXT DEFAULT 'new',
    processed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_qualified_leads_tier ON qualified_leads(tier);
CREATE INDEX idx_qualified_leads_status ON qualified_leads(status);
CREATE INDEX idx_qualified_leads_industry ON qualified_leads(industry);

-- Enable full-text search
CREATE INDEX idx_qualified_leads_company_name ON qualified_leads USING GIN(to_tsvector('english', company_name));
```

#### Step 3: Use RAG Orchestrator

```python
from agents.orchestrator_rag import OrchestratorRAG

# Initialize with RAG
orchestrator = OrchestratorRAG(
    data_dir="data/leads",
    enable_vector_db=True,      # Pinecone
    enable_relational_db=True   # Supabase
)

# Process posting (automatically stores in all 3 places)
result = orchestrator.process_posting(html, url)

# Check what was stored
print(f"Vector DB: {result.get('vector_db_stored')}")
print(f"Relational DB: {result.get('relational_db_stored')}")
print(f"File: {result.get('storage_path')}")
```

---

## RAG Features

### 1. Semantic Search

Find leads using natural language:

```python
# Search with natural language
results = orchestrator.semantic_search_leads(
    query="restaurant companies in Phoenix struggling with seasonal staffing",
    filters={"tier": 1},
    top_k=10
)

for match in results:
    print(f"{match['metadata']['company_name']}: {match['score']:.2f}")
```

### 2. Find Similar Leads

```python
# Find leads similar to a specific lead
similar = orchestrator.find_similar_leads(
    lead_id="desert_bistro_group_20251129_210616",
    top_k=5
)

for lead in similar:
    print(f"{lead['metadata']['company_name']}: {lead['score']:.2f}")
```

### 3. Historical Context

When processing new leads, RAG automatically:
- Finds similar companies we've processed
- Estimates company size from similar leads
- Suggests industry based on past data
- Provides conversion probability insights

```python
result = orchestrator.process_posting(html, url)

# Check RAG enhancements
print(result.get('rag_similar_companies'))
print(result.get('rag_estimated_size'))
print(result.get('rag_suggested_industry'))
print(result.get('conversion_insights'))
```

### 4. ML Training Data

Export data for machine learning:

```python
# Get tier 1-2 leads with specific features
training_data = orchestrator.get_ml_training_data(
    include_features=[
        'score', 'tier', 'company_size', 'is_local',
        'pain_points', 'status'
    ],
    min_tier=1,
    max_tier=2
)

# Use for training models
import pandas as pd
df = pd.DataFrame(training_data)
```

### 5. Check RAG Status

```python
status = orchestrator.get_rag_status()

print(f"Semantic Search: {status['semantic_search_enabled']}")
print(f"Vector DB: {status['vector_db']}")
print(f"Relational DB: {status['relational_db']}")
print(f"Total Vectors: {status.get('vector_db_stats', {}).get('total_vectors')}")
```

---

## Data Flow with RAG

```
Input: Job Posting HTML
│
├─ ExtractorAgent
│  └─ Output: Structured data
│
├─ RAG Enhancement (NEW)
│  ├─ Search vector DB for similar companies
│  ├─ Estimate size from historical data
│  └─ Suggest industry based on patterns
│
├─ ResearcherAgent (Enhanced)
│  └─ Uses RAG insights + web search
│
├─ ScorerAgent
│  └─ Output: Score & Tier
│
├─ AnalyzerAgent
│  ├─ Find pain points
│  └─ RAG: Get conversion insights (NEW)
│
├─ WriterAgent
│  └─ Generate scripts & emails
│
└─ Storage (3 layers)
   ├─ StorerAgent → JSON files
   ├─ VectorAgent → Pinecone (semantic search)
   └─ DatabaseAgent → Supabase (structured queries)
```

---

## Migration Path

### Current State: Basic System Working ✅
```python
# What you have now
from agents.orchestrator import Orchestrator
orchestrator = Orchestrator()
```

### Step 1: Add RAG (Optional)
```python
# Upgrade to RAG-enabled version
from agents.orchestrator_rag import OrchestratorRAG

# Start with file storage + vector DB only
orchestrator = OrchestratorRAG(
    enable_vector_db=True,       # Enable Pinecone
    enable_relational_db=False   # Keep Supabase off for now
)
```

### Step 2: Enable Full RAG
```python
# After setting up Supabase table
orchestrator = OrchestratorRAG(
    enable_vector_db=True,
    enable_relational_db=True
)
```

---

## Use Cases

### 1. Market Research
```python
# Find all retail companies in Phoenix
results = orchestrator.semantic_search_leads(
    query="retail companies Phoenix",
    filters={"is_local": True},
    top_k=50
)
```

### 2. Pattern Analysis
```python
# Find successful tier 1 leads
tier1 = orchestrator.get_ml_training_data(min_tier=1, max_tier=1)

# Analyze common pain points
pain_points = {}
for lead in tier1:
    for pain in lead.get('pain_points', []):
        category = pain.get('category')
        pain_points[category] = pain_points.get(category, 0) + 1

print("Most common pain points in tier 1 leads:")
for pain, count in sorted(pain_points.items(), key=lambda x: x[1], reverse=True):
    print(f"  {pain}: {count}")
```

### 3. Conversion Prediction
```python
# When processing a new lead, get conversion insights
result = orchestrator.process_posting(html, url)

insights = result.get('conversion_insights', {})
if insights.get('similar_conversions', 0) > 5:
    print(f"High conversion probability! {insights['similar_conversions']} similar leads converted")
```

---

## Performance Comparison

| Feature | Basic Orchestrator | RAG Orchestrator |
|---------|-------------------|------------------|
| Storage | JSON + CSV | JSON + CSV + Pinecone + Supabase |
| Search | Filters only | Semantic + Filters + Full-text |
| Context | None | Historical patterns |
| ML Ready | Manual export | Built-in export |
| Similar Leads | Not available | Semantic similarity |
| Speed | Fast | Slightly slower (embedding generation) |

---

## Cost Considerations

**Basic Mode**: Free

**RAG Mode**:
- Pinecone: ~$70/month for 1M vectors (free tier: 100K vectors)
- Supabase: Free tier sufficient for most use cases
- OpenAI Embeddings: ~$0.10 per 1000 leads

---

## Next Steps

1. **Test Basic System** ✅ (Already working)
   ```bash
   python test_system.py
   ```

2. **Try RAG Locally** (Optional)
   ```python
   # Test without external services
   from agents.orchestrator_rag import OrchestratorRAG

   # This will warn but still work with file storage
   orch = OrchestratorRAG(
       enable_vector_db=False,
       enable_relational_db=False
   )
   ```

3. **Enable Pinecone** (When ready)
   - Sign up: https://www.pinecone.io
   - Create index
   - Add API key to `.env`
   - Re-run with `enable_vector_db=True`

4. **Enable Supabase** (When ready)
   - Sign up: https://supabase.com
   - Run SQL above
   - Add credentials to `.env`
   - Re-run with `enable_relational_db=True`

---

## Summary

✅ **You have a fully functional RAG framework** - it just wasn't connected to the new agents
✅ **Now it's integrated** - Use `OrchestratorRAG` instead of `Orchestrator`
✅ **Backward compatible** - Original `Orchestrator` still works
✅ **Optional RAG** - Enable only what you need

**Decision Point**:
- Small scale (<100 leads): Use basic `Orchestrator`
- Large scale (1000+ leads): Use `OrchestratorRAG` with full RAG
- Need semantic search: Enable Pinecone
- Need complex queries: Enable Supabase
