# LEARNING - Self-Improvement System
Location: D:\Ghost Writer\learning\

## PURPOSE

Autonomous self-improvement through continuous sampling, pattern extraction, and database updates. Ghost Writer learns from every output it generates.

## KEY COMPONENTS

### voice.db
SQLite database containing extracted voice patterns. This is the MACHINE-READABLE voice knowledge.

**Schema:** See `scripts/db_manager.py` for complete schema
**Size:** Starts empty, grows with samples
**Queried by:** Claude during generation for pattern guidance

### samples/
Auto-collected outputs organized by source environment.

**Structure:**
```
samples/
├── from_dev/           # Technical docs generated in DEV
├── from_research/      # Academic writing from RESEARCH  
├── from_career/        # Applications from CAREER
├── from_work/          # Business comms from WORK
└── from_personal/      # Social posts, emails, etc.
```

**Naming Convention:** `YYYYMMDD_HHMMSS_{context}_{first_few_words}.md`

**Automatic Collection:** Every output Ghost Writer generates gets copied here

### session_logs/
Cross-session learning insights and improvement tracking.

**Files:**
- `SESSION_YYYYMMDD_HHMMSS.md` - What was learned this session
- `patterns_discovered.md` - New patterns found over time
- `voice_drift_log.md` - Tracks evolution of voice over time
- `quality_improvements.md` - Measurable quality increases

### scripts/
Database management and pattern extraction automation.

**Python Scripts:**
- `db_manager.py` - CRUD operations on voice.db
- `pattern_extractor.py` - Extract patterns from samples
- `db_cleaner.py` - Prune low-value patterns
- `confidence_updater.py` - Recalculate pattern confidence scores
- `sample_collector.py` - Auto-save outputs to samples/

## LEARNING WORKFLOW

```
1. OUTPUT GENERATED
   Ghost Writer creates document in {environment}
   
2. AUTO-SAVE
   Copy to samples/from_{environment}/TIMESTAMP_context.md
   
3. PATTERN EXTRACTION (async)
   scripts/pattern_extractor.py analyzes new sample
   
4. DATABASE UPDATE
   Patterns added/updated in voice.db
   Confidence scores adjusted based on frequency
   
5. SESSION LOG
   Insights recorded in session_logs/SESSION_*.md
   
6. PERIODIC CLEANING
   scripts/db_cleaner.py removes low-value patterns
   Consolidates similar patterns
   Archives old samples
```

## VOICE DATABASE SCHEMA

```sql
-- Core pattern storage
voice_patterns (
  id, pattern_type, pattern_text, environment,
  confidence, frequency, last_seen, source_samples, context
)

-- Complete samples for reference  
voice_samples (
  id, content_hash, content, environment, context_type,
  timestamp, word_count, contraction_rate, dash_density,
  quality_score, context_tags, extracted
)

-- Patterns to avoid
forbidden_patterns (
  id, pattern, reason, severity, category
)

-- Learning insights over time
learning_insights (
  id, insight_type, description, evidence,
  confidence, timestamp, applied
)
```

## SELF-CLEANING MECHANISMS

**Deduplication:**
- Use content_hash (SHA256) to detect duplicate samples
- Keep highest quality version

**Pruning:**
- Remove patterns with confidence < 0.3 not seen in 6 months
- Archive samples older than 12 months

**Consolidation:**
- Merge similar patterns using fuzzy matching
- Update confidence scores based on usage

**Run Frequency:** Every 10 samples OR weekly

## QUERYING THE DATABASE

**During Generation:**
```python
# Get high-confidence patterns for environment
patterns = db.query("""
  SELECT pattern_text, context
  FROM voice_patterns
  WHERE environment = ? AND confidence > 0.7
  ORDER BY confidence DESC
  LIMIT 20
""", (environment,))
```

**For Voice Analysis:**
```python
# Compare new output against database
score = voice_analyzer.calculate_authenticity(
  new_text, 
  reference_patterns=db.get_patterns(environment)
)
```

## CROSS-SESSION LEARNING

Session logs accumulate insights:
- "LinkedIn posts need more punch than email"
- "Cover letters work better with specific examples"
- "Technical docs benefit from code snippets"

These insights inform:
1. Protocol updates (core/protocols/)
2. Environment calibrations (environments/{env}/)
3. Tool specifications (core/tools/)

## PRIVACY & SECURITY

All samples are LOCAL. Nothing leaves D:\Ghost Writer\.
- No cloud storage
- No external APIs
- Complete data control

## MAINTENANCE

**Weekly:**
- Run `db_cleaner.py` for routine maintenance
- Review `session_logs/` for patterns to document

**Monthly:**
- Analyze voice drift trends
- Update environment calibrations if needed
- Archive old samples to compressed storage

**Quarterly:**
- Full database optimization
- Review and consolidate learning insights
- Update core protocols with proven patterns
