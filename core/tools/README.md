# TOOLS - Voice Analysis & Generation Specifications
Location: D:\Ghost Writer\core\tools\

## PURPOSE

Specifications for NEW capabilities being added to Ghost Writer. These are the "enhanced tools" that improve voice synthesis beyond the current manual process.

## TOOL SPECIFICATIONS (To Be Created)

### voice-confidence-scorer.md
Generates confidence scores for voice authenticity.

**Outputs:**
```yaml
confidence: 0.85  # 0.0-1.0
breakdown:
  formality: 8/10 (target: 7/10)
  directness: 6/10 (target: 8/10)
  contractions: 12/15 present
  authenticity_markers:
    - Natural transitions
    - Specific examples
    - Minimal hedging
  concerns:
    - Slightly too formal for context
    - Could be more direct
```

**Status:** SPECIFICATION TO BE WRITTEN

### intensity-calibrator.md
1-10 intensity slider for calibrating directness/confrontation.

**Scale:**
```
1-3: Maximum diplomacy, soft language
4-6: Professional peer communication
7-9: Direct, no sugar-coating
10: Confrontational, tension expected
```

**Outputs:** Intensity-adjusted version of text

**Status:** SPECIFICATION TO BE WRITTEN

### variation-generator.md
Creates 2-3 alternative versions of text.

**Default Variations:**
- Version A: More direct
- Version B: More analytical/explanatory
- Version C: Balanced (between A and B)

**User picks or hybridizes**

**Status:** SPECIFICATION TO BE WRITTEN

### automated-checker.md
Runs automated pattern validation before delivery.

**Checks:**
- Contraction rate (target: 70-80%)
- Dash density (max: 3 per page)
- Forbidden patterns (0 instances)
- Rhetorical questions (0-1)
- Expert audience (no condescension)
- Third-person self-refs (0)

**Outputs:** Pass/Fail report with line numbers

**Status:** SPECIFICATION TO BE WRITTEN

## DESIGN PRINCIPLES

1. **Specifications First** - Write .md spec before building tool
2. **Tool-Agnostic** - Specs don't mandate Python vs other implementation
3. **Testable** - All tools must have clear pass/fail criteria
4. **Composable** - Tools can be chained together
5. **Fast** - Tools should run in <5 seconds

## IMPLEMENTATION PATH

```
Phase 1: Write specifications (.md files)
Phase 2: Build Python implementations (tools/ directory)
Phase 3: Test on reference examples
Phase 4: Integrate into MASTER_PROTOCOL.md workflow
Phase 5: Document in GHOST_WRITER_INSTRUCTIONS.md
```

## RELATIONSHIP TO PYTHON TOOLS

```
core/tools/           → Specifications (WHAT tool does)
tools/                → Implementations (HOW tool works)
learning/scripts/     → Database automation
```

All specifications in `core/tools/` define interfaces that implementations in `tools/` must satisfy.

## FUTURE TOOLS

Potential additions:
- **tone-detector.md** - Detects unintended tone shifts
- **context-suggester.md** - Recommends best context for query
- **voice-drift-detector.md** - Catches evolution away from baseline
- **example-retriever.md** - Finds most similar reference examples
- **pattern-explainer.md** - Explains why pattern was suggested
