-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================
-- BUSINESSES TABLE
-- Core lead information
-- =====================
CREATE TABLE IF NOT EXISTS businesses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    google_place_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100) DEFAULT 'US',
    phone VARCHAR(50),
    website VARCHAR(500),
    email VARCHAR(255),
    business_type VARCHAR(100),
    google_rating DECIMAL(3,2),
    google_review_count INTEGER DEFAULT 0,
    price_level INTEGER,
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- =====================
-- LEAD SCORES TABLE
-- ML model outputs
-- =====================
CREATE TABLE IF NOT EXISTS lead_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE,
    score DECIMAL(5,4) NOT NULL,
    score_version VARCHAR(50) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    confidence DECIMAL(5,4),
    tier VARCHAR(20) CHECK (tier IN ('hot', 'warm', 'cold')),
    
    -- SHAP feature importance values
    shap_rating_impact DECIMAL(6,4),
    shap_review_count_impact DECIMAL(6,4),
    shap_website_impact DECIMAL(6,4),
    shap_email_impact DECIMAL(6,4),
    shap_location_impact DECIMAL(6,4),
    
    -- Feature values used for scoring
    feature_vector JSONB,
    
    scored_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP DEFAULT NOW() + INTERVAL '7 days'
);

-- =====================
-- OUTREACH TABLE
-- Email campaign tracking
-- =====================
CREATE TABLE IF NOT EXISTS outreach (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE,
    lead_score_id UUID REFERENCES lead_scores(id),
    
    -- Email details
    to_email VARCHAR(255) NOT NULL,
    subject VARCHAR(500),
    body TEXT,
    email_version VARCHAR(50),
    
    -- Status tracking
    status VARCHAR(50) DEFAULT 'pending' 
        CHECK (status IN ('pending', 'sent', 'delivered', 
                         'opened', 'clicked', 'replied', 
                         'bounced', 'failed')),
    
    -- Timestamps
    scheduled_at TIMESTAMP,
    sent_at TIMESTAMP,
    opened_at TIMESTAMP,
    replied_at TIMESTAMP,
    
    -- Agent metadata
    agent_model VARCHAR(100),
    generation_prompt TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================
-- OUTCOMES TABLE
-- Feedback loop data
-- =====================
CREATE TABLE IF NOT EXISTS outcomes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE,
    outreach_id UUID REFERENCES outreach(id),
    
    -- Outcome classification
    outcome_type VARCHAR(50) CHECK (
        outcome_type IN ('converted', 'not_interested', 
                        'no_response', 'follow_up_needed',
                        'invalid_contact')
    ),
    
    -- For ML retraining
    was_good_lead BOOLEAN,
    conversion_value DECIMAL(10,2),
    notes TEXT,
    
    recorded_at TIMESTAMP DEFAULT NOW()
);

-- =====================
-- MODEL VERSIONS TABLE
-- MLflow integration
-- =====================
CREATE TABLE IF NOT EXISTS model_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    version VARCHAR(50) UNIQUE NOT NULL,
    mlflow_run_id VARCHAR(255),
    
    -- Performance metrics
    roc_auc DECIMAL(6,4),
    precision_score DECIMAL(6,4),
    recall_score DECIMAL(6,4),
    f1_score DECIMAL(6,4),
    
    -- Training metadata
    training_sample_size INTEGER,
    feature_count INTEGER,
    is_active BOOLEAN DEFAULT FALSE,
    
    trained_at TIMESTAMP DEFAULT NOW(),
    deployed_at TIMESTAMP
);

-- =====================
-- PIPELINE RUNS TABLE
-- Temporal workflow tracking
-- =====================
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_id VARCHAR(255),
    workflow_type VARCHAR(100),
    status VARCHAR(50) DEFAULT 'running'
        CHECK (status IN ('running', 'completed', 'failed')),
    
    leads_discovered INTEGER DEFAULT 0,
    leads_scored INTEGER DEFAULT 0,
    emails_generated INTEGER DEFAULT 0,
    emails_sent INTEGER DEFAULT 0,
    
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    error_message TEXT
);

-- =====================
-- INDEXES
-- =====================
CREATE INDEX idx_businesses_city ON businesses(city);
CREATE INDEX idx_businesses_type ON businesses(business_type);
CREATE INDEX idx_lead_scores_business ON lead_scores(business_id);
CREATE INDEX idx_lead_scores_score ON lead_scores(score DESC);
CREATE INDEX idx_lead_scores_tier ON lead_scores(tier);
CREATE INDEX idx_outreach_business ON outreach(business_id);
CREATE INDEX idx_outreach_status ON outreach(status);
CREATE INDEX idx_outcomes_business ON outcomes(business_id);
CREATE INDEX idx_outcomes_type ON outcomes(outcome_type);