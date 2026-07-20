# SCRVNR Generation Workflow — Phased Approach
## Why single-pass generation fails and what to do instead

No good writer works in one pass. SCRVNR shouldn't either.

Single-pass generation (load all context → write → done) produces text that's technically compliant but emotionally flat. The patterns compete for attention instead of flowing naturally. More context in a single prompt ≠ better writing. It often makes it worse.

The phased workflow separates concerns so each phase does one thing well.

---

## Phase 1 — ARCHITECT (conversation, not generation)

**Goal:** Thesis, structure, emotional arc, central metaphor.

**Questions to resolve:**
- What's the thesis in one sentence?
- What's the central metaphor? (David's essays use metaphors with multiple meanings that run through the whole piece. "The Setup" in Crazy In Tents = circus setup / it's a setup / you've been set up.)
- What's the scaling arc? (Individual → national → civilizational?)
- What's the bookend? (Same reference at open and close, meaning changed by the essay.)
- What's the emotional register sequence? (Confrontational → analytical → vulnerable → confrontational?)
- What register mix does this need? (Evidence-only or full narrative voice? Weaponizable content or safe content?)

**Output:** A paragraph describing the essay's architecture. Not a document. A conversation.

---

## Phase 2 — ARM (search, not generation)

**Goal:** Ammunition for every pressure point.

**For each major claim in the essay:**
1. What cultural moment EMBODIES this claim? (Cultural Stab search)
2. What's the absurdist reduction? (Scale to min/max)
3. What's the weaponized contrast? (Two facts side by side)
4. What data is the weapon? (Specificity anchors)
5. What's the opponent's own language we can reframe? (Opponent framework reuse)

**Validation:** Every callback candidate validated against the 7 Cultural Stab rules. One callback per source. Go wide.

**Output:** An ammunition list. Not prose. Just: "paragraph 7: Greece/Iceland contrast. Stab candidate: [phrase]. Absurdist reduction: [sentence]. Data weapon: [numbers]."

---

## Phase 3 — WIREFRAME (structure, not prose)

**Goal:** Paragraph-level skeleton with rhetorical device assignments.

**Each node has:**
- What it argues
- What data it uses
- What device is primary (from the 30 patterns)
- What the emotional register is
- Where the register shifts happen
- Where the callbacks land

**Example:**
```
P7: Greece vs Iceland natural experiment
  Argues: Austerity achieves the opposite of its stated purpose
  Data: GDP -26%, debt 130→180%, unemployment 28% vs recovery by 2015
  Device: Weaponized Contrast (#29) + Staccato Repetition (#13)
  Register: ANALYTICAL → CONFRONTATIONAL on punchline
  Stab: None here (save ammunition for later)
  Punchline: "The policy failed by every measure. Including its own."
```

**Output:** The wireframe doc. Still not prose.

---

## Phase 4 — DRAFT (voice, not devices)

**Goal:** Write with flow. ONE focus: the voice.

**Load:** voice_description.md (register-specific section), retrieved corpus examples. NOT the full rhetorical patterns reference. The voice should emerge from the examples, not from a checklist.

**Prioritize:**
- Long accumulating sentences that carry the reader
- Contractions at the register target rate
- Bimodal beat (short punches after long runs)
- Stream-of-consciousness flow — data woven into the current
- Hyphens, never em-dashes
- Dropped subjects where fragments work

**Do NOT prioritize:** Deploying specific named patterns. If they emerge naturally, great. If they don't, Phase 5 handles it.

**Output:** A raw draft. It should flow. It doesn't need to stab yet.

---

## Phase 5 — WEAPONS PASS (editorial, not generative)

**Goal:** Surgically embed the ammunition from Phase 2.

**Operations:**
- Insert Cultural Stabs at the positions identified in the wireframe
- Sharpen Weaponized Contrasts — are the two facts DIRECTLY adjacent?
- Check for Absurdist Reductions — did any natural ones emerge in the draft? Add planned ones?
- Deploy Word-Swap Pivots at transition points
- Verify Register Shifts are clean — formal setup, casual punchline
- Check Lowbrow Cultural Callbacks — any historical references that could be downgraded?
- Verify punchlines are SHORT. Long punchlines aren't punchlines.

**This pass is surgical.** Don't rewrite flowing prose. Add edge to it.

**Output:** A draft with teeth.

---

## Phase 6 — MECHANICAL (autocorrect module, <10ms)

**Goal:** Fix every mechanical voice violation.

**Operations (automated):**
- Em-dash → hyphen
- Smart quotes → straight quotes
- Forbidden word removal
- Contraction rate check against register target
- Promoted substitution application

**Output:** Clean text. Run `autocorrect.correct(text, register)`.

---

## Phase 7 — SCORE (centrifuge, <3ms)

**Goal:** Quantitative voice fidelity check.

**Operations:**
- Centrifuge scoring (rarity + rhythm + style)
- Confidence banding (HIGH/GOOD/MARGINAL/LOW)
- Diagnostic: which dimensions are off-target?

**Output:** Score + diagnosis. If MARGINAL or LOW, the diagnosis tells you which phase to revisit.

---

## When to skip phases

**Short-form (LinkedIn reply, email):** Phases 1-3 collapse into a moment of thought. Phase 4 is the writing. Phase 5 might add one callback. Phases 6-7 are automatic.

**Medium-form (LinkedIn article, blog post):** Phase 1 is a quick conversation. Phase 2 is a quick search. Phase 3 is optional. Phases 4-7 are full.

**Long-form (essay, manifesto):** All seven phases, in order, no skipping.

---

## What this replaces

The old approach: dump voice_description.md + retrieved examples + register targets into a single system prompt, generate the full text, run autocorrect, score. That's Phase 4 alone. It misses the architecture, the ammunition, the surgical weapons pass, and the iterative quality check.

The new approach is slower. It should be. Writing that stabs takes longer than writing that informs.
