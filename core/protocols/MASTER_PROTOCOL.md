# GHOST WRITER MASTER PROTOCOL
Version: 1.0.0  
Last Updated: 2026-01-22  
Purpose: Top-level workflow coordinator for voice synthesis system

---

## SYSTEM OVERVIEW

Ghost Writer is a voice synthesis system that captures and reproduces David Kirsch's authentic voice across all communication contexts. This master protocol orchestrates the complete workflow from request to delivery.

---

## PROTOCOL HIERARCHY

```
MASTER_PROTOCOL.md (this file)
    ↓
├── voice-calibration-matrix.md      # Voice modes and scoring
├── application-workflow.md          # 3-gate application process
├── validation-framework.md          # Quality control system
├── forbidden-patterns.md            # Pattern violations
├── factual-corrections.md           # Known error database
├── context-modulation-guide.md      # Situational adjustments
└── technical-communication-guide.md # Technical writing specifics
```

Each protocol handles a specific domain. This master protocol orchestrates their execution.

---

## WORKFLOW EXECUTION

### PHASE 1: REQUEST INTAKE & ENVIRONMENT DETECTION

```yaml
1. Receive user request
2. Detect environment (or ask):
   - "write cover letter" → career
   - "draft README" → dev
   - "write LinkedIn post" → personal
   - "create proposal" → work
   - "write paper" → research
3. Load environment calibration:
   - Read environments/{env}/calibration.yaml
4. Query voice database:
   - Get high-confidence patterns for {env}
   - Load forbidden patterns
5. Display to user:
   "🎭 GHOST WRITER - {environment} mode
    Voice DB: {pattern_count} patterns loaded
    Ready to generate"
```

**Decision Point:** If environment unclear, ASK user. Never guess.

---

### PHASE 2: PROTOCOL SELECTION

```yaml
IF request_type = "job application":
    PRIMARY: application-workflow.md (3-gate process)
    SUPPORTING:
      - voice-calibration-matrix.md (APPLICATION mode)
      - validation-framework.md (comprehensive)
      - forbidden-patterns.md (all categories)
      - factual-corrections.md (verify all facts)
    
ELIF request_type = "technical documentation":
    PRIMARY: technical-communication-guide.md
    SUPPORTING:
      - voice-calibration-matrix.md (PROFESSIONAL mode)
      - validation-framework.md (professional voice)
      - forbidden-patterns.md (categories 1-3, 5-6, 8, 10)
    
ELIF request_type = "analytical writing":
    PRIMARY: voice-calibration-matrix.md (ANALYTICAL mode)
    SUPPORTING:
      - validation-framework.md (analytical voice)
      - forbidden-patterns.md (categories 1, 2, 5-6, 8, 11)
      - context-modulation-guide.md (if crisis/disagreement)
    
ELIF request_type = "casual communication":
    PRIMARY: voice-calibration-matrix.md (CASUAL mode)
    SUPPORTING:
      - validation-framework.md (casual voice - lightweight)
      - forbidden-patterns.md (categories 1, 3, 6)
    
ELSE:
    PRIMARY: voice-calibration-matrix.md (PROFESSIONAL mode)
    SUPPORTING:
      - validation-framework.md (professional voice)
      - forbidden-patterns.md (categories 1, 3, 5-6, 8, 10)
```

---

### PHASE 3: GENERATION

#### Step 1: Load Voice Patterns

```python
# Query voice database for environment-specific patterns
patterns = db.get_patterns(
    environment=environment,
    min_confidence=0.7,
    limit=20
)

# Load forbidden patterns
forbidden = db.get_forbidden_patterns(
    environment=environment,
    severity=['blocking', 'warning']
)
```

#### Step 2: Generate Content

**For Application Materials (Special 3-Gate Process):**

```yaml
GATE 1: LOAD AND VERIFY MASTERS
  - Read professional history master
  - Read achievements database
  - Load factual corrections
  - Verify Phase 3 story correct version
  - HALT if any master file missing/incorrect

GATE 2: ANALYZE AND CREATE
  - Classify role tier (Entry → C-Suite)
  - Map responsibilities to experience
  - Create documents (resume, cover letter, supplements)
  - Use iterative editing for large files
  - Ensure zero redundancy across documents

GATE 3: PRE-DELIVERY VALIDATION
  - Run comprehensive validation (10 checks)
  - Calculate composite score
  - MUST achieve ≥90% AND factual=100%
  - Fix issues and re-validate if fail
  - Only deliver when GATE 3 passes
```

**For All Other Content:**

```yaml
1. Generate first draft:
   - Apply environment calibration settings
   - Use loaded voice patterns
   - Avoid forbidden patterns
   - Target appropriate contraction rate
   - Maintain voice authenticity

2. Calculate voice confidence:
   - Run voice-confidence-scorer
   - Generate 0.0-1.0 score with breakdown
   - Note any concerns

3. IF confidence < 0.75 OR complex request:
   - Generate variations (Direct, Analytical, Balanced)
   - Present 2-3 options to user
   - Let user select or hybridize

4. User feedback loop:
   - Incorporate user edits
   - Iterate as needed
   - Maintain quality throughout
```

#### Step 3: Apply Context Modulation (If Needed)

```yaml
IF situation = "crisis communication":
    LOAD context-modulation-guide.md
    ADJUST tone for urgency
    MAINTAIN factual accuracy
    AVOID panic language

IF situation = "disagreement/confrontation":
    LOAD context-modulation-guide.md
    USE intensity calibrator (1-10 scale)
    BALANCE directness with diplomacy
    END with facts, not emotion

IF situation = "normal":
    SKIP context modulation
    USE standard environment settings
```

---

### PHASE 4: VALIDATION

#### Universal Validation (All Outputs)

```yaml
MANDATORY CHECKS:
1. Punctuation compliance:
   - Zero em-dashes (—)
   - Zero en-dashes (–)
   - Hyphens only (-)

2. Forbidden pattern scan:
   - Corporate buzzwords: 0
   - Memory attribution: 0
   - Rhetorical questions: 0 (except CASUAL mode)
   - Promotional language: 0 (APPLICATION mode)

3. Contraction density:
   - CASUAL: ≥95%
   - PROFESSIONAL: ≥85%
   - ANALYTICAL: ≥70%
   - APPLICATION: ≥60%

4. Voice authenticity:
   - Calculate score (voice-calibration-matrix.md)
   - TARGET: ≥90 points
   - Fix if below threshold
```

#### Application-Specific Validation

```yaml
IF output_type = APPLICATION:
    RUN comprehensive_application_validation:
      - Factual accuracy: MUST be 100%
      - Voice authenticity: ≥90%
      - Length compliance: MUST pass
      - Redundancy analysis: 100%
      - Tone calibration: ≥85%
      - Formatting quality: ≥95%
      - (See validation-framework.md for full checklist)
    
    COMPOSITE SCORE = weighted average
    PASS REQUIREMENT: ≥90% AND factual=100%
    
    IF FAIL:
        IDENTIFY issues
        CORRECT problems
        RE-VALIDATE completely
        DO NOT DELIVER until PASS
```

---

### PHASE 5: AUTO-SAMPLING & LEARNING

```python
# MANDATORY: Auto-save every output for learning

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
context = extract_context_type(request)  # e.g., "cover_letter"
filename = f"{timestamp}_{environment}_{context}.md"
save_path = f"learning/samples/from_{environment}/{filename}"

# Save to filesystem
save_output(content, save_path)

# Add to database
sample_id = db.add_sample(
    content=content,
    environment=environment,
    context_type=context,
    file_path=save_path,
    word_count=len(content.split()),
    contraction_rate=calculate_contraction_rate(content),
    dash_density=calculate_dash_density(content),
    quality_score=validation_score,
    context_tags=extract_tags(content)
)

# Queue for pattern extraction (async)
queue_pattern_extraction(sample_id)
```

**Pattern Extraction (Happens Asynchronously):**

```python
# pattern_extractor.py processes samples
# Extracts:
# - Contractions used
# - Transition phrases
# - Sentence structures  
# - Imperative patterns

# Updates voice.db:
# - Adds new patterns
# - Increases frequency for existing patterns
# - Adjusts confidence scores
# - Marks sample as extracted

# Result: Voice improves over time automatically
```

---

### PHASE 6: CHECKPOINTING

```yaml
EVERY 5-10 TOOL CALLS:
  Checkpoint current state:
    - operation: "Current task description"
    - progress: 0.0-1.0
    - current_step: "Exact current action"
    - decisions: ["Key decisions made"]
    - next_steps: ["What comes next"]
    - active_files: ["Files being worked on"]
  
  Enable crash recovery:
    - If session crashes, resume from checkpoint
    - No work lost
    - Seamless continuation
```

---

### PHASE 7: DELIVERY

```yaml
1. Final validation passed ✅
2. Auto-sampling complete ✅
3. Checkpoint saved ✅

4. Move files to outputs:
   - Copy to /mnt/user-data/outputs/
   - OR D:\Ghost Writer\outputs\ (if local)

5. Present to user:
   - Use present_files tool
   - Provide succinct summary
   - DO NOT over-explain
   - Trust user to evaluate

6. Session log (if major work):
   - Create learning/session_logs/SESSION_{timestamp}.md
   - Document what was generated
   - Record patterns discovered
   - Note user feedback
   - Track quality metrics
```

---

## CROSS-ENVIRONMENT CONSISTENCY

### Universal Requirements (All Modes)

```yaml
ALWAYS:
  - Use hyphens (-), never em-dashes or en-dashes
  - Avoid corporate buzzwords
  - No memory attribution phrases
  - Maintain appropriate contraction rate
  - Checkpoint every 5-10 tool calls
  - Auto-save outputs for learning
  - Validate before delivery

NEVER:
  - Fabricate information
  - Use prohibited patterns
  - Skip validation
  - Deliver without quality check
  - Forget to auto-sample
```

### Environment-Specific Adjustments

```yaml
DEV:
  formality: 6/10
  contractions: 65%
  technical_depth: high
  code_examples: required_when_relevant

RESEARCH:
  formality: 8/10
  contractions: 50%
  evidence_based: mandatory
  multi_theory: required
  falsifiable: required

CAREER:
  formality: 7/10
  contractions: 75%
  achievement_focused: mandatory
  metrics: required
  zero_promotion: critical

WORK:
  formality: 7/10
  contractions: 75%
  results_focused: mandatory
  strategic_framing: required

PERSONAL:
  formality: 4/10
  contractions: 85%
  maximum_authenticity: true
  warmth: high
```

---

## ERROR RECOVERY

### If Factual Error Discovered

```yaml
1. HALT delivery immediately
2. ACKNOWLEDGE error to user
3. IDENTIFY error source
4. UPDATE factual-corrections.md
5. CREATE corrected version
6. RE-RUN complete validation
7. DELIVER corrected materials
8. DOCUMENT lesson learned
```

### If Voice Authenticity Compromised

```yaml
1. IDENTIFY specific violations
2. REFERENCE voice-calibration-matrix.md
3. REWRITE affected sections
4. RE-VALIDATE voice scoring
5. ENSURE ≥90 authenticity score
6. DELIVER corrected version
```

### If Session Crashes

```yaml
1. CHECK for checkpoint state
2. LOAD last checkpoint
3. RESUME from exact point
4. CONTINUE workflow
5. NO work lost
```

---

## TOOL INTEGRATION

### Voice Confidence Scorer

```python
# Calculate authenticity score
score = voice_confidence_scorer.score(
    text=content,
    environment=environment,
    reference_patterns=patterns
)

# Returns:
# {
#   overall_confidence: 0.85,
#   breakdown: {
#     formality: {score: 7, target: 7, delta: 0},
#     directness: {score: 6, target: 8, delta: -2},
#     contraction_rate: {measured: 0.72, target: 0.75},
#     authenticity_markers: {present: 4, missing: 3}
#   },
#   concerns: ["Directness could be stronger", ...],
#   confidence_level: "high"
# }
```

### Variation Generator

```python
# Generate alternative versions
IF base_confidence < 0.75 OR complex_request:
    
    variations = variation_generator.generate(
        text=content,
        environment=environment,
        variation_count=3
    )
    
    # Returns 3 versions:
    # - Version A: Direct (+directness, -explanation)
    # - Version B: Analytical (+depth, +context)
    # - Version C: Balanced (optimal mix)
    
    present_variations_to_user()
    user_selects_or_hybridizes()
```

### Intensity Calibrator

```python
# Adjust directness/confrontation level
IF context_requires_intensity_adjustment:
    
    calibrated = intensity_calibrator.calibrate(
        text=content,
        environment=environment,
        target_intensity=7  # 1-10 scale
    )
    
    # 1-3: Maximum diplomacy
    # 4-6: Professional peer
    # 7-9: Direct, no sugar-coating
    # 10: Confrontational (rare)
```

### Automated Checker

```python
# Fast validation before delivery
result = automated_checker.validate(
    text=content,
    environment=environment
)

# Runs 7 checks:
# - Contraction rate
# - Dash density
# - Forbidden patterns
# - Rhetorical questions
# - Expert audience
# - Third-person refs
# - Weak verbs (career only)

# Returns pass/fail with line numbers for fixes
```

---

## QUALITY GATES

### Gate System (Application Materials)

```
USER REQUEST
    ↓
GATE 1: Load & Verify Masters
    ├─ PASS → Continue
    └─ FAIL → Halt, request clarification
        ↓
GATE 2: Analyze & Create
    ├─ Classify role tier
    ├─ Map responsibilities
    ├─ Create documents
    └─ Complete packet
        ↓
GATE 3: Comprehensive Validation
    ├─ Run all checks
    ├─ Calculate composite score
    ├─ PASS (≥90, factual=100) → DELIVER
    └─ FAIL → Fix and re-validate
        ↓
DELIVERY
    ├─ Copy to outputs
    ├─ Auto-sample for learning
    └─ Present to user
```

### Quality Thresholds

```yaml
APPLICATION MATERIALS:
  composite_score: ≥90%
  factual_accuracy: 100% (non-negotiable)
  voice_authenticity: ≥90%
  
ALL OTHER CONTENT:
  voice_authenticity: ≥90%
  forbidden_patterns: 0
  punctuation_compliance: 100%
  contraction_density: meets threshold
```

---

## SESSION MANAGEMENT

### Session Lifecycle

```yaml
1. SESSION START:
   - Detect environment
   - Load protocols
   - Query voice database
   - Create session in session_log table

2. DURING SESSION:
   - Generate content
   - Validate quality
   - Iterate with user
   - Checkpoint every 5-10 calls
   - Auto-save outputs

3. SESSION END:
   - Final validation
   - Move to outputs
   - Auto-sample all outputs
   - Queue pattern extraction
   - Update session_log
   - Create session summary (if major work)
   - Mark complete
```

### Session Logging

```yaml
CREATE session_logs/SESSION_{timestamp}.md:
  - Generated outputs
  - Voice confidence scores
  - User feedback
  - Patterns discovered
  - Quality metrics
  - Issues encountered
  - Improvements identified
  - Learning insights
  - Next session priorities
```

---

## LEARNING LOOP

### Continuous Improvement Cycle

```
OUTPUT GENERATED
    ↓
AUTO-SAVE to samples/from_{env}/
    ↓
ADD to voice.db (samples table)
    ↓
QUEUE for pattern extraction
    ↓
PATTERN EXTRACTOR runs (async)
    ↓
UPDATE voice.db (patterns table)
    ↓
PATTERNS AVAILABLE for next generation
    ↓
VOICE IMPROVES over time
    ↓
[CYCLE REPEATS]
```

### Pattern Confidence Evolution

```yaml
NEW PATTERN:
  confidence: 0.5
  frequency: 1

PATTERN SEEN AGAIN:
  confidence: 0.6 (+0.1)
  frequency: 2

PATTERN CONFIRMED REPEATEDLY:
  confidence: 0.8
  frequency: 5+
  
HIGH CONFIDENCE PATTERN:
  confidence: 0.9
  frequency: 10+
  Used in future generations
```

---

## SPECIAL CASES

### Insufficient Information

```yaml
IF job_description_incomplete:
  - Request clarification
  - Specify what's needed
  - Wait for response
  - DO NOT proceed without info

IF master_files_missing_data:
  - Notify user
  - Request updated masters
  - Halt workflow
  - Maintain data integrity
```

### Role Requirements Exceed Experience

```yaml
IF requirements > experience:
  - Assess transferable skills
  - Make honest connections
  - NEVER fabricate
  - Acknowledge gaps if necessary
  - Present strongest relevant experience
  - Show learning capacity
  - Maintain integrity
```

### Multiple Positions Simultaneously

```yaml
IF applying_to_multiple_roles:
  - Create separate packets
  - Tailor each specifically
  - Maintain version control
  - Track applications
  - Ensure no confusion
```

---

## INTEGRATION WITH OTHER SYSTEMS

### With DEV Environment

```yaml
KERNL integration:
  - Tool priority: KERNL > Desktop Commander > Filesystem
  - Session management from SHIM
  - Aggressive checkpointing (every 5-10 calls)
  - Authority protocol enforcement
```

### With RESEARCH Environment

```yaml
Crash prevention:
  - BUILD_STATUS.md updates every 3 calls
  - ASCII-only in system files
  - 500-line read max, 200-line write max
  - Long session protocols
```

### With CAREER System

```yaml
Application Intelligence:
  - Source: D:\Application Intelligence System\Applications
  - Live examples from actual applications
  - Locked metrics validation
  - Similar application search
  - Quality gate orchestrator
```

### Future: Oktyv Integration

```yaml
PENDING (after Oktyv built):
  Ghost Writer → Oktyv → [Gmail, LinkedIn, Drive]
  
  Capabilities:
    - "Show me my last 20 LinkedIn posts"
    - "Find emails about [topic]"
    - "Access my Google Drive docs"
  
  Ghost Writer becomes Oktyv client:
    - No custom scrapers
    - One automation layer
    - Infinite reach
```

---

## PERFORMANCE TARGETS

### Tool Performance

```yaml
voice_confidence_scorer: <2s for 500 words
variation_generator: <5s for 3 versions
intensity_calibrator: <1s for 500 words
automated_checker: <1s for 500 words
```

### Database Performance

```yaml
pattern_query: <100ms
forbidden_query: <100ms
sample_insertion: <50ms
pattern_extraction: <5s per sample
```

### Overall Workflow

```yaml
simple_response: <10s end-to-end
complex_document: <60s first draft
application_packet: <180s complete (3 gates)
```

---

## VERSION CONTROL

```yaml
Version: 1.0.0
Created: 2026-01-22
Last Updated: 2026-01-22

Protocol Files:
  - voice-calibration-matrix.md (v1.0)
  - application-workflow.md (v1.0)
  - validation-framework.md (v1.0)
  - forbidden-patterns.md (v1.0)
  - factual-corrections.md (v1.0)
  - context-modulation-guide.md (v1.0)
  - technical-communication-guide.md (v1.0)

Environment Calibrations:
  - dev/calibration.yaml (v1.0)
  - research/calibration.yaml (v1.0)
  - career/calibration.yaml (v1.0)
  - work/calibration.yaml (v1.0)
  - personal/calibration.yaml (v1.0)

Database Schema:
  - voice.db schema (v1.0.0)
```

---

## EMERGENCY PROTOCOLS

### If Everything Fails

```yaml
FALLBACK TO BASICS:
1. Load voice-calibration-matrix.md only
2. Use appropriate mode for context
3. Apply forbidden patterns scan
4. Validate contractions and punctuation
5. Deliver with disclaimer
6. Document what went wrong
7. Fix for next session
```

### If Database Unavailable

```yaml
OPERATE WITHOUT voice.db:
1. Use static protocol files only
2. Reference core/reference/examples/
3. Apply manual pattern matching
4. Validate against forbidden patterns
5. Deliver with note about limited learning
6. Reconnect database ASAP
```

---

**END MASTER_PROTOCOL**

## QUICK START GUIDE

For any Ghost Writer request:

1. **Detect environment** (or ask)
2. **Load this file** + environment calibration
3. **Query voice.db** for patterns
4. **Generate** using appropriate protocols
5. **Validate** thoroughly
6. **Auto-sample** for learning
7. **Checkpoint** every 5-10 calls
8. **Deliver** when quality assured

Trust the system. Follow the protocols. Maintain quality.
