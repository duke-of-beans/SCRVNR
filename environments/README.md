# ENVIRONMENTS - Context-Specific Calibrations
Location: D:\Ghost Writer\environments\

## PURPOSE

Context-specific voice calibrations for different work/communication environments. Each environment gets the core voice engine with adjustments for that context.

## ENVIRONMENTS

### dev/
Technical documentation and code-related writing.

**Characteristics:**
- More technical terminology
- Code examples expected
- Still conversational, not academic
- Contractions: 60-70% (slightly lower than personal)
- Audience: Developers, technical peers

**Use Cases:** README files, code comments, technical docs, architecture explanations

### research/
Academic and research communication.

**Characteristics:**
- More formal than dev
- Citations and references
- Evidence-based language
- Contractions: 40-60% (academic standards)
- Audience: Researchers, academics, peer reviewers

**Use Cases:** Papers, research notes, academic correspondence

### career/
Professional job application materials.

**Characteristics:**
- Professional but authentic
- Achievement-focused
- Metric-driven
- Contractions: 70-80% (authentic but polished)
- Audience: Recruiters, hiring managers, executives

**Use Cases:** Resumes, cover letters, LinkedIn about section, professional bios

### work/
Business communication and client work.

**Characteristics:**
- Professional with personality
- Results-focused
- Strategic framing
- Contractions: 70-80%
- Audience: Clients, business partners, investors

**Use Cases:** Business proposals, client emails, board updates, investor letters

### personal/
Social and family communication.

**Characteristics:**
- Maximum authenticity
- Warm but not saccharine
- Natural flow
- Contractions: 80-90% (as natural as spoken)
- Audience: Friends, family, social media followers

**Use Cases:** LinkedIn posts, personal emails, family communications, social media

## CALIBRATION FILES

Each environment contains:

### calibration.yaml
Environment-specific settings:
```yaml
environment:
  name: dev
  formality: 6  # 1-10 scale
  contraction_target: 0.65  # 65%
  dash_tolerance: 3  # per page
  technical_depth: high
  personality_integration: moderate
  
adjustments:
  # Relative to core protocols
  more_direct: true
  more_technical: true
  less_personal: true
  
forbidden_additions:
  # Environment-specific forbidden patterns
  - "as you can see"
  - "simply put"
  - "in other words"
  
required_patterns:
  # Must include in this environment
  - Code examples when explaining technical concepts
  - Specific references over general claims
```

### examples/
Curated examples specific to this environment. Shows how voice adjusts for context.

### README.md
Documents environment characteristics, when to use, and key differences from core.

## ENVIRONMENT DETECTION

Ghost Writer detects environment through:
1. **Explicit user statement** - "Write this in dev voice"
2. **Current directory** - D:\Career\ → career environment
3. **Project context** - Working in KERNL → dev environment
4. **Conversation keywords** - "cover letter" → career, "LinkedIn post" → personal
5. **User confirmation** - When ambiguous, ask

## CREATING NEW ENVIRONMENTS

To add a new environment:
1. Create `environments/{name}/` directory
2. Write `calibration.yaml` based on template
3. Add environment-specific examples
4. Update `GHOST_WRITER_INSTRUCTIONS.md` detection rules
5. Test across multiple scenarios

## ENVIRONMENT HIERARCHY

```
core/protocols/MASTER_PROTOCOL.md
  ↓ (universal base)
environments/{env}/calibration.yaml
  ↓ (environment adjustments)
Generated Output
```

Environment calibrations NEVER contradict core protocols. They only adjust parameters within acceptable ranges.

## CROSS-ENVIRONMENT LEARNING

Patterns discovered in one environment may inform others:
- **Personal → Work:** Authentic personality can enhance business communication
- **Career → Personal:** Professional polish can improve social posts
- **Dev → Research:** Technical precision improves academic clarity

The voice database (`learning/voice.db`) tracks which patterns work across multiple environments vs. are context-specific.
