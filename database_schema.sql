-- Database schema for Craigslist Job Scraper
-- Run this in your Supabase SQL editor to create the necessary tables

-- Table for storing parsed job postings
CREATE TABLE IF NOT EXISTS jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id VARCHAR(255) UNIQUE NOT NULL,  -- Hash of URL for deduplication
    url TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    location VARCHAR(255),
    category VARCHAR(100),
    posted_date VARCHAR(50),

    -- Extracted data
    skills TEXT[],  -- Array of skills
    pain_points TEXT[],  -- Array of pain points
    salary_min NUMERIC,
    salary_max NUMERIC,
    salary_text TEXT,

    -- Work arrangement
    is_remote BOOLEAN DEFAULT FALSE,
    is_hybrid BOOLEAN DEFAULT FALSE,
    is_onsite BOOLEAN DEFAULT TRUE,

    -- Metadata
    relevance_score NUMERIC,
    scraped_at TIMESTAMP DEFAULT NOW(),
    parsed_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Indexing
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table for storing raw scraped data (before parsing)
CREATE TABLE IF NOT EXISTS raw_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    location VARCHAR(255),
    category VARCHAR(100),
    posted_date VARCHAR(50),
    raw_html TEXT,
    scraped_at TIMESTAMP DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table for tracking scraping runs
CREATE TABLE IF NOT EXISTS scrape_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    city VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL,
    keywords TEXT[],
    jobs_found INTEGER DEFAULT 0,
    jobs_parsed INTEGER DEFAULT 0,
    jobs_stored INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'running',  -- running, completed, failed
    error_message TEXT,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table for job history (track changes over time)
CREATE TABLE IF NOT EXISTS job_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id VARCHAR(255) NOT NULL,
    url TEXT NOT NULL,
    title TEXT,
    description TEXT,
    salary_min NUMERIC,
    salary_max NUMERIC,
    is_remote BOOLEAN,
    snapshot_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_jobs_job_id ON jobs(job_id);
CREATE INDEX IF NOT EXISTS idx_jobs_url ON jobs(url);
CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs(location);
CREATE INDEX IF NOT EXISTS idx_jobs_category ON jobs(category);
CREATE INDEX IF NOT EXISTS idx_jobs_is_remote ON jobs(is_remote);
CREATE INDEX IF NOT EXISTS idx_jobs_scraped_at ON jobs(scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_relevance_score ON jobs(relevance_score DESC);

CREATE INDEX IF NOT EXISTS idx_raw_jobs_processed ON raw_jobs(processed);
CREATE INDEX IF NOT EXISTS idx_raw_jobs_scraped_at ON raw_jobs(scraped_at DESC);

CREATE INDEX IF NOT EXISTS idx_scrape_runs_status ON scrape_runs(status);
CREATE INDEX IF NOT EXISTS idx_scrape_runs_started_at ON scrape_runs(started_at DESC);

CREATE INDEX IF NOT EXISTS idx_job_history_job_id ON job_history(job_id);
CREATE INDEX IF NOT EXISTS idx_job_history_snapshot_at ON job_history(snapshot_at DESC);

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at
CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (optional, for multi-tenant setups)
-- ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE raw_jobs ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE scrape_runs ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE job_history ENABLE ROW LEVEL SECURITY;

-- Views for common queries

-- View: Recent jobs
CREATE OR REPLACE VIEW recent_jobs AS
SELECT
    job_id,
    url,
    title,
    location,
    category,
    is_remote,
    is_hybrid,
    salary_min,
    salary_max,
    relevance_score,
    skills,
    pain_points,
    scraped_at
FROM jobs
ORDER BY scraped_at DESC
LIMIT 100;

-- View: Remote jobs
CREATE OR REPLACE VIEW remote_jobs AS
SELECT
    job_id,
    url,
    title,
    location,
    category,
    salary_min,
    salary_max,
    skills,
    pain_points,
    relevance_score,
    scraped_at
FROM jobs
WHERE is_remote = TRUE
ORDER BY scraped_at DESC;

-- View: High-relevance jobs
CREATE OR REPLACE VIEW high_relevance_jobs AS
SELECT
    job_id,
    url,
    title,
    location,
    category,
    is_remote,
    salary_min,
    salary_max,
    skills,
    pain_points,
    relevance_score,
    scraped_at
FROM jobs
WHERE relevance_score >= 0.7
ORDER BY relevance_score DESC, scraped_at DESC;

-- Comments
COMMENT ON TABLE jobs IS 'Parsed and enriched job postings';
COMMENT ON TABLE raw_jobs IS 'Raw scraped job data before processing';
COMMENT ON TABLE scrape_runs IS 'Tracking information for each scraping run';
COMMENT ON TABLE job_history IS 'Historical snapshots of job postings for tracking changes';
