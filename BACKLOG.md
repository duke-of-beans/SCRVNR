

## PLEXUS Research Session — 2026-08-26

### Voice/Linguistic Tools via PLEXUS
PLEXUS adapters now provide real-time linguistic calibration for SCRVNR voice synthesis:
- **datamuse** — semantic neighbors with weighted scores + CMU phonetic transcriptions
- **thesaurus** — synonym gradients (near→far synonyms ranked)
- **wiktionary** — etymology and linguistic genealogy
- **urban-dictionary** — slang register and informal usage
- **jisho** — cross-linguistic precision (e.g., 5 Japanese words for "emergence" with distinct semantic fields)

### Application
SCRVNR can query PLEXUS at write-time to calibrate word choice against semantic distance, register, and etymology. This is voice synthesis with a live linguistic substrate instead of static training data.