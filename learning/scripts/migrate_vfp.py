"""
VFP Schema Migration — Extends voice.db with 5 new tables for voice fingerprint data.
ADDITIVE ONLY — never drops, alters, or deletes existing tables or data.
Safe to re-run (all CREATE TABLE IF NOT EXISTS, INSERT OR REPLACE).

Tables created:
  1. register_profiles  — per-register voice profile (the kite shape target)
  2. rarity_targets     — centrifuge calibration per register
  3. claude_baseline    — Claude vs David delta computation
  4. typo_fingerprint   — David's consistent typos
  5. idiosyncratic_vocab — rare-in-English, common-for-David words
"""

import json
import sqlite3
import os
from pathlib import Path


DB_PATH = Path(__file__).parent.parent / "voice.db"
PROFILE_PATH = Path(__file__).parent.parent.parent / "research" / "voice_fingerprint" / "voice_profile.json"

# Technical terms falsely flagged as typos
FALSE_POSITIVE_TYPOS = {
    'configs', 'params', 'deps', 'charset', 'webp', 'wcag', 'roas', 'holdco', 'kissa'
}


def create_tables(conn):
    """Create the 5 new VFP tables. Additive only."""
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS register_profiles (
        register TEXT PRIMARY KEY,
        n_messages INTEGER NOT NULL,
        n_words INTEGER NOT NULL,
        mean_zipf REAL,
        median_zipf REAL,
        std_zipf REAL,
        pct_rare REAL,
        pct_very_rare REAL,
        kite_skew REAL,
        mean_sentence_len REAL,
        median_sentence_len REAL,
        std_sentence_len REAL,
        bimodality_coefficient REAL,
        is_bimodal INTEGER,
        contraction_rate REAL,
        caps_emphasis_rate REAL,
        profanity_rate REAL,
        question_density REAL,
        double_period_rate REAL,
        hyphen_rate REAL,
        em_dash_rate REAL,
        exclamation_rate REAL,
        ellipsis_rate REAL,
        rarity_histogram_json TEXT,
        sentence_len_histogram_json TEXT,
        top_rare_words_json TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS rarity_targets (
        register TEXT PRIMARY KEY,
        target_mean_zipf REAL NOT NULL,
        target_pct_rare REAL NOT NULL,
        target_contraction_rate REAL NOT NULL,
        target_sentence_len_mean REAL NOT NULL,
        target_sentence_len_std REAL NOT NULL,
        target_em_dash_rate REAL NOT NULL DEFAULT 0.0,
        tolerance_zipf REAL DEFAULT 0.3,
        tolerance_rare REAL DEFAULT 2.0,
        tolerance_contraction REAL DEFAULT 0.15,
        tolerance_sentence REAL DEFAULT 5.0,
        created_at TEXT DEFAULT (datetime('now'))
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS claude_baseline (
        feature TEXT PRIMARY KEY,
        claude_estimate REAL NOT NULL,
        david_global REAL NOT NULL,
        delta REAL NOT NULL,
        note TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS typo_fingerprint (
        typo TEXT PRIMARY KEY,
        likely_intended TEXT,
        edit_distance INTEGER,
        message_count INTEGER,
        occurrence_count INTEGER,
        is_real_typo INTEGER DEFAULT 1,
        created_at TEXT DEFAULT (datetime('now'))
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS idiosyncratic_vocab (
        word TEXT PRIMARY KEY,
        mean_zipf REAL,
        message_count INTEGER,
        occurrence_count INTEGER,
        domain TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    )""")

    # Update schema version
    cur.execute("""
    INSERT OR IGNORE INTO schema_version (version, description)
    VALUES ('2.0.0', 'VFP migration - register_profiles, rarity_targets, claude_baseline, typo_fingerprint, idiosyncratic_vocab')
    """)

    conn.commit()
    print("Tables created (5 new + schema_version update)")


def classify_domain(word):
    """Rough domain classification for idiosyncratic vocab."""
    tech = {'onedrive', 'gpt', 'backend', 'frontend', 'typescript', 'shim',
            'initialized', 'timestamp', 'websocket', 'redis', 'cli',
            'powershell', 'deprecated', 'fallback', 'openai', 'cowork',
            'debug', 'uncaught', 'anthropic', 'localstorage', 'endpoints',
            'bootstrap', 'eslint', 'llm', 'ghm', 'utf', 'endpoint',
            'onboarding', 'todo', 'mcp', 'orchestration', 'debugging',
            'placeholders', 'handoff'}
    personal = {'kanna', 'kirsch', 'simi', 'forme', 'estrella', 'sauron',
                'eye-of-sauron', 'myrto'}
    cannabis = {'thca', 'krown'}
    mechanical = {'sqft', 'techs'}
    finance = {'kpis', 'subtotal', 'whp'}
    meta = {'triangulation-app-dev', 'cyrillic'}

    if word in tech: return 'technical'
    if word in personal: return 'personal'
    if word in cannabis: return 'cannabis-industry'
    if word in mechanical: return 'mechanical'
    if word in finance: return 'financial'
    if word in meta: return 'meta'
    return 'general'


def populate_tables(conn, profile):
    """Populate all 5 tables from voice_profile.json."""
    cur = conn.cursor()
    total_rows = 0

    # 1. register_profiles — all 11 registers
    registers = profile.get('registers', {})
    for reg_name, reg_data in registers.items():
        vocab = reg_data.get('vocabulary', {})
        rhythm = reg_data.get('rhythm', {})
        style = reg_data.get('style', {})

        cur.execute("""
        INSERT OR REPLACE INTO register_profiles
        (register, n_messages, n_words, mean_zipf, median_zipf, std_zipf,
         pct_rare, pct_very_rare, kite_skew, mean_sentence_len, median_sentence_len,
         std_sentence_len, bimodality_coefficient, is_bimodal, contraction_rate,
         caps_emphasis_rate, profanity_rate, question_density, double_period_rate,
         hyphen_rate, em_dash_rate, exclamation_rate, ellipsis_rate,
         rarity_histogram_json, sentence_len_histogram_json, top_rare_words_json)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            reg_name, reg_data.get('n_messages', 0), reg_data.get('n_words', 0),
            vocab.get('mean_zipf'), vocab.get('median_zipf'), vocab.get('std_zipf'),
            vocab.get('pct_rare'), vocab.get('pct_very_rare'), vocab.get('kite_skew'),
            rhythm.get('mean_sentence_len'), rhythm.get('median_sentence_len'),
            rhythm.get('std_sentence_len'), rhythm.get('bimodality_coefficient'),
            1 if rhythm.get('is_bimodal') else 0,
            style.get('contraction_rate'), style.get('caps_emphasis_rate'),
            style.get('profanity_rate'), style.get('question_density'),
            style.get('double_period_rate'), style.get('hyphen_rate'),
            style.get('em_dash_rate'), style.get('exclamation_rate'),
            style.get('ellipsis_rate'),
            json.dumps(vocab.get('rarity_histogram', [])),
            json.dumps(rhythm.get('sentence_len_histogram', [])),
            json.dumps(vocab.get('top_20_rare_words', []))
        ))
    rp_count = len(registers)
    total_rows += rp_count
    print(f"  register_profiles: {rp_count} rows")

    # 2. rarity_targets — computed from register_profiles
    rt_count = 0
    for reg_name, reg_data in registers.items():
        vocab = reg_data.get('vocabulary', {})
        rhythm = reg_data.get('rhythm', {})
        style = reg_data.get('style', {})
        std_zipf = vocab.get('std_zipf', 0.3)

        cur.execute("""
        INSERT OR REPLACE INTO rarity_targets
        (register, target_mean_zipf, target_pct_rare, target_contraction_rate,
         target_sentence_len_mean, target_sentence_len_std, target_em_dash_rate,
         tolerance_zipf, tolerance_rare, tolerance_contraction, tolerance_sentence)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            reg_name,
            vocab.get('mean_zipf', 4.3),
            vocab.get('pct_rare', 6.0),
            style.get('contraction_rate', 0.4),
            rhythm.get('mean_sentence_len', 15.0),
            rhythm.get('std_sentence_len', 10.0),
            style.get('em_dash_rate', 0.0),
            max(0.3, std_zipf),  # tolerance = 1 std, min 0.3
            2.0,
            0.15,
            max(5.0, rhythm.get('std_sentence_len', 10.0) * 0.5)
        ))
        rt_count += 1
    total_rows += rt_count
    print(f"  rarity_targets: {rt_count} rows")

    # 3. claude_baseline
    baseline = profile.get('claude_baseline_comparison', {})
    claude_est = baseline.get('claude_baseline_estimate', {})
    david_global = baseline.get('david_global', {})
    delta = baseline.get('delta_david_minus_claude', {})

    baseline_features = [
        ('mean_zipf', 'Vocabulary rarity center'),
        ('pct_rare', 'Percentage of rare words'),
        ('contraction_rate', 'Contraction frequency'),
        ('mean_sentence_len', 'Average sentence length'),
        ('em_dash_rate', 'Em-dash usage per 1K words'),
    ]
    cb_count = 0
    for feat_name, note in baseline_features:
        if feat_name in claude_est and feat_name in david_global:
            cur.execute("""
            INSERT OR REPLACE INTO claude_baseline
            (feature, claude_estimate, david_global, delta, note)
            VALUES (?,?,?,?,?)
            """, (
                feat_name,
                claude_est[feat_name],
                david_global[feat_name],
                delta.get(feat_name, 0.0),
                note
            ))
            cb_count += 1
    total_rows += cb_count
    print(f"  claude_baseline: {cb_count} rows")

    # 4. typo_fingerprint — top 20 typos
    global_data = profile.get('global', {})
    typos = global_data.get('consistent_typos', [])
    tp_count = 0
    for typo in typos[:20]:
        word = typo.get('word', '')
        is_real = 0 if word in FALSE_POSITIVE_TYPOS else 1
        cur.execute("""
        INSERT OR REPLACE INTO typo_fingerprint
        (typo, likely_intended, edit_distance, message_count, occurrence_count, is_real_typo)
        VALUES (?,?,?,?,?,?)
        """, (
            word,
            typo.get('looks_like', ''),
            typo.get('edit_distance', 0),
            typo.get('messages', 0),
            typo.get('occurrences', 0),
            is_real
        ))
        tp_count += 1
    total_rows += tp_count
    print(f"  typo_fingerprint: {tp_count} rows")

    # 5. idiosyncratic_vocab — top 50
    idio_words = global_data.get('idiosyncratic_words_top50', [])
    iv_count = 0
    for entry in idio_words[:50]:
        word = entry.get('word', '')
        cur.execute("""
        INSERT OR REPLACE INTO idiosyncratic_vocab
        (word, mean_zipf, message_count, occurrence_count, domain)
        VALUES (?,?,?,?,?)
        """, (
            word,
            entry.get('zipf', 0.0),
            entry.get('messages', 0),
            entry.get('occurrences', 0),
            classify_domain(word)
        ))
        iv_count += 1
    total_rows += iv_count
    print(f"  idiosyncratic_vocab: {iv_count} rows")

    conn.commit()
    return total_rows


def main():
    print(f"VFP Schema Migration")
    print(f"  DB: {DB_PATH}")
    print(f"  Profile: {PROFILE_PATH}")

    if not DB_PATH.exists():
        print(f"ERROR: voice.db not found at {DB_PATH}")
        return
    if not PROFILE_PATH.exists():
        print(f"ERROR: voice_profile.json not found at {PROFILE_PATH}")
        return

    with open(PROFILE_PATH, 'r', encoding='utf-8') as f:
        profile = json.load(f)

    conn = sqlite3.connect(str(DB_PATH))
    try:
        create_tables(conn)
        total = populate_tables(conn, profile)

        # Report DB size
        db_size = os.path.getsize(str(DB_PATH))
        print(f"\nTotal: {total} rows inserted across 5 tables")
        print(f"DB size: {db_size / 1024:.1f} KB")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
