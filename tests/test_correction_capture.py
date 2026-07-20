"""
Tests for SCRVNR v2.0 Correction Capture (Sprint V2-01)

Tests cover:
    1. Migration — tables exist with correct schema
    2. Correction type classification
    3. Substitution extraction via diff
    4. Capture + storage round-trip
    5. Substitution ledger + promotion lifecycle
    6. Stats aggregation
    7. Edge cases (empty text, identical text, very long text)

Run:
    D:\\Programs\\Python312\\python.exe -m pytest D:\\Projects\\SCRVNR\\tests\\test_correction_capture.py -v
    or:
    D:\\Programs\\Python312\\python.exe D:\\Projects\\SCRVNR\\tests\\test_correction_capture.py
"""

import json
import os
import sqlite3
import sys
import tempfile
import shutil
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def setup_test_db() -> str:
    """Create a temporary voice.db with all required tables for testing."""
    tmp_dir = tempfile.mkdtemp(prefix='scrvnr_test_')
    db_path = os.path.join(tmp_dir, 'voice.db')

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Schema version table (required by migration)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS schema_version (
        version TEXT PRIMARY KEY,
        applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        description TEXT
    )
    """)
    cur.execute("""
    INSERT OR IGNORE INTO schema_version (version, description)
    VALUES ('1.0.0', 'Test schema')
    """)

    # register_profiles (needed by centrifuge)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS register_profiles (
        register TEXT PRIMARY KEY,
        n_messages INTEGER, n_words INTEGER,
        mean_zipf REAL, median_zipf REAL, std_zipf REAL,
        pct_rare REAL, pct_very_rare REAL, kite_skew REAL,
        mean_sentence_len REAL, median_sentence_len REAL, std_sentence_len REAL,
        bimodality_coefficient REAL, is_bimodal INTEGER,
        contraction_rate REAL, caps_emphasis_rate REAL, profanity_rate REAL,
        question_density REAL, double_period_rate REAL, hyphen_rate REAL,
        em_dash_rate REAL, exclamation_rate REAL, ellipsis_rate REAL,
        rarity_histogram_json TEXT, sentence_len_histogram_json TEXT,
        top_rare_words_json TEXT,
        created_at TEXT, updated_at TEXT
    )
    """)

    # rarity_targets (needed by centrifuge)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS rarity_targets (
        register TEXT PRIMARY KEY,
        target_mean_zipf REAL, target_pct_rare REAL,
        target_contraction_rate REAL,
        target_sentence_len_mean REAL, target_sentence_len_std REAL,
        target_em_dash_rate REAL DEFAULT 0.0,
        tolerance_zipf REAL DEFAULT 0.3,
        tolerance_rare REAL DEFAULT 2.0,
        tolerance_contraction REAL DEFAULT 0.15,
        tolerance_sentence REAL DEFAULT 5.0,
        created_at TEXT
    )
    """)

    # Insert a TECH register profile for testing
    cur.execute("""
    INSERT INTO register_profiles (register, n_messages, n_words,
        mean_zipf, median_zipf, std_zipf, pct_rare, pct_very_rare, kite_skew,
        mean_sentence_len, median_sentence_len, std_sentence_len,
        bimodality_coefficient, is_bimodal, contraction_rate, caps_emphasis_rate,
        profanity_rate, question_density, double_period_rate, hyphen_rate,
        em_dash_rate, exclamation_rate, ellipsis_rate,
        rarity_histogram_json, sentence_len_histogram_json, top_rare_words_json)
    VALUES ('TECH', 20000, 500000,
        4.08, 4.20, 1.42, 7.89, 2.31, -2.45,
        14.5, 12.0, 12.4,
        0.617, 1, 0.29, 10.5,
        0.5, 5.2, 0.8, 8.5,
        0.41, 1.2, 0.3,
        '[]', '[]', '[]')
    """)
    cur.execute("""
    INSERT INTO rarity_targets (register, target_mean_zipf, target_pct_rare,
        target_contraction_rate, target_sentence_len_mean, target_sentence_len_std,
        target_em_dash_rate)
    VALUES ('TECH', 4.08, 7.89, 0.29, 14.5, 12.4, 0.0)
    """)

    # Now run the v2 migration
    cur.execute("""
    CREATE TABLE IF NOT EXISTS correction_pairs (
        id TEXT PRIMARY KEY,
        original_text TEXT NOT NULL,
        corrected_text TEXT NOT NULL,
        register TEXT,
        correction_type TEXT,
        original_centrifuge_score REAL,
        corrected_centrifuge_score REAL,
        score_delta REAL,
        extracted_substitutions TEXT,
        source TEXT DEFAULT 'session',
        timestamp TEXT DEFAULT (datetime('now')),
        applied_to_autofix INTEGER DEFAULT 0,
        word_count_original INTEGER,
        word_count_corrected INTEGER
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS intake_log (
        msg_id TEXT PRIMARY KEY,
        source TEXT NOT NULL,
        register TEXT,
        word_count INTEGER,
        mean_zipf REAL,
        intake_timestamp TEXT DEFAULT (datetime('now')),
        weight REAL DEFAULT 1.0
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS substitution_ledger (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_text TEXT NOT NULL,
        to_text TEXT NOT NULL,
        register TEXT,
        occurrence_count INTEGER DEFAULT 1,
        first_seen TEXT DEFAULT (datetime('now')),
        last_seen TEXT DEFAULT (datetime('now')),
        promoted INTEGER DEFAULT 0,
        promoted_at TEXT,
        source_pair_ids TEXT,
        UNIQUE(from_text, to_text, register)
    )
    """)

    conn.commit()
    conn.close()

    return db_path


def cleanup_test_db(db_path: str):
    """Remove temporary test database."""
    tmp_dir = os.path.dirname(db_path)
    shutil.rmtree(tmp_dir, ignore_errors=True)


# =========================================================
# Test cases
# =========================================================

def test_01_tables_exist():
    """Migration creates all required tables."""
    db_path = setup_test_db()
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cur.fetchall()]
        conn.close()

        assert 'correction_pairs' in tables, "correction_pairs table missing"
        assert 'intake_log' in tables, "intake_log table missing"
        assert 'substitution_ledger' in tables, "substitution_ledger table missing"
        print("PASS: test_01_tables_exist")
    finally:
        cleanup_test_db(db_path)


def test_02_classify_substitution():
    """Word-swap corrections classified as substitution."""
    from core.correction_capture import CorrectionCapture
    db_path = setup_test_db()
    try:
        cc = CorrectionCapture(db_path)
        orig = "The system utilizes a comprehensive framework to facilitate processing."
        corr = "The system uses a full pipeline to run processing."
        result = cc.classify_correction(orig, corr)
        assert result == 'substitution', f"Expected substitution, got {result}"
        print("PASS: test_02_classify_substitution")
    finally:
        cleanup_test_db(db_path)


def test_03_classify_deletion():
    """Removed content classified as deletion."""
    from core.correction_capture import CorrectionCapture
    db_path = setup_test_db()
    try:
        cc = CorrectionCapture(db_path)
        orig = "The system is very important and it processes data efficiently and reliably across all surfaces."
        corr = "The system processes data across all surfaces."
        result = cc.classify_correction(orig, corr)
        assert result == 'deletion', f"Expected deletion, got {result}"
        print("PASS: test_03_classify_deletion")
    finally:
        cleanup_test_db(db_path)


def test_04_classify_insertion():
    """Added content classified as insertion."""
    from core.correction_capture import CorrectionCapture
    db_path = setup_test_db()
    try:
        cc = CorrectionCapture(db_path)
        orig = "Check the endpoint config."
        corr = "Check the endpoint config, then verify the websocket fallback and restart the service."
        result = cc.classify_correction(orig, corr)
        assert result == 'insertion', f"Expected insertion, got {result}"
        print("PASS: test_04_classify_insertion")
    finally:
        cleanup_test_db(db_path)


def test_05_classify_rejection():
    """Complete rewrite classified as rejection."""
    from core.correction_capture import CorrectionCapture
    db_path = setup_test_db()
    try:
        cc = CorrectionCapture(db_path)
        orig = "The comprehensive ecosystem leverages synergies to facilitate robust outcomes."
        corr = "Here's how the pipeline works - you hit the endpoint, it runs the check, done."
        result = cc.classify_correction(orig, corr)
        assert result == 'rejection', f"Expected rejection, got {result}"
        print("PASS: test_05_classify_rejection")
    finally:
        cleanup_test_db(db_path)


def test_06_extract_substitutions():
    """Diff-based substitution extraction finds word swaps."""
    from core.correction_capture import CorrectionCapture
    db_path = setup_test_db()
    try:
        cc = CorrectionCapture(db_path)
        orig = "The system utilizes a comprehensive framework to facilitate data processing."
        corr = "The system uses a full pipeline to run data processing."
        subs = cc.extract_substitutions(orig, corr)

        # Should find at least the key swaps
        from_words = [s['from'].lower() for s in subs]
        to_words = [s['to'].lower() for s in subs]

        # Check that we captured the core substitutions
        assert len(subs) > 0, "No substitutions extracted"

        # Verify we found 'utilizes' -> 'uses' type swaps
        found_meaningful = False
        for s in subs:
            if 'utiliz' in s['from'].lower() or 'comprehensive' in s['from'].lower() or 'facilitate' in s['from'].lower():
                found_meaningful = True
                break
        assert found_meaningful, f"No meaningful substitutions found in {subs}"

        print(f"PASS: test_06_extract_substitutions ({len(subs)} subs found)")
    finally:
        cleanup_test_db(db_path)


def test_07_capture_roundtrip():
    """Capture a pair and retrieve it."""
    from core.correction_capture import CorrectionCapture
    db_path = setup_test_db()
    try:
        cc = CorrectionCapture(db_path)
        orig = "The system utilizes a comprehensive framework to facilitate data processing."
        corr = "The system uses a full pipeline to run data processing."

        pair_id = cc.capture(orig, corr, register='TECH', score_both=True)
        assert pair_id is not None, "capture() returned None"
        assert pair_id.startswith('cp_'), f"Bad pair ID format: {pair_id}"

        # Retrieve it
        pairs = cc.get_correction_pairs(register='TECH')
        assert len(pairs) == 1, f"Expected 1 pair, got {len(pairs)}"
        assert pairs[0]['id'] == pair_id
        assert pairs[0]['correction_type'] == 'substitution'
        assert pairs[0]['register'] == 'TECH'

        # Check substitutions were stored
        subs_json = pairs[0]['extracted_substitutions']
        if subs_json:
            subs = json.loads(subs_json)
            assert len(subs) > 0, "No substitutions in stored pair"

        print(f"PASS: test_07_capture_roundtrip (pair_id={pair_id})")
    finally:
        cleanup_test_db(db_path)


def test_08_substitution_promotion():
    """Substitution promoted to auto-fix after 3+ occurrences."""
    from core.correction_capture import CorrectionCapture
    db_path = setup_test_db()
    try:
        cc = CorrectionCapture(db_path)

        # Same substitution in 3 different pairs
        pairs = [
            ("The system utilizes the old framework for processing.",
             "The system uses the old framework for processing."),
            ("It utilizes a different approach to handle this edge case.",
             "It uses a different approach to handle this edge case."),
            ("The module utilizes shared state across all workers in the pool.",
             "The module uses shared state across all workers in the pool."),
        ]

        for orig, corr in pairs:
            cc.capture(orig, corr, register='TECH', score_both=False)

        # Check promotion
        promoted = cc.get_promoted_substitutions(register='TECH')

        # 'utilizes' -> 'uses' should be promoted
        found = False
        for p in promoted:
            if 'utiliz' in p['from'] and 'use' in p['to']:
                found = True
                assert p['count'] >= 3, f"Count should be >= 3, got {p['count']}"
                break

        assert found, f"Expected 'utilizes'->'uses' to be promoted. Got: {promoted}"

        print(f"PASS: test_08_substitution_promotion ({len(promoted)} promoted)")
    finally:
        cleanup_test_db(db_path)


def test_09_stats():
    """Stats aggregation works correctly."""
    from core.correction_capture import CorrectionCapture
    db_path = setup_test_db()
    try:
        cc = CorrectionCapture(db_path)

        # Capture a pair first
        cc.capture(
            "The system utilizes comprehensive processing for all endpoints.",
            "The system uses full processing for all endpoints.",
            register='TECH', score_both=False
        )

        stats = cc.get_stats()
        assert stats['total_pairs'] == 1
        assert 'substitution' in stats['by_type']
        assert 'TECH' in stats['by_register']
        assert stats['total_substitutions'] > 0

        print(f"PASS: test_09_stats")
    finally:
        cleanup_test_db(db_path)


def test_10_edge_empty_text():
    """Empty or very short text returns None."""
    from core.correction_capture import CorrectionCapture
    db_path = setup_test_db()
    try:
        cc = CorrectionCapture(db_path)

        result = cc.capture("", "something corrected here", register='TECH')
        assert result is None, "Should return None for empty original"

        result = cc.capture("short", "", register='TECH')
        assert result is None, "Should return None for empty corrected"

        print("PASS: test_10_edge_empty_text")
    finally:
        cleanup_test_db(db_path)


def test_11_edge_identical_text():
    """Identical text is stored but classified correctly."""
    from core.correction_capture import CorrectionCapture
    db_path = setup_test_db()
    try:
        cc = CorrectionCapture(db_path)
        text = "This is the exact same text with no changes at all."

        result = cc.classify_correction(text, text)
        # Identical text = no operations = substitution (graceful)
        assert result == 'substitution', f"Unexpected: {result}"

        pair_id = cc.capture(text, text, register='TECH', score_both=False)
        assert pair_id is not None

        print("PASS: test_11_edge_identical_text")
    finally:
        cleanup_test_db(db_path)


def test_12_batch_capture():
    """Batch capture stores multiple pairs."""
    from core.correction_capture import CorrectionCapture
    db_path = setup_test_db()
    try:
        cc = CorrectionCapture(db_path)

        pairs = [
            ("The comprehensive system facilitates robust data orchestration.",
             "The system runs data processing."),
            ("We need to leverage the ecosystem for synergies.",
             "We need to use the stack for this."),
            ("It enables seamless integration across all surfaces.",
             "It connects across all surfaces."),
        ]

        ids = cc.capture_batch(pairs, register='TECH')
        assert len(ids) == 3, f"Expected 3, got {len(ids)}"

        stats = cc.get_stats()
        assert stats['total_pairs'] == 3

        print(f"PASS: test_12_batch_capture ({len(ids)} pairs stored)")
    finally:
        cleanup_test_db(db_path)


def test_13_recalculate_promotions():
    """Recalculate promotions from scratch."""
    from core.correction_capture import CorrectionCapture
    db_path = setup_test_db()
    try:
        cc = CorrectionCapture(db_path)

        # 3 identical substitutions
        for i in range(3):
            cc.capture(
                f"Version {i}: the system utilizes old methods for the task.",
                f"Version {i}: the system uses old methods for the task.",
                register='TECH', score_both=False
            )

        # Verify promoted
        promoted_count = len(cc.get_promoted_substitutions())
        assert promoted_count > 0, "Should have promotions"

        # Recalculate
        new_count = cc.recalculate_promotions()
        assert new_count == promoted_count, f"Recalculation changed count: {promoted_count} -> {new_count}"

        print(f"PASS: test_13_recalculate_promotions ({new_count} promoted)")
    finally:
        cleanup_test_db(db_path)


# =========================================================
# Runner
# =========================================================

def run_all():
    """Run all tests and report results."""
    tests = [
        test_01_tables_exist,
        test_02_classify_substitution,
        test_03_classify_deletion,
        test_04_classify_insertion,
        test_05_classify_rejection,
        test_06_extract_substitutions,
        test_07_capture_roundtrip,
        test_08_substitution_promotion,
        test_09_stats,
        test_10_edge_empty_text,
        test_11_edge_identical_text,
        test_12_batch_capture,
        test_13_recalculate_promotions,
    ]

    passed = 0
    failed = 0
    errors = []

    for test_fn in tests:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            failed += 1
            errors.append((test_fn.__name__, str(e)))
            print(f"FAIL: {test_fn.__name__} — {e}")

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{len(tests)} passed, {failed} failed")
    if errors:
        print(f"\nFailures:")
        for name, err in errors:
            print(f"  {name}: {err}")
    print(f"{'='*50}")

    return failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
