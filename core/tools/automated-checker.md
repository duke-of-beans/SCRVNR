# AUTOMATED PATTERN CHECKER - Specification
Version: 1.0.0  
Purpose: Fast automated validation of common voice patterns before delivery  
Location: core/tools/automated-checker.md

---

## PURPOSE

Runs automated checks for common voice violations (forbidden patterns, contraction rate, dash density, etc.) before delivery. Provides pass/fail with line numbers for quick fixes.

---

## INTERFACE

### Input
```yaml
text: string  # Text to validate
environment: string  # 'dev', 'research', 'career', 'work', 'personal'
```

### Output
```yaml
overall_pass: bool  # True if all checks pass
checks:
  - name: str  # Check name
    pass: bool
    details: dict  # Check-specific details
    violations: list[dict]  # Line numbers and excerpts if failed
score: float  # 0.0-1.0 (percentage of checks passed)
summary: str  # Human-readable summary
```

---

## CHECKS PERFORMED

### 1. Contraction Rate
**Target:** Environment-specific (40-90%)  
**Minimum:** Environment minimum  
**Check:** Count contractions vs opportunities

```python
def check_contraction_rate(text, environment):
    contractions_found = count_contractions(text)
    opportunities = count_contraction_opportunities(text)
    rate = contractions_found / opportunities if opportunities > 0 else 0
    
    target = env_calibration[environment]['contraction_target']
    minimum = env_calibration[environment]['contraction_minimum']
    
    pass_check = rate >= minimum
    
    return {
        'name': 'contraction_rate',
        'pass': pass_check,
        'details': {
            'measured': rate,
            'target': target,
            'minimum': minimum,
            'count': contractions_found,
            'opportunities': opportunities
        },
        'violations': [] if pass_check else identify_missed_contractions(text)
    }
```

**Violations Format:**
```yaml
- line: 5
  excerpt: "it is important to"
  suggestion: "it's important to"
```

### 2. Dash Density
**Target:** ≤3 dashes per page (all types: em, en, hyphen for pause)  
**Check:** Count all dash usage

```python
def check_dash_density(text, environment):
    # Count all dash types used for pauses/emphasis
    em_dashes = text.count('—')
    en_dashes = text.count('–')
    # Don't count hyphens in compound words, only pause hyphens
    pause_hyphens = count_pause_hyphens(text)
    
    total_dashes = em_dashes + en_dashes + pause_hyphens
    
    # Estimate pages (500 words per page)
    word_count = len(text.split())
    pages = max(1, word_count / 500)
    dashes_per_page = total_dashes / pages
    
    pass_check = dashes_per_page <= 3
    
    return {
        'name': 'dash_density',
        'pass': pass_check,
        'details': {
            'total_dashes': total_dashes,
            'pages': pages,
            'per_page': dashes_per_page,
            'limit': 3
        },
        'violations': [] if pass_check else identify_excessive_dashes(text)
    }
```

### 3. Forbidden Patterns
**Target:** 0 instances  
**Check:** Query voice.db forbidden_patterns table

```python
def check_forbidden_patterns(text, environment):
    # Get forbidden patterns from database
    forbidden = query_forbidden_patterns(environment)
    
    violations = []
    for pattern in forbidden:
        matches = find_pattern(text, pattern['pattern'])
        if matches:
            for match in matches:
                violations.append({
                    'line': match['line'],
                    'excerpt': match['excerpt'],
                    'pattern': pattern['pattern'],
                    'reason': pattern['reason'],
                    'severity': pattern['severity']
                })
    
    pass_check = len(violations) == 0
    
    return {
        'name': 'forbidden_patterns',
        'pass': pass_check,
        'details': {
            'patterns_checked': len(forbidden),
            'violations_found': len(violations)
        },
        'violations': violations
    }
```

### 4. Rhetorical Questions
**Target:** 0 (max 1 if opening hook immediately answered)  
**Check:** Count question marks in rhetorical context

```python
def check_rhetorical_questions(text, environment):
    questions = find_questions(text)
    rhetorical = [q for q in questions if is_rhetorical(q, text)]
    
    # Allow 1 if it's opening hook immediately answered
    max_allowed = 1 if is_opening_hook_pattern(text, rhetorical) else 0
    
    pass_check = len(rhetorical) <= max_allowed
    
    return {
        'name': 'rhetorical_questions',
        'pass': pass_check,
        'details': {
            'found': len(rhetorical),
            'allowed': max_allowed
        },
        'violations': [] if pass_check else [
            {'line': q['line'], 'excerpt': q['text']}
            for q in rhetorical
        ]
    }
```

### 5. Expert Audience (No Condescension)
**Target:** 0 teaching phrases  
**Check:** Detect condescending patterns

```python
def check_expert_audience(text, environment):
    condescending_patterns = [
        "simply put", "in other words", "to put it another way",
        "as you can see", "obviously", "clearly", "of course",
        "let me explain", "for those unfamiliar", "as mentioned earlier",
        "it should be noted", "needless to say"
    ]
    
    violations = []
    for pattern in condescending_patterns:
        matches = find_pattern_case_insensitive(text, pattern)
        if matches:
            for match in matches:
                violations.append({
                    'line': match['line'],
                    'excerpt': match['excerpt'],
                    'pattern': pattern,
                    'reason': 'Condescending to expert audience'
                })
    
    pass_check = len(violations) == 0
    
    return {
        'name': 'expert_audience',
        'pass': pass_check,
        'details': {
            'patterns_checked': len(condescending_patterns),
            'violations_found': len(violations)
        },
        'violations': violations
    }
```

### 6. Third-Person Self-References
**Target:** 0  
**Check:** Detect "David's" or "his" in first-person documents

```python
def check_third_person_refs(text, environment):
    patterns = [
        r"David['']s\s+\w+",  # "David's project", "David's work"
        r"his\s+(experience|project|work|career|approach)",  # Context-specific
        r"David['']s\s+(experience|background|role)"
    ]
    
    violations = []
    for pattern in patterns:
        matches = find_regex_pattern(text, pattern)
        if matches:
            for match in matches:
                violations.append({
                    'line': match['line'],
                    'excerpt': match['excerpt'],
                    'suggestion': convert_to_first_person(match['text'])
                })
    
    pass_check = len(violations) == 0
    
    return {
        'name': 'third_person_self_refs',
        'pass': pass_check,
        'details': {
            'violations_found': len(violations)
        },
        'violations': violations
    }
```

### 7. Weak Verbs (CAREER-specific)
**Target:** Warning only (not blocking)  
**Check:** Count weak verbs, suggest replacements

```python
def check_weak_verbs(text, environment):
    if environment != 'career':
        return {'name': 'weak_verbs', 'pass': True, 'details': {}, 'violations': []}
    
    weak_verb_replacements = {
        'achieved': 'hit',
        'managed': ['ran', 'owned', 'handled'],
        'coordinated': 'ran',
        'oversaw': ['ran', 'owned'],
        'facilitated': 'ran',
        'utilized': 'used',
        'responsible for': ['owned', 'ran']
    }
    
    violations = []
    for weak, strong in weak_verb_replacements.items():
        matches = find_word(text, weak)
        if matches:
            for match in matches:
                violations.append({
                    'line': match['line'],
                    'excerpt': match['excerpt'],
                    'weak_verb': weak,
                    'suggested_replacement': strong if isinstance(strong, str) else ' or '.join(strong),
                    'severity': 'warning'  # Not blocking
                })
    
    # Pass check even with violations (warnings only)
    pass_check = True
    
    return {
        'name': 'weak_verbs',
        'pass': pass_check,
        'details': {
            'warnings': len(violations)
        },
        'violations': violations
    }
```

---

## SCORING

```python
def calculate_score(checks):
    # Count passing checks (ignore warnings)
    blocking_checks = [c for c in checks if c['name'] != 'weak_verbs']
    passing = sum(1 for c in blocking_checks if c['pass'])
    total = len(blocking_checks)
    
    return passing / total if total > 0 else 1.0
```

**Interpretation:**
- 1.0 (100%): All checks passed ✅
- 0.85-0.99: Minor issues (warnings only)
- 0.70-0.84: Some violations, needs fixes
- <0.70: Significant issues, regenerate recommended

---

## OUTPUT FORMAT

```yaml
overall_pass: false
score: 0.83  # 5/6 blocking checks passed
summary: "5 of 6 checks passed. Issues: dash_density."

checks:
  - name: contraction_rate
    pass: true
    details:
      measured: 0.75
      target: 0.75
      minimum: 0.60
      count: 18
      opportunities: 24
    violations: []
    
  - name: dash_density
    pass: false
    details:
      total_dashes: 8
      pages: 1.2
      per_page: 6.7
      limit: 3
    violations:
      - line: 5
        excerpt: "The approach—when done correctly—yields results"
        type: "em_dash"
      - line: 12
        excerpt: "Three factors—cost, speed, quality—matter most"
        type: "em_dash"
      - line: 18
        excerpt: "This pattern—surprisingly common—appears often"
        type: "em_dash"
        
  - name: forbidden_patterns
    pass: true
    details:
      patterns_checked: 47
      violations_found: 0
    violations: []
    
  - name: rhetorical_questions
    pass: true
    details:
      found: 0
      allowed: 0
    violations: []
    
  - name: expert_audience
    pass: true
    details:
      patterns_checked: 11
      violations_found: 0
    violations: []
    
  - name: third_person_self_refs
    pass: true
    details:
      violations_found: 0
    violations: []
    
  - name: weak_verbs
    pass: true  # Always true (warnings only)
    details:
      warnings: 2
    violations:
      - line: 8
        excerpt: "managed a team of 60"
        weak_verb: "managed"
        suggested_replacement: "ran or owned or handled"
        severity: "warning"
```

---

## IMPLEMENTATION NOTES

### Performance Targets
- Validation time: <1 second for 500-word text
- Database queries: <5 (forbidden patterns, environment calibration)

### Dependencies
```python
import re
import sqlite3
from typing import List, Dict
from learning.scripts.db_manager import query_forbidden_patterns
from environments import load_calibration
```

### Testing
- Test on all reference examples (should pass)
- Test on known violations (should fail appropriately)
- Verify line numbers accurate
- Check suggestions helpful

---

## INTEGRATION

Called by:
- `tools/orchestrator.py validate {file}`
- Pre-delivery workflow (mandatory)
- User request: "validate this"
- Automated before present_files

**Command Line:**
```bash
python tools/orchestrator.py validate output.md --environment career
```

---

## FUTURE ENHANCEMENTS

- Machine learning for pattern detection
- Context-aware validation (opening vs body vs closing)
- Custom user-defined checks
- Integration with IDE/editor (real-time checking)
- Automated fix suggestions (not just detection)
