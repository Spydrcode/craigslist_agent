# Project Structure

Complete overview of the Craigslist Agent project architecture.

## Directory Tree

```
craigslist_agent/
│
├── agents/                     # Agent modules (core logic)
│   ├── __init__.py            # Agent exports
│   ├── client_agent.py        # GPT API wrapper (AI reasoning)
│   ├── scraper_agent.py       # Craigslist scraper
│   ├── parser_agent.py        # Job parsing & extraction
│   ├── vector_agent.py        # Pinecone vector operations
│   └── database_agent.py      # Supabase database operations
│
├── dashboard/                  # Streamlit web interface
│   └── app.py                 # Interactive dashboard
│
├── examples/                   # Example scripts
│   ├── basic_scrape.py        # Simple scraping demo
│   ├── ai_parsing.py          # AI parsing demo
│   └── full_pipeline.py       # Complete workflow demo
│
├── utils/                      # Utility modules
│   ├── __init__.py
│   ├── logger.py              # Logging configuration
│   └── helpers.py             # Helper functions
│
├── logs/                       # Log files (created automatically)
├── data/                       # Data storage (created automatically)
├── exports/                    # CSV exports (created automatically)
│
├── config.py                   # Configuration management
├── models.py                   # Pydantic data models
├── orchestrator.py            # Main orchestrator
├── main.py                    # CLI entry point
│
├── database_schema.sql        # Supabase database schema
├── requirements.txt           # Python dependencies
├── setup.py                   # Setup wizard
│
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
├── LICENSE                    # MIT License
├── README.md                  # Full documentation
├── QUICKSTART.md              # Quick start guide
└── PROJECT_STRUCTURE.md       # This file
```

## Module Breakdown

### Core Agents (`agents/`)

#### 1. `client_agent.py` - AI Client
**Purpose**: Wrapper for OpenAI GPT API

**Key Classes**:
- `ClientAgent`: Main client for GPT interactions

**Key Methods**:
- `extract_pain_points()`: Extract business problems from job descriptions
- `extract_skills()`: Identify required and nice-to-have skills
- `analyze_work_arrangement()`: Determine remote/hybrid/onsite
- `score_relevance()`: Rate job relevance based on criteria
- `generate_summary()`: Create concise job summaries
- `analyze_job_posting()`: Comprehensive job analysis
- `get_embeddings()`: Generate text embeddings

**Dependencies**: OpenAI, tenacity (retry logic)

---

#### 2. `scraper_agent.py` - Web Scraper
**Purpose**: Scrape job listings from Craigslist

**Key Classes**:
- `ScraperAgent`: Handles web scraping with rate limiting

**Key Methods**:
- `scrape_listings()`: Main scraping method with pagination
- `_fetch_page()`: Fetch single page with retries
- `_parse_listing_page()`: Extract job listings from search results
- `_parse_job_detail()`: Extract full job description
- `scrape_single_job()`: Scrape individual job by URL
- `test_connection()`: Verify Craigslist connectivity

**Features**:
- Automatic pagination
- Rate limiting with random delays
- Retry logic with exponential backoff
- Anti-bot detection handling

**Dependencies**: requests, BeautifulSoup4, tenacity

---

#### 3. `parser_agent.py` - Data Parser
**Purpose**: Convert raw job data to structured format

**Key Classes**:
- `ParserAgent`: Processes raw jobs into structured data

**Key Methods**:
- `parse_job()`: Parse single job with AI or basic extraction
- `parse_jobs()`: Batch parsing
- `score_job_relevance()`: Score based on custom criteria
- `enrich_job()`: Add AI-powered insights
- `batch_parse_with_progress()`: Progress-tracked batch parsing

**Features**:
- AI-powered extraction (skills, pain points)
- Regex-based salary extraction
- Work arrangement detection
- Fallback to basic extraction if AI unavailable

**Dependencies**: ClientAgent, utils

---

#### 4. `vector_agent.py` - Vector Storage
**Purpose**: Manage embeddings and semantic search

**Key Classes**:
- `VectorAgent`: Pinecone integration for vector operations

**Key Methods**:
- `embed_job()`: Generate embeddings for job posting
- `upsert_job()`: Store single job embedding
- `upsert_jobs()`: Batch upload embeddings
- `search_similar_jobs()`: Semantic search
- `find_similar_to_job()`: Find jobs similar to specific job
- `get_job()`: Retrieve job by ID
- `delete_job()`: Remove job from index
- `search_by_criteria()`: Search by filters + semantic similarity

**Features**:
- Automatic index creation
- Batch processing for efficiency
- Metadata filtering
- Similarity scoring

**Dependencies**: Pinecone, ClientAgent (for embeddings)

---

#### 5. `database_agent.py` - Database Operations
**Purpose**: Persist data in Supabase PostgreSQL

**Key Classes**:
- `DatabaseAgent`: Supabase CRUD operations

**Key Methods**:
- `insert_raw_job()`: Store raw scraped data
- `insert_parsed_job()`: Store parsed job (upsert)
- `get_job_by_id()`: Retrieve job by ID
- `get_recent_jobs()`: Get latest jobs
- `get_jobs_by_criteria()`: Filtered query
- `search_jobs()`: Text search
- `update_job()`: Modify job data
- `create_scrape_run()`: Track scraping runs
- `complete_scrape_run()`: Mark run complete
- `get_stats()`: Database statistics

**Features**:
- Batch inserts for performance
- Upsert operations (no duplicates)
- Scrape run tracking
- Full-text search
- Statistics and analytics

**Dependencies**: Supabase client

---

### Orchestrator (`orchestrator.py`)

**Purpose**: Coordinate entire pipeline workflow

**Key Class**: `Orchestrator`

**Key Methods**:
- `run_pipeline()`: Execute complete scrape → parse → vector → DB workflow
- `search_jobs()`: Unified search interface (semantic or text)
- `get_job_recommendations()`: Find similar jobs
- `schedule_daily_scrape()`: Set up automated scraping
- `start_scheduler()`: Start background scheduler
- `analyze_job_market()`: Market statistics and trends
- `export_jobs_to_csv()`: Export data

**Workflow**:
1. Initialize all agents
2. Scrape jobs (ScraperAgent)
3. Parse with AI (ParserAgent + ClientAgent)
4. Generate embeddings (VectorAgent)
5. Store in database (DatabaseAgent)
6. Track metrics and errors

**Dependencies**: All agents, APScheduler

---

### Data Models (`models.py`)

**Pydantic Models**:

1. **RawJobPosting**: Raw scraped data
   - title, url, description, location, category
   - posted_date, scraped_at, raw_html

2. **ParsedJobPosting**: Structured job data
   - All fields from RawJobPosting
   - skills, pain_points
   - salary_min, salary_max, salary_text
   - is_remote, is_hybrid, is_onsite
   - relevance_score, parsed_at

3. **JobEmbedding**: Vector representation
   - job_id, url, title
   - description_embedding, pain_points_embedding
   - metadata

4. **ScraperConfig**: Scraper settings
   - city, category, keywords
   - max_pages, delay_min, delay_max

5. **SearchQuery**: Search parameters
   - query_text, top_k
   - filter_metadata, min_score

6. **JobAnalysis**: AI analysis results
   - pain_points, required_skills, nice_to_have_skills
   - work_arrangement, relevance_score, summary

---

### Configuration (`config.py`)

**Purpose**: Centralized configuration from environment variables

**Key Class**: `Config`

**Configuration Categories**:
- OpenAI: API key, model
- Pinecone: API key, environment, index name
- Supabase: URL, API key
- Scraping: Delays, retries, timeout
- Logging: Log level

**Features**:
- Loads from `.env` file
- Validation on import
- Type hints for all settings

---

### Utilities (`utils/`)

#### `logger.py`
- `setup_logger()`: Configure logger with file/console output
- `get_logger()`: Get logger instance

#### `helpers.py`
- `generate_job_id()`: Hash-based unique IDs
- `extract_salary_info()`: Regex salary extraction
- `detect_work_arrangement()`: Keyword-based detection
- `deduplicate_jobs()`: Remove duplicates by URL
- `clean_text()`: Text normalization
- `chunk_text()`: Split long text for token limits

---

### Main Entry Point (`main.py`)

**Purpose**: Command-line interface

**Commands**:
- `scrape`: Run scraping pipeline
- `search`: Search jobs
- `analyze`: Market analysis
- `schedule`: Schedule daily scraping
- `export`: Export to CSV

**Features**:
- Argument parsing with argparse
- Pretty-printed output
- Error handling and user feedback

---

### Dashboard (`dashboard/app.py`)

**Purpose**: Interactive web interface

**Pages**:
1. **Dashboard**: Overview and statistics
2. **Search Jobs**: Semantic and text search
3. **Run Scraper**: Interactive scraping
4. **Market Analysis**: Visualizations
5. **Export Data**: Filtered exports

**Features**:
- Built with Streamlit
- Plotly visualizations
- Real-time updates
- Interactive filters

**Dependencies**: Streamlit, Plotly, Pandas

---

### Database Schema (`database_schema.sql`)

**Tables**:

1. **jobs**: Parsed job postings
   - Primary data storage
   - Full-text search indexes
   - Relevance scoring

2. **raw_jobs**: Raw scraped data
   - Before processing
   - Backup of original HTML

3. **scrape_runs**: Run tracking
   - Execution history
   - Success/failure tracking
   - Performance metrics

4. **job_history**: Historical snapshots
   - Track changes over time
   - Salary trends
   - Job status changes

**Views**:
- `recent_jobs`: Latest 100 jobs
- `remote_jobs`: Remote positions only
- `high_relevance_jobs`: Score ≥ 0.7

**Indexes**: Optimized for common queries

---

## Data Flow

```
1. User Input
   ↓
2. Orchestrator.run_pipeline()
   ↓
3. ScraperAgent.scrape_listings()
   → Raw job listings
   ↓
4. ParserAgent.parse_jobs()
   → ClientAgent.extract_pain_points()
   → ClientAgent.extract_skills()
   → Structured data
   ↓
5. VectorAgent.upsert_jobs()
   → ClientAgent.get_embeddings()
   → Store in Pinecone
   ↓
6. DatabaseAgent.insert_parsed_jobs()
   → Store in Supabase
   ↓
7. Results returned to user
```

## Extension Points

### Adding New Features

1. **New Agent**: Create in `agents/` directory
   - Inherit from base patterns
   - Add to `agents/__init__.py`
   - Integrate in Orchestrator

2. **New Data Model**: Add to `models.py`
   - Use Pydantic for validation
   - Update database schema if needed

3. **New Dashboard Page**: Edit `dashboard/app.py`
   - Add to navigation sidebar
   - Create new function
   - Call `show_<page_name>()`

4. **New CLI Command**: Edit `main.py`
   - Add subparser
   - Create handler function
   - Add to command dispatcher

### Customization Examples

**Custom Scraper for Different Site**:
```python
# agents/custom_scraper.py
class CustomScraperAgent(ScraperAgent):
    def scrape_listings(self):
        # Your custom logic
        pass
```

**Custom Parser with Domain Logic**:
```python
# agents/domain_parser.py
class DomainParserAgent(ParserAgent):
    def extract_domain_specific_data(self, job):
        # Industry-specific extraction
        pass
```

**Custom Analysis**:
```python
# Add to orchestrator.py
def custom_analysis(self, jobs):
    # Your analysis logic
    return insights
```

---

## Technology Stack Summary

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Language | Python 3.10+ | Core development |
| Web Scraping | requests + BeautifulSoup4 | HTML parsing |
| AI/LLM | OpenAI GPT-4 | Intelligent extraction |
| Vector DB | Pinecone | Semantic search |
| Database | Supabase (PostgreSQL) | Structured storage |
| Validation | Pydantic | Data models |
| Dashboard | Streamlit | Web interface |
| Visualization | Plotly | Charts and graphs |
| Scheduling | APScheduler | Automation |
| Retry Logic | tenacity | Resilience |
| Data Processing | Pandas | Analysis |

---

## Performance Characteristics

- **Scraping Speed**: ~2-5 seconds per job (with delays)
- **Parsing Speed**: ~1-2 seconds per job (with AI)
- **Embedding Generation**: ~0.5 seconds per job
- **Database Insert**: <0.1 seconds per job (batched)
- **Semantic Search**: <1 second for top-k results

**Bottlenecks**:
1. Craigslist rate limiting (intentional delays)
2. OpenAI API calls (can be parallelized)
3. Network latency

**Optimizations**:
- Batch processing where possible
- Caching of embeddings
- Database connection pooling
- Parallel agent execution (future enhancement)

---

For more information, see README.md
