# SCRVNR Session Loader — Voice-Aware Writing Protocol

## What This Is
SCRVNR is a voice intelligence system at D:\Projects\SCRVNR\. It has a centrifuge that scores text against measured voice profiles at 2.2ms, a forbidden pattern database, and a 42,363-message corpus for few-shot retrieval. Use it for any writing task that needs to not sound like AI.

## Bootstrap (run at session start)
1. Read D:\Projects\SCRVNR\CLAUDE_INSTRUCTIONS.md
2. Read D:\Projects\SCRVNR\core\protocols\forbidden-patterns.md
3. Read D:\Projects\SCRVNR\research\voice_fingerprint\voice_signature.md (for anti-slop baselines)

## Two Modes

### MODE A: David's Voice
Use when writing AS David (essays, LinkedIn, emails, investigative writing).
- Register options: TECH, CASUAL, PROFESSIONAL, MECHANICAL, INVESTIGATE, ACADEMIC, ARGUMENTATIVE, CREATIVE_DIRECTION, PERSONAL, FRUSTRATED
- Score command: `D:\Programs\Python312\python.exe D:\Projects\SCRVNR\tools\centrifuge_cli.py score {filepath} --register {REGISTER}`
- Threshold: >= 0.65 PASS, 0.50-0.65 review, < 0.50 rewrite
- Read the target register's calibration: D:\Projects\SCRVNR\environments\{register}\calibration.yaml

### MODE B: Anti-Slop (any brand voice)
Use when writing for a website, product, or brand that isn't David. The centrifuge's David-specific targets don't apply, but the anti-slop detection does.

**Before writing**: Define the voice target with the user. Ask:
- Who is this for? (brand/product/person)
- What register? (professional, casual, technical, editorial)
- What's the audience expertise level?
- Any existing copy to use as reference?

**After generating ANY copy, run this self-check protocol:**

1. **Em-dash sweep**: Search output for "—". Replace ALL with " - " (hyphens). Em-dashes are the #1 AI tell (Claude produces 26 per 1,000 words natively; humans produce < 1).

2. **Forbidden pattern scan**: Run `D:\Programs\Python312\python.exe D:\Projects\SCRVNR\tools\quality_gate.py {filepath} --env work`
   Even in non-David mode, the forbidden patterns catch universal AI slop: "seamless", "robust", "leverage", "utilize", "facilitate", "cutting-edge", "in today's world", "it's important to note", "at the end of the day", "dive into", "navigate", "landscape", "tapestry".

3. **Sentence uniformity check**: If all sentences are 15-25 words, the rhythm is flat (AI's signature). Break it up: some sentences should be 4-8 words, some 25-35. Alternate. Real writers have sentence length variety (std > 8, not the AI-typical std of 3-5).

4. **Specificity audit**: Count named entities (real companies, real products, real people, real places, specific numbers). If the copy uses vague references ("industry leaders", "innovative solutions", "comprehensive platform") instead of specific ones, it reads as AI filler. Replace with specifics.

5. **Rarity check** (optional, more rigorous): Save copy to a temp file, run centrifuge in any register — the rarity sub-score tells you if the vocabulary is too generic even without David-specific targeting:
   `D:\Programs\Python312\python.exe D:\Projects\SCRVNR\tools\centrifuge_cli.py score {filepath} --register PROFESSIONAL`
   Ignore the overall score (it's calibrated to David). Look at the rarity sub-score: if mean Zipf > 5.0, the vocabulary is too common. Push toward more specific, domain-appropriate language.

6. **Opening line test**: Read the first sentence of each section. If it's a throat-clearing generality ("In today's rapidly evolving digital landscape..."), delete it. Start with the actual point.

## How to Retrieve Corpus Examples (for David's voice)
When writing in David's voice and you want real examples of how he writes in a register:
```
D:\Programs\Python312\python.exe -c "
import json
register = 'TECH'  # change as needed
with open(r'D:\Projects\SCRVNR\research\voice_fingerprint\final_corpus.jsonl') as f:
    msgs = [json.loads(line) for line in f if json.loads(line).get('register') == register and len(json.loads(line).get('text','')) > 50]
import random; samples = random.sample(msgs, min(5, len(msgs)))
for s in samples: print(s['text'][:300]); print('---')
"
```

## Key File Locations
| File | Purpose |
|------|---------|
| D:\Projects\SCRVNR\tools\centrifuge_cli.py | Score text against voice profile |
| D:\Projects\SCRVNR\tools\quality_gate.py | 8-check quality validation |
| D:\Projects\SCRVNR\core\protocols\forbidden-patterns.md | Words/phrases that mark AI output |
| D:\Projects\SCRVNR\learning\voice.db | SQLite with all voice data |
| D:\Projects\SCRVNR\research\voice_fingerprint\voice_profile.json | Quantitative profile (11 registers) |
| D:\Projects\SCRVNR\research\voice_fingerprint\final_corpus.jsonl | 42,363 tagged messages for retrieval |
| D:\Projects\SCRVNR\environments\{register}\calibration.yaml | Per-register voice parameters |

## The Rule
Never present generated copy without running at least checks 1-4 above. If the centrifuge tools are available, run the full score. The goal isn't a number — it's that the output doesn't read like every other AI-generated page on the internet.
