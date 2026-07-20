"""
SCRVNR v2.0 Schema Migration — Sprint V2-01: Correction Capture

Adds 2 new tables to voice.db:
  1. correction_pairs  — stores (original, corrected) pairs with extracted substitutions
  2. intake_log        — tracks incremental corpus intake for living profile

ADDITIVE ONLY — never drops, alters, or deletes existing tables or data.
Safe to re-run (all CREATE TABLE IF NOT EXISTS).

Run:
    D:\\Programs\\Python312\\python.exe D:\\Projects\\SCRVNR\\learning\\scripts\\migrate_v2.py
"""

import sqlite3
import os
from pathlib import Path


DB_PATH = Path(__file__).parent.parent / "voice.db"


def create_tables(conn):
    """Create v2.0 correction capture tables. Additive only."""
    cur = conn.cursor()

    # correction_pairs — the highest-value learning signal in v2.0
    # Every time David corrects AI output, we store the pair.
    # Correction types: substitution, deletion, insertion, restructure, rejection
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

    # Indexes for correction_pairs
    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_cp_register
    ON correction_pairs(register)
    """)
    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_cp_type
    ON correction_pairs(correction_type)
    """)
    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_cp_timestamp
    ON correction_pairs(timestamp DESC)
    """)
    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_cp_autofix
    ON correction_pairs(applied_to_autofix)
    """)
    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_cp_source
    ON correction_pairs(source)
    """)

    # intake_log — tracks incremental corpus additions
    # New messages added without re-running the full VFP pipeline.
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
    CREATE INDEX IF NOT EXISTS idx_intake_source
    ON intake_log(source)
    """)
    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_intake_register
    ON intake_log(register)
    """)
    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_intake_timestamp
    ON intake_log(intake_timestamp DESC)
    """)

    # substitution_ledger — tracks individual word/phrase swaps across correction pairs
    # When a substitution hits promotion_count >= 3, it becomes an auto-fix candidate
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

    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_sub_promoted
    ON substitution_ledger(promoted)
    """)
    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_sub_register
    ON substitution_ledger(register)
    """)
    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_sub_count
    ON substitution_ledger(occurrence_count DESC)
    """)

    # Update schema version
    cur.execute("""
    INSERT OR IGNORE INTO schema_version (version, description)
    VALUES ('3.0.0', 'v2.0 Sprint V2-01: correction_pairs, intake_log, substitution_ledger')
    """)

    conn.commit()


def verify_tables(conn):
    """Verify all tables exist and report counts."""
    cur = conn.cursor()
    tables = ['correction_pairs', 'intake_log', 'substitution_ledger']
    results = {}
    for table in tables:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        results[table] = cur.fetchone()[0]
    return results


def main():
    print(f"SCRVNR v2.0 Schema Migration — V2-01 Correction Capture")
    print(f"  DB: {DB_PATH}")

    if not DB_PATH.exists():
        print(f"ERROR: voice.db not found at {DB_PATH}")
        return

    db_size_before = os.path.getsize(str(DB_PATH))

    conn = sqlite3.connect(str(DB_PATH))
    try:
        create_tables(conn)
        counts = verify_tables(conn)

        db_size_after = os.path.getsize(str(DB_PATH))

        print(f"\nTables created:")
        for table, count in counts.items():
            print(f"  {table}: {count} rows")
        print(f"\nDB size: {db_size_before / 1024:.1f} KB -> {db_size_after / 1024:.1f} KB")

        # Verify schema version
        cur = conn.cursor()
        cur.execute("SELECT version, description FROM schema_version ORDER BY applied_at DESC LIMIT 1")
        row = cur.fetchone()
        print(f"Schema version: {row[0]} — {row[1]}")

        print("\nMigration complete.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
