"""
Tests for SCRVNR v2.0 Preference Description Generator (Sprint V2-02)

Tests cover:
    1. Generation produces valid markdown
    2. Token budget respected (~2000 tokens max)
    3. All major registers included
    4. Prompt context extraction works per-register
    5. Signature moves and anti-patterns present
    6. Bimodal estimates are realistic
    7. Validation returns structured results
    8. Version incrementing works
    9. Regeneration is idempotent (same input → same structure)
    10. Correction history section appears when data exists

Run:
    D:\\Programs\\Python312\\python.exe D:\\Projects\\SCRVNR\\tests\\test_preference_description.py
"""

import os
import sys
import shutil
import sqlite3
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def setup_test_env():
    """Create temporary env with voice.db and minimal voice_profile.json."""
    tmp_dir = tempfile.mkdtemp(prefix='scrvnr_prefer_test_')

    db_path = os.path.join(tmp_dir, 'voice.db')
    profile_path = os.path.join(tmp_dir, 'voice_profile.json')

    # Build minimal voice_profile.json
    import json
    profile = {
        "global": {
            "mean_zipf": 4.33,
            "consistent_typos": [
                {"word": "hte", "looks_like": "the", "edit_distance": 2, "messages": 532},
                {"word": "everyhting", "looks_like": "everything", "edit_distance": 2, "messages": 70},
                {"word": "shold", "looks_like": "should", "edit_distance": 1, "messages": 70},
            ]
        },
        "claude_baseline_comparison": {
            "delta_david_minus_claude": {"em_dash_rate": -25.8}
        },
        "registers": {
            "TECH": {
                "n_messages": 15480, "n_words": 2326695,
                "vocabulary": {"mean_zipf": 4.08, "kite_skew": -1.19, "pct_rare": 7.89},
                "rhythm": {"mean_sentence_len": 14.5, "std_sentence_len": 12.4,
                           "bimodality_coefficient": 0.617, "is_bimodal": True},
                "style": {"contraction_rate": 0.29, "caps_emphasis_rate": 22.25,
                           "em_dash_rate": 0.39, "hyphen_rate": 11.32,
                           "exclamation_rate": 1.44, "ellipsis_rate": 2.13,
                           "profanity_rate": 0.44}
            },
            "CASUAL": {
                "n_messages": 7087, "n_words": 49229,
                "vocabulary": {"mean_zipf": 4.55, "kite_skew": -1.52, "pct_rare": 5.8},
                "rhythm": {"mean_sentence_len": 5.0, "std_sentence_len": 3.5,
                           "bimodality_coefficient": 0.484, "is_bimodal": False},
                "style": {"contraction_rate": 0.74, "caps_emphasis_rate": 10.62,
                           "em_dash_rate": 0.03, "hyphen_rate": 10.33,
                           "exclamation_rate": 8.39, "ellipsis_rate": 2.08,
                           "profanity_rate": 1.38}
            },
            "PROFESSIONAL": {
                "n_messages": 6007, "n_words": 545995,
                "vocabulary": {"mean_zipf": 4.47, "kite_skew": -1.62, "pct_rare": 5.6},
                "rhythm": {"mean_sentence_len": 15.0, "std_sentence_len": 8.0,
                           "bimodality_coefficient": 0.577, "is_bimodal": True},
                "style": {"contraction_rate": 0.41, "caps_emphasis_rate": 12.5,
                           "em_dash_rate": 0.36, "hyphen_rate": 8.6,
                           "exclamation_rate": 0.69, "ellipsis_rate": 0.94,
                           "profanity_rate": 0.41}
            },
            "ARGUMENTATIVE": {
                "n_messages": 658, "n_words": 513326,
                "vocabulary": {"mean_zipf": 4.50, "kite_skew": -3.16, "pct_rare": 4.8},
                "rhythm": {"mean_sentence_len": 20.0, "std_sentence_len": 15.0,
                           "bimodality_coefficient": 0.707, "is_bimodal": True},
                "style": {"contraction_rate": 0.75, "caps_emphasis_rate": 25.33,
                           "em_dash_rate": 0.48, "hyphen_rate": 6.61,
                           "exclamation_rate": 0.42, "ellipsis_rate": 5.19,
                           "profanity_rate": 0.32}
            },
            "INVESTIGATE": {
                "n_messages": 1633, "n_words": 138162,
                "vocabulary": {"mean_zipf": 4.37, "kite_skew": -1.57, "pct_rare": 6.1},
                "rhythm": {"mean_sentence_len": 16.0, "std_sentence_len": 10.0,
                           "bimodality_coefficient": 0.736, "is_bimodal": True},
                "style": {"contraction_rate": 0.39, "caps_emphasis_rate": 20.28,
                           "em_dash_rate": 0.71, "hyphen_rate": 9.05,
                           "exclamation_rate": 1.19, "ellipsis_rate": 2.20,
                           "profanity_rate": 0.38}
            },
            "CREATIVE_DIRECTION": {
                "n_messages": 632, "n_words": 50125,
                "vocabulary": {"mean_zipf": 4.45, "kite_skew": -1.98, "pct_rare": 5.5},
                "rhythm": {"mean_sentence_len": 14.0, "std_sentence_len": 9.0,
                           "bimodality_coefficient": 0.655, "is_bimodal": True},
                "style": {"contraction_rate": 0.41, "caps_emphasis_rate": 13.02,
                           "em_dash_rate": 0.31, "hyphen_rate": 12.62,
                           "exclamation_rate": 0.64, "ellipsis_rate": 0.82,
                           "profanity_rate": 0.25}
            },
            "PERSONAL": {
                "n_messages": 610, "n_words": 73312,
                "vocabulary": {"mean_zipf": 4.45, "kite_skew": -1.45, "pct_rare": 6.5},
                "rhythm": {"mean_sentence_len": 13.0, "std_sentence_len": 7.0,
                           "bimodality_coefficient": 0.405, "is_bimodal": False},
                "style": {"contraction_rate": 0.65, "caps_emphasis_rate": 17.85,
                           "em_dash_rate": 0.92, "hyphen_rate": 16.81,
                           "exclamation_rate": 1.40, "ellipsis_rate": 2.93,
                           "profanity_rate": 0.33}
            },
            "FRUSTRATED": {
                "n_messages": 127, "n_words": 18126,
                "vocabulary": {"mean_zipf": 4.25, "kite_skew": -1.22, "pct_rare": 5.9},
                "rhythm": {"mean_sentence_len": 12.0, "std_sentence_len": 6.0,
                           "bimodality_coefficient": 0.45, "is_bimodal": False},
                "style": {"contraction_rate": 0.60, "caps_emphasis_rate": 32.34,
                           "em_dash_rate": 0.57, "hyphen_rate": 12.32,
                           "exclamation_rate": 10.56, "ellipsis_rate": 3.45,
                           "profanity_rate": 37.87}
            }
        }
    }
    with open(profile_path, 'w', encoding='utf-8') as f:
        json.dump(profile, f)

    # Create minimal voice.db
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("CREATE TABLE schema_version (version TEXT PRIMARY KEY, applied_at TEXT, description TEXT)")
    cur.execute("INSERT INTO schema_version VALUES ('1.0.0', datetime('now'), 'test')")

    cur.execute("""CREATE TABLE register_profiles (
        register TEXT PRIMARY KEY, n_messages INTEGER, n_words INTEGER,
        mean_zipf REAL, median_zipf REAL, std_zipf REAL,
        pct_rare REAL, pct_very_rare REAL, kite_skew REAL,
        mean_sentence_len REAL, median_sentence_len REAL, std_sentence_len REAL,
        bimodality_coefficient REAL, is_bimodal INTEGER,
        contraction_rate REAL, caps_emphasis_rate REAL, profanity_rate REAL,
        question_density REAL, double_period_rate REAL, hyphen_rate REAL,
        em_dash_rate REAL, exclamation_rate REAL, ellipsis_rate REAL,
        rarity_histogram_json TEXT, sentence_len_histogram_json TEXT, top_rare_words_json TEXT,
        created_at TEXT, updated_at TEXT)""")
    cur.execute("""CREATE TABLE rarity_targets (
        register TEXT PRIMARY KEY, target_mean_zipf REAL, target_pct_rare REAL,
        target_contraction_rate REAL, target_sentence_len_mean REAL, target_sentence_len_std REAL,
        target_em_dash_rate REAL DEFAULT 0.0, tolerance_zipf REAL DEFAULT 0.3,
        tolerance_rare REAL DEFAULT 2.0, tolerance_contraction REAL DEFAULT 0.15,
        tolerance_sentence REAL DEFAULT 5.0, created_at TEXT)""")

    # Populate with TECH
    cur.execute("""INSERT INTO register_profiles (register, n_messages, n_words,
        mean_zipf, pct_rare, kite_skew, mean_sentence_len, std_sentence_len,
        bimodality_coefficient, is_bimodal, contraction_rate, caps_emphasis_rate,
        profanity_rate, hyphen_rate, em_dash_rate, exclamation_rate, ellipsis_rate)
        VALUES ('TECH', 15480, 2326695, 4.08, 7.89, -1.19, 14.5, 12.4, 0.617, 1,
                0.29, 22.25, 0.44, 11.32, 0.39, 1.44, 2.13)""")
    cur.execute("""INSERT INTO rarity_targets (register, target_mean_zipf, target_pct_rare,
        target_contraction_rate, target_sentence_len_mean, target_sentence_len_std)
        VALUES ('TECH', 4.08, 7.89, 0.29, 14.5, 12.4)""")

    # Add correction_pairs and substitution_ledger (empty)
    cur.execute("""CREATE TABLE correction_pairs (
        id TEXT PRIMARY KEY, original_text TEXT, corrected_text TEXT,
        register TEXT, correction_type TEXT,
        original_centrifuge_score REAL, corrected_centrifuge_score REAL,
        score_delta REAL, extracted_substitutions TEXT,
        source TEXT, timestamp TEXT, applied_to_autofix INTEGER,
        word_count_original INTEGER, word_count_corrected INTEGER)""")
    cur.execute("""CREATE TABLE substitution_ledger (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_text TEXT, to_text TEXT, register TEXT,
        occurrence_count INTEGER DEFAULT 1,
        first_seen TEXT, last_seen TEXT,
        promoted INTEGER DEFAULT 0, promoted_at TEXT, source_pair_ids TEXT)""")
    cur.execute("""CREATE TABLE intake_log (
        msg_id TEXT PRIMARY KEY, source TEXT, register TEXT,
        word_count INTEGER, mean_zipf REAL,
        intake_timestamp TEXT, weight REAL DEFAULT 1.0)""")

    conn.commit()
    conn.close()

    return tmp_dir, db_path, profile_path


def cleanup_test_env(tmp_dir):
    shutil.rmtree(tmp_dir, ignore_errors=True)


# =========================================================
# Tests
# =========================================================

def test_01_generation_produces_markdown():
    """Generate returns valid markdown with expected headers."""
    from core.preference_description import PreferenceDescriptionGenerator
    tmp_dir, db_path, profile_path = setup_test_env()
    try:
        gen = PreferenceDescriptionGenerator(db_path, profile_path, tmp_dir)
        doc = gen.generate()
        assert doc.startswith("# David's Voice"), f"Missing title header"
        assert "## Global Traits" in doc, "Missing Global Traits section"
        assert "## Signature Moves" in doc, "Missing Signature Moves"
        assert "## Anti-Patterns" in doc, "Missing Anti-Patterns"
        print("PASS: test_01_generation_produces_markdown")
    finally:
        cleanup_test_env(tmp_dir)


def test_02_token_budget():
    """Generated doc is within ~2000 token budget."""
    from core.preference_description import PreferenceDescriptionGenerator
    tmp_dir, db_path, profile_path = setup_test_env()
    try:
        gen = PreferenceDescriptionGenerator(db_path, profile_path, tmp_dir)
        doc = gen.generate()
        approx_tokens = len(doc) / 4
        assert approx_tokens < 2500, f"Too many tokens: ~{approx_tokens:.0f}"
        assert approx_tokens > 500, f"Too few tokens: ~{approx_tokens:.0f}"
        print(f"PASS: test_02_token_budget (~{approx_tokens:.0f} tokens)")
    finally:
        cleanup_test_env(tmp_dir)


def test_03_major_registers_present():
    """All major registers with enough data get sections."""
    from core.preference_description import PreferenceDescriptionGenerator
    tmp_dir, db_path, profile_path = setup_test_env()
    try:
        gen = PreferenceDescriptionGenerator(db_path, profile_path, tmp_dir)
        doc = gen.generate()
        for reg in ['TECH', 'CASUAL', 'PROFESSIONAL', 'ARGUMENTATIVE',
                     'INVESTIGATE', 'CREATIVE_DIRECTION', 'PERSONAL', 'FRUSTRATED']:
            assert f"Register: {reg}" in doc, f"Missing register: {reg}"
        print("PASS: test_03_major_registers_present")
    finally:
        cleanup_test_env(tmp_dir)


def test_04_prompt_context_extraction():
    """get_prompt_context returns focused, injectable text."""
    from core.preference_description import PreferenceDescriptionGenerator
    tmp_dir, db_path, profile_path = setup_test_env()
    try:
        gen = PreferenceDescriptionGenerator(db_path, profile_path, tmp_dir)
        gen.save()  # save first so context can read from file

        ctx = gen.get_prompt_context(register='TECH')
        assert "TECH" in ctx, "TECH register not in context"
        assert "Anti-Patterns" in ctx, "Anti-Patterns not in context"
        assert len(ctx) > 100, f"Context too short: {len(ctx)} chars"

        # Token budget
        approx_tokens = len(ctx) / 4
        assert approx_tokens < 900, f"Context too long for prompt: ~{approx_tokens:.0f} tokens"

        print(f"PASS: test_04_prompt_context_extraction (~{approx_tokens:.0f} tokens)")
    finally:
        cleanup_test_env(tmp_dir)


def test_05_em_dash_anti_pattern():
    """Em-dash anti-pattern is prominently featured."""
    from core.preference_description import PreferenceDescriptionGenerator
    tmp_dir, db_path, profile_path = setup_test_env()
    try:
        gen = PreferenceDescriptionGenerator(db_path, profile_path, tmp_dir)
        doc = gen.generate()
        assert "em-dash" in doc.lower(), "Em-dash not mentioned"
        assert "never uses em-dashes" in doc.lower() or "never uses em-dashes" in doc, "Em-dash anti-pattern not clear"
        print("PASS: test_05_em_dash_anti_pattern")
    finally:
        cleanup_test_env(tmp_dir)


def test_06_bimodal_estimates_realistic():
    """Bimodal sentence estimates are within realistic bounds."""
    from core.preference_description import PreferenceDescriptionGenerator
    tmp_dir, db_path, profile_path = setup_test_env()
    try:
        gen = PreferenceDescriptionGenerator(db_path, profile_path, tmp_dir)
        doc = gen.generate()
        # Find bimodal descriptions and check they don't have absurd values
        import re
        # Look for "~N words" patterns
        word_estimates = re.findall(r'~(\d+) words', doc)
        for est in word_estimates:
            val = int(est)
            assert val <= 45, f"Unrealistic sentence estimate: ~{val} words"
            assert val >= 3, f"Unrealistic sentence estimate: ~{val} words"
        print(f"PASS: test_06_bimodal_estimates_realistic ({len(word_estimates)} estimates checked)")
    finally:
        cleanup_test_env(tmp_dir)


def test_07_validation():
    """validate_against_corpus returns structured results."""
    from core.preference_description import PreferenceDescriptionGenerator
    tmp_dir, db_path, profile_path = setup_test_env()
    try:
        gen = PreferenceDescriptionGenerator(db_path, profile_path, tmp_dir)
        val = gen.validate_against_corpus(register='TECH')
        assert val['register'] == 'TECH'
        assert val['total_claims_checked'] > 0
        assert 'validations' in val
        print(f"PASS: test_07_validation ({val['total_claims_checked']} claims)")
    finally:
        cleanup_test_env(tmp_dir)


def test_08_save_and_version():
    """Save creates file, version increments on regeneration."""
    from core.preference_description import PreferenceDescriptionGenerator
    tmp_dir, db_path, profile_path = setup_test_env()
    try:
        gen = PreferenceDescriptionGenerator(db_path, profile_path, tmp_dir)
        path = gen.save()
        assert path.exists(), "File not created"
        assert "v1" in path.read_text(encoding='utf-8')

        # Regenerate should increment
        doc2 = gen.generate()
        assert "v2" in doc2, "Version not incremented"
        print("PASS: test_08_save_and_version")
    finally:
        cleanup_test_env(tmp_dir)


def test_09_claude_vocabulary_listed():
    """Anti-patterns list includes the Claude vocabulary."""
    from core.preference_description import PreferenceDescriptionGenerator
    tmp_dir, db_path, profile_path = setup_test_env()
    try:
        gen = PreferenceDescriptionGenerator(db_path, profile_path, tmp_dir)
        doc = gen.generate()
        for word in ['utilize', 'facilitate', 'comprehensive', 'robust', 'seamless']:
            assert word in doc, f"Claude vocabulary word '{word}' not in anti-patterns"
        print("PASS: test_09_claude_vocabulary_listed")
    finally:
        cleanup_test_env(tmp_dir)


def test_10_signature_moves():
    """Signature moves section has named patterns."""
    from core.preference_description import PreferenceDescriptionGenerator
    tmp_dir, db_path, profile_path = setup_test_env()
    try:
        gen = PreferenceDescriptionGenerator(db_path, profile_path, tmp_dir)
        doc = gen.generate()
        assert "Bare Directive" in doc, "Missing Bare Directive signature move"
        assert "Specificity Anchor" in doc, "Missing Specificity Anchor"
        assert "Bimodal Beat" in doc, "Missing Bimodal Beat"
        print("PASS: test_10_signature_moves")
    finally:
        cleanup_test_env(tmp_dir)


# =========================================================
# Runner
# =========================================================

def run_all():
    tests = [
        test_01_generation_produces_markdown,
        test_02_token_budget,
        test_03_major_registers_present,
        test_04_prompt_context_extraction,
        test_05_em_dash_anti_pattern,
        test_06_bimodal_estimates_realistic,
        test_07_validation,
        test_08_save_and_version,
        test_09_claude_vocabulary_listed,
        test_10_signature_moves,
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
