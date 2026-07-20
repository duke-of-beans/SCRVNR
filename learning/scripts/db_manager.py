"""
Database Manager - CRUD operations for voice.db
Provides high-level interface for querying and updating voice patterns, samples, and insights.
"""

import sqlite3
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# Database location
DB_PATH = Path(__file__).parent.parent / "voice.db"

class VoiceDatabase:
    """Interface for Ghost Writer voice database."""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        
    def connect(self) -> sqlite3.Connection:
        """Create database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dicts
        return conn
    
    # ==========================================
    # VOICE PATTERNS
    # ==========================================
    
    def get_patterns(self, environment: str, min_confidence: float = 0.7, limit: int = 20) -> List[Dict]:
        """Get high-confidence patterns for environment."""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT pattern_type, pattern_text, confidence, frequency, context
                FROM voice_patterns
                WHERE (environment = ? OR environment = 'universal')
                  AND confidence >= ?
                ORDER BY confidence DESC, frequency DESC
                LIMIT ?
            """, (environment, min_confidence, limit))
            return [dict(row) for row in cursor.fetchall()]
    
    def add_pattern(self, pattern_type: str, pattern_text: str, environment: str,
                   confidence: float = 0.5, context: str = None,
                   source_sample_id: int = None) -> int:
        """Add or update a voice pattern."""
        with self.connect() as conn:
            cursor = conn.cursor()
            
            # Check if pattern exists
            cursor.execute("""
                SELECT id, frequency, source_samples
                FROM voice_patterns
                WHERE pattern_type = ? AND pattern_text = ? AND environment = ?
            """, (pattern_type, pattern_text, environment))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing pattern
                pattern_id = existing['id']
                new_frequency = existing['frequency'] + 1
                
                # Update source samples list
                source_samples = json.loads(existing['source_samples'] or '[]')
                if source_sample_id and source_sample_id not in source_samples:
                    source_samples.append(source_sample_id)
                
                cursor.execute("""
                    UPDATE voice_patterns
                    SET frequency = ?,
                        last_seen = CURRENT_TIMESTAMP,
                        source_samples = ?,
                        confidence = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (new_frequency, json.dumps(source_samples), confidence, pattern_id))
            else:
                # Insert new pattern
                source_samples = [source_sample_id] if source_sample_id else []
                cursor.execute("""
                    INSERT INTO voice_patterns 
                    (pattern_type, pattern_text, environment, confidence, context, source_samples)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (pattern_type, pattern_text, environment, confidence, context, 
                     json.dumps(source_samples)))
                pattern_id = cursor.lastrowid
            
            conn.commit()
            return pattern_id
    
    # ==========================================
    # VOICE SAMPLES
    # ==========================================
    
    def add_sample(self, content: str, environment: str, context_type: str,
                  file_path: str, word_count: int, contraction_rate: float,
                  dash_density: float, quality_score: float,
                  context_tags: List[str]) -> Optional[int]:
        """Add a voice sample (with deduplication)."""
        
        # Generate content hash
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        with self.connect() as conn:
            cursor = conn.cursor()
            
            # Check for duplicate
            cursor.execute("SELECT id FROM voice_samples WHERE content_hash = ?", (content_hash,))
            existing = cursor.fetchone()
            
            if existing:
                print(f"Sample already exists (ID: {existing['id']}), skipping.")
                return None
            
            # Insert new sample
            cursor.execute("""
                INSERT INTO voice_samples
                (content_hash, content, environment, context_type, word_count,
                 contraction_rate, dash_density, quality_score, context_tags, file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (content_hash, content, environment, context_type, word_count,
                 contraction_rate, dash_density, quality_score,
                 json.dumps(context_tags), file_path))
            
            sample_id = cursor.lastrowid
            conn.commit()
            return sample_id
    
    def get_unextracted_samples(self, limit: int = 10) -> List[Dict]:
        """Get samples that haven't had patterns extracted yet."""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, content, environment, context_type, file_path
                FROM voice_samples
                WHERE extracted = 0
                ORDER BY timestamp ASC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def mark_sample_extracted(self, sample_id: int):
        """Mark sample as having patterns extracted."""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE voice_samples
                SET extracted = 1
                WHERE id = ?
            """, (sample_id,))
            conn.commit()
    
    # ==========================================
    # FORBIDDEN PATTERNS
    # ==========================================
    
    def get_forbidden_patterns(self, environment: Optional[str] = None, 
                              severity: Optional[str] = None) -> List[Dict]:
        """Get forbidden patterns (optionally filtered)."""
        with self.connect() as conn:
            cursor = conn.cursor()
            
            query = "SELECT pattern, reason, severity, category FROM forbidden_patterns WHERE 1=1"
            params = []
            
            if environment:
                query += " AND (environment = ? OR environment IS NULL)"
                params.append(environment)
            
            if severity:
                query += " AND severity = ?"
                params.append(severity)
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    # ==========================================
    # LEARNING INSIGHTS
    # ==========================================
    
    def add_insight(self, insight_type: str, description: str,
                   evidence: Dict, confidence: float,
                   environment: Optional[str] = None,
                   source_samples: List[int] = None) -> int:
        """Add a learning insight."""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO learning_insights
                (insight_type, description, evidence, confidence, environment, source_samples)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (insight_type, description, json.dumps(evidence), confidence,
                 environment, json.dumps(source_samples or [])))
            
            insight_id = cursor.lastrowid
            conn.commit()
            return insight_id
    
    def get_unapplied_insights(self, limit: int = 10) -> List[Dict]:
        """Get insights that haven't been applied to protocols yet."""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, insight_type, description, evidence, confidence, environment
                FROM learning_insights
                WHERE applied = 0
                ORDER BY confidence DESC, timestamp DESC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    # ==========================================
    # SESSION TRACKING
    # ==========================================
    
    def create_session(self, environment: str) -> Tuple[str, int]:
        """Create a new session, return (session_id, db_id)."""
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO session_log (session_id, environment)
                VALUES (?, ?)
            """, (session_id, environment))
            
            db_id = cursor.lastrowid
            conn.commit()
            return session_id, db_id
    
    def update_session(self, session_id: str, samples_generated: int,
                      quality_avg: float, notes: str):
        """Update session with final stats."""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE session_log
                SET samples_generated = ?,
                    quality_avg = ?,
                    notes = ?,
                    end_time = CURRENT_TIMESTAMP,
                    status = 'complete'
                WHERE session_id = ?
            """, (samples_generated, quality_avg, notes, session_id))
            conn.commit()
    
    # ==========================================
    # STATISTICS
    # ==========================================
    
    def get_stats(self) -> Dict:
        """Get database statistics."""
        with self.connect() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Total samples
            cursor.execute("SELECT COUNT(*) as count FROM voice_samples")
            stats['total_samples'] = cursor.fetchone()['count']
            
            # Samples by environment
            cursor.execute("""
                SELECT environment, COUNT(*) as count
                FROM voice_samples
                GROUP BY environment
            """)
            stats['by_environment'] = {row['environment']: row['count'] 
                                      for row in cursor.fetchall()}
            
            # Extracted vs pending
            cursor.execute("SELECT COUNT(*) as count FROM voice_samples WHERE extracted = 1")
            stats['extracted'] = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM voice_samples WHERE extracted = 0")
            stats['pending_extraction'] = cursor.fetchone()['count']
            
            # Total patterns
            cursor.execute("SELECT COUNT(*) as count FROM voice_patterns")
            stats['total_patterns'] = cursor.fetchone()['count']
            
            # High confidence patterns
            cursor.execute("SELECT COUNT(*) as count FROM voice_patterns WHERE confidence > 0.7")
            stats['high_confidence_patterns'] = cursor.fetchone()['count']
            
            return stats


# ==========================================
# CLI INTERFACE
# ==========================================

if __name__ == "__main__":
    import sys
    
    db = VoiceDatabase()
    
    if len(sys.argv) < 2:
        print("Usage: python db_manager.py <command> [args]")
        print("\nCommands:")
        print("  get-patterns <environment> [min_confidence] [limit]")
        print("  get-forbidden [environment] [severity]")
        print("  stats")
        print("  unextracted [limit]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "get-patterns":
        env = sys.argv[2] if len(sys.argv) > 2 else "personal"
        min_conf = float(sys.argv[3]) if len(sys.argv) > 3 else 0.7
        limit = int(sys.argv[4]) if len(sys.argv) > 4 else 20
        
        patterns = db.get_patterns(env, min_conf, limit)
        print(f"\nHigh-confidence patterns for {env}:")
        for p in patterns:
            print(f"  [{p['pattern_type']}] {p['pattern_text']} (confidence: {p['confidence']:.2f}, freq: {p['frequency']})")
    
    elif command == "get-forbidden":
        env = sys.argv[2] if len(sys.argv) > 2 else None
        severity = sys.argv[3] if len(sys.argv) > 3 else None
        
        forbidden = db.get_forbidden_patterns(env, severity)
        print(f"\nForbidden patterns:")
        for p in forbidden:
            print(f"  [{p['severity']}] {p['pattern']} - {p['reason']}")
    
    elif command == "stats":
        stats = db.get_stats()
        print("\nDatabase Statistics:")
        print(f"  Total samples: {stats['total_samples']}")
        print(f"  By environment:")
        for env, count in stats['by_environment'].items():
            print(f"    - {env}: {count}")
        print(f"  Extracted: {stats['extracted']}")
        print(f"  Pending extraction: {stats['pending_extraction']}")
        print(f"  Total patterns: {stats['total_patterns']}")
        print(f"  High confidence patterns: {stats['high_confidence_patterns']}")
    
    elif command == "unextracted":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        samples = db.get_unextracted_samples(limit)
        print(f"\nSamples pending extraction ({len(samples)}):")
        for s in samples:
            print(f"  [{s['id']}] {s['environment']} - {s['context_type']} ({s['file_path']})")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
