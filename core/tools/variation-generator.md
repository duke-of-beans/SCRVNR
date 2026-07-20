# VARIATION GENERATOR - Specification
Version: 1.0.0  
Purpose: Create 2-3 alternative versions of text with different approaches  
Location: core/tools/variation-generator.md

---

## PURPOSE

Generates multiple variations of the same content with different voice adjustments (directness, analytical depth, balance). Allows user to select best approach or hybridize elements from multiple versions.

---

## INTERFACE

### Input
```yaml
text: string  # Original generated text
environment: string  # 'dev', 'research', 'career', 'work', 'personal'
variation_count: int  # 2 or 3 (default: 3)
base_confidence: float  # Confidence score of original (from voice-confidence-scorer)
```

### Output
```yaml
variations:
  - name: str  # "Direct", "Analytical", "Balanced"
    text: str  # Generated variation
    adjustments: dict  # What was changed
    best_for: str  # When to use this version
    confidence: float  # Expected confidence (0.0-1.0)
    differences: list[str]  # Key differences from original
```

---

## VARIATION STRATEGIES

### Version A: Direct (+Directness, -Explanation)
```yaml
name: "Direct"
adjustments:
  directness: +2  # On 1-10 scale
  explanation_depth: -30%  # Reduce explanatory content
  imperatives: +40%  # More commands
  qualifiers: -80%  # Remove hedging
best_for: "When user wants punch, brevity, action-oriented"
```

**Transformations:**
- "You might want to consider X" → "Use X"
- "This approach can help with Y" → "This solves Y"
- "One way to handle this is..." → "Handle this by:"
- Remove: "perhaps", "maybe", "possibly", "might"
- Add: Imperatives ("Run", "Use", "Call", "Set")

### Version B: Analytical (+Depth, +Context)
```yaml
name: "Analytical"
adjustments:
  analytical_depth: +30%  # More explanation
  context_addition: +25%  # Add background
  examples: +2  # More concrete examples
  implications: +40%  # Discuss consequences
best_for: "When user wants thoroughness, understanding, teaching"
```

**Transformations:**
- "Use X" → "Use X because it handles Y and avoids Z"
- "This returns A" → "This returns A, which lets you B. This matters because C"
- Add: "Here's why", "The reason is", "This matters because"
- Add: More examples, edge cases, caveats
- Expand: Abbreviated explanations

### Version C: Balanced (Midpoint)
```yaml
name: "Balanced"
adjustments:
  directness: +0.5  # Slight increase from original
  explanation_depth: +5%  # Slightly more context
  optimal_mix: true  # Best of both approaches
best_for: "Default, most situations, general audience"
```

**Transformations:**
- Find balance between A (too terse) and B (too verbose)
- Keep imperatives but add brief rationale
- Maintain directness but include key context
- "Use X. It solves Y" (direct + reason, no lengthy explanation)

---

## GENERATION ALGORITHM

```python
def generate_variations(text, environment, variation_count=3, base_confidence=0.8):
    calibration = load_calibration(environment)
    
    # Parse original text
    sentences = parse_sentences(text)
    structure = analyze_structure(text)
    
    variations = []
    
    # Version A: Direct
    version_a = transform_direct(
        sentences=sentences,
        adjustments={
            'remove_qualifiers': True,
            'increase_imperatives': True,
            'reduce_explanations': 0.7,  # Keep 70%
            'simplify_transitions': True
        }
    )
    variations.append({
        'name': 'Direct',
        'text': version_a,
        'adjustments': {
            'directness': '+20%',
            'explanation': '-30%',
            'imperatives': '+40%'
        },
        'best_for': 'When you want punch and brevity',
        'confidence': estimate_confidence(version_a, environment, adjust_direct=True),
        'differences': identify_differences(text, version_a)
    })
    
    # Version B: Analytical
    version_b = transform_analytical(
        sentences=sentences,
        adjustments={
            'add_rationale': True,
            'expand_examples': True,
            'include_implications': True,
            'add_context': 0.25  # 25% more content
        }
    )
    variations.append({
        'name': 'Analytical',
        'text': version_b,
        'adjustments': {
            'depth': '+30%',
            'context': '+25%',
            'examples': '+2 additional'
        },
        'best_for': 'When you want thoroughness and teaching',
        'confidence': estimate_confidence(version_b, environment, adjust_analytical=True),
        'differences': identify_differences(text, version_b)
    })
    
    # Version C: Balanced (only if variation_count == 3)
    if variation_count == 3:
        version_c = blend_versions(version_a, version_b, ratio=0.6)  # 60% direct, 40% analytical
        variations.append({
            'name': 'Balanced',
            'text': version_c,
            'adjustments': {
                'directness': '+10%',
                'depth': '+15%',
                'optimal_mix': True
            },
            'best_for': 'Default, most situations',
            'confidence': estimate_confidence(version_c, environment),
            'differences': identify_differences(text, version_c)
        })
    
    return variations
```

---

## TRANSFORMATION FUNCTIONS

### transform_direct()
```python
def transform_direct(sentences, adjustments):
    transformed = []
    
    for sentence in sentences:
        # Remove qualifiers
        if adjustments['remove_qualifiers']:
            sentence = remove_patterns(sentence, [
                "perhaps", "maybe", "possibly", "might",
                "I think", "I believe", "in my opinion"
            ])
        
        # Increase imperatives
        if adjustments['increase_imperatives']:
            sentence = convert_to_imperative(sentence)
            # "You should use X" → "Use X"
            # "You might want to Y" → "Y"
            # "Consider using Z" → "Use Z"
        
        # Reduce explanations
        if adjustments['reduce_explanations'] < 1.0:
            # Keep main claim, remove elaboration
            sentence = trim_explanation(sentence, keep_ratio=adjustments['reduce_explanations'])
        
        transformed.append(sentence)
    
    return ' '.join(transformed)
```

### transform_analytical()
```python
def transform_analytical(sentences, adjustments):
    transformed = []
    
    for sentence in sentences:
        # Add rationale
        if adjustments['add_rationale']:
            sentence = add_because_clause(sentence)
            # "Use X" → "Use X because it handles Y"
        
        # Expand examples
        if adjustments['expand_examples']:
            if is_example(sentence):
                sentence = elaborate_example(sentence)
        
        # Include implications
        if adjustments['include_implications']:
            sentence = add_implication(sentence)
            # "X returns Y" → "X returns Y, which lets you Z. This matters because W"
        
        # Add context
        if adjustments['add_context']:
            sentence = add_context_before(sentence)
        
        transformed.append(sentence)
    
    return ' '.join(transformed)
```

### blend_versions()
```python
def blend_versions(version_a, version_b, ratio=0.6):
    # Parse both versions
    sentences_a = parse_sentences(version_a)
    sentences_b = parse_sentences(version_b)
    
    blended = []
    for sent_a, sent_b in zip(sentences_a, sentences_b):
        # Take directness from A, context from B
        base = sent_a  # Direct version
        
        # Add selective context from B
        if has_valuable_context(sent_b, sent_a):
            base = append_concise_context(base, sent_b)
        
        blended.append(base)
    
    return ' '.join(blended)
```

---

## WHEN TO GENERATE VARIATIONS

**Auto-generate when:**
- Base confidence < 0.75 (voice uncertain)
- Text > 200 words (complex enough to vary)
- User request is ambiguous
- Environment is PERSONAL or CAREER (high stakes)

**Skip variations when:**
- Base confidence > 0.85 (already strong)
- Text < 100 words (too simple)
- User explicitly asks for one style
- Quick factual response

---

## PRESENTATION TO USER

```markdown
I've generated 3 variations for you to choose from:

**Version A: Direct** (Best for: punch and brevity)
[Text...]

**Version B: Analytical** (Best for: thoroughness and teaching)
[Text...]

**Version C: Balanced** (Best for: most situations)
[Text...]

Which style do you prefer? Or would you like me to blend elements from multiple versions?
```

---

## IMPLEMENTATION NOTES

### Performance Targets
- Generation time: <5 seconds for 500-word text × 3 variations
- Each variation should differ by 20-40% from original

### Dependencies
```python
from core.tools.voice_confidence_scorer import score_confidence
from learning.scripts.db_manager import query_patterns
from environments import load_calibration
```

### Testing
Test on reference examples:
- Generate variations for each reference example
- Verify variations are meaningfully different
- Check all variations pass quality gates
- Confirm user can distinguish purposes

---

## EXAMPLE OUTPUT

**Original:**
```
The session manager tracks state across Claude instances. When a crash happens, 
it has everything needed to resume. You should call auto_checkpoint every 5-10 
tool calls, and if things break, check_recovery will load the last checkpoint.
```

**Version A (Direct):**
```
The session manager tracks state. On crash, it resumes. Call auto_checkpoint 
every 5-10 tool calls. If crashed, check_recovery loads last checkpoint.
```

**Version B (Analytical):**
```
The session manager tracks state across Claude instances, preserving your 
current operation, file paths, decisions, and next steps. When a crash happens, 
this stored context is critical because it prevents you from losing work—
you can resume exactly where you left off. Call auto_checkpoint every 5-10 tool 
calls to save this state incrementally. If things break, check_recovery loads 
the most recent checkpoint automatically, so you're never starting from scratch.
```

**Version C (Balanced):**
```
The session manager tracks state across Claude instances. On crash, it has 
everything needed to resume—current operation, file paths, decisions, next steps. 
Call auto_checkpoint every 5-10 tool calls. If crashed, check_recovery loads 
last checkpoint automatically.
```

---

## INTEGRATION

Called by:
- `tools/orchestrator.py generate --variations 3`
- Automatic when base confidence < 0.75
- User request: "show me variations"

---

## FUTURE ENHANCEMENTS

- Environment-specific variation strategies
- User preference learning (which variations picked historically)
- Hybrid generation (user picks sentence-by-sentence)
- Style transfer from reference examples
- A/B testing which variations resonate most
