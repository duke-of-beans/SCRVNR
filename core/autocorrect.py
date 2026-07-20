"""
Auto-Correct Module — SCRVNR v2.0 Subsystem 4 (CORRECT)

After generation, applies mechanical fixes that don't require judgment.
No API calls, pure string operations. Target: <10ms for 1000 words.

Fix categories (ordered by impact):
  4A — Binary fixes (always apply): em-dashes, forbidden words, smart quotes
  4B — Rate-targeted fixes: contraction insertion, sentence splitting
  4C — Substitution table (from correction_pairs promotion)
  4D — Suggestions (surface, don't apply)

Usage:
    from core.autocorrect import AutoCorrector
    ac = AutoCorrector()

    # Full auto-correct pass
    result = ac.correct(text, register='TECH')
    fixed_text = result['text']
    fixes_applied = result['fixes']
    suggestions = result['suggestions']
"""

import re
import sqlite3
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ---- Patterns ----

# Em-dash and en-dash → hyphen with spaces
EM_DASH_PATTERN = re.compile(r'\s*[—–]\s*')

# Smart/curly quotes → straight quotes
SMART_QUOTES = {
    '\u201c': '"',  # left double
    '\u201d': '"',  # right double
    '\u2018': "'",  # left single
    '\u2019': "'",  # right single
    '\u201e': '"',  # double low-9
    '\u201a': "'",  # single low-9
}
SMART_QUOTE_PATTERN = re.compile('[' + ''.join(SMART_QUOTES.keys()) + ']')

# Contraction expansion patterns (for inserting contractions)
EXPANSION_TO_CONTRACTION = [
    # Ordered by frequency in David's corpus (most impactful first)
    (r"\bdo not\b", "don't"),
    (r"\bcan not\b", "can't"),
    (r"\bcannot\b", "can't"),
    (r"\bit is\b", "it's"),
    (r"\bthat is\b", "that's"),
    (r"\bI am\b", "I'm"),
    (r"\bI have\b", "I've"),
    (r"\bI will\b", "I'll"),
    (r"\bI would\b", "I'd"),
    (r"\bwill not\b", "won't"),
    (r"\bdoes not\b", "doesn't"),
    (r"\bdid not\b", "didn't"),
    (r"\bis not\b", "isn't"),
    (r"\bare not\b", "aren't"),
    (r"\bwas not\b", "wasn't"),
    (r"\bwere not\b", "weren't"),
    (r"\bwould not\b", "wouldn't"),
    (r"\bcould not\b", "couldn't"),
    (r"\bshould not\b", "shouldn't"),
    (r"\bhave not\b", "haven't"),
    (r"\bhas not\b", "hasn't"),
    (r"\bhad not\b", "hadn't"),
    (r"\byou are\b", "you're"),
    (r"\bthey are\b", "they're"),
    (r"\bwe are\b", "we're"),
    (r"\bhere is\b", "here's"),
    (r"\bthere is\b", "there's"),
    (r"\bwhat is\b", "what's"),
    (r"\blet us\b", "let's"),
    (r"\bhe is\b", "he's"),
    (r"\bshe is\b", "she's"),
    (r"\byou will\b", "you'll"),
    (r"\bthey will\b", "they'll"),
    (r"\bwe will\b", "we'll"),
    (r"\byou have\b", "you've"),
    (r"\bthey have\b", "they've"),
    (r"\bwe have\b", "we've"),
]

# Precompile contraction patterns
CONTRACTION_PATTERNS = [(re.compile(p, re.IGNORECASE), r) for p, r in EXPANSION_TO_CONTRACTION]

# Contraction counting (for rate measurement)
CONTRACTION_COUNT_PATTERN = re.compile(
    r"\b(?:i'm|you're|we're|they're|it's|that's|here's|there's|"
    r"what's|where's|when's|who's|how's|let's|"
    r"can't|won't|don't|didn't|doesn't|isn't|aren't|wasn't|weren't|"
    r"haven't|hasn't|hadn't|couldn't|wouldn't|shouldn't|mightn't|mustn't|"
    r"i've|you've|we've|they've|i'd|you'd|we'd|they'd|"
    r"i'll|you'll|we'll|they'll|he'll|she'll|it'll|"
    r"he's|she's)\b",
    re.IGNORECASE
)

WORD_PATTERN = re.compile(r"[a-zA-Z']+")


class AutoCorrector:
    """Apply mechanical voice fixes to generated text."""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = str(Path(__file__).parent.parent / 'learning' / 'voice.db')
        self.db_path = db_path
        self._forbidden = None
        self._promoted_subs = None
        self._targets = None

    def _load_data(self):
        """Load forbidden patterns, promoted substitutions, and targets."""
        if self._forbidden is not None:
            return

        self._forbidden = {}
        self._promoted_subs = {}
        self._targets = {}

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            cur = conn.cursor()

            # Forbidden patterns (blocking severity only for auto-fix)
            cur.execute("""
            SELECT pattern, reason, severity, environment
            FROM forbidden_patterns
            WHERE severity = 'blocking'
            """)
            for row in cur.fetchall():
                self._forbidden[row['pattern'].lower()] = {
                    'reason': row['reason'],
                    'environment': row['environment'],
                }

            # Rarity targets (for contraction rate)
            cur.execute("SELECT * FROM rarity_targets")
            for row in cur.fetchall():
                self._targets[row['register']] = dict(row)

            # Promoted substitutions from correction_pairs
            try:
                cur.execute("""
                SELECT from_text, to_text, register, occurrence_count
                FROM substitution_ledger
                WHERE promoted = 1
                """)
                for row in cur.fetchall():
                    reg = row['register'] or '_global'
                    if reg not in self._promoted_subs:
                        self._promoted_subs[reg] = []
                    self._promoted_subs[reg].append({
                        'from': row['from_text'],
                        'to': row['to_text'],
                        'count': row['occurrence_count'],
                    })
            except sqlite3.OperationalError:
                pass  # table doesn't exist yet

        finally:
            conn.close()

    # ------------------------------------------------------------------
    # 4A — Binary fixes (always apply)
    # ------------------------------------------------------------------

    def _fix_em_dashes(self, text: str) -> Tuple[str, List[Dict]]:
        """Replace em-dashes and en-dashes with hyphens."""
        fixes = []
        matches = list(EM_DASH_PATTERN.finditer(text))
        if matches:
            text = EM_DASH_PATTERN.sub(' - ', text)
            fixes.append({
                'type': 'em_dash',
                'count': len(matches),
                'category': '4A',
            })
        return text, fixes

    def _fix_smart_quotes(self, text: str) -> Tuple[str, List[Dict]]:
        """Replace smart/curly quotes with straight quotes."""
        fixes = []
        matches = SMART_QUOTE_PATTERN.findall(text)
        if matches:
            for smart, straight in SMART_QUOTES.items():
                text = text.replace(smart, straight)
            fixes.append({
                'type': 'smart_quotes',
                'count': len(matches),
                'category': '4A',
            })
        return text, fixes

    def _fix_forbidden_words(self, text: str, register: str) -> Tuple[str, List[Dict]]:
        """Replace blocking forbidden patterns."""
        self._load_data()
        fixes = []

        for pattern, info in self._forbidden.items():
            env = info.get('environment')
            if env and env.upper() != register:
                continue

            # Case-insensitive word boundary search
            regex = re.compile(r'\b' + re.escape(pattern) + r'\b', re.IGNORECASE)
            matches = regex.findall(text)
            if matches:
                # Remove the forbidden word (replace with empty or a safe alternative)
                text = regex.sub('', text)
                # Clean up double spaces
                text = re.sub(r'  +', ' ', text)
                fixes.append({
                    'type': 'forbidden_word',
                    'word': pattern,
                    'count': len(matches),
                    'reason': info['reason'],
                    'category': '4A',
                })

        return text, fixes

    # ------------------------------------------------------------------
    # 4B — Rate-targeted fixes
    # ------------------------------------------------------------------

    def _fix_contraction_rate(self, text: str, register: str) -> Tuple[str, List[Dict]]:
        """Insert contractions when rate is below register target."""
        self._load_data()
        target = self._targets.get(register, {})
        target_rate = target.get('target_contraction_rate', 0.4)
        tolerance = target.get('tolerance_contraction', 0.15)

        # Measure current rate
        words = WORD_PATTERN.findall(text)
        word_count = len(words)
        if word_count < 20:
            return text, []  # too short to measure meaningfully

        contractions = len(CONTRACTION_COUNT_PATTERN.findall(text))
        current_rate = contractions / (word_count / 100)

        # Only fix if below target minus tolerance
        if current_rate >= target_rate - tolerance:
            return text, []

        # Apply contraction insertions
        fixes = []
        insertions_made = 0
        max_insertions = max(1, int((target_rate - current_rate) * word_count / 100))

        for pattern, replacement in CONTRACTION_PATTERNS:
            if insertions_made >= max_insertions:
                break
            matches = pattern.findall(text)
            if matches:
                # Replace first occurrence only (conservative)
                text = pattern.sub(replacement, text, count=1)
                insertions_made += 1

        if insertions_made > 0:
            fixes.append({
                'type': 'contraction_insertion',
                'count': insertions_made,
                'rate_before': round(current_rate, 3),
                'target_rate': round(target_rate, 3),
                'category': '4B',
            })

        return text, fixes

    # ------------------------------------------------------------------
    # 4C — Substitution table (learned from corrections)
    # ------------------------------------------------------------------

    def _fix_promoted_substitutions(self, text: str, register: str) -> Tuple[str, List[Dict]]:
        """Apply promoted substitutions from the correction ledger."""
        self._load_data()
        fixes = []

        subs = self._promoted_subs.get(register, []) + self._promoted_subs.get('_global', [])

        for sub in subs:
            from_text = sub['from']
            to_text = sub['to']

            # Case-insensitive word boundary match
            pattern = re.compile(r'\b' + re.escape(from_text) + r'\b', re.IGNORECASE)
            matches = pattern.findall(text)
            if matches:
                # Preserve case of first character
                def replace_preserving_case(match):
                    orig = match.group()
                    if orig[0].isupper() and to_text[0].islower():
                        return to_text[0].upper() + to_text[1:]
                    return to_text

                text = pattern.sub(replace_preserving_case, text)
                fixes.append({
                    'type': 'promoted_substitution',
                    'from': from_text,
                    'to': to_text,
                    'count': len(matches),
                    'times_seen': sub['count'],
                    'category': '4C',
                })

        return text, fixes

    # ------------------------------------------------------------------
    # 4D — Suggestions (surface, don't apply)
    # ------------------------------------------------------------------

    def _generate_suggestions(self, text: str, register: str) -> List[Dict]:
        """Generate suggestions without modifying text."""
        self._load_data()
        suggestions = []

        words = WORD_PATTERN.findall(text)
        word_count = len(words)
        if word_count < 10:
            return suggestions

        # Claude vocabulary detection
        claude_tells = ['utilize', 'facilitate', 'leverage', 'comprehensive',
                         'robust', 'seamless', 'streamline', 'synergy',
                         'holistic', 'paradigm', 'ecosystem', 'utilize',
                         'harness', 'empower', 'optimize']
        found_tells = list(set(w.lower() for w in words if w.lower() in claude_tells))
        if found_tells:
            suggestions.append({
                'type': 'claude_vocabulary',
                'words': found_tells,
                'suggestion': 'Replace with David-authentic vocabulary',
                'category': '4D',
            })

        # Sentence uniformity check
        try:
            from nltk.tokenize import sent_tokenize
            sentences = sent_tokenize(text)
            if len(sentences) > 3:
                lengths = [len(s.split()) for s in sentences]
                mean_len = sum(lengths) / len(lengths)
                if len(lengths) > 1:
                    std_len = (sum((l - mean_len)**2 for l in lengths) / (len(lengths) - 1)) ** 0.5
                else:
                    std_len = 0

                target = self._targets.get(register, {})
                target_std = target.get('target_sentence_len_std', 10.0)

                if std_len < 3.0 and target_std > 6.0:
                    suggestions.append({
                        'type': 'sentence_uniformity',
                        'current_std': round(std_len, 1),
                        'target_std': round(target_std, 1),
                        'suggestion': 'Mix short directives with longer explanations',
                        'category': '4D',
                    })
        except ImportError:
            pass

        # Low specificity check (no named entities / file paths)
        has_paths = bool(re.search(r'[A-Za-z]:\\|/[a-z]+/', text))
        has_backticks = '`' in text
        has_caps_names = bool(re.search(r'\b[A-Z]{2,}\b', text))

        if not has_paths and not has_backticks and not has_caps_names and register == 'TECH':
            suggestions.append({
                'type': 'low_specificity',
                'suggestion': "David's TECH register names specific files, tools, and systems. This output is generic.",
                'category': '4D',
            })

        return suggestions

    # ------------------------------------------------------------------
    # Main correction pipeline
    # ------------------------------------------------------------------

    def correct(self, text: str, register: str = 'TECH') -> Dict:
        """
        Run the full auto-correct pipeline on generated text.

        Processing order: 4A → 4B → 4C → 4D (suggestions appended as metadata)

        Args:
            text: Generated text to correct
            register: Target register

        Returns:
            {
                'text': corrected text,
                'fixes': list of applied fixes,
                'suggestions': list of suggestions (not applied),
                'fix_count': total fixes applied,
                'processing_ms': time taken
            }
        """
        start = time.perf_counter()
        all_fixes = []

        # 4A — Binary fixes
        text, fixes = self._fix_em_dashes(text)
        all_fixes.extend(fixes)

        text, fixes = self._fix_smart_quotes(text)
        all_fixes.extend(fixes)

        text, fixes = self._fix_forbidden_words(text, register)
        all_fixes.extend(fixes)

        # 4B — Rate-targeted fixes
        text, fixes = self._fix_contraction_rate(text, register)
        all_fixes.extend(fixes)

        # 4C — Substitution table
        text, fixes = self._fix_promoted_substitutions(text, register)
        all_fixes.extend(fixes)

        # 4D — Suggestions (don't modify text)
        suggestions = self._generate_suggestions(text, register)

        # Clean up any double spaces from fixes
        text = re.sub(r'  +', ' ', text).strip()

        elapsed_ms = (time.perf_counter() - start) * 1000

        return {
            'text': text,
            'fixes': all_fixes,
            'suggestions': suggestions,
            'fix_count': len(all_fixes),
            'processing_ms': round(elapsed_ms, 2),
        }


if __name__ == "__main__":
    ac = AutoCorrector()
    print("AutoCorrector initialized")

    # Test with Claude-style text
    test = (
        "The system utilizes a comprehensive framework — leveraging robust APIs — "
        "to facilitate seamless data processing across the ecosystem. "
        "It is not complicated but you will need to verify that the endpoint "
        "does not collide with the existing configuration. "
        "We have not tested the websocket handler yet."
    )

    result = ac.correct(test, register='TECH')
    print(f"\nOriginal ({len(test)} chars):")
    print(f"  {test[:120]}...")
    print(f"\nCorrected ({len(result['text'])} chars):")
    print(f"  {result['text'][:120]}...")
    print(f"\nFixes applied: {result['fix_count']} ({result['processing_ms']:.1f}ms)")
    for f in result['fixes']:
        print(f"  [{f['category']}] {f['type']}: {f.get('count', '')} {f.get('from', '')} {f.get('to', '')}")
    print(f"\nSuggestions: {len(result['suggestions'])}")
    for s in result['suggestions']:
        print(f"  [{s['category']}] {s['type']}: {s.get('suggestion', '')}")
