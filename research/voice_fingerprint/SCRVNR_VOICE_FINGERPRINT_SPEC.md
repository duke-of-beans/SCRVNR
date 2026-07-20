# SCRVNR Voice Fingerprint Research Spec
## Project: Quantitative Voice Profile Extraction Pipeline
### Version: 1.0.0 | Date: 2026-07-15 | Author: Claude (specced with David)

---

## §0 — Premise

StoryScope (UMD + Google DeepMind, arXiv:2604.03136, April 2026) proved that AI-generated writing is structurally distinguishable from human writing with 93.2% accuracy using narrative features alone. The key finding for SCRVNR: human vocabulary occupies a "kite shape" in rarity space (mean percentile 0.71), while AI vocabulary clusters symmetrically at the median (0.49, Cohen's d = 0.83). This is an inevitable consequence of next-token prediction optimizing toward the statistical center of all training data.

SCRVNR currently operates on qualitative rules (forbidden word lists, environment-scoped calibration YAMLs, pattern confidence scores). This project replaces that with a quantitative voice fingerprint: David's measured rarity distribution, sentence rhythm, specificity rate, and register-switching behavior, extracted from his actual writing across every available corpus.

The output is not a classifier. It is a centrifuge — a generation-time constraint that pushes Claude's output away from the 0.5 median and toward David's measured kite shape for the active register.

---

## §1 — Authorship Model (Critical Correction)

Not all text attributed to David is David's voice. The corpus must be weighted by actual authorship:

### Pure David (primary corpus, full weight)
| Source | Location | Format | Est. Volume |
|--------|----------|--------|-------------|
| Claude chat — Human: turns | `D:\Meta\claude_export\b0\conversations.json` (497MB) + `b1\conversations.json` (1.34GB) | JSON array, `chat_messages[].sender == "human"` | ~500K+ messages |
| Claude chat — gap fill | conversation_search / recent_chats API (June 18 – present) | API retrieval | ~20 sessions |
| GPT chat — user turns | `D:\Personal\GPT Data\conversations-000.json` through `-016.json` (~187MB total) | JSON tree, `mapping[].message.author.role == "user"`, text in `content.parts[]` | ~50K+ messages |
| Outlook — sent mail | Oktyv browser automation (Brave, logged in) | Browser scrape/export | Variable |
| SMS messages | `D:\OneDrive\Downloads\sms-20260508124842.xml` + `parse_sms.py` | XML parse (parser exists) | Full SMS history |
| LinkedIn comments | Conversation history references (Eemaan Khan thread, others) | Extracted from chat context | ~20 samples |
| AIS Profile Master docs | `D:\Application Intelligence System\Profile_Master\` | .md, .docx, .txt | 40 files |
| AIS Master Data | `D:\Application Intelligence System\Master_Data\` | .md | 15 files |
| Career Voice & Writing | `D:\Career\Voice-and-Writing\` | .md | 20 files |
| Throwbak records | `D:\Projects\Throwbak\record\` | .yaml | 150+ files |

### Hybrid (Claude prose + David architecture/rarity spikes, 0.3 weight for prose, 1.0 for structural choices)
| Source | Location | Notes |
|--------|----------|-------|
| Published essays | `D:\Projects\davidkirsch-me\writing\` | 7+ essays, 18K+ words. Extract: sardonic beats, metaphor choices, structural moves, specific references. Discard: connective prose. |
| SCRVNR samples | `D:\Projects\SCRVNR\learning\samples\` | 5 environment dirs. Some may be David-authored, some Claude-generated. Tag individually. |

### Not David (exclude from voice corpus)
| Source | Reason |
|--------|--------|
| Git commit messages | Written by Claude via smart_commit |
| CLAUDE_INSTRUCTIONS.md files | Written by Claude, directed by David |
| BACKLOG.md files | Written by Claude, directed by David |
| Research papers | ~95% Claude in academic register |

---

## §2 — Register Taxonomy

Every corpus sample gets tagged with a register. The initial taxonomy below is a seed — the pipeline should discover additional registers dynamically from clustering in feature space. If a cluster of messages shares a feature profile distinct from all existing registers, it becomes a new register. The system grows with the data, not from pre-definition:

| Register ID | Description | Primary Sources | Expected Traits |
|-------------|-------------|-----------------|-----------------|
| `TECH` | Technical direction, architecture, debugging | Claude/GPT chat (working sessions) | Compressed, imperative, specific file paths and tool names |
| `INVESTIGATE` | Research direction, evidence evaluation, 9/11/Epstein/Crisis Cap | Claude chat (Tranche sessions), LinkedIn threads | Cold precision, evidence-first, primary-source anchored |
| `PERSONAL` | Relationships, emotions, vulnerability, self-reflection | Claude/GPT chat (personal), text messages, Throwbak | Raw, fragments, self-aware humor, double periods |
| `CASUAL` | Cooking, music, cars, low-stakes Q&A | Claude/GPT chat, text messages | Shortest messages, most typos, most contractions |
| `PROFESSIONAL` | Emails to clients/colleagues, Upwork, outreach | Gmail, AIS Profile Master docs | Warm but credible, specific, no filler |
| `ARGUMENTATIVE` | LinkedIn debates, pushback, intellectual combat | LinkedIn comments, Claude chat corrections | Structured claims, evidence exhibits, sardonic compression |
| `CREATIVE_DIRECTION` | Essay architecture, voice correction, editorial choices | Claude chat (essay sessions) | Meta-commentary on writing, "no, say it this way" |
| `MECHANICAL` | Volvo, hardware, physical systems | Claude/GPT chat (Volvo sessions) | First-principles reasoning, sensory observation, hands-dirty vocabulary |
| `FRUSTRATED` | Correction, pushback, "the fuck is going on??" | Claude/GPT chat (when things break) | Profanity spike, extreme compression, interrogative |

---

## §3 — Feature Extraction (StoryScope-Aligned + David-Specific)

### 3A — StoryScope Features That Transfer to Conversational Prose

These are the 30 core features from StoryScope, filtered to those measurable in short-form and conversational writing:

| Feature | StoryScope ID | Measurement Method |
|---------|---------------|-------------------|
| Vocabulary rarity distribution | Rarity percentile (k=25 NN) | `wordfreq.zipf_frequency(word, 'en')` per token. Words with Zipf < 3.0 are "rare" (< 1 per million). Compute per-message rarity as mean Zipf of all content words (excluding stopwords). Aggregate per-register. Build the kite shape. The multi-source fusion (SUBTLEX + Books + Reddit + Twitter + Wikipedia + OpenSubtitles + Leeds) means "rare" reflects genuine idiosyncrasy, not register mismatch. |
| Specificity rate | Intertextual Strategy → explicit named reference | Ratio of named entities (brands, people, places, specific texts) to vague references ("someone," "a company," "studies show"). |
| Theme explicitness | Thematic Explicitness and Moralizing | Does David state conclusions or let implications land? (Measured in argumentative and creative direction registers.) |
| Temporal complexity | Degree of Chronological Discontinuity | Frequency of time jumps, flashbacks, non-linear references in narrative passages. |
| Bodily metaphor rate | Dominant Emotional Expression → embodied | How often does David use physical sensation to describe emotion vs. naming the emotion directly? |
| Resolution pattern | Mode of Resolution | Does David leave things unresolved, ambiguous, or tied up? |
| Dialogue ratio | Dialogue-to-Narration Proportion | In essay/argument contexts, how much does David quote vs. narrate? |
| Moral ambiguity | Moral Polarity Toward Protagonist | Does David present situations as clear-cut or complex? |

### 3B — David-Specific Features (Not in StoryScope)

| Feature | Description | Measurement |
|---------|-------------|-------------|
| Sentence length distribution | Not average — the SHAPE. Bimodal? How wide is the spread? | Compute length histogram per register. Expect bimodal: ultra-short directives + longer analytical observations. |
| Contraction rate by register | How contracted is the prose? | `n't`/`'re`/`'ll`/`'ve` per 100 words, segmented by register. |
| Typo/abbreviation rate | How much does David self-correct vs. leave typos? | Ratio of non-dictionary words to total words, excluding technical terms. Higher = more informal register. |
| Caps-as-emphasis rate | "IS lexical erosion" — caps for definitional force | Instances of single ALL-CAPS words mid-sentence per 1000 words. |
| Question density | How often does David pose questions? | Questions per message, segmented by register. |
| Profanity density by register | Surgical emphasis vs. never | Profanity tokens per 1000 words, by register. |
| Domain-crossing vocabulary | "A very convincing retraction" — importing terminology across contexts | Requires semantic analysis: words from one domain appearing in the context of another. Most complex feature. Flag candidates, human-verify. |
| Sardonic compression | Compressed irony, deadpan modifiers, weaponized professional vocab | Instance count per corpus segment. Requires pattern matching against known examples (SCRVNR samples). |
| Correction style | States right answer vs. explains wrong answer | In FRUSTRATED and CREATIVE_DIRECTION registers: ratio of "it's X" to "that's wrong because Y." |
| Metaphor sourcing domains | Where does David draw metaphors from? | Tag each metaphor by source domain: mechanical, financial, architectural, culinary, natural, musical, etc. Build distribution. |
| Staccato repetition | Rhythmic device: "The documentation exists. The FEC filings exist. The mortality data exists." | Consecutive sentences with identical syntactic structure, per 1000 words. |
| Double-period usage | ".." as deliberate pause | Instances per 1000 words, by register. |
| Hyphens vs. em-dashes | David uses hyphens, NEVER em-dashes | Confirm: em-dash count should be ~0 in pure-David corpus. Hyphens per 1000 words. |

---

## §4 — Pipeline Architecture

### Phase 1: Corpus Assembly

**Script: `extract_corpus.py`**

1. Parse Claude JSON export (`b0/conversations.json`, `b1/conversations.json`)
   - Extract all messages where `sender == "human"`
   - Preserve: text, timestamp, conversation title, conversation ID
   - Stream-parse (ijson or similar) — files are 497MB and 1.34GB

2. Parse GPT JSON export (`conversations-000.json` through `-016.json`)
   - Walk the tree structure: for each conversation, traverse `mapping` nodes following `children` pointers
   - Extract messages where `message.author.role == "user"`
   - Text lives in `message.content.parts[]` — join parts
   - Preserve: text, timestamp (Unix float → ISO), conversation title

3. Parse AIS/Career/Throwbak docs
   - Read all `.md`, `.txt`, `.yaml`, `.docx` files from the 4 directories
   - Tag each file with source directory as initial register hint

4. Gap-fill: Export recent Claude chats (June 18 – July 15, 2026) from conversation_search/recent_chats API, extract Human: turns

**Output: `corpus_manifest.json`**
```json
{
  "total_messages": N,
  "total_words": N,
  "by_source": {
    "claude_chat": { "messages": N, "words": N },
    "gpt_chat": { "messages": N, "words": N },
    "ais_docs": { "files": N, "words": N },
    "throwbak": { "files": N, "words": N }
  },
  "by_register": {
    "TECH": { "messages": N, "words": N },
    "PERSONAL": { "messages": N, "words": N },
    ...
  }
}
```

### Phase 2: Register Tagging

**Script: `tag_registers.py`**

Auto-tag each message/document with a register using a lightweight classifier:

1. Conversation title keywords → register mapping (e.g., "Volvo" → MECHANICAL, "Tranche" → INVESTIGATE/TECH)
2. Content heuristics: profanity density → FRUSTRATED, question marks + "what do you think" → ARGUMENTATIVE
3. Message length: < 10 words → likely CASUAL or FRUSTRATED
4. Fall back to `UNTAGGED` — manual review for ambiguous cases
5. For multi-register conversations, tag per-message where register shifts are detectable

**Output: `tagged_corpus.jsonl`** — one JSON object per message with `text`, `register`, `source`, `timestamp`, `conversation_id`, `word_count`

### Phase 3: Feature Extraction

**Script: `extract_features.py`**

For each message in the tagged corpus, compute:

1. **Word-level**: token count, unique token count, vocabulary richness (type-token ratio), mean word length, rarity score per word (against COCA frequency list)
2. **Sentence-level**: sentence count, sentence length distribution (min, max, mean, median, std, skewness, kurtosis), question count
3. **Character-level**: contraction count, caps-emphasis count, profanity count, double-period count, hyphen count, em-dash count, typo/non-dictionary-word count
4. **Specificity**: named entity count (spaCy NER), vague reference count (regex: "someone," "a company," "studies show," "experts say," "some people")
5. **Register-specific**: only compute domain-crossing vocabulary for ARGUMENTATIVE and CREATIVE_DIRECTION; only compute sardonic compression for INVESTIGATE and ARGUMENTATIVE

**Output: `features.jsonl`** — one JSON object per message with all computed features alongside the tagged metadata

### Phase 4: Profile Generation

**Script: `build_profile.py`**

Aggregate features into per-register profiles:

1. **Vocabulary rarity distribution**: For each register, compute the histogram of word-rarity percentiles. This IS the kite shape. Compare against Claude's baseline (generate ~1000 messages in each register using current SCRVNR calibration, compute the same histogram).

2. **Sentence rhythm signature**: Per-register sentence length distribution. Render as histogram. Identify bimodality.

3. **Feature summary statistics**: For each feature × register, compute mean, median, std, p5, p25, p75, p95. These become the target ranges for SCRVNR generation.

4. **Delta analysis for hybrid samples**: For essays, compare David's insertions/corrections (extracted from conversation history of essay sessions) against the surrounding Claude prose. Compute feature deltas to isolate David's voice contribution.

**Output: `voice_profile.json`**
```json
{
  "registers": {
    "TECH": {
      "vocabulary_rarity_distribution": { "histogram": [...], "mean_percentile": 0.XX, "kite_skew": X.X },
      "sentence_length": { "mean": X, "std": X, "bimodality_coefficient": X },
      "contraction_rate": X.X,
      "caps_emphasis_rate": X.X,
      "question_density": X.X,
      "profanity_density": X.X,
      "specificity_rate": X.X,
      "typo_rate": X.X,
      ...
    },
    ...
  },
  "global": {
    "metaphor_domains": { "mechanical": X, "financial": X, "architectural": X, ... },
    "forbidden_words_confirmed": ["seamless", "robust", "leverage", ...],
    "signature_moves": {
      "sardonic_compression": { "count": N, "examples": [...] },
      "domain_crossing": { "count": N, "examples": [...] },
      "staccato_repetition": { "count": N, "examples": [...] }
    }
  }
}
```

### Phase 5: SCRVNR Integration

**Deliverable: Updated voice.db schema + rarity calibration layer**

1. Extend voice.db with new tables:
   - `register_profiles` — one row per register, storing the full feature profile
   - `rarity_targets` — per-register vocabulary rarity distribution targets
   - `rhythm_targets` — per-register sentence length distribution targets
   - `feature_ranges` — per-register acceptable ranges for each extracted feature

2. Build rarity calibration function:
   - Input: generated text + target register
   - Output: rarity score (how well does this text match David's measured distribution?)
   - The centrifuge: flag words/sentences that fall too close to the 0.5 median and suggest alternatives from David's measured high-rarity vocabulary

3. Update SCRVNR generation pipeline:
   - After generating text, run rarity calibration
   - If rarity score < threshold, re-generate with constraints weighted toward David's measured preferences
   - Quality gate: existing 7-check system + new rarity check

---

## §5 — Technical Requirements

- **Python 3.12** (David's installed version, `D:\Programs\Python312\python.exe`)
- **Dependencies**: ijson (stream JSON parsing), spacy + en_core_web_lg (NER), nltk (tokenization, frequency), pandas (aggregation), matplotlib (visualization), scipy (distribution analysis)
- **Reference corpus**: `wordfreq` Python library (pip install wordfreq, MIT license, free, offline). Already fuses 7 independent sources for English: SUBTLEX-US (TV subtitles / casual speech), OpenSubtitles (movies/TV), Google Books (formal/literary), Wikipedia (encyclopedic), Twitter (social/ultra-casual), Leeds Internet Corpus (web crawl), and Reddit (conversational/argumentative). Uses weighted median across all sources so no single register dominates. Covers words down to 1-per-100-million frequency in 'large' wordlist. API: `word_frequency(word, 'en')` returns 0-1 decimal; `zipf_frequency(word, 'en')` returns Zipf scale (6 = top-1000, 3 = one-per-million, 1 = one-per-100M). This IS the multi-corpus hybrid — no need to pick one source or download anything separately.
- **Compute**: All local. No API calls for feature extraction. LLM calls only for register tagging of ambiguous cases and domain-crossing vocabulary detection.
- **Storage**: Working directory `D:\Projects\SCRVNR\research\voice_fingerprint\`
- **Output**: All artifacts stored alongside voice.db in SCRVNR project

---

## §6 — Success Criteria

1. **Corpus coverage**: At minimum 10,000 David-authored messages extracted and register-tagged across at least 6 registers
2. **Kite shape measurable**: David's vocabulary rarity distribution is statistically distinct from Claude's baseline (p < 0.01 on KS test)
3. **Register differentiation**: At least 3 features show statistically significant differences across David's registers (confirming SCRVNR's multi-environment model is justified)
4. **Rarity calibration functional**: Given a block of Claude-generated text in David's voice, the calibration function can score how well it matches David's measured profile and identify specific divergences
5. **Integration shipped**: voice.db schema extended, rarity targets populated, generation pipeline updated

---

## §7 — Execution Plan

| Phase | Deliverable | Estimated Effort | Dependencies |
|-------|-------------|-----------------|--------------|
| 1: Corpus Assembly | `corpus_manifest.json`, raw extracted corpus | 1 Cowork sprint | File access to all source directories |
| 2: Register Tagging | `tagged_corpus.jsonl` | 1 Cowork sprint (can parallel with Phase 1 for non-chat sources) | Phase 1 output |
| 3: Feature Extraction | `features.jsonl` | 1 Cowork sprint | Phase 2 output, spaCy model, COCA frequency list |
| 4: Profile Generation | `voice_profile.json`, visualization charts | 1 session with David (review + iterate) | Phase 3 output |
| 5: SCRVNR Integration | Updated voice.db, rarity calibration layer | 1 Cowork sprint | Phase 4 approved profile |

Total: ~4 sprint-equivalents + 1 review session

---

## §8 — Resolved Questions

1. **Email**: Outlook, not Gmail. David is logged into Outlook in Brave. Access via Oktyv browser automation. ✅
2. **Text messages**: Full SMS export at `D:\OneDrive\Downloads\sms-20260508124842.xml` with existing parser `parse_sms.py`. ✅
3. **Reference corpus**: COCA via WordFrequency.info. Reasoning: Ngrams skews literary; COCA covers spoken + written American English across registers. ✅
4. **Register boundaries**: Seed taxonomy is starting point. Pipeline discovers new registers dynamically via feature-space clustering. System grows with data. ✅
5. **Hybrid essays — included**: "Crazy In Tents," "What Lies Beneath," "Through the Overton Glass," "By Any Means," "A Beautiful Mosaic." **Excluded**: "The Natural Order of Intelligence," "Shadows on the Wall" (too heavily Claude-authored). ✅
