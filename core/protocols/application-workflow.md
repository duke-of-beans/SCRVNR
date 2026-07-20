# APPLICATION_WORKFLOW_v1.0

## SYSTEM_ARCHITECTURE

### 3_GATE_MANDATORY_SEQUENCE:
```
GATE_1: LOAD_AND_VERIFY_MASTERS
    â†“
GATE_2: ROLE_ANALYSIS_AND_DOCUMENT_CREATION
    â†“
GATE_3: PRE_DELIVERY_VALIDATION
    â†“
DELIVERY (only if all gates pass)
```

**CRITICAL:** NEVER skip any gate. NEVER deliver without Gate 3 validation passing.

---

## GATE_1: LOAD_AND_VERIFY_MASTERS

### EXECUTION_SEQUENCE:
```
STEP_1: CHECK_MASTER_FILES_PRESENT
    project_knowledge_search "professional history master"
    project_knowledge_search "achievements database"
    project_knowledge_search "education"
    project_knowledge_search "employment dates"
    project_knowledge_search "phase 3 cultivation"

STEP_2: VERIFY_VERSIONS_CURRENT
    CONFIRM last_updated dates recent
    VERIFY professional_history_master_v5_1.md exists
    VERIFY achievements_database_v5_1.md exists

STEP_3: LOAD_FACTUAL_CORRECTIONS
    READ factual_corrections.md
    LOAD into active_memory for cross-reference

STEP_4: VERIFY_PHASE_3_STORY
    CONFIRM correct_version loaded:
    "Untested integrated systems, keeping Phase 2 alive as insurance"
    NOT "extraction lab bottleneck"
```

### GATE_1_VALIDATION_CHECKLIST:
```
â–¡ All 5 master files accessible
â–¡ Versions confirmed (v5_1 or latest)
â–¡ Last updated dates verified
â–¡ Phase 3 story correct version confirmed
â–¡ Factual corrections database loaded
â–¡ Education verified (Pierce + Oaksterdam)
â–¡ GreenRush dates verified (Aug 2018 - Mar 2019)
â–¡ Good Day Farm growth verified (4x NOT 5x)

IF any_checkbox_fails:
    HALT_WORKFLOW
    NOTIFY_USER "Missing or incorrect master file data"
    REQUEST_CLARIFICATION
```

### CRITICAL_FACTS_VERIFICATION:
```
EMPLOYMENT_DATES:
- Good Day Farm: March 2020 - May 2023
- GreenRush: August 2018 - March 2019 (NOT 2014-2015)
- de Krown Consulting: March 2014 - November 2018
- Farmacy Berkeley: 2011 - 2014

EDUCATION:
- Pierce College (NOT Ventura College)
- Oaksterdam University

KEY_METRICS:
- Good Day Farm growth: 4x (NOT 5x)
- Client count: 30-40 concurrent (NOT 80% of brands)
- de Krown role: "instrumental in building" (NOT "built")

PHASE_3_NARRATIVE:
CORRECT: "Untested integrated systems, kept Phase 2 alive as insurance"
WRONG: "Extraction lab created bottleneck"
```

---

## GATE_2: ROLE_ANALYSIS_AND_DOCUMENT_CREATION

### STEP_1: ANALYZE_ROLE_TIER

```
CLASSIFY_POSITION â†’ [ENTRY | MID | SENIOR_LEAD | EXECUTIVE | C_SUITE]

ENTRY (0-3 years experience expected):
- Focus: foundational skills, learning capacity
- Tone: eager but not desperate
- Detail_level: moderate

MID (3-7 years experience expected):
- Focus: proven execution, specific achievements
- Tone: confident, results-oriented
- Detail_level: high specificity

SENIOR_LEAD (7-12 years experience expected):
- Focus: system design, team leadership, strategic impact
- Tone: peer-level, strategic thinking
- Detail_level: very high, include methodology

EXECUTIVE (12+ years, leadership role):
- Focus: organizational impact, vision execution, P&L
- Tone: executive peer, strategic vision
- Detail_level: business outcomes, team scale

C_SUITE (C-level positions):
- Focus: company direction, market positioning, stakeholder value
- Tone: peer executive, industry perspective
- Detail_level: strategic, market-level impact
```

### STEP_2: MAP_RESPONSIBILITIES_TO_EXPERIENCE

```
FOR_EACH required_responsibility IN job_description:
    SEARCH achievements_database FOR matching_experience
    VERIFY against professional_history_master
    SELECT most_relevant_examples
    ENSURE no_fabrication
    
IF no_direct_match_found:
    IDENTIFY transferable_experience
    MAKE explicit_connection
    NEVER claim_experience_not_held
```

### STEP_3: DETERMINE_DOCUMENT_TYPES

```
STANDARD_PACKET:
- Resume (tailored to role)
- Cover Letter
- [Optional] Supplemental documents

DECISION_LOGIC:
IF role_requires_specific_expertise:
    ADD supplement_showcasing_expertise

IF cultural_fit_evident:
    INTEGRATE into_cover_letter (authentically)

IF portfolio_or_work_samples_requested:
    CREATE relevant_samples (if applicable)
```

### STEP_4: CREATE_DOCUMENTS

#### RESUME_CREATION_PROTOCOL:
```
READ /mnt/skills/public/docx/SKILL.md

FORMAT:
- Name and contact (top)
- Summary (2-3 sentences, role-specific)
- Professional Experience (reverse chronological)
- Education
- Skills/Certifications (relevant only)

BULLET_POINT_FORMULA:
[Action] [Specific System/Method] [Quantified Result] [Business Impact]

EXAMPLE:
"Redesigned inventory tracking (NetSuite + custom middleware), reducing variance from 8.2% to 1.4% and cutting monthly reconciliation from 40 to 6 hours."

LENGTH_TARGET:
Entry/Mid: 1 page
Senior/Executive: 1-2 pages
C-Suite: 2 pages maximum

REQUIREMENTS:
- Every metric verified against masters
- Zero redundancy with cover letter
- Contractions â‰¥60%
- No promotional language
- Peer-to-peer tone
```

#### COVER_LETTER_CREATION_PROTOCOL:
```
READ /mnt/skills/public/docx/SKILL.md

STRUCTURE:
Para 1: Connection to role (not excitement about opportunity)
Para 2-3: Relevant experience with methodology and outcomes
Para 4: [Optional] Cultural fit (only if authentic)
Para 5: Direct next step (no pleading)

LENGTH_TARGET:
Entry: 250-350 words
Mid: 350-450 words
Senior/Executive: 450-600 words

REQUIREMENTS:
- Different examples than resume
- Process and methodology evident
- Strategic thinking demonstrated
- Zero overlap with resume specifics
- Facts and data only, no selling
- End with direct statement, not request

FORBIDDEN_PHRASES:
- "I would be excited to..."
- "I am passionate about..."
- "I believe I would be a great fit..."
- "I look forward to hearing from you..."
- "Thank you for your consideration..."

ACCEPTABLE_CLOSINGS:
- "I'm available to discuss the [specific system/challenge]."
- "I can walk through the [methodology] in detail."
- Direct statement of availability
```

#### SUPPLEMENT_CREATION_PROTOCOL:
```
IF supplemental_document_needed:
    READ appropriate skill file
    
FORMAT_OPTIONS:
- Deep-dive case study
- Technical documentation sample
- Process methodology document
- Analysis or report sample

CONTENT_RULES:
- NO overlap with resume or cover letter
- Deep technical detail appropriate to role
- Problem â†’ Approach â†’ Solution â†’ Result
- Actual work examples (anonymized if needed)
- Data-driven throughout
```

### STEP_5: ITERATIVE_EDITING_PROTOCOL

```
IF document_length > 100_lines:
    USE iterative_editing_method
    
PROCESS:
1. CREATE_FILE in /home/claude/[filename].docx
2. BUILD_SECTION_1 (use str_replace to add content)
3. BUILD_SECTION_2 (use str_replace to add content)
4. BUILD_SECTION_3 (use str_replace to add content)
5. CONTINUE until complete
6. VALIDATE full document
7. COPY to /mnt/user-data/outputs/[filename].docx

ELSE:
    CREATE_DIRECTLY in /mnt/user-data/outputs/[filename].docx
```

### STEP_6: CULTURAL_FIT_ASSESSMENT

```
IF company_culture_information_available:
    ASSESS authentic_alignment
    
IF genuine_alignment_exists:
    INTEGRATE naturally (not forced)
    USE specific_observations
    AVOID generic_enthusiasm
    
IF no_genuine_alignment OR unclear:
    SKIP cultural_fit_discussion
    FOCUS_ON role_requirements_only

FORBIDDEN:
- Manufacturing fit that doesn't exist
- Generic "passionate about mission" statements
- Forced enthusiasm
- Corporate culture buzzwords
```

---

## GATE_3: PRE_DELIVERY_VALIDATION

### MANDATORY_VALIDATION_CHECKLIST:

#### FACTUAL_ACCURACY_VALIDATION:
```
â–¡ All employment dates verified against master
â–¡ All metrics verified against achievements_database
â–¡ Education institutions correct (Pierce + Oaksterdam)
â–¡ Growth figures accurate (Good Day Farm 4x)
â–¡ GreenRush dates correct (Aug 2018 - Mar 2019)
â–¡ Phase 3 story correct version used
â–¡ Client descriptions accurate (30-40 concurrent)
â–¡ de Krown role description accurate (instrumental in building)
â–¡ No fabricated experience
â–¡ No exaggerated metrics
â–¡ All system names spelled correctly
â–¡ All company names spelled correctly

SCORING: MUST be 100% accurate. Single error = GATE_3_FAIL
```

#### VOICE_AUTHENTICITY_VALIDATION:
```
â–¡ Contraction density â‰¥60% (application mode)
â–¡ Zero em-dashes present
â–¡ Zero en-dashes present
â–¡ Hyphens used for emphasis (not dashes)
â–¡ No rhetorical questions in cover letter
â–¡ No corporate buzzwords
â–¡ No promotional language
â–¡ No manufactured enthusiasm
â–¡ Peer-to-peer tone maintained
â–¡ Direct observations, not selling
â–¡ Specific examples with data
â–¡ Parenthetical clarifications present
â–¡ Semicolons used appropriately

SCORING: â‰¥90% target (see voice_calibration_matrix.md scoring system)
```

#### LENGTH_COMPLIANCE_VALIDATION:
```
RESUME:
â–¡ Entry/Mid: 1 page
â–¡ Senior/Executive: 1-2 pages  
â–¡ C-Suite: 2 pages maximum

COVER_LETTER:
â–¡ Entry: 250-350 words
â–¡ Mid: 350-450 words
â–¡ Senior/Executive/C-Suite: 450-600 words

SUPPLEMENTS (if applicable):
â–¡ Appropriate length for document type
â–¡ Not redundant with other materials

IF out_of_range:
    EDIT to comply
    RE-VALIDATE
```

#### REDUNDANCY_CHECK_VALIDATION:
```
â–¡ Resume and cover letter use DIFFERENT specific examples
â–¡ No metric appears in multiple documents
â–¡ No achievement described identically across documents
â–¡ Each document provides unique value
â–¡ Strategic distribution of accomplishments

METHOD:
EXTRACT all_specific_examples FROM resume
EXTRACT all_specific_examples FROM cover_letter
COMPARE for duplicates
IF duplicates_found:
    REDISTRIBUTE achievements
    ENSURE zero_overlap
```

#### TONE_CALIBRATION_VALIDATION:
```
â–¡ Tone appropriate for role_tier
â–¡ No applicant-to-gatekeeper dynamic
â–¡ Confidence without arrogance
â–¡ Facts without overselling
â–¡ Professional without stiffness
â–¡ Accessible without casual
â–¡ Direct without bluntness

ROLE_TIER_TONE_CHECK:
IF entry_level:
    ENSURE competence_demonstrated, learning_capacity_evident
IF mid_level:
    ENSURE proven_execution, specific_results
IF senior_lead:
    ENSURE strategic_thinking, methodology_evident, system_design
IF executive:
    ENSURE business_impact, P&L_awareness, org_leadership
IF c_suite:
    ENSURE market_perspective, company_direction, stakeholder_value
```

#### PHASE_3_STORY_VALIDATION:
```
IF phase_3_cultivation_mentioned:
    VERIFY_EXACT_NARRATIVE:
    âœ“ "Untested integrated systems"
    âœ“ "Kept Phase 2 alive as insurance"
    âœ“ "Running two facilities simultaneously"
    âœ“ Result: zero stockouts, supply continuity maintained
    
    FORBIDDEN_NARRATIVE:
    âœ— "Extraction lab bottleneck"
    âœ— "Processing limitations"
    âœ— Any other version
    
    IF wrong_version_detected:
        HALT_DELIVERY
        CORRECT_NARRATIVE
        RE_VALIDATE_COMPLETE_GATE_3
```

#### CULTURAL_FIT_VALIDATION:
```
IF cultural_fit_discussed:
    â–¡ Authentic connection (not manufactured)
    â–¡ Specific observations (not generic)
    â–¡ Natural integration (not forced)
    â–¡ No corporate buzzwords
    â–¡ No "passionate about mission" language
    
IF no_cultural_fit_discussed:
    â–¡ Omission is acceptable
    â–¡ Focus remains on role requirements
```

#### FORMATTING_VALIDATION:
```
â–¡ Professional document formatting
â–¡ Consistent font and sizing
â–¡ Appropriate spacing
â–¡ Clean margins
â–¡ No formatting artifacts
â–¡ Proper header/footer (if used)
â–¡ Contact information correct
â–¡ File named appropriately
```

#### EM_DASH_DENSITY_CHECK:
```
COUNT total_punctuation_marks
COUNT em_dashes
CALCULATE em_dash_percentage

TARGET: 0% (zero em-dashes)
MAXIMUM_ALLOWED: 0%

IF em_dashes_detected:
    REPLACE_ALL with hyphens
    RE_VALIDATE
```

#### RHETORICAL_QUESTION_CHECK:
```
SCAN_FOR question_marks IN [cover_letter, supplements]
FOR_EACH question_mark:
    EVALUATE if rhetorical_question
    IF rhetorical_question_detected:
        REWRITE as declarative_statement
        RE_VALIDATE

APPLICATION_MODE: ZERO rhetorical questions allowed
```

#### CONTRACTION_DENSITY_CHECK:
```
COUNT total_words
COUNT contractions_used
CALCULATE contraction_percentage

TARGET_APPLICATION_MODE: â‰¥60%

IF below_target:
    IDENTIFY candidates for contraction
    REVISE to increase density
    RE_VALIDATE
    
AVOID over-contraction (sounds forced)
MAINTAIN natural flow
```

#### CORPORATE_BUZZWORD_SCAN:
```
FORBIDDEN_TERMS:
- "synergy", "leverage" (as verb), "circle back"
- "move the needle", "low-hanging fruit"
- "game-changer", "disruptive" (overused)
- "best practices", "thought leader"
- "paradigm shift", "core competencies"
- "strategic initiatives", "going forward"
- "touch base", "take offline"
- "bandwidth", "deep dive" (unless technical context)

IF any_detected:
    REPLACE with direct_language
    RE_VALIDATE
```

### GATE_3_SCORING_SYSTEM:

```
CALCULATE composite_score:

FACTUAL_ACCURACY: [0-100 points]
- 100 points: perfect accuracy
- 0 points: any factual error
- BINARY: either 100 or 0

VOICE_AUTHENTICITY: [0-100 points]
- Use scoring system from voice_calibration_matrix.md
- Target: â‰¥90 points

LENGTH_COMPLIANCE: [0-100 points]
- 100 points: within range
- 0 points: outside range
- BINARY: either 100 or 0

REDUNDANCY_CHECK: [0-100 points]
- 100 points: zero overlap
- -25 points per duplicate example
- Minimum: 0 points

TONE_CALIBRATION: [0-100 points]
- Subjective assessment
- Target: â‰¥85 points

FINAL_SCORE = (FACTUAL + VOICE + LENGTH + REDUNDANCY + TONE) / 5

PASS_THRESHOLD: â‰¥90 points
FACTUAL_ACCURACY: MUST be 100 (override all other scores)

IF score < 90 OR factual_accuracy < 100:
    GATE_3_FAIL
    IDENTIFY_ISSUES
    CORRECT_PROBLEMS
    RE_RUN_GATE_3
ELSE:
    GATE_3_PASS
    PROCEED_TO_DELIVERY
```

---

## DELIVERY_PROTOCOL

### GATE_3_PASSED:
```
1. COPY all_files TO /mnt/user-data/outputs/
2. VERIFY files_present in outputs directory
3. GENERATE computer:// links for each file
4. PRESENT_TO_USER with succinct summary

FORMAT:
"[View Resume](computer:///mnt/user-data/outputs/resume.docx)
[View Cover Letter](computer:///mnt/user-data/outputs/cover_letter.docx)"

AVOID:
- Lengthy explanations of what was done
- Over-description of contents
- Excessive postamble

USER can view files directly - trust them to evaluate
```

### GATE_3_FAILED:
```
DO_NOT_DELIVER

INSTEAD:
1. IDENTIFY specific_failures
2. DOCUMENT issues_found
3. CORRECT problems
4. RE_RUN complete GATE_3 validation
5. ONLY_DELIVER when GATE_3_PASS achieved

NEVER deliver incomplete or inaccurate materials
```

---

## SPECIAL_CASE_PROTOCOLS

### INSUFFICIENT_INFORMATION:
```
IF job_description_incomplete:
    REQUEST_CLARIFICATION from user
    SPECIFY what_information_needed
    WAIT for response
    DO_NOT_PROCEED without adequate information

IF master_files_missing_critical_data:
    NOTIFY_USER
    REQUEST updated_masters OR clarification
    HALT_WORKFLOW until resolved
```

### ROLE_REQUIREMENTS_EXCEED_EXPERIENCE:
```
IF requirements_significantly_beyond_experience:
    ASSESS transferable_skills
    MAKE honest_connections
    NEVER fabricate_experience
    ACKNOWLEDGE_GAPS if necessary (rare)
    
PRESENT strongest_relevant_experience
SHOW learning_capacity and adaptability (if appropriate for tier)
MAINTAIN integrity - never lie or exaggerate
```

### MULTIPLE_POSITIONS_SIMULTANEOUSLY:
```
IF user_applying_to_multiple_roles:
    CREATE separate_packets for each
    TAILOR each_application specifically
    MAINTAIN version_control
    ENSURE no_confusion between applications
    
TRACK:
- Company name
- Position title
- Tailoring decisions
- Documents created
```

### REVISION_REQUESTS:
```
IF user_requests_revisions:
    IDENTIFY specific_changes_needed
    VERIFY changes_maintain_gate_3_compliance
    IMPLEMENT revisions
    RE_RUN appropriate_validation_sections
    DELIVER updated_materials
    
MAINTAIN:
- Factual accuracy
- Voice authenticity
- No regression in quality
```

---

## ERROR_RECOVERY_PROTOCOL

### IF_FACTUAL_ERROR_DISCOVERED_POST_DELIVERY:
```
IMMEDIATELY:
1. ACKNOWLEDGE error
2. IDENTIFY error_source
3. UPDATE factual_corrections.md
4. CREATE corrected_version
5. RE_RUN complete_GATE_3
6. DELIVER corrected_materials
7. DOCUMENT lesson_learned
```

### IF_VOICE_AUTHENTICITY_COMPROMISED:
```
1. IDENTIFY specific_violations
2. REFERENCE voice_calibration_matrix.md
3. REWRITE affected_sections
4. RE_VALIDATE voice_scoring
5. ENSURE â‰¥90 authenticity_score
6. DELIVER corrected_version
```

---

## WORKFLOW_DECISION_TREE

```
APPLICATION_REQUEST_RECEIVED
    â†“
GATE_1: LOAD_AND_VERIFY_MASTERS
    â”œâ”€ PASS â†’ Continue
    â””â”€ FAIL â†’ Halt, request clarification
        â†“
GATE_2: ANALYZE_AND_CREATE
    â”œâ”€ Classify role tier
    â”œâ”€ Map responsibilities to experience
    â”œâ”€ Determine document types
    â”œâ”€ Create documents (iterative if >100 lines)
    â””â”€ Complete document packet
        â†“
GATE_3: COMPREHENSIVE_VALIDATION
    â”œâ”€ Run all validation checklists
    â”œâ”€ Calculate composite score
    â”œâ”€ PASS (â‰¥90, factual=100) â†’ DELIVER
    â””â”€ FAIL (<90 OR factual<100) â†’ Fix and re-validate
        â†“
DELIVERY
    â”œâ”€ Copy to /mnt/user-data/outputs/
    â”œâ”€ Generate computer:// links
    â””â”€ Present succinctly to user
```

---

**END APPLICATION_WORKFLOW**
