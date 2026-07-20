"""
Correction Capture — SCRVNR v2.0 Subsystem 1 (CORPUS) + Subsystem 6 (LEARN)

The correction is worth more than the sample.

Captures, stores, and learns from every correction David makes to AI output.
Extracts word/phrase substitutions, manages the promotion lifecycle
(3+ occurrences -> auto-fix candidate), and provides the substitution table
for downstream modules (auto-correct, preference description).

Research basis:
    CIPHER (Gao et al., 2024): Correction-pair learning
    EMG-RAG (EMNLP 2024): Editable memory graph

Usage:
    from core.correction_capture import CorrectionCapture
    cc = CorrectionCapture()

    # Store a correction pair
    pair_id = cc.capture(original_text, corrected_text, register='TECH')

    # Get promoted substitutions for auto-fix
    subs = cc.get_promoted_substitutions(register='TECH')

    # Get all substitution candidates (including not-yet-promoted)
    candidates = cc.get_substitution_candidates(register='TECH', min_count=2)
"""

import difflib
import hashlib
import json
import re
import sqlite3
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple


WORD_PATTERN = re.compile(r"[a-zA-Z']+")

# Minimum text length to attempt correction analysis
MIN_TEXT_LENGTH = 10

# Promotion threshold: how many times a substitution must appear before auto-fix
PROMOTION_THRESHOLD = 3

# Maximum edit distance ratio for two texts to be considered a correction pair
# (vs. a complete rewrite / new content)
MAX_EDIT_RATIO = 0.85  # if > 85% of the text changed, it's a rejection, not a correction


class CorrectionCapture:
    """Capture, store, and learn from corrections to AI-generated text."""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = str(Path(__file__).parent.parent / 'learning' / 'voice.db')
        self.db_path = db_path
        self._centrifuge = None  # lazy-loaded

    def _get_conn(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _get_centrifuge(self):
        """Lazy-load the centrifuge for scoring."""
        if self._centrifuge is None:
            from core.centrifuge import VoiceCentrifuge
            self._centrifuge = VoiceCentrifuge(self.db_path)
        return self._centrifuge

    def _generate_id(self, original: str, corrected: str) -> str:
        """Generate a deterministic ID for a correction pair."""
        combined = f"{original}|||{corrected}"
        digest = hashlib.sha256(combined.encode('utf-8')).hexdigest()[:12]
        return f"cp_{digest}"

    def _word_count(self, text: str) -> int:
        """Count words in text."""
        return len(WORD_PATTERN.findall(text))

    # ------------------------------------------------------------------
    # Correction type classification
    # ------------------------------------------------------------------

    def classify_correction(self, original: str, corrected: str) -> str:
        """
        Classify the type of correction.

        Returns one of:
            substitution  — word/phrase swaps, same structure
            deletion      — content removed
            insertion     — content added
            restructure   — reordered or substantially rewritten
            rejection     — complete rewrite (> MAX_EDIT_RATIO changed)
        """
        if not original.strip() or not corrected.strip():
            return 'rejection'

        orig_words = original.lower().split()
        corr_words = corrected.lower().split()

        if not orig_words or not corr_words:
            return 'rejection'

        # Length differential — strong signal for insertion/deletion
        len_orig = len(orig_words)
        len_corr = len(corr_words)
        len_ratio = len_corr / max(len_orig, 1)

        # Sequence matcher for structural comparison
        sm = difflib.SequenceMatcher(None, orig_words, corr_words)
        ratio = sm.ratio()

        # If very little matches, it's a rejection
        if ratio < (1.0 - MAX_EDIT_RATIO):
            return 'rejection'

        # Count operations
        opcodes = sm.get_opcodes()
        n_replace = 0
        n_insert = 0
        n_delete = 0
        n_equal = 0
        words_replaced = 0
        words_inserted = 0
        words_deleted = 0

        for tag, i1, i2, j1, j2 in opcodes:
            if tag == 'equal':
                n_equal += 1
            elif tag == 'replace':
                n_replace += 1
                words_replaced += max(i2 - i1, j2 - j1)
            elif tag == 'insert':
                n_insert += 1
                words_inserted += j2 - j1
            elif tag == 'delete':
                n_delete += 1
                words_deleted += i2 - i1

        total_ops = n_replace + n_insert + n_delete

        if total_ops == 0:
            return 'substitution'  # identical text, unusual but handle gracefully

        # Net words added/removed — accounts for junction replacements
        # (e.g. "config." -> "config, then verify..." is a 1-word replace + N-word insert)
        net_added = len_corr - len_orig

        # Length-based override: if the corrected text is significantly longer/shorter
        # and the original content is mostly preserved, length change dominates
        if net_added > 3 and len_ratio > 1.4 and ratio > 0.3:
            return 'insertion'
        if net_added < -3 and len_ratio < 0.7 and ratio > 0.3:
            return 'deletion'

        # Dominant operation determines type
        if words_replaced > words_inserted and words_replaced > words_deleted:
            # Check if the replacements are structural (reordering) or lexical (word swaps)
            if n_replace > 3 and ratio < 0.6:
                return 'restructure'
            return 'substitution'
        elif words_deleted > words_inserted and words_deleted > words_replaced:
            return 'deletion'
        elif words_inserted > words_deleted and words_inserted > words_replaced:
            return 'insertion'
        elif n_replace > 0 and ratio < 0.5:
            return 'restructure'
        else:
            return 'substitution'

    # ------------------------------------------------------------------
    # Substitution extraction
    # ------------------------------------------------------------------

    def extract_substitutions(self, original: str, corrected: str) -> List[Dict]:
        """
        Extract word/phrase substitutions from a correction pair.

        Uses difflib to find 'replace' operations and extracts the
        (from_text, to_text) pairs. Groups adjacent replacements into
        phrase-level substitutions.

        Returns list of:
            {'from': str, 'to': str, 'context': str}
        """
        orig_words = original.split()
        corr_words = corrected.split()

        sm = difflib.SequenceMatcher(None, orig_words, corr_words)
        opcodes = sm.get_opcodes()

        substitutions = []

        for tag, i1, i2, j1, j2 in opcodes:
            if tag == 'replace':
                from_phrase = ' '.join(orig_words[i1:i2])
                to_phrase = ' '.join(corr_words[j1:j2])

                # Skip if either side is very long (structural change, not a substitution)
                if (i2 - i1) > 8 or (j2 - j1) > 8:
                    continue

                # Get surrounding context (2 words on each side)
                ctx_start = max(0, i1 - 2)
                ctx_end = min(len(orig_words), i2 + 2)
                context = ' '.join(orig_words[ctx_start:ctx_end])

                substitutions.append({
                    'from': from_phrase,
                    'to': to_phrase,
                    'context': context,
                })

                # Also extract single-word swaps from multi-word replacements
                # if the replacement is roughly the same length
                if (i2 - i1) == (j2 - j1) and (i2 - i1) > 1:
                    for k in range(i2 - i1):
                        ow = orig_words[i1 + k].lower().strip('.,;:!?')
                        cw = corr_words[j1 + k].lower().strip('.,;:!?')
                        if ow != cw and len(ow) > 2 and len(cw) > 2:
                            substitutions.append({
                                'from': ow,
                                'to': cw,
                                'context': f"(word-level from phrase swap)",
                            })

        return substitutions

    # ------------------------------------------------------------------
    # Core capture
    # ------------------------------------------------------------------

    def capture(self, original: str, corrected: str,
                register: str = None,
                source: str = 'session',
                score_both: bool = True) -> Optional[str]:
        """
        Capture a correction pair.

        Stores the pair, extracts substitutions, updates the substitution
        ledger, and checks for promotion.

        Args:
            original: The AI-generated text that was corrected
            corrected: David's corrected version
            register: Target register (auto-detected if None)
            source: Origin of the correction (session/retroactive/manual)
            score_both: Whether to score both texts with the centrifuge

        Returns:
            The correction pair ID, or None if the texts are too short
        """
        if len(original.strip()) < MIN_TEXT_LENGTH or len(corrected.strip()) < MIN_TEXT_LENGTH:
            return None

        pair_id = self._generate_id(original, corrected)

        # Classify correction type
        correction_type = self.classify_correction(original, corrected)

        # Extract substitutions
        substitutions = self.extract_substitutions(original, corrected)

        # Score both texts if requested
        orig_score = None
        corr_score = None
        score_delta = None

        if score_both and register:
            try:
                centrifuge = self._get_centrifuge()
                orig_result = centrifuge.score(original, register)
                corr_result = centrifuge.score(corrected, register)
                orig_score = orig_result['overall_score']
                corr_score = corr_result['overall_score']
                score_delta = corr_score - orig_score
            except Exception:
                pass  # scoring is optional, don't fail the capture

        # Store the correction pair
        conn = self._get_conn()
        try:
            cur = conn.cursor()

            cur.execute("""
            INSERT OR REPLACE INTO correction_pairs
            (id, original_text, corrected_text, register, correction_type,
             original_centrifuge_score, corrected_centrifuge_score, score_delta,
             extracted_substitutions, source,
             word_count_original, word_count_corrected)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                pair_id, original, corrected, register, correction_type,
                orig_score, corr_score, score_delta,
                json.dumps(substitutions) if substitutions else None,
                source,
                self._word_count(original), self._word_count(corrected)
            ))

            # Update substitution ledger
            if substitutions and register:
                self._update_ledger(cur, substitutions, register, pair_id)

            conn.commit()
        finally:
            conn.close()

        return pair_id

    # ------------------------------------------------------------------
    # Substitution ledger management
    # ------------------------------------------------------------------

    def _update_ledger(self, cur: sqlite3.Cursor, substitutions: List[Dict],
                       register: str, pair_id: str):
        """
        Update the substitution ledger with extracted substitutions.
        Checks for promotion threshold.
        """
        for sub in substitutions:
            from_text = sub['from'].lower().strip()
            to_text = sub['to'].lower().strip()

            if not from_text or not to_text or from_text == to_text:
                continue

            # Check if this substitution already exists
            cur.execute("""
            SELECT id, occurrence_count, source_pair_ids, promoted
            FROM substitution_ledger
            WHERE from_text = ? AND to_text = ? AND register = ?
            """, (from_text, to_text, register))

            row = cur.fetchone()

            if row:
                # Increment count, append pair_id
                existing_ids = row['source_pair_ids'] or ''
                if pair_id not in existing_ids:
                    new_ids = f"{existing_ids},{pair_id}" if existing_ids else pair_id
                    new_count = row['occurrence_count'] + 1

                    cur.execute("""
                    UPDATE substitution_ledger
                    SET occurrence_count = ?,
                        last_seen = datetime('now'),
                        source_pair_ids = ?
                    WHERE id = ?
                    """, (new_count, new_ids, row['id']))

                    # Check for promotion
                    if new_count >= PROMOTION_THRESHOLD and not row['promoted']:
                        cur.execute("""
                        UPDATE substitution_ledger
                        SET promoted = 1,
                            promoted_at = datetime('now')
                        WHERE id = ?
                        """, (row['id'],))
            else:
                # New substitution
                cur.execute("""
                INSERT INTO substitution_ledger
                (from_text, to_text, register, occurrence_count, source_pair_ids)
                VALUES (?,?,?,1,?)
                """, (from_text, to_text, register, pair_id))

    # ------------------------------------------------------------------
    # Query methods
    # ------------------------------------------------------------------

    def get_promoted_substitutions(self, register: str = None) -> List[Dict]:
        """
        Get all promoted substitutions (auto-fix candidates).

        Args:
            register: Filter by register, or None for all

        Returns:
            List of {'from': str, 'to': str, 'register': str, 'count': int}
        """
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            if register:
                cur.execute("""
                SELECT from_text, to_text, register, occurrence_count
                FROM substitution_ledger
                WHERE promoted = 1 AND register = ?
                ORDER BY occurrence_count DESC
                """, (register,))
            else:
                cur.execute("""
                SELECT from_text, to_text, register, occurrence_count
                FROM substitution_ledger
                WHERE promoted = 1
                ORDER BY occurrence_count DESC
                """)

            return [
                {
                    'from': row['from_text'],
                    'to': row['to_text'],
                    'register': row['register'],
                    'count': row['occurrence_count'],
                }
                for row in cur.fetchall()
            ]
        finally:
            conn.close()

    def get_substitution_candidates(self, register: str = None,
                                     min_count: int = 2) -> List[Dict]:
        """
        Get substitutions approaching promotion threshold.

        Args:
            register: Filter by register
            min_count: Minimum occurrence count

        Returns:
            List of substitution candidates with counts
        """
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            if register:
                cur.execute("""
                SELECT from_text, to_text, register, occurrence_count,
                       promoted, first_seen, last_seen
                FROM substitution_ledger
                WHERE register = ? AND occurrence_count >= ?
                ORDER BY occurrence_count DESC
                """, (register, min_count))
            else:
                cur.execute("""
                SELECT from_text, to_text, register, occurrence_count,
                       promoted, first_seen, last_seen
                FROM substitution_ledger
                WHERE occurrence_count >= ?
                ORDER BY occurrence_count DESC
                """, (min_count,))

            return [dict(row) for row in cur.fetchall()]
        finally:
            conn.close()

    def get_correction_pairs(self, register: str = None,
                              correction_type: str = None,
                              limit: int = 50) -> List[Dict]:
        """
        Retrieve stored correction pairs.

        Args:
            register: Filter by register
            correction_type: Filter by type (substitution/deletion/etc.)
            limit: Max results

        Returns:
            List of correction pair dicts
        """
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            query = "SELECT * FROM correction_pairs WHERE 1=1"
            params = []

            if register:
                query += " AND register = ?"
                params.append(register)
            if correction_type:
                query += " AND correction_type = ?"
                params.append(correction_type)

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            cur.execute(query, params)
            return [dict(row) for row in cur.fetchall()]
        finally:
            conn.close()

    def get_stats(self) -> Dict:
        """Get summary statistics for the correction capture system."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            stats = {}

            # Total correction pairs
            cur.execute("SELECT COUNT(*) FROM correction_pairs")
            stats['total_pairs'] = cur.fetchone()[0]

            # By correction type
            cur.execute("""
            SELECT correction_type, COUNT(*) as cnt
            FROM correction_pairs
            GROUP BY correction_type
            ORDER BY cnt DESC
            """)
            stats['by_type'] = {row[0]: row[1] for row in cur.fetchall()}

            # By register
            cur.execute("""
            SELECT register, COUNT(*) as cnt
            FROM correction_pairs
            WHERE register IS NOT NULL
            GROUP BY register
            ORDER BY cnt DESC
            """)
            stats['by_register'] = {row[0]: row[1] for row in cur.fetchall()}

            # Substitution ledger
            cur.execute("SELECT COUNT(*) FROM substitution_ledger")
            stats['total_substitutions'] = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM substitution_ledger WHERE promoted = 1")
            stats['promoted_substitutions'] = cur.fetchone()[0]

            # Mean score delta (when available)
            cur.execute("""
            SELECT AVG(score_delta), MIN(score_delta), MAX(score_delta)
            FROM correction_pairs
            WHERE score_delta IS NOT NULL
            """)
            row = cur.fetchone()
            if row[0] is not None:
                stats['score_delta'] = {
                    'mean': round(row[0], 4),
                    'min': round(row[1], 4),
                    'max': round(row[2], 4),
                }

            # Intake log
            cur.execute("SELECT COUNT(*) FROM intake_log")
            stats['intake_count'] = cur.fetchone()[0]

            return stats
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Batch operations
    # ------------------------------------------------------------------

    def capture_batch(self, pairs: List[Tuple[str, str]],
                       register: str = None,
                       source: str = 'retroactive') -> List[str]:
        """
        Capture multiple correction pairs in one transaction.

        Args:
            pairs: List of (original, corrected) tuples
            register: Target register for all pairs
            source: Origin tag

        Returns:
            List of pair IDs that were stored
        """
        stored_ids = []
        for original, corrected in pairs:
            pair_id = self.capture(
                original, corrected,
                register=register,
                source=source,
                score_both=True
            )
            if pair_id:
                stored_ids.append(pair_id)
        return stored_ids

    def recalculate_promotions(self):
        """
        Recalculate all promotions from scratch.
        Useful after bulk import or manual ledger edits.
        """
        conn = self._get_conn()
        try:
            cur = conn.cursor()

            # Demote all
            cur.execute("""
            UPDATE substitution_ledger
            SET promoted = 0, promoted_at = NULL
            WHERE promoted = 1
            """)

            # Re-promote those meeting threshold
            cur.execute("""
            UPDATE substitution_ledger
            SET promoted = 1, promoted_at = datetime('now')
            WHERE occurrence_count >= ?
            """, (PROMOTION_THRESHOLD,))

            conn.commit()

            cur.execute("SELECT COUNT(*) FROM substitution_ledger WHERE promoted = 1")
            return cur.fetchone()[0]
        finally:
            conn.close()


if __name__ == "__main__":
    cc = CorrectionCapture()
    print("CorrectionCapture initialized")
    print(f"  DB: {cc.db_path}")

    stats = cc.get_stats()
    print(f"\nCurrent stats:")
    for k, v in stats.items():
        print(f"  {k}: {v}")

    # Demo: classify and extract from a test pair
    orig = "The system utilizes a comprehensive framework to facilitate data processing across the ecosystem."
    corr = "The system uses a full pipeline to run data processing across the stack."

    print(f"\nDemo correction pair:")
    print(f"  Type: {cc.classify_correction(orig, corr)}")
    subs = cc.extract_substitutions(orig, corr)
    print(f"  Substitutions found: {len(subs)}")
    for s in subs:
        print(f"    '{s['from']}' -> '{s['to']}'")
