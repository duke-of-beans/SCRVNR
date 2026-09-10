# SCRVNR Multi-Tenant Architecture — Design v1.0.0

## §0 — What This Is

SCRVNR is becoming a multi-tenant voice synthesis platform. Voices are tenants. Each tenant is a fully independent voice profile — not a register of one person, but a distinct character with its own corpus, fingerprint, registers, and enforcement thresholds.

Nothing in the architecture ties it to any specific person. The current David Kirsch voice data is tenant data, not architecture. The platform must be generalizable to any voice — a brand bot, a company's editorial tone, a fictional character, an institutional register.

This is the Dream → Design phase per the portfolio blueprint standard. Recon is complete (VFP-04 shipped, SCRVNR codebase inspected, multi-register profiles exist but single-tenant). Code quality gut-check and enforcement spec follow.

## §1 — Tenant Model

```
TENANT (voice)
├── id: string (ulid)
├── name: string ("gravee-bot", "david-kirsch", "asuriq-verifier")
├── description: string
├── created_at: timestamp
├── owner_id: string (for future multi-user; nullable for now)
│
├── REGISTERS[]
│   ├── id: string
│   ├── name: string ("feed", "reply", "disarmament", "technical", "personal")
│   ├── description: string
│   ├── fingerprint: VoiceFingerprint
│   └── enforcement_threshold: float (0.0-1.0, how tightly to match)
│
├── CORPUS[]
│   ├── id: string
│   ├── register_id: string (which register this sample belongs to)
│   ├── source_type: "original" | "correction" | "approved" | "rejected"
│   ├── content: string
│   ├── metadata: json (session_id, timestamp, correction_pair_id)
│   └── created_at: timestamp
│
├── DELTA_PAIRS[]
│   ├── id: string
│   ├── register_id: string
│   ├── drafted: string (the AI-generated version)
│   ├── corrected: string (the human correction)
│   ├── pattern_label: string ("reassurance-seeking→cut", "theatrical→flat")
│   ├── extracted_rules: json (measurable pattern deltas)
│   └── created_at: timestamp
│
├── ANTI_PATTERNS[]
│   ├── id: string
│   ├── pattern: string (regex or semantic description)
│   ├── category: "structural" | "content" | "tone"
│   ├── example_violation: string
│   ├── example_correct: string
│   └── severity: "hard_reject" | "flag" | "suggest"
│
└── VOICE_BIBLE: markdown (human-readable voice spec, generated from above)
```

## §2 — VoiceFingerprint Schema

Each register has a quantitative fingerprint — measurable targets extracted from the corpus. These are the VFP-04 metrics generalized:

```
VoiceFingerprint
├── sentence_length: { mean: float, std: float, max: int }
├── zipf_distribution: { mean: float, target_range: [float, float] }
├── vocabulary_rarity: { target_mean_zipf: float, rare_word_rate: float }
├── em_dash_rate: float (per 1000 words)
├── question_rate: float (per 1000 words; gravee-bot: near zero)
├── exclamation_rate: float
├── rhetorical_question_rate: float (gravee-bot: hard zero)
├── passive_voice_rate: float
├── contraction_rate: float
├── first_person_rate: float ("I" vs "we" vs neither)
├── hedge_word_rate: float ("might", "perhaps", "possibly")
├── qualifier_rate: float ("very", "really", "quite")
│
├── structural_patterns: {
│   declarative_ratio: float,     (% of sentences that are flat declarations)
│   imperative_ratio: float,
│   interrogative_ratio: float,
│   compound_sentence_ratio: float,
│   fragment_ratio: float         (intentional sentence fragments)
│ }
│
├── vocabulary_constraints: {
│   banned_words: string[],       (from anti-patterns)
│   preferred_words: string[],    (observed high-frequency words)
│   domain_vocabulary: string[]   (industry-specific terms)
│ }
│
├── rhythm_targets: {
│   short_sentence_clusters: float,  (rate of 2+ consecutive short sentences)
│   paragraph_length_mean: float,
│   list_avoidance: boolean          (gravee-bot: true)
│ }
│
└── custom_metrics: json           (tenant-defined measures)
```

## §3 — The Feedback Loop Pipeline

This is the core product capability — the mechanism by which a voice gets better over time. Same pipeline for every tenant.

```
INTAKE
  ├── Direct corpus upload (bulk text samples tagged by register)
  ├── ROSETTA conversation ingest (ambient capture from chat sessions)
  ├── Delta pair submission (AI draft + human correction + pattern label)
  └── Anti-pattern registration (violation examples + correct alternatives)
          │
          ▼
EXTRACTION
  ├── Tokenize and measure all VoiceFingerprint dimensions
  ├── For delta pairs: compute the DELTA between drafted and corrected
  │   (what measurably changed — sentence length, vocabulary, structure)
  ├── Identify recurring delta patterns (cluster similar corrections)
  ├── Extract anti-pattern signatures from rejected content
  └── Build/update register-specific fingerprint from approved + original content
          │
          ▼
PROFILE
  ├── Merge new measurements into existing fingerprint (weighted by recency)
  ├── Update enforcement thresholds based on correction frequency
  │   (more corrections → tighter threshold until voice stabilizes)
  ├── Generate/refresh voice_bible.md from structured data
  └── Version the profile (every update is a new version, rollback possible)
          │
          ▼
ENFORCEMENT
  ├── Score new generated content against the fingerprint
  │   ├── Per-dimension score (0.0-1.0 match)
  │   ├── Anti-pattern scan (hard reject on violation)
  │   ├── Composite match score (weighted by dimension importance)
  │   └── Pass/fail against enforcement threshold
  ├── Return: { score, violations[], suggestions[], pass: boolean }
  └── Optional: auto-correct mode (rewrite violations, re-score)
          │
          ▼
ITERATE
  ├── Corrections to enforced content become new delta pairs
  ├── Profile auto-updates (or manual trigger)
  └── Voice bible regenerated on each profile version
```

## §4 — Storage Architecture

Two options considered:

**Option A: SQLite per tenant (voice.db pattern)**
Each tenant gets their own SQLite file. Portable, self-contained, works offline. The VFP-04 pattern extended. Good for the internal use case.

**Option B: Supabase multi-tenant (product pattern)**
Single database, tenant isolation via RLS. Scales to many tenants. API-ready. Good for productization.

**Decision: Build for B, start with A.** The schema targets Supabase (portfolio.scrvnr_* tables) but the extraction pipeline operates on SQLite files that can be synced. This matches PLEXUS's pattern — local SQLite for dev/personal, Supabase for production/multi-user.

```sql
-- Tenant registry
create table portfolio.scrvnr_tenants (
  id text primary key,
  name text not null,
  description text,
  owner_id text,
  created_at timestamptz default now()
);

-- Registers per tenant
create table portfolio.scrvnr_registers (
  id text primary key,
  tenant_id text references portfolio.scrvnr_tenants(id),
  name text not null,
  description text,
  fingerprint jsonb,
  enforcement_threshold float default 0.7,
  version int default 1,
  created_at timestamptz default now()
);

-- Corpus samples
create table portfolio.scrvnr_corpus (
  id text primary key,
  tenant_id text references portfolio.scrvnr_tenants(id),
  register_id text references portfolio.scrvnr_registers(id),
  source_type text check (source_type in ('original','correction','approved','rejected')),
  content text not null,
  metadata jsonb,
  created_at timestamptz default now()
);

-- Delta pairs (corrections)
create table portfolio.scrvnr_delta_pairs (
  id text primary key,
  tenant_id text references portfolio.scrvnr_tenants(id),
  register_id text references portfolio.scrvnr_registers(id),
  drafted text not null,
  corrected text not null,
  pattern_label text,
  extracted_rules jsonb,
  created_at timestamptz default now()
);

-- Anti-patterns
create table portfolio.scrvnr_anti_patterns (
  id text primary key,
  tenant_id text references portfolio.scrvnr_tenants(id),
  pattern text not null,
  category text check (category in ('structural','content','tone')),
  example_violation text,
  example_correct text,
  severity text check (severity in ('hard_reject','flag','suggest')),
  created_at timestamptz default now()
);
```

## §5 — API Surface

SCRVNR exposes these operations for any consumer (CORTEX adapter, composition layer, external API):

```
POST /v1/tenants                    — create a voice tenant
GET  /v1/tenants/:id                — get tenant + registers
POST /v1/tenants/:id/corpus         — ingest corpus samples
POST /v1/tenants/:id/deltas         — submit delta pairs
POST /v1/tenants/:id/anti-patterns  — register anti-patterns

POST /v1/tenants/:id/extract        — trigger fingerprint extraction
GET  /v1/tenants/:id/fingerprint    — get current fingerprint per register

POST /v1/score                      — score content against a tenant/register
  body: { tenant_id, register_id, content }
  returns: { score, violations[], suggestions[], pass }

POST /v1/generate                   — generate content in a voice (future)
  body: { tenant_id, register_id, prompt, constraints }
  returns: { content, score, enforcement_applied }

GET  /v1/tenants/:id/bible          — get human-readable voice bible
```

## §6 — Integration with CORTEX

SCRVNR's CORTEX adapter (cortex/src/adapters/scrvnr.ts) currently proxies observations. Extended:

1. **Recall path** (existing, enhanced): when Greg or any surface asks about a voice, the adapter returns the fingerprint and voice bible for the requested tenant.

2. **Scoring path** (new): any articulation pipeline can POST generated content to SCRVNR for scoring before emission. The cognitive gate already exists — SCRVNR scoring becomes another gate dimension.

3. **Ingest path** (new): ROSETTA conversations can be tagged with a tenant_id. When a ROSETTA message is ingested and the session involves voice corrections for a specific tenant, the delta pairs are automatically extracted and fed to SCRVNR.

## §7 — Productization Path

When SCRVNR becomes its own product:

- **Tenant = customer.** Each customer creates voice tenants.
- **The feedback loop IS the product.** Upload samples, make corrections, get a tighter voice over time.
- **API-first.** The /v1/score endpoint is the billable surface — content in, score out.
- **Voice bible generation** is a deliverable — customers get a human-readable spec of their voice.
- **No lock-in.** Voice profiles are exportable as JSON. The fingerprint is data, not a secret.
- **PLEXUS integration.** SCRVNR can use PLEXUS linguistic adapters (datamuse, thesaurus, wiktionary) for real-time vocabulary calibration during scoring and generation.

## §8 — Build Order

1. Schema: create Supabase tables (portfolio.scrvnr_*)
2. Ingest: tenant creation + corpus upload + delta pair submission
3. Extract: fingerprint extraction pipeline (port VFP-04 metrics to multi-tenant)
4. Score: content scoring against fingerprint
5. Bible: voice bible generation from structured data
6. CORTEX: extend adapter for scoring and ingest paths
7. ROSETTA: auto-extract delta pairs from tagged conversations
8. API: expose HTTP endpoints on Sentinel
9. Product: auth, multi-user, billing (future)

## §9 — First Tenant: gravee-bot

The voice bible at `duke-of-beans/gravee/VOICE_BIBLE.md` defines the first tenant. Seeding:

- **Corpus:** David's original lines from the 2026-09-10 session (source_type: "original")
- **Delta pairs:** 5 correction pairs from the session (see VOICE_BIBLE.md §8)
- **Anti-patterns:** 18 anti-patterns across structural/content/tone categories
- **Registers:** feed, reply, disarmament — each with distinct fingerprint targets
- **Enforcement threshold:** 0.8 (tight — this voice has a very specific frequency)
