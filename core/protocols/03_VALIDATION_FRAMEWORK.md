# VALIDATION_FRAMEWORK_v1.0

## VALIDATION_PHILOSOPHY

```
PRINCIPLE: Trust but verify. Every output undergoes systematic validation before delivery.
METHOD: Checklist-driven quality control with quantitative scoring.
STANDARD: â‰¥90% composite score, 100% factual accuracy (non-negotiable).
```

---

## VALIDATION_TYPE_SELECTOR

```
IF output_type = APPLICATION_MATERIALS:
    RUN comprehensive_application_validation
    
IF output_type = CASUAL_COMMUNICATION:
    RUN casual_voice_validation
    
IF output_type = PROFESSIONAL_COMMUNICATION:
    RUN professional_voice_validation
    
IF output_type = ANALYTICAL_CONTENT:
    RUN analytical_voice_validation
    
IF output_type = GENERAL_RESPONSE:
    RUN basic_voice_validation
```

---

## COMPREHENSIVE_APPLICATION_VALIDATION

### EXECUTION_PROTOCOL:
```
RUN_IN_SEQUENCE:
1. factual_accuracy_check â†’ MUST score 100%
2. voice_authenticity_check â†’ TARGET â‰¥90%
3. length_compliance_check â†’ MUST pass
4. redundancy_analysis â†’ MUST score 100%
5. tone_calibration_check â†’ TARGET â‰¥85%
6. formatting_quality_check â†’ TARGET â‰¥95%
7. punctuation_compliance_check â†’ MUST score 100%
8. contraction_density_check â†’ MUST meet threshold
9. forbidden_pattern_scan â†’ MUST score 100%
10. role_alignment_check â†’ TARGET â‰¥90%

COMPOSITE_SCORE = weighted_average(all_checks)
PASS_REQUIREMENT: composite â‰¥90 AND factual=100
```

### 1. FACTUAL_ACCURACY_CHECK [CRITICAL - MUST BE 100%]

```
VERIFICATION_AGAINST_MASTERS:

â–¡ Employment dates exact match
  FOR_EACH position:
    VERIFY start_date against professional_history_master
    VERIFY end_date against professional_history_master
    VERIFY company_name spelling exact

â–¡ Achievements data verified
  FOR_EACH quantified_achievement:
    VERIFY metric against achievements_database
    VERIFY context accurate
    VERIFY timeframe correct
    CONFIRM no exaggeration

â–¡ Education institutions correct
  âœ“ Pierce College (NOT Ventura College)
  âœ“ Oaksterdam University
  âœ“ Spelling exact
  âœ“ No fabricated degrees

â–¡ Critical metrics verified
  âœ“ Good Day Farm: 4x growth (NOT 5x)
  âœ“ GreenRush dates: August 2018 - March 2019 (NOT 2014-2015)
  âœ“ Client count: 30-40 concurrent (NOT "80% of major brands")
  âœ“ de Krown role: "instrumental in building" (NOT "built")

â–¡ Phase 3 narrative correct
  âœ“ "Untested integrated systems" version
  âœ“ "Kept Phase 2 alive as insurance"
  âœ“ NOT "extraction lab bottleneck"
  âœ“ Result: zero stockouts, supply continuity

â–¡ System/technology names spelled correctly
  CHECK: NetSuite, QuickBooks, METRC, BioTrack, etc.

â–¡ Company names spelled correctly
  CHECK: Good Day Farm, GreenRush, de Krown, etc.

SCORING:
100 points: Zero factual errors
0 points: Any factual error present

FAIL_ACTION:
IF score < 100:
    IDENTIFY_EACH_ERROR
    CORRECT_USING_MASTER_FILES
    UPDATE_FACTUAL_CORRECTIONS_DB if new_pattern
    RE_RUN_COMPLETE_CHECK
```

### 2. VOICE_AUTHENTICITY_CHECK [TARGET â‰¥90 points]

```
SCORING_SYSTEM (from voice_calibration_matrix.md):

POSITIVE_INDICATORS:
+10 points: Each appropriate contraction
+15 points: Hyphen used for emphasis
+20 points: Specific data/example from experience
+10 points: Parenthetical aside adds context
+15 points: Semicolon connects related ideas
+20 points: Ends with fact/precedent (analytical)
+15 points: Natural sentence flow
+10 points: Technical precision with accessibility

NEGATIVE_INDICATORS:
-25 points: Em-dash used (â€”)
-25 points: En-dash used (â€“)
-20 points: Rhetorical question (prof/analytical/application)
-30 points: Corporate buzzword
-20 points: Promotional language (application)
-15 points: Hedging qualifier
-25 points: Emotional ending (analytical)
-20 points: Memory attribution phrase
-15 points: Manufactured enthusiasm
-20 points: Applicant-to-gatekeeper tone

CALCULATION:
SUM(positive_indicators) - SUM(negative_indicators) = VOICE_SCORE

TARGET_APPLICATION_MODE: â‰¥90 points
TARGET_OTHER_MODES: â‰¥90 points

FAIL_ACTION:
IF score < 90:
    IDENTIFY_SPECIFIC_VIOLATIONS
    REFERENCE voice_calibration_matrix.md
    REWRITE_PROBLEMATIC_SECTIONS
    RE_SCORE
```

### 3. LENGTH_COMPLIANCE_CHECK [BINARY PASS/FAIL]

```
DOCUMENT_TYPE_RANGES:

RESUME:
IF role_tier = [ENTRY, MID]:
    REQUIREMENT: Exactly 1 page
IF role_tier = [SENIOR_LEAD, EXECUTIVE]:
    REQUIREMENT: 1-2 pages
IF role_tier = C_SUITE:
    REQUIREMENT: Maximum 2 pages

COVER_LETTER:
IF role_tier = ENTRY:
    REQUIREMENT: 250-350 words
IF role_tier = MID:
    REQUIREMENT: 350-450 words
IF role_tier = [SENIOR_LEAD, EXECUTIVE, C_SUITE]:
    REQUIREMENT: 450-600 words

SUPPLEMENTS (if applicable):
    REQUIREMENT: Appropriate to document type
    NO arbitrary page limits
    MUST provide value (not filler)

VERIFICATION:
COUNT pages (resume)
COUNT words (cover letter)
ASSESS value (supplements)

SCORING:
100 points: Within range
0 points: Outside range

FAIL_ACTION:
IF score < 100:
    IF too_long: EDIT for concision
    IF too_short: ADD substance (not filler)
    MAINTAIN quality while adjusting length
    RE_VERIFY
```

### 4. REDUNDANCY_ANALYSIS [MUST BE 100%]

```
CROSS_DOCUMENT_COMPARISON:

EXTRACT all_specific_examples FROM resume
EXTRACT all_specific_examples FROM cover_letter
EXTRACT all_specific_examples FROM supplements (if exist)

FOR_EACH example:
    CHECK if appears in multiple_documents
    IF duplicate_found:
        FLAG as redundancy_violation

SPECIFIC_CHECKS:
â–¡ No identical metric in multiple documents
â–¡ No achievement described same way twice
â–¡ Different examples demonstrate different capabilities
â–¡ Strategic distribution of accomplishments
â–¡ Each document provides unique value

EXAMPLE_VIOLATION:
Resume: "Reduced inventory variance from 8.2% to 1.4%"
Cover Letter: "Reduced inventory variance from 8.2% to 1.4%"
â†’ FAIL: exact duplicate metric

EXAMPLE_ACCEPTABLE:
Resume: "Reduced inventory variance from 8.2% to 1.4%"
Cover Letter: "Redesigned supply chain tracking methodology"
â†’ PASS: different aspect of same project

SCORING:
100 points: Zero redundancy
-25 points: Each duplicate found
Minimum: 0 points

FAIL_ACTION:
IF score < 100:
    IDENTIFY all_duplicates
    REDISTRIBUTE achievements across documents
    ENSURE each_document_unique_value
    RE_ANALYZE
```

### 5. TONE_CALIBRATION_CHECK [TARGET â‰¥85 points]

```
ROLE_TIER_APPROPRIATE_TONE:

IF role_tier = ENTRY:
    ASSESS:
    â–¡ Competence demonstrated without overconfidence
    â–¡ Learning capacity evident
    â–¡ Foundational skills highlighted
    â–¡ Enthusiasm natural, not manufactured
    â–¡ Appropriate humility balanced with capability
    
IF role_tier = MID:
    ASSESS:
    â–¡ Proven execution emphasized
    â–¡ Specific results prominent
    â–¡ Confidence without arrogance
    â–¡ Results-oriented language
    â–¡ Technical competence clear

IF role_tier = SENIOR_LEAD:
    ASSESS:
    â–¡ Strategic thinking demonstrated
    â–¡ Methodology evident
    â–¡ System design capability shown
    â–¡ Team leadership included
    â–¡ Peer-level communication maintained

IF role_tier = EXECUTIVE:
    ASSESS:
    â–¡ Business impact focus
    â–¡ P&L awareness demonstrated
    â–¡ Organizational leadership shown
    â–¡ Strategic vision evident
    â–¡ Executive peer tone

IF role_tier = C_SUITE:
    ASSESS:
    â–¡ Market perspective demonstrated
    â–¡ Company direction capability
    â–¡ Stakeholder value focus
    â–¡ Industry positioning discussed
    â–¡ C-level peer communication

UNIVERSAL_TONE_REQUIREMENTS:
â–¡ Peer-to-peer (never applicant-to-gatekeeper)
â–¡ Confidence without arrogance
â–¡ Facts without overselling
â–¡ Professional without stiffness
â–¡ Accessible without casualness
â–¡ Direct without bluntness

SCORING:
100 points: Perfect tone calibration
-5 points: Minor tone misalignment
-15 points: Moderate tone issue
-30 points: Major tone violation

TARGET: â‰¥85 points

FAIL_ACTION:
IF score < 85:
    IDENTIFY tone_issues
    ADJUST for role_tier
    REWRITE problematic_sections
    RE_ASSESS
```

### 6. FORMATTING_QUALITY_CHECK [TARGET â‰¥95 points]

```
DOCUMENT_FORMATTING:

â–¡ Font consistent throughout
â–¡ Font size appropriate (10-12pt body)
â–¡ Spacing consistent
â–¡ Margins appropriate (0.5-1 inch)
â–¡ Headers/footers professional (if used)
â–¡ Bullet points aligned correctly
â–¡ No orphaned text
â–¡ No formatting artifacts
â–¡ Clean paragraph breaks
â–¡ Consistent date formatting
â–¡ Contact information formatted correctly
â–¡ File named appropriately

SCORING:
100 points: Perfect formatting
-5 points: Minor formatting inconsistency
-10 points: Noticeable formatting issue
-20 points: Major formatting problem

TARGET: â‰¥95 points

FAIL_ACTION:
IF score < 95:
    CLEAN_UP formatting_issues
    ENSURE consistency
    RE_CHECK
```

### 7. PUNCTUATION_COMPLIANCE_CHECK [MUST BE 100%]

```
CRITICAL_RULE: NO EM-DASHES OR EN-DASHES

SCAN_FOR:
- Em-dashes (â€”)
- En-dashes (â€“)

COUNT_VIOLATIONS:
em_dash_count = 0 (required)
en_dash_count = 0 (required)

VERIFY:
â–¡ Zero em-dashes present
â–¡ Zero en-dashes present
â–¡ Hyphens (-) used instead
â–¡ Parentheses used appropriately
â–¡ Semicolons used correctly
â–¡ Commas placed correctly

SCORING:
100 points: Zero violations
0 points: Any em-dash or en-dash present

FAIL_ACTION:
IF score < 100:
    REPLACE all_em_dashes WITH hyphens
    REPLACE all_en_dashes WITH hyphens
    VERIFY_REPLACEMENT
    RE_SCAN
```

### 8. CONTRACTION_DENSITY_CHECK [MODE-SPECIFIC]

```
COUNT total_words
COUNT contractions_present
CALCULATE contraction_percentage = (contractions / total_words) * 100

THRESHOLDS_BY_MODE:
CASUAL: â‰¥95% of opportunities
PROFESSIONAL: â‰¥85% of opportunities
ANALYTICAL: â‰¥70% of opportunities
APPLICATION: â‰¥60% of opportunities

NOTE: "Opportunities" = places where contraction natural/appropriate

VERIFICATION:
FOR_EACH potential_contraction_location:
    IF sounds_natural:
        EXPECT contraction
        IF not_present:
            FLAG as density_issue

COMMON_CONTRACTIONS_REQUIRED:
- I'm, you're, we're, it's, that's
- can't, won't, don't, didn't, doesn't
- could've, would've, should've
- isn't, aren't, wasn't, weren't
- there's, here's, what's, who's

SCORING:
100 points: Meets or exceeds threshold
-10 points: Each 5% below threshold
Minimum: 0 points

FAIL_ACTION:
IF score < 100:
    IDENTIFY contraction_opportunities
    ADD contractions naturally
    AVOID over-contraction (forced sound)
    RE_COUNT and RE_CALCULATE
```

### 9. FORBIDDEN_PATTERN_SCAN [MUST BE 100%]

```
SCAN_FOR_VIOLATIONS:

PUNCTUATION_VIOLATIONS:
â–¡ No em-dashes (â€”)
â–¡ No en-dashes (â€“)

STRUCTURAL_VIOLATIONS:
â–¡ No rhetorical questions (professional/analytical/application)
â–¡ No emotional endings (analytical)
â–¡ No call-to-action endings (analytical)

LANGUAGE_VIOLATIONS:
â–¡ No corporate buzzwords
â–¡ No promotional language (application)
â–¡ No manufactured enthusiasm
â–¡ No hedging qualifiers
â–¡ No memory attribution phrases
â–¡ No excessive exclamation points

CORPORATE_BUZZWORD_LIST:
- synergy, leverage (verb), circle back
- move the needle, low-hanging fruit
- game-changer, disruptive (overused)
- best practices, thought leader
- paradigm shift, core competencies
- touch base, take offline
- bandwidth (non-technical)

PROMOTIONAL_LANGUAGE_LIST:
- "excited to", "passionate about"
- "great fit", "perfect opportunity"
- "would love to", "look forward to"
- "thank you for your consideration"

SCORING:
100 points: Zero violations
-20 points: Each violation found
Minimum: 0 points

FAIL_ACTION:
IF score < 100:
    IDENTIFY each_violation
    REWRITE using allowed_patterns
    REFERENCE forbidden_patterns.md
    RE_SCAN
```

### 10. ROLE_ALIGNMENT_CHECK [TARGET â‰¥90 points]

```
ASSESS_FIT_BETWEEN_EXPERIENCE_AND_ROLE:

â–¡ Required responsibilities mapped to actual experience
â–¡ Transferable skills identified correctly
â–¡ No experience fabrication
â–¡ Appropriate examples selected
â–¡ Skill level matches role tier
â–¡ Relevant achievements emphasized
â–¡ Irrelevant experience minimized

VERIFICATION:
FOR_EACH required_responsibility:
    CHECK if experience_demonstrated
    VERIFY against master_files
    ASSESS relevance_strength [HIGH|MEDIUM|LOW]
    
STRENGTH_DISTRIBUTION:
HIGH_relevance: â‰¥70% of requirements
MEDIUM_relevance: â‰¤25% of requirements
LOW_relevance: â‰¤5% of requirements

SCORING:
100 points: Perfect alignment
-5 points: Each misaligned element
-30 points: Fabricated experience (automatic fail)

TARGET: â‰¥90 points

FAIL_ACTION:
IF score < 90:
    RE_ASSESS requirement mapping
    FIND better_examples from experience
    ADJUST emphasis
    RE_EVALUATE
```

---

## CASUAL_VOICE_VALIDATION

```
STREAMLINED_CHECK (less comprehensive than application):

â–¡ Contraction density â‰¥95%
â–¡ Natural speech patterns
â–¡ Short sentence structure (8-15 words avg)
â–¡ Warm but not effusive
â–¡ Playful if appropriate
â–¡ No corporate language
â–¡ No excessive formality
â–¡ Hyphens (not em-dashes)

SCORING: PASS/FAIL (qualitative assessment)

FAIL_ACTION:
IF fails:
    REFERENCE voice_calibration_matrix.md CASUAL_MODE
    ADJUST tone and structure
    RE_VALIDATE
```

---

## PROFESSIONAL_VOICE_VALIDATION

```
FOCUSED_CHECK:

â–¡ Contraction density â‰¥85%
â–¡ Methodical communication
â–¡ Parenthetical clarifications present
â–¡ Technical precision maintained
â–¡ Solutions-oriented framing
â–¡ Peer-to-peer tone
â–¡ No corporate buzzwords
â–¡ Hyphens (not em-dashes)
â–¡ Specific examples included

SCORING: PASS/FAIL (qualitative assessment)

FAIL_ACTION:
IF fails:
    REFERENCE voice_calibration_matrix.md PROFESSIONAL_MODE
    ADJUST approach
    RE_VALIDATE
```

---

## ANALYTICAL_VOICE_VALIDATION

```
RIGOROUS_CHECK:

â–¡ Contraction density â‰¥70%
â–¡ Complex sentence structure (3-4 clauses)
â–¡ Evidence accumulation present
â–¡ Argument builds: phenomenon â†’ data â†’ pattern â†’ implication â†’ fact
â–¡ Ends with precedent/fact (NOT emotion/question)
â–¡ Historical parallels if appropriate
â–¡ Controlled frustration (not performative)
â–¡ Declarative statements
â–¡ No rhetorical questions
â–¡ Hyphens (not em-dashes)
â–¡ Specific data points included

SCORING: PASS/FAIL (qualitative assessment)

FAIL_ACTION:
IF fails:
    REFERENCE voice_calibration_matrix.md ANALYTICAL_MODE
    REBUILD argument_structure
    RE_VALIDATE
```

---

## BASIC_VOICE_VALIDATION

```
MINIMAL_CHECK (general responses):

â–¡ Appropriate contraction usage
â–¡ Natural flow
â–¡ No forbidden patterns
â–¡ Hyphens (not em-dashes)
â–¡ Tone appropriate to query
â–¡ Helpful and clear

SCORING: PASS/FAIL (qualitative assessment)

FAIL_ACTION:
IF fails:
    IDENTIFY issue
    CORRECT
    RE_CHECK
```

---

## COMPOSITE_SCORING_SYSTEM

### FOR_APPLICATION_MATERIALS:

```
CALCULATE_COMPOSITE:

WEIGHTS:
factual_accuracy: 30% (but MUST be 100%)
voice_authenticity: 25%
length_compliance: 10% (but MUST pass)
redundancy_analysis: 15%
tone_calibration: 10%
formatting_quality: 5%
punctuation_compliance: 5% (but MUST be 100%)

FORMULA:
composite_score = (
    factual * 0.30 +
    voice * 0.25 +
    length * 0.10 +
    redundancy * 0.15 +
    tone * 0.10 +
    formatting * 0.05 +
    punctuation * 0.05
)

ADDITIONAL_REQUIREMENTS:
contraction_density MUST meet threshold
forbidden_pattern_scan MUST score 100%
role_alignment MUST score â‰¥90%

PASS_CRITERIA:
composite_score â‰¥90 AND
factual_accuracy = 100 AND
length_compliance = PASS AND
punctuation_compliance = 100 AND
contraction_density MEETS_THRESHOLD AND
forbidden_pattern_scan = 100 AND
role_alignment â‰¥90

IF any_requirement_fails:
    OVERALL_STATUS = FAIL
    DOCUMENT issues
    CORRECT
    RE_VALIDATE_COMPLETE
```

---

## VALIDATION_EXECUTION_PROTOCOL

### SYSTEMATIC_APPROACH:

```
STEP_1: RUN_ALL_CHECKS
    EXECUTE each validation in sequence
    RECORD scores for each
    DOCUMENT any violations found

STEP_2: CALCULATE_COMPOSITE
    APPLY weighting formula
    CHECK critical requirements
    DETERMINE pass/fail status

STEP_3: IF_FAIL_DETECTED
    IDENTIFY_ALL_ISSUES
    PRIORITIZE_BY_SEVERITY:
        - CRITICAL: factual errors, forbidden patterns
        - HIGH: voice authenticity, role alignment
        - MEDIUM: tone, formatting
        - LOW: minor style adjustments
    
STEP_4: CORRECT_ISSUES
    FIX in priority order
    VERIFY each correction
    MAINTAIN overall quality

STEP_5: RE_VALIDATE
    RUN_COMPLETE_VALIDATION again
    CONFIRM all issues resolved
    VERIFY no regression

STEP_6: DELIVER_OR_ITERATE
    IF PASS:
        PROCEED to delivery
    ELSE:
        REPEAT STEP_3 through STEP_5
```

---

## VALIDATION_DOCUMENTATION

### RECORD_KEEPING:

```
FOR_EACH_VALIDATION_RUN:
    LOG:
    - Timestamp
    - Document type
    - Validation scores (each check)
    - Composite score
    - Pass/fail status
    - Issues identified
    - Corrections made
    - Re-validation results

PURPOSE:
- Track quality over time
- Identify recurring issues
- Improve process
- Maintain accountability
```

---

## EMERGENCY_VALIDATION_OVERRIDE

```
ONLY_USE_IF:
- User explicitly requests incomplete validation
- Time-sensitive emergency
- User accepts risk

PROCEDURE:
1. DOCUMENT override reason
2. WARN user of quality risk
3. SKIP non-critical checks ONLY
4. NEVER skip factual_accuracy check
5. DELIVER with disclaimer

USE_SPARINGLY: Overrides undermine system integrity
```

---

**END VALIDATION_FRAMEWORK**
