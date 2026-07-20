# SESSION LOGS - Cross-Session Learning
Location: D:\Ghost Writer\learning\session_logs\

## PURPOSE

Track what happens in each Ghost Writer session to enable cross-session learning and continuous improvement.

## LOG TYPES

### 1. Session Summary Logs
**Format:** `SESSION_YYYYMMDD_HHMMSS.md`

Created at end of each session. Documents:
- What was generated
- Environment used
- Voice confidence scores
- User feedback
- Corrections made
- Patterns discovered
- Issues encountered

### 2. Error Logs
**Format:** `errors.log` (append-only)

Continuous log of:
- Tool failures
- Database errors
- Pattern extraction issues
- Validation failures

### 3. Learning Insights
**Format:** `learning_insights.md` (updated continuously)

Accumulated insights:
- "LinkedIn posts need more punch than email"
- "Cover letters work better with specific examples"
- "Technical docs benefit from code snippets"

### 4. Voice Drift Tracking
**Format:** `voice_drift_YYYY_MM.md` (monthly)

Tracks evolution:
- Contraction rate changes
- Formality shifts
- Pattern frequency changes
- Quality score trends

## SESSION SUMMARY TEMPLATE

```markdown
# SESSION SUMMARY - [DATE] [TIME]
Session ID: [UUID]
Environment: [dev|research|career|work|personal]
Duration: [X minutes]

## GENERATED OUTPUTS
1. [Filename] - [Context]
   - Word count: [X]
   - Quality score: [0-1.0]
   - Confidence: [0-1.0]
   - User feedback: [accepted/revised/rejected]

## VOICE CONFIDENCE
Average: [0-1.0]
Breakdown:
- Formality: [X/10]
- Directness: [X/10]
- Contractions: [X%]
- Authenticity markers: [X/Y]

## USER FEEDBACK
- [Positive feedback]
- [Requested changes]
- [Corrections provided]

## PATTERNS DISCOVERED
- [New pattern 1]
- [New pattern 2]

## ISSUES ENCOUNTERED
- [Issue 1]
- [Resolution]

## QUALITY METRICS
- Outputs generated: [X]
- Validation pass rate: [X%]
- Average quality score: [0-1.0]

## IMPROVEMENTS IDENTIFIED
- [Suggested protocol update]
- [Tool enhancement needed]
- [Pattern to add/remove]

## NEXT SESSION PRIORITIES
- [Carry-over work]
- [Follow-up needed]
```

## CREATING SESSION LOGS

**Automatic:**
Session log created automatically at session end via `orchestrator.py`

**Manual:**
User or Claude can trigger: "Create session log for this work"

## LEARNING FROM LOGS

Session logs feed into:
1. **learning_insights table** in voice.db
2. **Protocol updates** (core/protocols/)
3. **Environment calibration adjustments**
4. **Tool specifications refinements**

## CURRENT SESSION TRACKING

Track in voice.db `session_log` table:
```sql
INSERT INTO session_log (
    session_id, environment, start_time, 
    samples_generated, notes, status
) VALUES (?, ?, ?, ?, ?, 'active');
```

Update at checkpoints:
```sql
UPDATE session_log 
SET samples_generated = ?, 
    quality_avg = ?,
    end_time = CURRENT_TIMESTAMP,
    status = 'complete'
WHERE session_id = ?;
```

## LOG RETENTION

**Keep:**
- All session summaries (compressed after 1 year)
- Last 6 months of detailed logs
- Error logs (last 3 months)
- Learning insights (permanent)

**Archive:**
- Session logs older than 1 year → Compressed
- Error logs older than 3 months → Archived

## QUERYING LOGS

**Recent sessions:**
```sql
SELECT * FROM session_log 
ORDER BY start_time DESC 
LIMIT 10;
```

**Session statistics:**
```sql
SELECT 
    environment,
    COUNT(*) as session_count,
    AVG(samples_generated) as avg_samples,
    AVG(quality_avg) as avg_quality
FROM session_log
GROUP BY environment;
```

## INTEGRATION

Session logs inform:
- Voice confidence scorer improvements
- Variation generator enhancements
- Environment calibration adjustments
- Tool specification updates
- Protocol refinements
