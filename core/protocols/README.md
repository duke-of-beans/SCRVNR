# PROTOCOLS - Voice Rules & Workflows
Location: D:\Ghost Writer\core\protocols\

## PURPOSE

Source of truth documents that define HOW Ghost Writer operates. These are the authoritative specifications for voice synthesis, validation, and workflow execution.

## KEY FILES (Move existing files here)

### MASTER_PROTOCOL.md
Central orchestrator document. Defines:
- Initialization sequence
- Tool selection logic
- Voice calibration routing
- Validation gate system
- Skill utilization
- Error prevention
- Response construction
- Quality metrics targets

**Token Budget:** ~3-4K (comprehensive)  
**Status:** MOVE from D:\ghost writer\

### voice-calibration-matrix.md
Context-specific voice rules. Maps scenarios to voice parameters:
- Formality levels
- Directness scales
- Contraction usage
- Personality integration
- Intensity calibration

**Status:** MOVE from D:\ghost writer\01_VOICE_CALIBRATION_MATRIX.md

### application-workflow.md
3-gate validation system for applications:
- GATE 1: Load master data
- GATE 2: Generate documents
- GATE 3: Comprehensive validation

**Status:** MOVE from D:\ghost writer\02_APPLICATION_WORKFLOW.md

### validation-framework.md
Quality control checklists. Defines:
- Pre-delivery checks
- Voice authenticity scoring
- Pattern compliance
- Factual accuracy verification

**Status:** MOVE from D:\ghost writer\03_VALIDATION_FRAMEWORK.md

### forbidden-patterns.md
Anti-patterns reference. Lists:
- Prohibited phrases
- Corporate buzzwords
- Fabrication markers
- Tone violations
- Memory attribution issues

**Status:** MOVE from D:\ghost writer\04_FORBIDDEN_PATTERNS.md

### factual-corrections.md
Error prevention database. Documents:
- Historical corrections
- Metric clarifications
- Date/timeline fixes
- Attribution corrections

**Status:** MOVE from D:\ghost writer\05_FACTUAL_CORRECTIONS.md

### context-modulation-guide.md
Intensity/disagreement protocols. Handles:
- Crisis communication
- Disagreement/tension
- Multi-audience scenarios
- High-stakes situations

**Status:** MOVE from D:\ghost writer\06_CONTEXT_MODULATION_GUIDE.md

### technical-communication-guide.md
Teaching/documentation frameworks. Covers:
- Technical explanations
- System descriptions
- Teaching/mentoring voice
- Documentation standards

**Status:** MOVE from D:\ghost writer\07_TECHNICAL_COMMUNICATION_GUIDE.md

## FILE ORGANIZATION

All files use `.md` format with:
- Clear section headers
- YAML code blocks for structured data
- Examples throughout
- Cross-references to related files

## PROTOCOL VERSIONING

Protocols use semantic versioning in frontmatter:
```yaml
---
version: 1.2.0
last_updated: 2026-01-22
breaking_changes: false
---
```

## UPDATING PROTOCOLS

Changes require:
1. **Rationale** - Why is this changing?
2. **Evidence** - What voice samples support this?
3. **Testing** - Validated across environments?
4. **Documentation** - MASTER_PROTOCOL.md updated?
5. **Backward compatibility** - Will old outputs still validate?

## CROSS-REFERENCES

Protocols frequently reference:
- `core/reference/AUTHENTIC_VOICE_REFERENCE.md` (examples)
- `learning/voice.db` (pattern data)
- `environments/{env}/calibration.yaml` (context adjustments)
