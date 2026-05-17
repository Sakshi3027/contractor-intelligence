-- Create database
CREATE DATABASE IF NOT EXISTS contractor_analytics;

-- =====================
-- LEAD EVENTS TABLE
-- Real-time scoring stream
-- =====================
CREATE TABLE IF NOT EXISTS contractor_analytics.lead_events (
    event_id UUID DEFAULT generateUUIDv4(),
    business_id String,
    event_type LowCardinality(String),
    score Float32,
    tier LowCardinality(String),
    city String,
    business_type String,
    google_rating Float32,
    review_count UInt32,
    has_website UInt8,
    has_email UInt8,
    model_version String,
    event_time DateTime DEFAULT now()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_time)
ORDER BY (event_time, business_id)
TTL event_time + INTERVAL 1 YEAR;

-- =====================
-- OUTREACH EVENTS TABLE
-- Email funnel tracking
-- =====================
CREATE TABLE IF NOT EXISTS contractor_analytics.outreach_events (
    event_id UUID DEFAULT generateUUIDv4(),
    business_id String,
    outreach_id String,
    event_type LowCardinality(String),
    email_version String,
    agent_model String,
    city String,
    tier LowCardinality(String),
    event_time DateTime DEFAULT now()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_time)
ORDER BY (event_time, business_id)
TTL event_time + INTERVAL 1 YEAR;

-- =====================
-- MODEL PERFORMANCE TABLE
-- Track model drift over time
-- =====================
CREATE TABLE IF NOT EXISTS contractor_analytics.model_performance (
    run_id UUID DEFAULT generateUUIDv4(),
    model_version String,
    roc_auc Float32,
    precision_score Float32,
    recall_score Float32,
    f1_score Float32,
    training_samples UInt32,
    recorded_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (recorded_at, model_version)
TTL recorded_at + INTERVAL 2 YEAR;

-- =====================
-- PIPELINE METRICS TABLE
-- DAG run statistics
-- =====================
CREATE TABLE IF NOT EXISTS contractor_analytics.pipeline_metrics (
    run_id UUID DEFAULT generateUUIDv4(),
    workflow_type LowCardinality(String),
    leads_discovered UInt32,
    leads_scored UInt32,
    emails_generated UInt32,
    emails_sent UInt32,
    duration_seconds Float32,
    status LowCardinality(String),
    run_time DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (run_time, workflow_type)
TTL run_time + INTERVAL 1 YEAR;

-- =====================
-- CONVERSION FUNNEL VIEW
-- For Grafana dashboard
-- =====================
CREATE VIEW IF NOT EXISTS contractor_analytics.conversion_funnel AS
SELECT
    tier,
    city,
    countIf(event_type = 'scored') AS total_scored,
    countIf(event_type = 'email_sent') AS emails_sent,
    countIf(event_type = 'email_opened') AS emails_opened,
    countIf(event_type = 'email_replied') AS emails_replied,
    countIf(event_type = 'converted') AS converted,
    round(countIf(event_type = 'email_opened') / 
          nullIf(countIf(event_type = 'email_sent'), 0) * 100, 2) AS open_rate,
    round(countIf(event_type = 'converted') / 
          nullIf(countIf(event_type = 'email_sent'), 0) * 100, 2) AS conversion_rate
FROM contractor_analytics.lead_events
GROUP BY tier, city;