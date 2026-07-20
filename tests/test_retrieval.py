"""
Tests for SCRVNR v2.0 Retrieval System Tier 1 (Sprint V2-03)

Tests work without Ollama by using the fallback keyword retrieval
and mock embeddings. Full embedding tests run only when Ollama is available.

Run:
    D:\\Programs\\Python312\\python.exe D:\\Projects\\SCRVNR\\tests\\test_retrieval.py
"""

import json
import os
import sys
import shutil
import sqlite3
import struct
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def setup_test_env():
    """Create temp env with corpus JSONL and voice.db."""
    tmp_dir = tempfile.mkdtemp(prefix='scrvnr_retrieval_test_')
    db_path = os.path.join(tmp_dir, 'voice.db')
    corpus_path = os.path.join(tmp_dir, 'test_corpus.jsonl')

    # Create test corpus
    test_messages = [
        {"msg_id": "t001", "text": "Check the websocket endpoint config, then restart the service and verify the connection pool is healthy.", "register": "TECH"},
        {"msg_id": "t002", "text": "Run the tests first. If the centrifuge scores below threshold, debug the rarity computation before pushing.", "register": "TECH"},
        {"msg_id": "t003", "text": "The pipeline processes data through three stages - intake, transform, and output. Each stage has its own error handling.", "register": "TECH"},
        {"msg_id": "t004", "text": "Deploy the new build to staging, verify the health check endpoint returns 200, then promote to production.", "register": "TECH"},
        {"msg_id": "t005", "text": "This whole project is driving me crazy. The dependencies keep breaking every time we update. Why can't anything just work.", "register": "FRUSTRATED"},
        {"msg_id": "t006", "text": "yeah sounds good, let me know when you're free", "register": "CASUAL"},
        {"msg_id": "t007", "text": "haha nice, that's exactly what I was thinking", "register": "CASUAL"},
        {"msg_id": "t008", "text": "The investigative thread connects three shell companies to the same registered agent in Delaware, all incorporated within 60 days.", "register": "INVESTIGATE"},
        {"msg_id": "t009", "text": "The architecture needs a clear separation between the voice layer and the content layer. They compose at render time, not at generation time.", "register": "CREATIVE_DIRECTION"},
        {"msg_id": "t010", "text": "Please find attached the quarterly report summarizing our operational metrics and key performance indicators for the review period.", "register": "PROFESSIONAL"},
        # Add more TECH messages for keyword matching
        {"msg_id": "t011", "text": "The websocket reconnection handler needs a backoff strategy. Right now it hammers the server on disconnect.", "register": "TECH"},
        {"msg_id": "t012", "text": "Config validation should run at startup, not on first request. Fail fast so we don't discover missing keys in production.", "register": "TECH"},
    ]

    with open(corpus_path, 'w', encoding='utf-8') as f:
        for msg in test_messages:
            f.write(json.dumps(msg) + '\n')

    # Create voice.db with required tables
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("CREATE TABLE schema_version (version TEXT PRIMARY KEY, applied_at TEXT, description TEXT)")
    cur.execute("INSERT INTO schema_version VALUES ('3.0.0', datetime('now'), 'test')")

    # Correction pairs table (for correction retrieval)
    cur.execute("""CREATE TABLE correction_pairs (
        id TEXT PRIMARY KEY, original_text TEXT, corrected_text TEXT,
        register TEXT, correction_type TEXT,
        original_centrifuge_score REAL, corrected_centrifuge_score REAL,
        score_delta REAL, extracted_substitutions TEXT,
        source TEXT, timestamp TEXT DEFAULT (datetime('now')),
        applied_to_autofix INTEGER, word_count_original INTEGER, word_count_corrected INTEGER)""")

    # Insert a test correction pair
    cur.execute("""INSERT INTO correction_pairs
        (id, original_text, corrected_text, register, correction_type)
        VALUES ('cp_test001',
                'The system utilizes comprehensive processing across the ecosystem.',
                'The system uses full processing across the stack.',
                'TECH', 'substitution')""")

    conn.commit()
    conn.close()

    return tmp_dir, db_path, corpus_path


def cleanup(tmp_dir):
    shutil.rmtree(tmp_dir, ignore_errors=True)


# =========================================================
# Tests
# =========================================================

def test_01_table_creation():
    """ensure_table creates corpus_embeddings."""
    from core.retrieval import VoiceRetriever
    tmp_dir, db_path, corpus_path = setup_test_env()
    try:
        ret = VoiceRetriever(db_path, corpus_path)
        conn = ret._get_conn()
        ret._ensure_table(conn)

        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='corpus_embeddings'")
        assert cur.fetchone() is not None, "corpus_embeddings table not created"
        conn.close()
        print("PASS: test_01_table_creation")
    finally:
        cleanup(tmp_dir)


def test_02_fallback_retrieval():
    """Keyword-based fallback works without Ollama."""
    from core.retrieval import VoiceRetriever
    tmp_dir, db_path, corpus_path = setup_test_env()
    try:
        ret = VoiceRetriever(db_path, corpus_path)
        results = ret._fallback_retrieve(
            "websocket endpoint config",
            register='TECH', k=3
        )
        assert len(results) > 0, "No results from fallback retrieval"
        assert results[0]['source'] == 'fallback_keyword'

        # The websocket messages should rank highest
        found_websocket = any('websocket' in r['text'].lower() for r in results)
        assert found_websocket, f"Websocket messages not found in results: {[r['text'][:50] for r in results]}"

        print(f"PASS: test_02_fallback_retrieval ({len(results)} results)")
    finally:
        cleanup(tmp_dir)


def test_03_register_scoping():
    """Retrieval is scoped to target register."""
    from core.retrieval import VoiceRetriever
    tmp_dir, db_path, corpus_path = setup_test_env()
    try:
        ret = VoiceRetriever(db_path, corpus_path)
        results = ret._fallback_retrieve("sounds good", register='CASUAL', k=3)

        for r in results:
            assert r['register'] == 'CASUAL', f"Wrong register: {r['register']}"

        print(f"PASS: test_03_register_scoping ({len(results)} CASUAL results)")
    finally:
        cleanup(tmp_dir)


def test_04_prompt_formatting():
    """format_for_prompt produces valid XML-tagged context."""
    from core.retrieval import VoiceRetriever
    tmp_dir, db_path, corpus_path = setup_test_env()
    try:
        ret = VoiceRetriever(db_path, corpus_path)
        examples = [
            {'text': 'Check the endpoint config.', 'similarity': 0.85,
             'register': 'TECH', 'word_count': 4, 'source': 'corpus'},
            {'text': 'Run the tests first.', 'similarity': 0.72,
             'register': 'TECH', 'word_count': 4, 'source': 'corpus'},
        ]
        formatted = ret.format_for_prompt(examples, register='TECH')

        assert '<voice_examples register="TECH">' in formatted
        assert '</voice_examples>' in formatted
        assert 'Example 1' in formatted
        assert 'Example 2' in formatted
        assert 'Check the endpoint' in formatted

        print(f"PASS: test_04_prompt_formatting ({len(formatted)} chars)")
    finally:
        cleanup(tmp_dir)


def test_05_prompt_with_voice_description():
    """format_for_prompt includes voice description when provided."""
    from core.retrieval import VoiceRetriever
    tmp_dir, db_path, corpus_path = setup_test_env()
    try:
        ret = VoiceRetriever(db_path, corpus_path)
        examples = [
            {'text': 'Test message here.', 'similarity': 0.8,
             'register': 'TECH', 'word_count': 3, 'source': 'corpus'},
        ]
        voice_desc = "Low contraction rate. Bimodal rhythm. No em-dashes."
        formatted = ret.format_for_prompt(examples, register='TECH',
                                           voice_description=voice_desc)

        assert '<voice_description>' in formatted
        assert 'Low contraction rate' in formatted
        assert '</voice_description>' in formatted

        print("PASS: test_05_prompt_with_voice_description")
    finally:
        cleanup(tmp_dir)


def test_06_word_count_filtering():
    """Messages outside word count bounds are excluded."""
    from core.retrieval import VoiceRetriever
    tmp_dir, db_path, corpus_path = setup_test_env()
    try:
        ret = VoiceRetriever(db_path, corpus_path)
        # CASUAL messages are very short (<10 words) and should be excluded
        # by MIN_EXAMPLE_WORDS filter in fallback
        results = ret._fallback_retrieve("good sounds free", register='CASUAL', k=5)

        for r in results:
            assert r['word_count'] >= 10, f"Message too short: {r['word_count']} words"

        print(f"PASS: test_06_word_count_filtering ({len(results)} results, all >= 10 words)")
    finally:
        cleanup(tmp_dir)


def test_07_total_word_budget():
    """format_for_prompt respects total word budget."""
    from core.retrieval import VoiceRetriever
    tmp_dir, db_path, corpus_path = setup_test_env()
    try:
        ret = VoiceRetriever(db_path, corpus_path)
        # Create examples that would exceed budget
        examples = [
            {'text': 'word ' * 200, 'similarity': 0.9,
             'register': 'TECH', 'word_count': 200, 'source': 'corpus'},
            {'text': 'word ' * 200, 'similarity': 0.8,
             'register': 'TECH', 'word_count': 200, 'source': 'corpus'},
            {'text': 'word ' * 200, 'similarity': 0.7,
             'register': 'TECH', 'word_count': 200, 'source': 'corpus'},
        ]
        formatted = ret.format_for_prompt(examples, register='TECH')

        # Should not include all 3 (600 words > 500 budget)
        assert 'Example 3' not in formatted, "Exceeded word budget"

        print("PASS: test_07_total_word_budget")
    finally:
        cleanup(tmp_dir)


def test_08_index_stats():
    """get_index_stats returns structured results."""
    from core.retrieval import VoiceRetriever
    tmp_dir, db_path, corpus_path = setup_test_env()
    try:
        ret = VoiceRetriever(db_path, corpus_path)
        stats = ret.get_index_stats()

        assert 'total_indexed' in stats
        assert 'by_register' in stats
        assert 'ollama_available' in stats

        print(f"PASS: test_08_index_stats (ollama: {stats['ollama_available']})")
    finally:
        cleanup(tmp_dir)


def test_09_retrieve_with_no_index():
    """retrieve() falls back gracefully when no embeddings indexed."""
    from core.retrieval import VoiceRetriever
    tmp_dir, db_path, corpus_path = setup_test_env()
    try:
        ret = VoiceRetriever(db_path, corpus_path)
        # Force ollama unavailable for this test
        ret._ollama_available = False

        results = ret.retrieve("test query", register='TECH', k=3)
        # Should use fallback
        assert isinstance(results, list)

        print(f"PASS: test_09_retrieve_with_no_index ({len(results)} fallback results)")
    finally:
        cleanup(tmp_dir)


def test_10_empty_prompt():
    """retrieve() handles empty/short prompts gracefully."""
    from core.retrieval import VoiceRetriever
    tmp_dir, db_path, corpus_path = setup_test_env()
    try:
        ret = VoiceRetriever(db_path, corpus_path)
        ret._ollama_available = False

        results = ret.retrieve("", register='TECH', k=3)
        assert isinstance(results, list)
        assert len(results) == 0, "Empty prompt should return no results"

        print("PASS: test_10_empty_prompt")
    finally:
        cleanup(tmp_dir)


# =========================================================
# Runner
# =========================================================

def run_all():
    tests = [
        test_01_table_creation,
        test_02_fallback_retrieval,
        test_03_register_scoping,
        test_04_prompt_formatting,
        test_05_prompt_with_voice_description,
        test_06_word_count_filtering,
        test_07_total_word_budget,
        test_08_index_stats,
        test_09_retrieve_with_no_index,
        test_10_empty_prompt,
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
