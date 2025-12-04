-- Clients Management Schema
-- Table for storing clients added from qualified prospects

CREATE TABLE IF NOT EXISTS clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Company Information
    company_name VARCHAR(500) NOT NULL,
    industry VARCHAR(200),
    location VARCHAR(255),
    
    -- Contact Information
    contact_name VARCHAR(255),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    contact_title VARCHAR(255),
    
    -- Lead Scoring
    tier VARCHAR(50) NOT NULL,  -- HOT, QUALIFIED, POTENTIAL
    score NUMERIC DEFAULT 0,
    qualification_reason TEXT,
    
    -- Business Intelligence
    pain_points TEXT[],
    growth_indicators TEXT[],
    value_proposition TEXT,
    job_count INTEGER DEFAULT 0,
    
    -- Source Information
    source_url TEXT,  -- Original job posting URL
    source_description TEXT,  -- Full job description
    source_date TIMESTAMP,
    
    -- Outreach Status
    outreach_status VARCHAR(50) DEFAULT 'NEW',  -- NEW, CONTACTED, RESPONDED, QUALIFIED, CLOSED_WON, CLOSED_LOST
    outreach_method VARCHAR(50),  -- EMAIL, PHONE, LINKEDIN, etc.
    last_contact_date TIMESTAMP,
    next_followup_date TIMESTAMP,
    
    -- Generated Content
    email_draft TEXT,
    call_script TEXT,
    
    -- Interaction History
    notes TEXT,
    interaction_count INTEGER DEFAULT 0,
    
    -- Metadata
    added_by VARCHAR(255),
    added_date TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Full-text search
    search_vector tsvector
);

-- Table for tracking client interactions/touchpoints
CREATE TABLE IF NOT EXISTS client_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    
    interaction_type VARCHAR(50) NOT NULL,  -- EMAIL_SENT, CALL_MADE, MEETING_SCHEDULED, etc.
    interaction_date TIMESTAMP DEFAULT NOW(),
    
    subject VARCHAR(500),
    content TEXT,
    outcome VARCHAR(50),  -- SUCCESS, NO_RESPONSE, VOICEMAIL, CALLBACK_REQUESTED, etc.
    
    next_action VARCHAR(500),
    next_action_date TIMESTAMP,
    
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_clients_company_name ON clients(company_name);
CREATE INDEX IF NOT EXISTS idx_clients_tier ON clients(tier);
CREATE INDEX IF NOT EXISTS idx_clients_score ON clients(score DESC);
CREATE INDEX IF NOT EXISTS idx_clients_outreach_status ON clients(outreach_status);
CREATE INDEX IF NOT EXISTS idx_clients_added_date ON clients(added_date DESC);
CREATE INDEX IF NOT EXISTS idx_clients_next_followup ON clients(next_followup_date);
CREATE INDEX IF NOT EXISTS idx_clients_search_vector ON clients USING gin(search_vector);

CREATE INDEX IF NOT EXISTS idx_interactions_client_id ON client_interactions(client_id);
CREATE INDEX IF NOT EXISTS idx_interactions_date ON client_interactions(interaction_date DESC);
CREATE INDEX IF NOT EXISTS idx_interactions_type ON client_interactions(interaction_type);

-- Trigger to update search_vector for full-text search
CREATE OR REPLACE FUNCTION update_client_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', COALESCE(NEW.company_name, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.industry, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.location, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.qualification_reason, '')), 'C') ||
        setweight(to_tsvector('english', COALESCE(NEW.notes, '')), 'D');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_clients_search_vector
BEFORE INSERT OR UPDATE ON clients
FOR EACH ROW EXECUTE FUNCTION update_client_search_vector();

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_clients_updated_at
BEFORE UPDATE ON clients
FOR EACH ROW EXECUTE FUNCTION update_updated_at();
