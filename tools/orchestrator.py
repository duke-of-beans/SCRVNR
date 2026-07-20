"""
scrvnr Orchestrator - Main workflow coordinator
Handles complete generation workflow from request to delivery
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from learning.scripts.db_manager import VoiceDatabase
from learning.scripts.sample_collector import SampleCollector

class scrvnrOrchestrator:
    """Main workflow coordinator for scrvnr."""

    def __init__(self):
        self.db = VoiceDatabase()
        self.collector = SampleCollector()
        self.environments = ['dev', 'research', 'career', 'work', 'personal']
        self.outputs_dir = Path(__file__).parent.parent / "outputs"
        self.outputs_dir.mkdir(exist_ok=True)

    # ==========================================
    # GENERATE COMMAND
    # ==========================================

    def generate(self, environment: str, context: str, intensity: Optional[int] = None,
                variations: bool = False, output_file: Optional[str] = None) -> Dict:
        """
        Generate content with scrvnr.

        Args:
            environment: dev, research, career, work, personal
            context: Context type (e.g., cover_letter, linkedin_post)
            intensity: Optional 1-10 directness scale
            variations: Generate 3 variations (Direct, Analytical, Balanced)
            output_file: Optional output filename

        Returns:
            Dict with generation results
        """

        print(f"\n[SCRVNR] scrvnr - {environment.upper()} MODE")
        print("=" * 60)

        # Validate environment
        if environment not in self.environments:
            raise ValueError(f"Invalid environment. Must be one of: {self.environments}")

        # Load voice patterns
        print(f"\n[LOAD] Loading voice patterns...")
        patterns = self.db.get_patterns(environment, min_confidence=0.7, limit=20)
        print(f"   Loaded {len(patterns)} high-confidence patterns")

        # Load forbidden patterns
        forbidden = self.db.get_forbidden_patterns(environment)
        print(f"   Loaded {len(forbidden)} forbidden patterns")

        # Load environment calibration
        calibration_path = Path(__file__).parent.parent / f"environments/{environment}/calibration.yaml"
        if calibration_path.exists():
            print(f"   [OK] Environment calibration loaded")
        else:
            print(f"   [WARN] Warning: No calibration file found for {environment}")

        # Create session
        session_id, session_db_id = self.db.create_session(environment)
        print(f"\n[NOTE] Session created: {session_id}")

        print(f"\n[READY] Ready to generate!")
        print(f"   Context: {context}")
        if intensity:
            print(f"   Intensity: {intensity}/10")
        if variations:
            print(f"   Variations: 3 (Direct, Analytical, Balanced)")

        # Note: Actual generation would be done by Claude in the conversation
        # This tool provides the infrastructure and reporting

        return {
            'session_id': session_id,
            'environment': environment,
            'context': context,
            'patterns_loaded': len(patterns),
            'forbidden_loaded': len(forbidden),
            'intensity': intensity,
            'variations': variations,
            'status': 'ready'
        }

    # ==========================================
    # VALIDATE COMMAND
    # ==========================================

    def validate(self, file_path: str, environment: str, verbose: bool = False) -> Dict:
        """
        Validate a generated file against quality gates.

        Args:
            file_path: Path to file to validate
            environment: Environment context
            verbose: Show detailed validation output

        Returns:
            Dict with validation results
        """

        print(f"\n[SCAN] VALIDATING: {file_path}")
        print("=" * 60)

        # Read file
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        print(f"\n[FILE] File loaded: {len(content.split())} words")

        # Run validation checks
        print(f"\n[OK] Running validation checks...")

        results = {
            'file': str(file_path),
            'environment': environment,
            'word_count': len(content.split()),
            'checks': {}
        }

        # Check 1: Contraction rate
        contraction_rate = self._calculate_contraction_rate(content)
        target_rate = self._get_contraction_target(environment)
        contraction_pass = contraction_rate >= target_rate

        results['checks']['contraction_rate'] = {
            'measured': contraction_rate,
            'target': target_rate,
            'pass': contraction_pass
        }

        print(f"   Contraction rate: {contraction_rate:.1%} (target: {target_rate:.1%}) {'[OK]' if contraction_pass else '[FAIL]'}")

        # Check 2: Dash density
        dash_density = self._calculate_dash_density(content)
        dash_pass = dash_density <= 3.0

        results['checks']['dash_density'] = {
            'measured': dash_density,
            'limit': 3.0,
            'pass': dash_pass
        }

        print(f"   Dash density: {dash_density:.1f} per page (limit: 3.0) {'[OK]' if dash_pass else '[FAIL]'}")

        # Check 3: Forbidden patterns
        forbidden = self.db.get_forbidden_patterns(environment, severity='blocking')
        violations = self._scan_forbidden_patterns(content, forbidden)
        forbidden_pass = len(violations) == 0

        results['checks']['forbidden_patterns'] = {
            'violations': len(violations),
            'pass': forbidden_pass
        }

        print(f"   Forbidden patterns: {len(violations)} violations {'[OK]' if forbidden_pass else '[FAIL]'}")

        if violations and verbose:
            for v in violations[:5]:  # Show first 5
                print(f"      - {v['pattern']}: {v['reason']}")

        # Overall result
        all_pass = contraction_pass and dash_pass and forbidden_pass
        results['overall_pass'] = all_pass
        results['score'] = sum([contraction_pass, dash_pass, forbidden_pass]) / 3.0

        print(f"\n{'[OK] VALIDATION PASSED' if all_pass else '[FAIL] VALIDATION FAILED'}")
        print(f"   Score: {results['score']:.1%}")

        return results

    # ==========================================
    # ANALYZE COMMAND
    # ==========================================

    def analyze(self, file_path: str, environment: str) -> Dict:
        """
        Analyze voice characteristics of a file.

        Args:
            file_path: Path to file to analyze
            environment: Environment context

        Returns:
            Dict with analysis results
        """

        print(f"\n[ANALYZE] ANALYZING: {file_path}")
        print("=" * 60)

        # Read file
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        results = {
            'file': str(file_path),
            'environment': environment,
            'metrics': {}
        }

        # Word count
        word_count = len(content.split())
        results['metrics']['word_count'] = word_count
        print(f"\n[STATS] Word count: {word_count}")

        # Sentence count
        sentence_count = content.count('.') + content.count('!') + content.count('?')
        results['metrics']['sentence_count'] = sentence_count
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        results['metrics']['avg_sentence_length'] = avg_sentence_length
        print(f"[STATS] Sentences: {sentence_count} (avg: {avg_sentence_length:.1f} words)")

        # Contraction analysis
        contraction_rate = self._calculate_contraction_rate(content)
        results['metrics']['contraction_rate'] = contraction_rate
        print(f"[STATS] Contraction rate: {contraction_rate:.1%}")

        # Dash density
        dash_density = self._calculate_dash_density(content)
        results['metrics']['dash_density'] = dash_density
        print(f"[STATS] Dash density: {dash_density:.1f} per page")

        # Pattern matching
        patterns = self.db.get_patterns(environment, min_confidence=0.7, limit=50)
        patterns_found = []
        for pattern in patterns:
            if pattern['pattern_text'].lower() in content.lower():
                patterns_found.append(pattern['pattern_text'])

        results['metrics']['patterns_found'] = len(patterns_found)
        print(f"[STATS] Voice patterns: {len(patterns_found)} matched")

        # Voice consistency score (0-1.0)
        target_contraction = self._get_contraction_target(environment)
        contraction_score = 1.0 - min(1.0, abs(contraction_rate - target_contraction) / 0.3)
        dash_score = 1.0 if dash_density <= 3.0 else 0.5
        pattern_score = min(1.0, len(patterns_found) / 10.0)  # Target: 10+ patterns

        voice_consistency = (contraction_score + dash_score + pattern_score) / 3.0
        results['metrics']['voice_consistency'] = voice_consistency

        print(f"\n[SCRVNR] Voice Consistency Score: {voice_consistency:.1%}")

        if voice_consistency >= 0.9:
            print("   [OK] Excellent voice match!")
        elif voice_consistency >= 0.75:
            print("   [OK] Good voice match")
        elif voice_consistency >= 0.6:
            print("   [WARN] Voice needs improvement")
        else:
            print("   [FAIL] Poor voice match")

        return results

    # ==========================================
    # STATUS COMMAND
    # ==========================================

    def status(self) -> Dict:
        """Get scrvnr system status."""

        print("\n[SCRVNR] scrvnr STATUS")
        print("=" * 60)

        # Database stats
        stats = self.db.get_stats()

        print(f"\n[STATS] Database Statistics:")
        print(f"   Total samples: {stats['total_samples']}")
        print(f"   Total patterns: {stats['total_patterns']}")
        print(f"   High confidence patterns: {stats['high_confidence_patterns']}")
        print(f"   Extracted: {stats['extracted']}")
        print(f"   Pending extraction: {stats['pending_extraction']}")

        print(f"\n[DIRS] Samples by environment:")
        for env, count in stats.get('by_environment', {}).items():
            print(f"   - {env}: {count}")

        # Check for unextracted samples
        if stats['pending_extraction'] > 0:
            print(f"\n[WARN] {stats['pending_extraction']} samples pending pattern extraction")
            print(f"   Run: python learning/scripts/pattern_extractor.py")

        return stats

    # ==========================================
    # COLLECT COMMAND
    # ==========================================

    def collect(self, file_path: str, environment: str, context: str,
               quality_score: float = 0.8, tags: List[str] = None) -> Dict:
        """
        Collect a generated file as a sample for learning.

        Args:
            file_path: Path to file to collect
            environment: Environment context
            context: Context type
            quality_score: Quality score (0.0-1.0)
            tags: Context tags

        Returns:
            Dict with collection results
        """

        print(f"\n[SAVE] COLLECTING SAMPLE: {file_path}")
        print("=" * 60)

        # Read file
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Collect
        result = self.collector.collect(
            content=content,
            environment=environment,
            context_type=context,
            quality_score=quality_score,
            context_tags=tags or ['generated']
        )

        print(f"\n[OK] Sample collected!")
        print(f"   Sample ID: {result['sample_id']}")
        print(f"   File saved: {result['file_path']}")

        # Suggest pattern extraction
        print(f"\n[INFO] To extract patterns, run:")
        print(f"   python learning/scripts/pattern_extractor.py")

        return result

    # ==========================================
    # HELPER METHODS
    # ==========================================

    def _calculate_contraction_rate(self, text: str) -> float:
        """Calculate contraction rate in text."""
        contractions = [
            "it's", "you'll", "here's", "that's", "don't", "won't", "can't",
            "isn't", "aren't", "wasn't", "weren't", "haven't", "hasn't",
            "hadn't", "i'm", "you're", "we're", "they're", "i've", "we've",
            "they've", "i'd", "you'd", "we'd", "they'd", "what's", "where's",
            "when's", "who's", "how's", "there's", "let's"
        ]

        text_lower = text.lower()
        count = sum(1 for c in contractions if c in text_lower)

        words = len(text.split())
        opportunities = words / 10  # Rough estimate

        if opportunities == 0:
            return 0.0

        rate = min(1.0, count / opportunities)
        return rate

    def _calculate_dash_density(self, text: str) -> float:
        """Calculate dashes per page."""
        em_dashes = text.count('—')
        en_dashes = text.count('–')
        pause_hyphens = text.count(' - ')

        total_dashes = em_dashes + en_dashes + pause_hyphens

        word_count = len(text.split())
        pages = max(1, word_count / 500)

        return total_dashes / pages

    def _get_contraction_target(self, environment: str) -> float:
        """Get target contraction rate for environment."""
        targets = {
            'dev': 0.65,
            'research': 0.50,
            'career': 0.75,
            'work': 0.75,
            'personal': 0.85
        }
        return targets.get(environment, 0.70)

    def _scan_forbidden_patterns(self, text: str, forbidden: List[Dict]) -> List[Dict]:
        """Scan text for forbidden patterns."""
        violations = []
        text_lower = text.lower()

        for pattern in forbidden:
            if pattern['pattern'].lower() in text_lower:
                violations.append({
                    'pattern': pattern['pattern'],
                    'reason': pattern['reason'],
                    'severity': pattern['severity']
                })

        return violations


# ==========================================
# CLI INTERFACE
# ==========================================

def main():
    parser = argparse.ArgumentParser(
        description="scrvnr Orchestrator - Main workflow coordinator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate content
  python orchestrator.py generate --env career --context cover_letter

  # Generate with variations
  python orchestrator.py generate --env personal --context linkedin_post --variations

  # Validate file
  python orchestrator.py validate output.docx --env career

  # Analyze voice
  python orchestrator.py analyze output.md --env dev

  # Collect sample
  python orchestrator.py collect output.md --env personal --context email

  # Check status
  python orchestrator.py status
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate content')
    gen_parser.add_argument('--env', required=True, choices=['dev', 'research', 'career', 'work', 'personal'])
    gen_parser.add_argument('--context', required=True, help='Context type (e.g., cover_letter, email)')
    gen_parser.add_argument('--intensity', type=int, choices=range(1, 11), help='Directness level (1-10)')
    gen_parser.add_argument('--variations', action='store_true', help='Generate 3 variations')
    gen_parser.add_argument('--output', help='Output filename')

    # Validate command
    val_parser = subparsers.add_parser('validate', help='Validate file')
    val_parser.add_argument('file', help='File to validate')
    val_parser.add_argument('--env', required=True, choices=['dev', 'research', 'career', 'work', 'personal'])
    val_parser.add_argument('--verbose', action='store_true', help='Show detailed output')

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze voice')
    analyze_parser.add_argument('file', help='File to analyze')
    analyze_parser.add_argument('--env', required=True, choices=['dev', 'research', 'career', 'work', 'personal'])

    # Collect command
    collect_parser = subparsers.add_parser('collect', help='Collect sample')
    collect_parser.add_argument('file', help='File to collect')
    collect_parser.add_argument('--env', required=True, choices=['dev', 'research', 'career', 'work', 'personal'])
    collect_parser.add_argument('--context', required=True, help='Context type')
    collect_parser.add_argument('--quality', type=float, default=0.8, help='Quality score (0.0-1.0)')
    collect_parser.add_argument('--tags', nargs='*', help='Context tags')

    # Status command
    subparsers.add_parser('status', help='Show system status')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    orchestrator = scrvnrOrchestrator()

    try:
        if args.command == 'generate':
            result = orchestrator.generate(
                environment=args.env,
                context=args.context,
                intensity=args.intensity,
                variations=args.variations,
                output_file=args.output
            )

        elif args.command == 'validate':
            result = orchestrator.validate(
                file_path=args.file,
                environment=args.env,
                verbose=args.verbose
            )

        elif args.command == 'analyze':
            result = orchestrator.analyze(
                file_path=args.file,
                environment=args.env
            )

        elif args.command == 'collect':
            result = orchestrator.collect(
                file_path=args.file,
                environment=args.env,
                context=args.context,
                quality_score=args.quality,
                tags=args.tags
            )

        elif args.command == 'status':
            result = orchestrator.status()

    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
