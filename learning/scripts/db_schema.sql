-- GHOST WRITER VOICE DATABASE SCHEMA
-- Version: 1.0.0
-- SQLite Database for Voice Pattern Storage and Learning
-- Location: D:\Ghost Writer\learning\voice.db

-- =====================================================
-- VOICE PATTERNS TABLE
-- =====================================================
-- Stores extracted voice patterns from samples
-- Used during generation to guide voice authenticity

CREATE TABLE IF NOT EXISTS voice_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_type TEXT NOT NULL,  -- 'contraction', 'sentence_structure', 'transition', 'phrase', 'tone_marker'
    pattern_text TEXT NOT NULL,  -- The actual pattern (e.g., "it's", "Here's how", "The way I see it:")
    environment TEXT,  -- 'dev', 'research', 'career', 'work', 'personal', 'universal' (NULL = universal)
    confidence REAL DEFAULT 0.5,  -- 0.0-1.0 (how confident we are this is authentic)
    frequency INTEGER DEFAULT 1,  -- How many times seen
    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
    source_samples TEXT,  -- JSON array of sample IDs: ["sample_123", "sample_456"]
    context TEXT,  -- When this pattern appears (e.g., "opening hook", "closing", "transition")
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(pattern_type, pattern_text, environment)
);

CREATE INDEX idx_patterns_type_env ON voice_patterns(pattern_type, environment);
CREATE INDEX idx_patterns_confidence ON voice_patterns(confidence DESC);
CREATE INDEX idx_patterns_frequency ON voice_patterns(frequency DESC);
CREATE INDEX idx_patterns_last_seen ON voice_patterns(last_seen DESC);

-- =====================================================
-- VOICE SAMPLES TABLE
-- =====================================================
-- Complete outputs stored for reference and pattern extraction
-- Deduplication via content_hash

CREATE TABLE IF NOT EXISTS voice_samples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_hash TEXT UNIQUE NOT NULL,  -- SHA256 for deduplication
    content TEXT NOT NULL,  -- Full text content
    environment TEXT NOT NULL,  -- 'dev', 'research', 'career', 'work', 'personal'
    context_type TEXT,  -- 'cover_letter', 'linkedin_post', 'email', 'documentation', etc.
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    word_count INTEGER,
    contraction_rate REAL,  -- 0.0-1.0
    dash_density REAL,  -- dashes per page
    quality_score REAL,  -- 0.0-1.0 (from quality_gate.py)
    context_tags TEXT,  -- JSON array: ['professional', 'direct', 'analytical']
    extracted BOOLEAN DEFAULT 0,  -- Has pattern extraction been run?
    file_path TEXT,  -- Original file location
    FOREIGN KEY (id) REFERENCES voice_patterns(source_samples)
);

CREATE INDEX idx_samples_hash ON voice_samples(content_hash);
CREATE INDEX idx_samples_env ON voice_samples(environment);
CREATE INDEX idx_samples_quality ON voice_samples(quality_score DESC);
CREATE INDEX idx_samples_timestamp ON voice_samples(timestamp DESC);
CREATE INDEX idx_samples_extracted ON voice_samples(extracted);
CREATE INDEX idx_samples_context ON voice_samples(context_type);

-- =====================================================
-- FORBIDDEN PATTERNS TABLE
-- =====================================================
-- Patterns to avoid (buzzwords, fabrications, tone violations)

CREATE TABLE IF NOT EXISTS forbidden_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern TEXT UNIQUE NOT NULL,  -- Pattern to avoid (can be regex)
    reason TEXT NOT NULL,  -- Why this is forbidden
    severity TEXT DEFAULT 'warning',  -- 'blocking', 'warning', 'suggestion'
    category TEXT,  -- 'fabrication', 'buzzword', 'tone', 'grammar', etc.
    environment TEXT,  -- NULL = applies to all, otherwise environment-specific
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_forbidden_severity ON forbidden_patterns(severity);
CREATE INDEX idx_forbidden_category ON forbidden_patterns(category);
CREATE INDEX idx_forbidden_env ON forbidden_patterns(environment);

-- =====================================================
-- LEARNING INSIGHTS TABLE
-- =====================================================
-- Cross-session learning and pattern discoveries

CREATE TABLE IF NOT EXISTS learning_insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    insight_type TEXT NOT NULL,  -- 'voice_drift', 'new_pattern', 'quality_improvement', 'environment_calibration'
    description TEXT NOT NULL,  -- Human-readable insight
    evidence TEXT,  -- JSON with supporting data
    confidence REAL,  -- 0.0-1.0 (how confident in this insight)
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    applied BOOLEAN DEFAULT 0,  -- Has this been incorporated into protocols?
    environment TEXT,  -- Which environment this applies to (NULL = universal)
    source_samples TEXT  -- JSON array of sample IDs that led to this insight
);

CREATE INDEX idx_insights_type ON learning_insights(insight_type);
CREATE INDEX idx_insights_applied ON learning_insights(applied);
CREATE INDEX idx_insights_timestamp ON learning_insights(timestamp DESC);
CREATE INDEX idx_insights_env ON learning_insights(environment);

-- =====================================================
-- SESSION LOG TABLE
-- =====================================================
-- Track sessions and what was generated

CREATE TABLE IF NOT EXISTS session_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,  -- UUID or timestamp-based
    environment TEXT NOT NULL,
    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    end_time DATETIME,
    samples_generated INTEGER DEFAULT 0,
    patterns_extracted INTEGER DEFAULT 0,
    quality_avg REAL,  -- Average quality score for session
    notes TEXT,  -- Session summary, user feedback, corrections
    status TEXT DEFAULT 'active'  -- 'active', 'complete', 'crashed'
);

CREATE INDEX idx_sessions_env ON session_log(environment);
CREATE INDEX idx_sessions_start ON session_log(start_time DESC);
CREATE INDEX idx_sessions_status ON session_log(status);

-- =====================================================
-- QUALITY METRICS TABLE
-- =====================================================
-- Track quality metrics over time

CREATE TABLE IF NOT EXISTS quality_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sample_id INTEGER NOT NULL,
    metric_name TEXT NOT NULL,  -- 'contraction_rate', 'dash_density', 'forbidden_count', etc.
    metric_value REAL NOT NULL,
    pass BOOLEAN,  -- Did this metric pass validation?
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sample_id) REFERENCES voice_samples(id)
);

CREATE INDEX idx_metrics_sample ON quality_metrics(sample_id);
CREATE INDEX idx_metrics_name ON quality_metrics(metric_name);
CREATE INDEX idx_metrics_pass ON quality_metrics(pass);

-- =====================================================
-- VOICE DRIFT TRACKING
-- =====================================================
-- Track how voice evolves over time

CREATE TABLE IF NOT EXISTS voice_drift (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    environment TEXT NOT NULL,
    metric_name TEXT NOT NULL,  -- 'contraction_rate', 'formality', 'directness', etc.
    baseline_value REAL,  -- Original baseline
    current_value REAL,  -- Current measured value
    drift_percentage REAL,  -- % change from baseline
    direction TEXT  -- 'increasing', 'decreasing', 'stable'
);

CREATE INDEX idx_drift_env ON voice_drift(environment);
CREATE INDEX idx_drift_timestamp ON voice_drift(timestamp DESC);
CREATE INDEX idx_drift_metric ON voice_drift(metric_name);

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- High-confidence patterns by environment
CREATE VIEW IF NOT EXISTS high_confidence_patterns AS
SELECT 
    pattern_type,
    pattern_text,
    environment,
    confidence,
    frequency,
    context
FROM voice_patterns
WHERE confidence > 0.7
ORDER BY environment, confidence DESC, frequency DESC;

-- Recent high-quality samples
CREATE VIEW IF NOT EXISTS recent_quality_samples AS
SELECT 
    id,
    environment,
    context_type,
    timestamp,
    quality_score,
    contraction_rate,
    word_count
FROM voice_samples
WHERE quality_score > 0.8 AND extracted = 1
ORDER BY timestamp DESC
LIMIT 50;

-- Patterns needing extraction
CREATE VIEW IF NOT EXISTS unextracted_samples AS
SELECT 
    id,
    environment,
    context_type,
    timestamp,
    file_path
FROM voice_samples
WHERE extracted = 0
ORDER BY timestamp ASC;

-- Voice drift summary by environment
CREATE VIEW IF NOT EXISTS drift_summary AS
SELECT 
    environment,
    metric_name,
    AVG(drift_percentage) as avg_drift,
    MAX(drift_percentage) as max_drift,
    COUNT(*) as measurement_count
FROM voice_drift
WHERE timestamp > datetime('now', '-30 days')
GROUP BY environment, metric_name
ORDER BY environment, ABS(avg_drift) DESC;

-- =====================================================
-- INITIAL DATA - FORBIDDEN PATTERNS
-- =====================================================
-- Seed database with known forbidden patterns

INSERT OR IGNORE INTO forbidden_patterns (pattern, reason, severity, category) VALUES
-- Corporate buzzwords
('spearheaded', 'Corporate buzzword', 'warning', 'buzzword'),
('leveraged', 'Corporate buzzword', 'warning', 'buzzword'),
('synergies', 'Corporate buzzword', 'warning', 'buzzword'),
('passionate about', 'Corporate buzzword', 'warning', 'buzzword'),
('results-driven', 'Corporate buzzword', 'warning', 'buzzword'),
('team player', 'Corporate buzzword', 'warning', 'buzzword'),
('detail-oriented', 'Corporate buzzword', 'warning', 'buzzword'),
('self-starter', 'Corporate buzzword', 'warning', 'buzzword'),
('proven track record', 'Corporate buzzword', 'warning', 'buzzword'),
('think outside the box', 'Corporate buzzword', 'warning', 'buzzword'),
('hit the ground running', 'Corporate buzzword', 'warning', 'buzzword'),
('wear many hats', 'Corporate buzzword', 'warning', 'buzzword'),
('fast-paced environment', 'Corporate buzzword', 'warning', 'buzzword'),
('low hanging fruit', 'Corporate buzzword', 'warning', 'buzzword'),
('move the needle', 'Corporate buzzword', 'warning', 'buzzword'),

-- Memory attribution (Claude-specific)
('based on my memories', 'Memory attribution phrase', 'blocking', 'tone'),
('according to my memories', 'Memory attribution phrase', 'blocking', 'tone'),
('from my memories', 'Memory attribution phrase', 'blocking', 'tone'),
('I remember that', 'Memory attribution in Claude', 'warning', 'tone'),

-- Em-dash overuse (check density separately)
-- Handled by dash_density metric

-- Rhetorical questions (check count)
-- Handled by rhetorical_question metric

-- Third-person self-references
('David''s project', 'Third-person self-reference', 'blocking', 'grammar'),
('his experience', 'Third-person self-reference', 'blocking', 'grammar'),
('David''s work', 'Third-person self-reference', 'blocking', 'grammar');

-- =====================================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- =====================================================

-- Update voice_patterns.updated_at on modification
CREATE TRIGGER IF NOT EXISTS update_pattern_timestamp 
AFTER UPDATE ON voice_patterns
BEGIN
    UPDATE voice_patterns 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;

-- =====================================================
-- SCHEMA VERSION TRACKING
-- =====================================================

CREATE TABLE IF NOT EXISTS schema_version (
    version TEXT PRIMARY KEY,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

INSERT OR IGNORE INTO schema_version (version, description) VALUES 
('1.0.0', 'Initial schema - voice patterns, samples, forbidden patterns, learning insights');

-- =====================================================
-- END SCHEMA
-- =====================================================
