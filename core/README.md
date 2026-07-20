# CORE - Universal Voice Engine
Location: D:\Ghost Writer\core\

## PURPOSE

The universal voice engine that powers Ghost Writer across all environments. Contains the fundamental protocols, reference materials, and tool specifications that define how David's voice is captured, analyzed, and reproduced.

## SUBDIRECTORIES

### protocols\
Voice rules, workflows, and validation frameworks. These are the source of truth documents that define HOW Ghost Writer operates.

**Key Files:**
- `MASTER_PROTOCOL.md` - Central orchestrator (workflow, gates, decision trees)
- `voice-calibration-matrix.md` - Context-specific voice rules
- `application-workflow.md` - 3-gate validation system
- `validation-framework.md` - Quality control checklists
- `forbidden-patterns.md` - Anti-patterns reference
- `factual-corrections.md` - Error prevention database
- `context-modulation-guide.md` - Intensity/disagreement protocols
- `technical-communication-guide.md` - Teaching/documentation frameworks

### reference\
Authentic voice samples and working examples. The ground truth of what David's voice actually sounds like in different contexts.

**Key Files:**
- `AUTHENTIC_VOICE_REFERENCE.md` - Source truth examples
- `examples/` - 16+ working documents organized by type

### tools\
Specifications for voice analysis and generation tools. These define the NEW capabilities we're adding to Ghost Writer.

**Specifications (to be built):**
- `voice-confidence-scorer.md` - How to generate confidence scores
- `intensity-calibrator.md` - 1-10 intensity slider logic
- `variation-generator.md` - Creating 3 alternative versions
- `automated-checker.md` - Pattern validation automation

## DESIGN PRINCIPLES

1. **Environment-Agnostic** - Core protocols work across all contexts
2. **Evidence-Based** - All rules derived from actual voice samples
3. **Falsifiable** - Patterns must be testable and measurable
4. **Self-Correcting** - Learning from outputs improves core patterns

## RELATIONSHIP TO ENVIRONMENTS

Core provides the BASE voice engine. Environments provide CALIBRATION:

```
core/protocols/MASTER_PROTOCOL.md
  ↓ (universal rules)
environments/dev/calibration.yaml
  ↓ (technical adjustments)
Generated Output
```

## UPDATING CORE

Core files should update when:
- **New patterns discovered** across multiple environments (universal)
- **Fundamental workflows change** (e.g., new validation gate)
- **Base voice characteristics refined** (contraction rate, dash usage, etc.)

Core should NOT update for:
- Environment-specific adjustments (goes in environments/{env}/)
- One-off examples (goes in learning/samples/)
- Experimental approaches (test first)

## VERSION CONTROL

All core files are source of truth. Changes must be:
1. Tested across multiple environments
2. Documented with rationale
3. Backward compatible when possible
4. Reflected in MASTER_PROTOCOL.md
