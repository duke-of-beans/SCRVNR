"""
Initialize Ghost Writer voice database from schema.
Reads db_schema.sql and creates voice.db with all tables, indexes, views, and initial data.
"""

import sqlite3
import os
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
SCHEMA_FILE = SCRIPT_DIR / "db_schema.sql"
DB_FILE = SCRIPT_DIR.parent / "voice.db"

def initialize_database():
    """Create voice.db from schema file."""
    
    # Check if database already exists
    if DB_FILE.exists():
        response = input(f"Database already exists at {DB_FILE}. Overwrite? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted. Database not modified.")
            return
        os.remove(DB_FILE)
        print(f"Deleted existing database: {DB_FILE}")
    
    # Read schema
    with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    # Create database
    print(f"Creating database: {DB_FILE}")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Execute schema (split by semicolons for multiple statements)
        cursor.executescript(schema_sql)
        conn.commit()
        
        # Verify tables created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        print(f"\n✅ Database initialized successfully!")
        print(f"   Location: {DB_FILE}")
        print(f"   Tables created: {len(tables)}")
        for table in tables:
            print(f"   - {table[0]}")
        
        # Check initial data
        cursor.execute("SELECT COUNT(*) FROM forbidden_patterns")
        forbidden_count = cursor.fetchone()[0]
        print(f"\n   Initial data: {forbidden_count} forbidden patterns loaded")
        
        # Check views
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")
        views = cursor.fetchall()
        print(f"   Views created: {len(views)}")
        for view in views:
            print(f"   - {view[0]}")
        
    except sqlite3.Error as e:
        print(f"\n❌ Error initializing database: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()
    
    print("\n✅ Database ready for use!")

if __name__ == "__main__":
    initialize_database()
