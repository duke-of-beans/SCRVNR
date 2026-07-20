# VOICE CONFIDENCE SCORER - Specification
Version: 1.0.0  
Purpose: Generate confidence scores for voice authenticity  
Location: core/tools/voice-confidence-scorer.md

---

## PURPOSE

Provides quantitative confidence assessment of how well generated text matches David's authentic voice for a given environment. Goes beyond simple pass/fail validation to provide nuanced scoring and specific improvement suggestions.

---

## INTERFACE

### Input
```yaml
text: string  # Generated text to score
environment: string  # 'dev', 'research', 'career', 'work', 'personal'
reference_patterns: dict  # High-confidence patterns from voice.db
```

### Output
```yaml
overall_confidence: float  # 0.0-1.0
breakdown:
  formality:
    score: int  # 1-10
    target: int  # Environment target
    delta: int  # Difference from target
  directness:
    score: int  # 1-10
    target: int
    delta: int
  contraction_rate:
    measured: float  # 0.0-1.0
    target: float
    delta: float
    count: int  # Contractions found
    opportunities: int  # Possible locations
  authenticity_markers:
    present: list[str]  # Patterns found
    missing: list[str]  # Expected but absent
    count: int
    total_expected: int
concerns:
  - description: str
  - severity: str  # 'minor', 'moderate', 'major'
  - suggestion: str
confidence_level: str  # 'high' (>0.8), 'good' (0.6-0.8), 'needs_work' (<0.6)
```

---

## SCORING METHODOLOGY

### Overall Confidence Calculation
```python
# Weighted average
overall = (
    formality_score * 0.20 +
    directness_score * 0.20 +
    contraction_score * 0.25 +
    authenticity_markers_score * 0.25 +
    forbidden_patterns_score * 0.10
) / 5.0
```

### Formality Score (0.0-1.0)
```python
# Based on environment-specific target
formality_target = environment_calibration['voice_parameters']['formality']
formality_measured = measure_formality(text)  # 1-10 scale

# Normalize distance from target
distance = abs(formality_measured - formality_target)
formality_score = max(0, 1.0 - (distance / 5.0))  # Penalize deviation
```

**Formality Indicators:**
- Passive voice frequency
- Sentence complexity
- Vocabulary sophistication
- Hedge words usage
- Technical terminology density

### Directness Score (0.0-1.0)
```python
directness_target = environment_calibration['voice_parameters']['directness']
directness_measured = measure_directness(text)  # 1-10 scale

distance = abs(directness_measured - directness_target)
directness_score = max(0, 1.0 - (distance / 5.0))
```

**Directness Indicators:**
- Imperatives vs suggestions
- Qualification frequency ("perhaps", "maybe")
- Hedging ("I think", "I believe")
- Passive constructions
- Direct statements vs tentative language

### Contraction Score (0.0-1.0)
```python
contraction_target = environment_calibration['voice_parameters']['contraction_target']
contraction_measured = count_contractions(text) / count_opportunities(text)

# Penalize deviation from target
distance = abs(contraction_measured - contraction_target)
contraction_score = max(0, 1.0 - (distance / 0.3))  # ±30% tolerance
```

**Contraction Detection:**
```python
contractions = ["it's", "you'll", "here's", "that's", "don't", "won't", "can't", "isn't", ...]
opportunities = [
    "it is" -> "it's",
    "you will" -> "you'll",
    "here is" -> "here's",
    ...
]
```

### Authenticity Markers Score (0.0-1.0)
```python
# Query voice.db for high-confidence patterns
expected_patterns = query_patterns(environment, confidence > 0.7, limit=20)

present = [p for p in expected_patterns if p in text]
missing = [p for p in expected_patterns if p not in text]

authenticity_score = len(present) / len(expected_patterns)
```

**Pattern Types Checked:**
- Transitions ("Here's how", "The way I see it")
- Phrase patterns (environment-specific)
- Sentence structures
- Tone markers

### Forbidden Patterns Score (0.0-1.0)
```python
# Query forbidden_patterns table
forbidden = query_forbidden(severity='blocking', environment=environment)

violations = [f for f in forbidden if f in text]
forbidden_score = 1.0 if len(violations) == 0 else 0.0  # Binary
```

---

## CONFIDENCE LEVELS

### High Confidence (0.8-1.0)
**Meaning:** Text strongly matches authentic voice  
**Action:** Good to deliver with minor/no revisions

### Good Confidence (0.6-0.8)
**Meaning:** Text is close but has some voice deviations  
**Action:** Review concerns, make targeted improvements

### Needs Work (<0.6)
**Meaning:** Significant voice mismatches detected  
**Action:** Regenerate or substantial revisions needed

---

## CONCERN GENERATION

Generate specific, actionable concerns:

```python
def generate_concerns(scores, text, environment):
    concerns = []
    
    # Formality concerns
    if abs(scores['formality']['delta']) >= 2:
        direction = "too formal" if scores['formality']['delta'] > 0 else "too casual"
        concerns.append({
            'description': f"Formality is {direction} for {environment} context",
            'severity': 'moderate' if abs(delta) < 3 else 'major',
            'suggestion': f"Target formality: {scores['formality']['target']}/10, measured: {scores['formality']['score']}/10"
        })
    
    # Contraction concerns
    if scores['contraction_rate']['delta'] < -0.15:
        concerns.append({
            'description': f"Contraction rate too low ({scores['contraction_rate']['measured']:.0%})",
            'severity': 'moderate',
            'suggestion': f"Target: {scores['contraction_rate']['target']:.0%}. Consider: 'it is' -> 'it's', 'you will' -> 'you'll'"
        })
    
    # Authenticity markers concerns
    if scores['authenticity_markers']['count'] < 5:
        concerns.append({
            'description': f"Missing characteristic voice patterns ({scores['authenticity_markers']['count']}/{scores['authenticity_markers']['total_expected']} present)",
            'severity': 'moderate',
            'suggestion': f"Consider incorporating: {', '.join(scores['authenticity_markers']['missing'][:3])}"
        })
    
    # Forbidden patterns concerns
    if forbidden_violations:
        for violation in forbidden_violations:
            concerns.append({
                'description': f"Forbidden pattern detected: '{violation}'",
                'severity': 'major',
                'suggestion': "Remove or rephrase this pattern"
            })
    
    return concerns
```

---

## IMPLEMENTATION NOTES

### Performance Targets
- Scoring time: <2 seconds for 500-word text
- Database queries: <3 queries total (patterns, forbidden, calibration)

### Dependencies
```python
# Standard library
import re
import sqlite3
from typing import Dict, List

# Ghost Writer
from learning.scripts.db_manager import query_patterns, query_forbidden
from environments import load_calibration
```

### Testing
Test against known good/bad examples:
- **High confidence examples:** Reference examples from core/reference/examples/
- **Low confidence examples:** Generated samples with known issues

---

## EXAMPLE OUTPUT

```yaml
overall_confidence: 0.85
breakdown:
  formality:
    score: 7
    target: 7
    delta: 0
  directness:
    score: 6
    target: 8
    delta: -2
  contraction_rate:
    measured: 0.72
    target: 0.75
    delta: -0.03
    count: 18
    opportunities: 25
  authenticity_markers:
    present: ["Here's how", "The way this works", "You'll want to", "What's interesting"]
    missing: ["Under the hood", "The trick here", "This lets you"]
    count: 4
    total_expected: 7
concerns:
  - description: "Directness could be stronger for dev context"
    severity: "minor"
    suggestion: "Use more imperatives: 'Run this' instead of 'You might want to run'"
  - description: "Missing 3 characteristic patterns"
    severity: "minor"
    suggestion: "Consider: 'Under the hood', 'The trick here', 'This lets you'"
confidence_level: "high"
```

---

## INTEGRATION

Called by:
- `tools/orchestrator.py generate` - Automatically score outputs
- `tools/voice_analyzer.py` - Voice consistency analysis
- Post-generation workflow before validation

Used for:
- Determining if variations should be generated
- Guiding revision suggestions
- Tracking voice quality over time

---

## FUTURE ENHANCEMENTS

- Machine learning model trained on reference examples
- Context-aware pattern weighting (opening vs closing, etc.)
- Historical comparison (current vs past outputs)
- Voice drift detection integration
- Real-time scoring during generation
