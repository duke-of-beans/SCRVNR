# GHOST WRITER TOOLS
Python automation tools for Ghost Writer workflow

---

## TOOLS OVERVIEW

### 1. orchestrator.py - Main Workflow Coordinator
**Purpose:** Coordinates complete Ghost Writer workflow from request to delivery

**Commands:**
```bash
# Generate content (prepares environment)
python orchestrator.py generate --env career --context cover_letter

# Generate with variations
python orchestrator.py generate --env personal --context linkedin_post --variations

# Validate file
python orchestrator.py validate output.docx --env career

# Analyze voice
python orchestrator.py analyze output.md --env dev

# Collect sample for learning
python orchestrator.py collect output.md --env personal --context email

# Check system status
python orchestrator.py status
```

**What it does:**
- Loads voice patterns from database
- Loads environment calibration
- Validates generated content
- Analyzes voice authenticity
- Collects samples for learning
- Shows system statistics

---

### 2. environment_detector.py - Auto-Detect Environment
**Purpose:** Automatically detect which environment to use based on context

**Usage:**
```python
from environment_detector import EnvironmentDetector

detector = EnvironmentDetector()
env, confidence = detector.detect("write a cover letter for VP position")
# Returns: ('career', 0.95)

if detector.should_ask_user(confidence):
    # Low confidence, ask user to confirm
    pass
```

**Detection Logic:**
- Scans query for environment keywords
- Considers context hints (file path, previous environment)
- Returns environment + confidence score (0.0-1.0)
- Recommends asking user if confidence < 0.7

---

### 3. quality_gate.py - Automated Validation
**Purpose:** Fast automated validation with line-level feedback

**Usage:**
```bash
# Validate file
python quality_gate.py output.md --env career --mode application

# Returns pass/fail with violations and line numbers
```

**Checks (7 total):**
1. **Contraction rate** - Meets environment minimum
2. **Dash density** - ≤3 per page
3. **Forbidden patterns** - Zero blocking violations
4. **Rhetorical questions** - Max 1 (opening hook only)
5. **Expert audience** - No condescension
6. **Third-person refs** - Use first-person only
7. **Weak verbs** - Warning only (career mode)

**Output:**
- Overall pass/fail
- Score (percentage of checks passed)
- Violations with line numbers and excerpts
- Suggestions for fixes

---

## WORKFLOW INTEGRATION

### Complete Generation Flow

```bash
# Step 1: Generate (happens in Claude conversation)
python orchestrator.py generate --env career --context cover_letter

# Step 2: Validate the output
python orchestrator.py validate cover_letter.docx --env career

# Step 3: If validation passes, collect for learning
python orchestrator.py collect cover_letter.docx --env career --context cover_letter

# Step 4: Extract patterns (async)
python ../learning/scripts/pattern_extractor.py
```

### Quick Validation

```bash
# Fast check with quality gate
python quality_gate.py document.md --env personal

# Detailed analysis
python orchestrator.py analyze document.md --env personal
```

---

## DEPENDENCIES

All tools depend on:
- `learning/scripts/db_manager.py` - Database interface
- `learning/scripts/sample_collector.py` - Sample collection
- `learning/voice.db` - Pattern database

**Install requirements:**
```bash
pip install --break-system-packages
```

---

## INTEGRATION WITH CLAUDE

These tools provide infrastructure for Ghost Writer but don't replace Claude's generation. Here's the flow:

### In Claude Conversation:

1. **User requests:** "Write a cover letter for this role"

2. **Claude calls:** `orchestrator.py generate --env career --context cover_letter`
   - Loads patterns from voice.db
   - Loads environment calibration
   - Displays ready state

3. **Claude generates content** using:
   - Loaded voice patterns
   - Environment settings
   - MASTER_PROTOCOL.md workflow
   - Application-workflow.md (if career)

4. **Claude validates** using `quality_gate.py` or `orchestrator.py validate`
   - Checks all quality gates
   - Shows pass/fail with line numbers

5. **If pass, Claude collects** using `orchestrator.py collect`
   - Saves to learning/samples/
   - Adds to voice.db
   - Queues for pattern extraction

6. **Background:** `pattern_extractor.py` runs (async)
   - Extracts new patterns
   - Updates voice.db
   - Improves future generations

---

## TOOL PERFORMANCE

**Target speeds:**
- environment_detector: <100ms
- quality_gate: <1s for 500 words
- orchestrator validate: <2s for 500 words
- orchestrator analyze: <3s for 500 words
- orchestrator collect: <1s

**Database operations:**
- Pattern query: <100ms
- Forbidden query: <50ms
- Sample insertion: <50ms

---

## TESTING

Each tool includes a `__main__` block for testing:

```bash
# Test environment detector
python environment_detector.py

# Test quality gate on sample file
python quality_gate.py ../outputs/sample.md --env personal

# Test orchestrator status
python orchestrator.py status
```

---

## FUTURE ENHANCEMENTS

### Post-Oktyv Integration

When Oktyv is built, these tools will integrate:

```python
# Example: Fetch LinkedIn posts for learning
orchestrator.collect_from_source(
    source="oktyv://linkedin/posts?last=20",
    environment="personal",
    context="linkedin_post"
)

# Oktyv fetches posts → Tools collect → Patterns extracted → Voice improves
```

### Planned Tool Additions

1. **variation_generator.py** - Generate Direct/Analytical/Balanced versions
2. **intensity_calibrator.py** - Adjust directness on 1-10 scale
3. **voice_drift_monitor.py** - Track voice evolution over time
4. **pattern_consolidator.py** - Merge similar patterns

---

## TROUBLESHOOTING

**"Module not found" errors:**
```bash
# Make sure you're in the tools directory
cd "D:\Ghost Writer\tools"

# Or use absolute imports
python -c "import sys; sys.path.append('..');  from learning.scripts import db_manager"
```

**"Database not found" errors:**
```bash
# Initialize database
python ../learning/scripts/init_database.py
```

**"File not found" errors:**
- Always use absolute paths for reliability
- Or run from Ghost Writer root directory

---

## INTEGRATION WITH BOOTSTRAP

Ghost Writer integrates with your global bootstrap (v6.2.0):

**Auto-detection triggers:**
- "write a [cover letter|email|post]"
- "draft [type]"
- "help me write"

**Never auto-load:**
- Technical questions
- Code debugging
- Analysis requests

**Manual override:**
- "use ghost writer" - Force load
- "skip ghost writer" - Don't load

---

## STATUS

✅ **orchestrator.py** - Complete, tested
✅ **environment_detector.py** - Complete, tested
✅ **quality_gate.py** - Complete, tested

**Ready for production use!**

---

For questions or issues, see: `../core/protocols/MASTER_PROTOCOL.md`
