"""
Database Cleaner - Maintain voice.db health
Prunes low-value patterns, consolidates duplicates, archives old samples
"""

from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent))
from db_manager import VoiceDatabase

class DatabaseCleaner:
    """Maintain voice database health."""
    
    def __init__(self):
        self.db = VoiceDatabase()
    
    def clean(self, dry_run: bool = False):
        """Run all cleaning operations."""
        
        print("=" * 60)
        print("GHOST WRITER DATABASE CLEANING")
        print("=" * 60)
        
        if dry_run:
            print("\n🔍 DRY RUN MODE - No changes will be made\n")
        
        # 1. Prune low-confidence patterns
        print("\n1. PRUNING LOW-CONFIDENCE PATTERNS")
        self.prune_low_confidence(threshold=0.3, months_inactive=6, dry_run=dry_run)
        
        # 2. Consolidate similar patterns
        print("\n2. CONSOLIDATING SIMILAR PATTERNS")
        self.consolidate_patterns(dry_run=dry_run)
        
        # 3. Archive old samples
        print("\n3. ARCHIVING OLD SAMPLES")
        self.archive_old_samples(months=12, dry_run=dry_run)
        
        # 4. Update statistics
        print("\n4. DATABASE STATISTICS")
        self.print_stats()
        
        print("\n" + "=" * 60)
        print("✅ CLEANING COMPLETE")
        print("=" * 60)
    
    def prune_low_confidence(self, threshold: float = 0.3, months_inactive: int = 6,
                           dry_run: bool = False):
        """Remove patterns with low confidence not seen recently."""
        
        cutoff_date = datetime.now() - timedelta(days=30 * months_inactive)
        cutoff_str = cutoff_date.strftime("%Y-%m-%d %H:%M:%S")
        
        with self.db.connect() as conn:
            cursor = conn.cursor()
            
            # Find patterns to prune
            cursor.execute("""
                SELECT id, pattern_type, pattern_text, confidence, last_seen
                FROM voice_patterns
                WHERE confidence < ?
                  AND last_seen < ?
            """, (threshold, cutoff_str))
            
            patterns = cursor.fetchall()
            
            print(f"   Found {len(patterns)} patterns to prune:")
            print(f"   - Confidence < {threshold}")
            print(f"   - Not seen since {cutoff_str}")
            
            if not dry_run and patterns:
                # Delete patterns
                pattern_ids = [p['id'] for p in patterns]
                placeholders = ','.join('?' * len(pattern_ids))
                cursor.execute(f"""
                    DELETE FROM voice_patterns
                    WHERE id IN ({placeholders})
                """, pattern_ids)
                conn.commit()
                print(f"   ✅ Pruned {len(patterns)} patterns")
            elif dry_run:
                print(f"   [DRY RUN] Would prune {len(patterns)} patterns")
    
    def consolidate_patterns(self, dry_run: bool = False):
        """Consolidate very similar patterns (placeholder)."""
        
        # TODO: Implement fuzzy matching for pattern consolidation
        # For now, just report potential duplicates
        
        with self.db.connect() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT pattern_text, COUNT(*) as count
                FROM voice_patterns
                GROUP BY pattern_text
                HAVING count > 1
            """)
            
            duplicates = cursor.fetchall()
            
            print(f"   Found {len(duplicates)} exact duplicate patterns")
            
            if not dry_run and duplicates:
                print(f"   [TODO] Consolidation logic not yet implemented")
            elif dry_run:
                print(f"   [DRY RUN] Would consolidate {len(duplicates)} patterns")
    
    def archive_old_samples(self, months: int = 12, dry_run: bool = False):
        """Archive samples older than X months."""
        
        cutoff_date = datetime.now() - timedelta(days=30 * months)
        cutoff_str = cutoff_date.strftime("%Y-%m-%d %H:%M:%S")
        
        with self.db.connect() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM voice_samples
                WHERE timestamp < ?
            """, (cutoff_str,))
            
            count = cursor.fetchone()['count']
            
            print(f"   Found {count} samples older than {months} months")
            print(f"   Cutoff date: {cutoff_str}")
            
            if not dry_run and count > 0:
                # TODO: Implement actual archival (compress and move)
                print(f"   [TODO] Archival logic not yet implemented")
            elif dry_run:
                print(f"   [DRY RUN] Would archive {count} samples")
    
    def print_stats(self):
        """Print database statistics."""
        stats = self.db.get_stats()
        
        print(f"   Total samples: {stats['total_samples']}")
        print(f"   Total patterns: {stats['total_patterns']}")
        print(f"   High confidence patterns: {stats['high_confidence_patterns']}")
        print(f"   Extracted: {stats['extracted']}")
        print(f"   Pending extraction: {stats['pending_extraction']}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean Ghost Writer database")
    parser.add_argument('--dry-run', action='store_true', 
                       help="Show what would be done without making changes")
    
    args = parser.parse_args()
    
    cleaner = DatabaseCleaner()
    cleaner.clean(dry_run=args.dry_run)
