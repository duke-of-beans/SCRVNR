# SAMPLES - Auto-Collected Outputs
Location: D:\Ghost Writer\learning\samples\

## PURPOSE

Automatic collection of ALL Ghost Writer outputs for pattern extraction and learning. Every document generated gets saved here, organized by source environment.

## DIRECTORY STRUCTURE

```
samples/
├── from_dev/           # Technical documentation outputs
├── from_research/      # Academic writing outputs
├── from_career/        # Job application outputs
├── from_work/          # Business communication outputs
└── from_personal/      # Social/family outputs
```

## AUTOMATIC COLLECTION

Every output Ghost Writer generates is automatically saved here:

```python
# After generation
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
context = extract_context(user_query)  # e.g., "cover_letter", "linkedin_post"
filename = f"{timestamp}_{environment}_{context}.md"
save_path = f"learning/samples/from_{environment}/{filename}"
```

## NAMING CONVENTION

**Format:** `YYYYMMDD_HHMMSS_{context}_{first_few_words}.md`

**Examples:**
- `20260122_143055_career_cover_letter_blue_sky.md`
- `20260122_150233_personal_linkedin_post_ai_trends.md`
- `20260122_162148_dev_readme_kernl_bootstrap.md`
- `20260123_091542_work_proposal_thiccles_distribution.md`
- `20260123_104729_research_paper_intro_hirm_consciousness.md`

## PATTERN EXTRACTION

Samples are periodically processed for pattern extraction:

1. **Pattern Extractor** (`learning/scripts/pattern_extractor.py`) runs on new samples
2. Extracts:
   - Contraction patterns
   - Sentence structures
   - Transition phrases
   - Tone markers
   - Voice characteristics
3. Updates `voice.db` with patterns
4. Marks sample as `extracted = 1`

## QUALITY METADATA

Each sample includes quality metadata in voice.db:

```sql
-- From voice_samples table
word_count: int
contraction_rate: float
dash_density: float
quality_score: float  -- From quality_gate.py
context_tags: JSON array  -- ['professional', 'direct', 'analytical']
```

## DEDUPLICATION

Samples are deduplicated by content hash (SHA256):
- If identical content already exists, skip save
- Keeps highest quality version
- Updates frequency count for patterns

## CLEANUP & ARCHIVAL

**Automatic Cleanup:**
- Samples older than 12 months → Archived (compressed)
- Low-quality samples (quality_score < 0.5) → Reviewed for deletion
- Duplicate patterns consolidated

**Manual Review:**
- Monthly: Review samples for manual tagging
- Quarterly: Archive old samples
- Annually: Deep clean and consolidate

## CROSS-ENVIRONMENT LEARNING

Patterns discovered in one environment inform others:

```python
# Example: Pattern from PERSONAL works in WORK
pattern = "Here's what's interesting:"
environments_used = ['personal', 'work']
confidence = 0.85  # High confidence cross-environment
```

## PRIVACY

All samples are LOCAL:
- No cloud storage
- No external APIs
- Complete data control
- Stored only in D:\Ghost Writer\

## CURRENT STATUS

```
Total samples: [query voice.db]
By environment:
  - from_dev: [count]
  - from_research: [count]
  - from_career: [count]
  - from_work: [count]
  - from_personal: [count]
  
Extracted: [count with extracted=1]
Pending extraction: [count with extracted=0]
```

## QUERYING SAMPLES

**Find recent high-quality samples:**
```sql
SELECT * FROM recent_quality_samples LIMIT 10;
```

**Find samples needing extraction:**
```sql
SELECT * FROM unextracted_samples;
```

**Find samples by environment:**
```sql
SELECT * FROM voice_samples 
WHERE environment = 'career' 
ORDER BY timestamp DESC;
```

## INTEGRATION

Samples feed the learning loop:
1. Output generated → Auto-saved here
2. Pattern extractor runs (async)
3. Patterns added to voice.db
4. Future generations use learned patterns
5. Voice quality improves over time
