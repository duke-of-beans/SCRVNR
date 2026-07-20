# INTENSITY CALIBRATOR - Specification
Version: 1.0.0  
Purpose: Adjust directness/confrontation level on 1-10 scale  
Location: core/tools/intensity-calibrator.md

---

## PURPOSE

Provides fine-grained control over how direct, confrontational, or diplomatic text should be. Acts as a "tone dial" that adjusts intensity without changing core voice authenticity.

---

## INTERFACE

### Input
```yaml
text: string  # Text to calibrate
environment: string  # 'dev', 'research', 'career', 'work', 'personal'
target_intensity: int  # 1-10 scale
current_intensity: int  # Optional: detected from text (if not provided, auto-detect)
```

### Output
```yaml
calibrated_text: string  # Intensity-adjusted version
original_intensity: int  # Detected from input
target_intensity: int  # Requested level
actual_intensity: int  # Achieved level (may differ slightly from target)
adjustments_made: list[str]  # Specific changes applied
```

---

## INTENSITY SCALE

### 1-3: Maximum Diplomacy
**Characteristics:**
- Soft language, maximum politeness
- Heavy qualification ("perhaps", "might", "possibly")
- Suggestions instead of directives
- Gentle framing
- Conflict avoidance

**Use Cases:**
- Sensitive family communications
- Diplomatic negotiations
- First contact with strangers
- High-stakes delicate situations

**Example Transformations:**
- "This doesn't work" → "This approach might not be ideal in this context"
- "You need to fix X" → "Perhaps we could explore alternative approaches to X"
- "That's wrong" → "There might be another way to think about this"

### 4-6: Professional Peer Communication
**Characteristics:**
- Balanced directness
- Minimal qualification
- Clear but not harsh
- Respectful but honest
- Standard professional tone

**Use Cases:**
- LinkedIn posts
- Professional emails
- Colleague communications
- Business proposals
- Most CAREER/WORK outputs

**Example Transformations:**
- "This doesn't work" → "This approach has some limitations"
- "You need to fix X" → "X needs attention"
- "That's wrong" → "That's not quite right"

### 7-9: Direct, No Sugar-Coating
**Characteristics:**
- Minimal hedging
- Direct statements
- Honest assessments
- Unvarnished truth
- Respectful but blunt

**Use Cases:**
- Executive feedback
- Technical assessments
- Crisis communication
- Opinion pieces
- When honesty required

**Example Transformations:**
- "This might not work" → "This doesn't work"
- "Perhaps we should reconsider X" → "Fix X"
- "This could be clearer" → "This is unclear"

### 10: Confrontational/Tension Expected
**Characteristics:**
- Deliberately provocative
- No hedging whatsoever
- Challenging statements
- Tension acknowledged
- Strong disagreement

**Use Cases:**
- Rare, only when necessary
- Public disagreement
- Calling out problems
- Breaking from consensus

**Example Transformations:**
- "This approach has issues" → "This approach is fundamentally broken"
- "We should reconsider X" → "X is wrong, here's why"
- "This could be better" → "This is unacceptable"

---

## CALIBRATION ALGORITHM

```python
def calibrate_intensity(text, environment, target_intensity, current_intensity=None):
    # Detect current intensity if not provided
    if current_intensity is None:
        current_intensity = detect_intensity(text)
    
    # Calculate adjustment needed
    intensity_delta = target_intensity - current_intensity
    
    if intensity_delta == 0:
        return {
            'calibrated_text': text,
            'original_intensity': current_intensity,
            'target_intensity': target_intensity,
            'actual_intensity': current_intensity,
            'adjustments_made': ['No adjustment needed']
        }
    
    # Apply transformations based on direction and magnitude
    if intensity_delta > 0:
        # Increase directness
        calibrated = increase_directness(text, magnitude=abs(intensity_delta))
    else:
        # Decrease directness (add diplomacy)
        calibrated = decrease_directness(text, magnitude=abs(intensity_delta))
    
    # Verify actual intensity achieved
    actual_intensity = detect_intensity(calibrated)
    
    return {
        'calibrated_text': calibrated,
        'original_intensity': current_intensity,
        'target_intensity': target_intensity,
        'actual_intensity': actual_intensity,
        'adjustments_made': list_transformations_applied(text, calibrated)
    }
```

---

## INTENSITY DETECTION

```python
def detect_intensity(text):
    score = 5  # Baseline neutral
    
    # Analyze linguistic markers
    qualifiers = count_patterns(text, [
        "perhaps", "maybe", "possibly", "might",
        "could", "may", "I think", "I believe"
    ])
    score -= (qualifiers / word_count(text)) * 10  # More qualifiers = lower intensity
    
    imperatives = count_imperatives(text)
    score += (imperatives / sentence_count(text)) * 2  # More commands = higher intensity
    
    hedging = count_patterns(text, [
        "somewhat", "rather", "quite", "fairly",
        "kind of", "sort of", "a bit"
    ])
    score -= (hedging / word_count(text)) * 10
    
    strong_language = count_patterns(text, [
        "must", "should", "need to", "have to",
        "wrong", "broken", "failure", "unacceptable"
    ])
    score += (strong_language / word_count(text)) * 15
    
    # Clamp to 1-10 range
    return max(1, min(10, round(score)))
```

---

## TRANSFORMATION FUNCTIONS

### increase_directness()
```python
def increase_directness(text, magnitude):
    """Increase intensity by removing softeners and adding directness"""
    
    transformations = []
    
    # Level 1-2 increase: Remove qualifiers
    if magnitude >= 1:
        text = remove_patterns(text, [
            "perhaps", "maybe", "possibly", "might",
            "I think", "I believe", "in my opinion"
        ])
        transformations.append("Removed qualifiers")
    
    # Level 3-4 increase: Convert suggestions to directives
    if magnitude >= 3:
        text = suggestions_to_directives(text)
        # "You might want to X" → "X"
        # "Consider doing Y" → "Do Y"
        transformations.append("Converted suggestions to directives")
    
    # Level 5+ increase: Add strong language
    if magnitude >= 5:
        text = soften_to_strong(text)
        # "This approach has issues" → "This approach doesn't work"
        # "This could be better" → "This needs fixing"
        transformations.append("Strengthened language")
    
    return text, transformations
```

### decrease_directness()
```python
def decrease_directness(text, magnitude):
    """Decrease intensity by adding softeners and removing harshness"""
    
    transformations = []
    
    # Level 1-2 decrease: Add qualifiers
    if magnitude >= 1:
        text = add_qualifiers(text)
        # "This doesn't work" → "This might not work"
        # "You need to X" → "You might want to X"
        transformations.append("Added qualifiers")
    
    # Level 3-4 decrease: Convert directives to suggestions
    if magnitude >= 3:
        text = directives_to_suggestions(text)
        # "Do X" → "Consider doing X"
        # "Fix Y" → "Perhaps we should address Y"
        transformations.append("Converted directives to suggestions")
    
    # Level 5+ decrease: Maximum diplomacy
    if magnitude >= 5:
        text = strong_to_soft(text)
        # "This doesn't work" → "This approach might not be ideal"
        # "That's wrong" → "There might be another perspective"
        transformations.append("Applied maximum diplomacy")
    
    return text, transformations
```

---

## PATTERN TRANSFORMATIONS

### Increasing Directness

| Original (Lower Intensity) | Transformed (Higher Intensity) |
|----------------------------|--------------------------------|
| Perhaps we should | We should |
| You might want to | You need to |
| This could be improved | This needs improvement |
| I think this approach | This approach |
| This might not work | This doesn't work |
| Consider using X | Use X |
| It would be better to | You must |
| This seems problematic | This is broken |

### Decreasing Directness

| Original (Higher Intensity) | Transformed (Lower Intensity) |
|-----------------------------|-------------------------------|
| This doesn't work | This might not be ideal |
| You must X | Perhaps you could consider X |
| Fix this | Perhaps we should address this |
| That's wrong | There might be another way to think about this |
| This is broken | This approach has some challenges |
| Use X | You might want to explore X |
| This needs fixing | This could be improved |
| Do Y immediately | Consider doing Y |

---

## ENVIRONMENT-SPECIFIC DEFAULTS

```yaml
dev:
  default_intensity: 7  # Direct technical communication
  range: 5-9
  
research:
  default_intensity: 5  # Diplomatic academic
  range: 4-7
  
career:
  default_intensity: 7  # Confident professional
  range: 6-8
  
work:
  default_intensity: 7  # Results-focused
  range: 6-9
  
personal:
  default_intensity: 6  # Varies widely by context
  range: 1-10  # Full range available
```

---

## VALIDATION

After calibration, verify:
1. **Actual intensity within ±1 of target** (some slippage acceptable)
2. **Core voice maintained** (authenticity preserved)
3. **Meaning unchanged** (only tone adjusted)
4. **Grammar correct** (transformations don't break language)

---

## IMPLEMENTATION NOTES

### Performance Targets
- Calibration time: <1 second for 500-word text
- Accuracy: ±1 intensity level

### Dependencies
```python
import re
from typing import List, Dict
```

### Testing
- Test on known intensity examples (1, 5, 10)
- Verify transformations preserve meaning
- Check grammar remains correct
- Validate intensity detection accuracy

---

## EXAMPLE USAGE

**Original (Detected Intensity: 5):**
```
The session manager tracks state. You should call auto_checkpoint every 5-10 tool calls.
```

**Calibrated to Intensity 3 (More Diplomatic):**
```
The session manager tracks state. You might want to consider calling auto_checkpoint 
every 5-10 tool calls, perhaps.
```

**Calibrated to Intensity 8 (More Direct):**
```
The session manager tracks state. Call auto_checkpoint every 5-10 tool calls.
```

---

## INTEGRATION

Called by:
- `tools/orchestrator.py generate --intensity 7`
- User request: "make this more direct" or "soften this"
- Context modulation guide (crisis, disagreement scenarios)

---

## FUTURE ENHANCEMENTS

- Learn user's preferred intensity by environment
- Situational intensity (intro vs closing different)
- Cultural calibration (Western vs Eastern communication styles)
- Relationship-based defaults (family softer, executives more direct)
