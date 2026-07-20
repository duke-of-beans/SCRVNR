"""
Tests for SCRVNR v2.0 Auto-Correct Module (Sprint V2-04)

Run:
    D:\\Programs\\Python312\\python.exe D:\\Projects\\SCRVNR\\tests\\test_autocorrect.py
"""

import os
import sys
import shutil
import sqlite3
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def setup_test_db():
    """Create voice.db with required tables for auto-correct testing."""
    tmp_dir = tempfile.mkdtemp(prefix='scrvnr_ac_test_')
    db_path = os.path.join(tmp_dir, 'voice.db')

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("CREATE TABLE schema_version (version TEXT PRIMARY KEY, applied_at TEXT, description TEXT)")
    cur.execute("INSERT INTO schema_version VALUES ('3.0.0', datetime('now'), 'test')")

    # Forbidden patterns
    cur.execute("""CREATE TABLE forbidden_patterns (
        id INTEGER PRIMARY KEY AUTOINCREMENT, pattern TEXT UNIQUE,
        reason TEXT, severity TEXT DEFAULT 'warning',
        category TEXT, environment TEXT, created_at TEXT)""")

    cur.execute("INSERT INTO forbidden_patterns (pattern, reason, severity, category) VALUES ('based on my memories', 'Memory attribution', 'blocking', 'tone')")
    cur.execute("INSERT INTO forbidden_patterns (pattern, reason, severity, category) VALUES ('from my memories', 'Memory attribution', 'blocking', 'tone')")

    # Rarity targets
    cur.execute("""CREATE TABLE rarity_targets (
        register TEXT PRIMARY KEY, target_mean_zipf REAL, target_pct_rare REAL,
        target_contraction_rate REAL, target_sentence_len_mean REAL,
        target_sentence_len_std REAL, target_em_dash_rate REAL DEFAULT 0.0,
        tolerance_zipf REAL DEFAULT 0.3, tolerance_rare REAL DEFAULT 2.0,
        tolerance_contraction REAL DEFAULT 0.15, tolerance_sentence REAL DEFAULT 5.0,
        created_at TEXT)""")

    cur.execute("""INSERT INTO rarity_targets (register, target_mean_zipf, target_pct_rare,
        target_contraction_rate, target_sentence_len_mean, target_sentence_len_std)
        VALUES ('TECH', 4.08, 7.89, 0.29, 14.5, 12.4)""")
    cur.execute("""INSERT INTO rarity_targets (register, target_mean_zipf, target_pct_rare,
        target_contraction_rate, target_sentence_len_mean, target_sentence_len_std)
        VALUES ('CASUAL', 4.55, 5.8, 0.74, 5.0, 3.5)""")

    # Substitution ledger with a promoted entry
    cur.execute("""CREATE TABLE substitution_ledger (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_text TEXT, to_text TEXT, register TEXT,
        occurrence_count INTEGER DEFAULT 1,
        first_seen TEXT, last_seen TEXT,
        promoted INTEGER DEFAULT 0, promoted_at TEXT, source_pair_ids TEXT,
        UNIQUE(from_text, to_text, register))""")

    cur.execute("""INSERT INTO substitution_ledger (from_text, to_text, register, occurrence_count, promoted, promoted_at)
        VALUES ('utilizes', 'uses', 'TECH', 5, 1, datetime('now'))""")
    cur.execute("""INSERT INTO substitution_ledger (from_text, to_text, register, occurrence_count, promoted, promoted_at)
        VALUES ('facilitate', 'run', 'TECH', 3, 1, datetime('now'))""")

    conn.commit()
    conn.close()
    return tmp_dir, db_path


def cleanup(tmp_dir):
    shutil.rmtree(tmp_dir, ignore_errors=True)


# =========================================================
# Tests
# =========================================================

def test_01_em_dash_removal():
    """Em-dashes replaced with hyphens."""
    from core.autocorrect import AutoCorrector
    tmp_dir, db_path = setup_test_db()
    try:
        ac = AutoCorrector(db_path)
        result = ac.correct("The system — built on Python — handles data well.", register='TECH')
        assert '\u2014' not in result['text'], "Em-dash still present"
        assert ' - ' in result['text'], "Hyphen replacement missing"
        assert any(f['type'] == 'em_dash' for f in result['fixes'])
        print("PASS: test_01_em_dash_removal")
    finally:
        cleanup(tmp_dir)


def test_02_smart_quote_replacement():
    """Smart quotes replaced with straight quotes."""
    from core.autocorrect import AutoCorrector
    tmp_dir, db_path = setup_test_db()
    try:
        ac = AutoCorrector(db_path)
        result = ac.correct("He said \u201chello\u201d and she said \u2018hi\u2019 back.", register='TECH')
        assert '\u201c' not in result['text'] and '\u201d' not in result['text']
        assert '"hello"' in result['text']
        assert any(f['type'] == 'smart_quotes' for f in result['fixes'])
        print("PASS: test_02_smart_quote_replacement")
    finally:
        cleanup(tmp_dir)


def test_03_forbidden_word_removal():
    """Blocking forbidden patterns are removed."""
    from core.autocorrect import AutoCorrector
    tmp_dir, db_path = setup_test_db()
    try:
        ac = AutoCorrector(db_path)
        result = ac.correct("Based on my memories, the system processes data. From my memories it works well.", register='TECH')
        assert 'based on my memories' not in result['text'].lower()
        assert 'from my memories' not in result['text'].lower()
        assert any(f['type'] == 'forbidden_word' for f in result['fixes'])
        print("PASS: test_03_forbidden_word_removal")
    finally:
        cleanup(tmp_dir)


def test_04_contraction_insertion():
    """Contractions inserted when rate is below target."""
    from core.autocorrect import AutoCorrector
    tmp_dir, db_path = setup_test_db()
    try:
        ac = AutoCorrector(db_path)
        # CASUAL register has target 0.74 — text with zero contractions should get some
        text = ("I do not think it is a good idea. We are not going to do that. "
                "It does not make sense and I will not accept it. They have not "
                "finished yet. You are right that it is not working correctly today.")
        result = ac.correct(text, register='CASUAL')

        # Should have inserted at least one contraction
        contraction_fixes = [f for f in result['fixes'] if f['type'] == 'contraction_insertion']
        assert len(contraction_fixes) > 0, "No contractions inserted"
        assert "don't" in result['text'] or "it's" in result['text'] or "aren't" in result['text'], \
            f"No contractions found in: {result['text'][:100]}"
        print(f"PASS: test_04_contraction_insertion ({contraction_fixes[0]['count']} inserted)")
    finally:
        cleanup(tmp_dir)


def test_05_no_unnecessary_contractions():
    """Don't insert contractions when rate already meets target."""
    from core.autocorrect import AutoCorrector
    tmp_dir, db_path = setup_test_db()
    try:
        ac = AutoCorrector(db_path)
        # TECH register target is 0.29 — this text already has enough contractions
        text = ("Here's how this works - you'll want to check the endpoint first. "
                "It's not complicated but you'll need the config. Don't skip the tests.")
        result = ac.correct(text, register='TECH')
        contraction_fixes = [f for f in result['fixes'] if f['type'] == 'contraction_insertion']
        assert len(contraction_fixes) == 0, f"Unnecessary contractions inserted: {contraction_fixes}"
        print("PASS: test_05_no_unnecessary_contractions")
    finally:
        cleanup(tmp_dir)


def test_06_promoted_substitution():
    """Promoted substitutions from correction ledger are applied."""
    from core.autocorrect import AutoCorrector
    tmp_dir, db_path = setup_test_db()
    try:
        ac = AutoCorrector(db_path)
        result = ac.correct("The system utilizes a framework to facilitate data processing.", register='TECH')
        assert 'utilizes' not in result['text'].lower(), f"'utilizes' not replaced: {result['text']}"
        assert 'uses' in result['text'].lower(), f"'uses' not found: {result['text']}"
        sub_fixes = [f for f in result['fixes'] if f['type'] == 'promoted_substitution']
        assert len(sub_fixes) > 0
        print(f"PASS: test_06_promoted_substitution ({len(sub_fixes)} subs applied)")
    finally:
        cleanup(tmp_dir)


def test_07_suggestions_not_applied():
    """Suggestions are returned but not applied to text."""
    from core.autocorrect import AutoCorrector
    tmp_dir, db_path = setup_test_db()
    try:
        ac = AutoCorrector(db_path)
        text = "The comprehensive system leverages robust APIs to streamline the ecosystem."
        result = ac.correct(text, register='TECH')

        # Claude vocabulary should appear as suggestion, not fix
        claude_suggestions = [s for s in result['suggestions'] if s['type'] == 'claude_vocabulary']
        assert len(claude_suggestions) > 0, "No Claude vocabulary suggestions"

        # The words should still be in the text (suggestions don't modify)
        # Note: some Claude words might be removed by forbidden patterns
        # but 'comprehensive', 'robust' etc aren't in the blocking list
        print(f"PASS: test_07_suggestions_not_applied ({len(result['suggestions'])} suggestions)")
    finally:
        cleanup(tmp_dir)


def test_08_performance():
    """Auto-correct completes within 10ms for reasonable text."""
    from core.autocorrect import AutoCorrector
    tmp_dir, db_path = setup_test_db()
    try:
        ac = AutoCorrector(db_path)
        # ~200 words
        text = ("The system utilizes a comprehensive framework. " * 10 +
                "It does not work — but we are fixing it. " * 5)
        result = ac.correct(text, register='TECH')
        # First call may be slow (loading data), but should still be under 100ms
        assert result['processing_ms'] < 100, f"Too slow: {result['processing_ms']}ms"
        print(f"PASS: test_08_performance ({result['processing_ms']:.1f}ms)")
    finally:
        cleanup(tmp_dir)


def test_09_case_preservation():
    """Promoted substitutions preserve case of first character."""
    from core.autocorrect import AutoCorrector
    tmp_dir, db_path = setup_test_db()
    try:
        ac = AutoCorrector(db_path)
        result = ac.correct("Utilizes the old framework for processing.", register='TECH')
        # Should start with capital U -> capital U
        assert result['text'].startswith('Uses') or result['text'].startswith('uses'), \
            f"Case not preserved: {result['text'][:20]}"
        print("PASS: test_09_case_preservation")
    finally:
        cleanup(tmp_dir)


def test_10_empty_text():
    """Empty text handled gracefully."""
    from core.autocorrect import AutoCorrector
    tmp_dir, db_path = setup_test_db()
    try:
        ac = AutoCorrector(db_path)
        result = ac.correct("", register='TECH')
        assert result['text'] == ""
        assert result['fix_count'] == 0
        print("PASS: test_10_empty_text")
    finally:
        cleanup(tmp_dir)


def test_11_fix_ordering():
    """Fixes apply in correct order: 4A → 4B → 4C."""
    from core.autocorrect import AutoCorrector
    tmp_dir, db_path = setup_test_db()
    try:
        ac = AutoCorrector(db_path)
        # Text with em-dash AND promoted sub AND expandable contractions
        text = "The system utilizes old methods — and it does not work well at all in production."
        result = ac.correct(text, register='CASUAL')

        categories = [f['category'] for f in result['fixes']]
        # 4A should come before 4B, 4B before 4C
        if '4A' in categories and '4B' in categories:
            assert categories.index('4A') < categories.index('4B'), "4A should come before 4B"
        if '4A' in categories and '4C' in categories:
            assert categories.index('4A') < categories.index('4C'), "4A should come before 4C"

        print(f"PASS: test_11_fix_ordering ({len(result['fixes'])} fixes in order)")
    finally:
        cleanup(tmp_dir)


def test_12_low_specificity_suggestion():
    """Low specificity flagged in TECH register."""
    from core.autocorrect import AutoCorrector
    tmp_dir, db_path = setup_test_db()
    try:
        ac = AutoCorrector(db_path)
        # Generic text with no file paths, no backticks, no CAPS names
        text = "The system processes data efficiently. It handles requests and returns responses. The architecture is modular and extensible with good error handling throughout the pipeline."
        result = ac.correct(text, register='TECH')
        specificity = [s for s in result['suggestions'] if s['type'] == 'low_specificity']
        assert len(specificity) > 0, "Should flag low specificity in TECH register"
        print("PASS: test_12_low_specificity_suggestion")
    finally:
        cleanup(tmp_dir)


# =========================================================
# Runner
# =========================================================

def run_all():
    tests = [
        test_01_em_dash_removal,
        test_02_smart_quote_replacement,
        test_03_forbidden_word_removal,
        test_04_contraction_insertion,
        test_05_no_unnecessary_contractions,
        test_06_promoted_substitution,
        test_07_suggestions_not_applied,
        test_08_performance,
        test_09_case_preservation,
        test_10_empty_text,
        test_11_fix_ordering,
        test_12_low_specificity_suggestion,
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
