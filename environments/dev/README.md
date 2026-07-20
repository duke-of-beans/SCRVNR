# DEV ENVIRONMENT - Technical Documentation Voice
Location: D:\Ghost Writer\environments\dev\

## CHARACTERISTICS

**Voice Profile:**
- Technical but conversational
- Code-aware (examples expected)
- Precise without being pedantic
- Still authentic David voice, just more technical

**Metrics:**
- Contraction rate: 60-70% (slightly lower than personal)
- Dash usage: 3 per page max
- Formality: 6/10
- Technical depth: High
- Personality integration: Moderate

**Audience:** Developers, technical peers, engineers

## USE CASES

- README files
- Code comments (when substantial)
- Technical documentation
- Architecture explanations
- API documentation
- Developer guides
- Technical blog posts
- Pull request descriptions

## CALIBRATION ADJUSTMENTS

**Relative to Core Protocols:**

### More Technical
- Use precise technical terminology
- Include code examples when explaining concepts
- Reference specific technologies/frameworks
- Quantify performance metrics

### Still Conversational
- Don't slip into academic/formal tone
- Keep contractions (but slightly less than personal)
- Use "you" not "one" or "the developer"
- Maintain authentic voice underneath technical content

### Pattern Additions
```yaml
encouraged_patterns:
  - Code examples for technical concepts
  - Specific metrics over vague claims
  - "Here's how it works:" transitions
  - Command examples with expected output
  
discouraged_patterns:
  - "Simply" or "just" (condescending to readers)
  - "Obviously" or "clearly" (assumes knowledge)
  - "As you can see" (patronizing)
  - Academic passive voice
```

## EXAMPLES

### Good (DEV Voice)
```
The session manager tracks state across Claude instances. When a crash happens, 
it's got everything needed to resume - current operation, file paths, decisions 
made, next steps. You call auto_checkpoint every 5-10 tool calls, and if things 
blow up, check_recovery loads the last checkpoint automatically.
```

**Why it works:**
- Technical precision ("auto_checkpoint", "5-10 tool calls")
- Contractions maintained ("it's got", "things blow up")
- Direct ("you call")
- Specific examples

### Avoid (Too Academic)
```
The session management system provides state persistence functionality across 
multiple Claude instances. In the event of an unplanned termination, the system 
maintains sufficient context to enable continuation of operations. One should 
invoke the checkpoint method at regular intervals to ensure state preservation.
```

**Problems:**
- No contractions (sounds like IEEE paper)
- Passive voice ("is provided", "should invoke")
- Too formal ("unplanned termination" vs "crash")
- "One should" instead of "you"

## FILES

### calibration.yaml
Environment-specific settings and adjustments

**Status:** TO BE CREATED (Phase 2)

### examples/
Curated technical documentation examples showing proper DEV voice

**Status:** TO BE POPULATED (Phase 4 - after file migration)

## CROSS-ENVIRONMENT NOTES

**DEV ↔ RESEARCH:**
- DEV is more conversational than RESEARCH
- DEV uses more contractions
- RESEARCH allows more passive voice (academic standards)

**DEV ↔ CAREER:**
- DEV has more technical depth
- CAREER balances technical with accessibility
- Both maintain high contraction rates

**DEV ↔ PERSONAL:**
- DEV slightly more formal
- Both highly authentic
- DEV includes code examples, PERSONAL doesn't
