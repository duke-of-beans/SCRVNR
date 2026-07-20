"""
Tests for SCRVNR v2.0 Pipeline Integration (Sprint V2-05)

Run:
    D:\\Programs\\Python312\\python.exe D:\\Projects\\SCRVNR\\tests\\test_pipeline.py
"""

import os
import sys
import json
import shutil
import sqlite3
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def setup_test_env():
    """Full test environment with voice.db, profile, and corpus."""
    tmp_dir = tempfile.mkdtemp(prefix='scrvnr_pipe_test_')
    db_path = os.path.join(tmp_dir, 'voice.db')
    profile_path = os.path.join(tmp_dir, 'voice_profile.json')
    corpus_path = os.path.join(tmp_dir, 'final_corpus.jsonl')

    # Minimal profile JSON
    profile = {
        "global": {"mean_zipf": 4.33, "consistent_typos": []},
        "claude_baseline_comparison": {"delta_david_minus_claude": {"em_dash_rate": -25.8}},
        "registers": {
            "TECH": {
                "n_messages": 15480, "n_words": 2326695,
                "vocabulary": {"mean_zipf": 4.08, "kite_skew": -1.19, "pct_rare": 7.89},
                "rhythm": {"mean_sentence_len": 14.5, "std_sentence_len": 12.4,
                           "bimodality_coefficient": 0.617, "is_bimodal": True},
                "style": {"contraction_rate": 0.29, "caps_emphasis_rate": 22.25,
                           "em_dash_rate": 0.39, "hyphen_rate": 11.32,
                           "exclamation_rate": 1.44, "ellipsis_rate": 2.13, "profanity_rate": 0.44}
            }
        }
    }
    with open(profile_path, 'w', encoding='utf-8') as f:
        json.dump(profile, f)

    # Test corpus
    msgs = [
        {"msg_id": "t001", "text": "Check the websocket endpoint config then restart the service and verify the pool.", "register": "TECH"},
        {"msg_id": "t002", "text": "Run the tests first. If centrifuge scores below threshold debug the rarity computation.", "register": "TECH"},
    ]
    with open(corpus_path, 'w', encoding='utf-8') as f:
        for m in msgs:
            f.write(json.dumps(m) + '\n')

    # Build voice.db
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("CREATE TABLE schema_version (version TEXT PRIMARY KEY, applied_at TEXT, description TEXT)")
    cur.execute("INSERT INTO schema_version VALUES ('3.0.0', datetime('now'), 'test')")

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
    cur.execute("""INSERT INTO register_profiles (register, n_messages, n_words,
        mean_zipf, pct_rare, kite_skew, mean_sentence_len, std_sentence_len,
        bimodality_coefficient, is_bimodal, contraction_rate, caps_emphasis_rate,
        profanity_rate, hyphen_rate, em_dash_rate, exclamation_rate, ellipsis_rate)
        VALUES ('TECH', 15480, 2326695, 4.08, 7.89, -1.19, 14.5, 12.4, 0.617, 1,
                0.29, 22.25, 0.44, 11.32, 0.39, 1.44, 2.13)""")

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

    cur.execute("""CREATE TABLE forbidden_patterns (
        id INTEGER PRIMARY KEY AUTOINCREMENT, pattern TEXT UNIQUE,
        reason TEXT, severity TEXT DEFAULT 'warning',
        category TEXT, environment TEXT, created_at TEXT)""")

    cur.execute("""CREATE TABLE correction_pairs (
        id TEXT PRIMARY KEY, original_text TEXT, corrected_text TEXT,
        register TEXT, correction_type TEXT,
        original_centrifuge_score REAL, corrected_centrifuge_score REAL,
        score_delta REAL, extracted_substitutions TEXT,
        source TEXT, timestamp TEXT DEFAULT (datetime('now')),
        applied_to_autofix INTEGER, word_count_original INTEGER, word_count_corrected INTEGER)""")

    cur.execute("""CREATE TABLE substitution_ledger (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_text TEXT, to_text TEXT, register TEXT,
        occurrence_count INTEGER DEFAULT 1,
        first_seen TEXT, last_seen TEXT,
        promoted INTEGER DEFAULT 0, promoted_at TEXT, source_pair_ids TEXT,
        UNIQUE(from_text, to_text, register))""")

    cur.execute("""CREATE TABLE intake_log (
        msg_id TEXT PRIMARY KEY, source TEXT, register TEXT,
        word_count INTEGER, mean_zipf REAL,
        intake_timestamp TEXT, weight REAL DEFAULT 1.0)""")

    conn.commit()
    conn.close()

    return tmp_dir, db_path, profile_path, corpus_path


def cleanup(tmp_dir):
    shutil.rmtree(tmp_dir, ignore_errors=True)


# =========================================================
# Tests
# =========================================================

def test_01_evaluate_banding():
    """evaluate() returns correct confidence bands."""
    from core.pipeline import VoicePipeline
    tmp_dir, db_path, _, _ = setup_test_env()
    try:
        pipe = VoicePipeline(db_path)

        # David-like text should score higher
        david = "Here's how this works - you'll want to check the endpoint first, then run the tests. It's not complicated."
        result = pipe.evaluate(david, register='TECH')
        assert 'band' in result
        assert 'recommendation' in result
        assert result['band'] in ('HIGH', 'GOOD', 'MARGINAL', 'LOW')
        print(f"PASS: test_01_evaluate_banding (band={result['band']}, score={result['overall_score']:.3f})")
    finally:
        cleanup(tmp_dir)


def test_02_process_corrects_and_scores():
    """process() applies auto-correct then scores."""
    from core.pipeline import VoicePipeline
    tmp_dir, db_path, _, _ = setup_test_env()
    try:
        pipe = VoicePipeline(db_path)

        text = "The system \u2014 built on Python \u2014 handles data processing efficiently."
        result = pipe.process(text, register='TECH')

        assert 'text' in result
        assert 'original_text' in result
        assert 'score' in result
        assert 'fixes' in result
        assert 'band' in result
        assert '\u2014' not in result['text'], "Em-dashes not removed"
        assert result['processing_ms'] < 200, f"Too slow: {result['processing_ms']}ms"

        print(f"PASS: test_02_process_corrects_and_scores ({result['band']}, {result['processing_ms']:.1f}ms)")
    finally:
        cleanup(tmp_dir)


def test_03_process_improves_score():
    """Auto-correct should improve or maintain centrifuge score."""
    from core.pipeline import VoicePipeline
    tmp_dir, db_path, _, _ = setup_test_env()
    try:
        pipe = VoicePipeline(db_path)

        # Text with em-dashes should score worse before correction
        text = "The system \u2014 a Python framework \u2014 processes data \u2014 using robust endpoints \u2014 efficiently."
        before = pipe.evaluate(text, register='TECH')
        result = pipe.process(text, register='TECH')
        after = result['score']

        assert after['overall_score'] >= before['overall_score'], \
            f"Score decreased: {before['overall_score']:.3f} -> {after['overall_score']:.3f}"

        print(f"PASS: test_03_process_improves_score ({before['overall_score']:.3f} -> {after['overall_score']:.3f})")
    finally:
        cleanup(tmp_dir)


def test_04_learn_stores_correction():
    """learn() stores correction pair and returns ID."""
    from core.pipeline import VoicePipeline
    tmp_dir, db_path, _, _ = setup_test_env()
    try:
        pipe = VoicePipeline(db_path)

        pair_id = pipe.learn(
            "The system utilizes comprehensive processing for all endpoints.",
            "The system uses full processing for all endpoints.",
            register='TECH'
        )

        assert pair_id is not None
        assert pair_id.startswith('cp_')

        # Verify it's stored
        pairs = pipe.correction_capture.get_correction_pairs(register='TECH')
        assert len(pairs) == 1

        print(f"PASS: test_04_learn_stores_correction ({pair_id})")
    finally:
        cleanup(tmp_dir)


def test_05_build_generation_context():
    """build_generation_context returns structured context."""
    from core.pipeline import VoicePipeline
    tmp_dir, db_path, profile_path, corpus_path = setup_test_env()
    try:
        # Patch retriever to use test corpus
        pipe = VoicePipeline(db_path)
        pipe._retriever = None
        from core.retrieval import VoiceRetriever
        pipe._retriever = VoiceRetriever(db_path, corpus_path)
        pipe._retriever._ollama_available = False  # force fallback

        # Patch pref gen
        from core.preference_description import PreferenceDescriptionGenerator
        pipe._pref_gen = PreferenceDescriptionGenerator(db_path, profile_path, tmp_dir)
        pipe._pref_gen.save()

        ctx = pipe.build_generation_context("check the websocket endpoint", register='TECH')

        assert 'voice_context' in ctx
        assert 'examples_retrieved' in ctx
        assert 'retrieval_confidence' in ctx
        assert 'register' in ctx
        assert ctx['register'] == 'TECH'
        assert ctx['context_chars'] > 0

        print(f"PASS: test_05_build_generation_context ({ctx['context_chars']} chars, {ctx['examples_retrieved']} examples)")
    finally:
        cleanup(tmp_dir)


def test_06_get_stats():
    """get_stats returns comprehensive pipeline info."""
    from core.pipeline import VoicePipeline
    tmp_dir, db_path, _, _ = setup_test_env()
    try:
        pipe = VoicePipeline(db_path)
        stats = pipe.get_stats()

        assert 'registers' in stats
        assert 'register_count' in stats
        assert stats['register_count'] > 0
        assert 'corrections' in stats

        print(f"PASS: test_06_get_stats ({stats['register_count']} registers)")
    finally:
        cleanup(tmp_dir)


def test_07_end_to_end_claude_text():
    """Full end-to-end: process Claude-style text, verify improvement."""
    from core.pipeline import VoicePipeline
    tmp_dir, db_path, _, _ = setup_test_env()
    try:
        pipe = VoicePipeline(db_path)

        claude_text = (
            "The system utilizes a comprehensive framework \u2014 leveraging robust APIs \u2014 "
            "to facilitate seamless data processing across the \u201cecosystem.\u201d "
            "It is not complicated but you will need to verify that the endpoint "
            "does not collide with the existing configuration. "
            "We have not tested the websocket handler yet."
        )

        result = pipe.process(claude_text, register='TECH')

        # Verify fixes were applied
        assert result['fix_count'] > 0, "No fixes applied to Claude-style text"
        assert '\u2014' not in result['text'], "Em-dashes remain"
        assert '\u201c' not in result['text'], "Smart quotes remain"

        print(f"PASS: test_07_end_to_end_claude_text (score={result['overall_score']:.3f}, "
              f"{result['fix_count']} fixes, {result['processing_ms']:.1f}ms)")
    finally:
        cleanup(tmp_dir)


def test_08_pipeline_performance():
    """Full pipeline under 100ms for typical text."""
    from core.pipeline import VoicePipeline
    tmp_dir, db_path, _, _ = setup_test_env()
    try:
        pipe = VoicePipeline(db_path)

        text = (
            "Here's how the websocket handler works. First you'll connect to the endpoint. "
            "Then the config loads. If it fails, check the logs. "
            "The fallback kicks in after 3 retries. Don't skip the health check."
        )

        # Warm up
        pipe.process(text, register='TECH')

        # Measure
        result = pipe.process(text, register='TECH')
        assert result['processing_ms'] < 100, f"Pipeline too slow: {result['processing_ms']}ms"

        print(f"PASS: test_08_pipeline_performance ({result['processing_ms']:.1f}ms)")
    finally:
        cleanup(tmp_dir)


# =========================================================
# Runner
# =========================================================

def run_all():
    tests = [
        test_01_evaluate_banding,
        test_02_process_corrects_and_scores,
        test_03_process_improves_score,
        test_04_learn_stores_correction,
        test_05_build_generation_context,
        test_06_get_stats,
        test_07_end_to_end_claude_text,
        test_08_pipeline_performance,
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
            print(f"FAIL: {test_fn.__name__} \u2014 {e}")

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
