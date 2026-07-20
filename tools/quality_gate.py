"""
Quality Gate - Fast automated validation with line-level feedback
Implements automated-checker.md specification
"""

import re
import sys
import os
from typing import Dict, List, Tuple
from pathlib import Path

# Add project root to path for centrifuge import
sys.path.insert(0, str(Path(__file__).parent.parent))
try:
    from core.centrifuge import VoiceCentrifuge
    _HAS_CENTRIFUGE = True
except ImportError:
    _HAS_CENTRIFUGE = False

class QualityGate:
    """Automated quality checks with pass/fail and line-level feedback."""
    
    # Environment to register mapping for centrifuge
    ENV_REGISTER_MAP = {
        'dev': 'TECH',
        'research': 'ACADEMIC',
        'career': 'PROFESSIONAL',
        'work': 'PROFESSIONAL',
        'personal': 'PERSONAL',
    }

    def __init__(self, voice_db_path: str = None):
        # Initialize centrifuge if available
        self._centrifuge = None
        if _HAS_CENTRIFUGE:
            try:
                self._centrifuge = VoiceCentrifuge(db_path=voice_db_path)
            except Exception:
                pass
        # Standard contractions to check for
        self.contractions = [
            "it's", "you'll", "here's", "that's", "don't", "won't", "can't",
            "isn't", "aren't", "wasn't", "weren't", "haven't", "hasn't",
            "hadn't", "i'm", "you're", "we're", "they're", "i've", "we've",
            "they've", "i'd", "you'd", "we'd", "they'd", "what's", "where's",
            "when's", "who's", "how's", "there's", "let's"
        ]
        
        # Forbidden patterns (subset - full list in voice.db)
        self.forbidden_blocking = [
            'based on my memories', 'according to my memories', 'from my memories',
            "david's project", "his experience", "david's work"
        ]
        
        self.forbidden_warning = [
            'spearheaded', 'leveraged', 'synergies', 'passionate about',
            'results-driven', 'team player', 'detail-oriented'
        ]
        
        # Weak verbs (career mode only)
        self.weak_verbs = {
            'achieved': 'hit',
            'managed': 'ran/owned',
            'handled': 'processed/resolved',
            'worked on': 'built/designed',
            'responsible for': 'owned/ran'
        }
    
    def validate(self, text: str, environment: str, mode: str = 'application') -> Dict:
        """
        Run all quality checks.
        
        Args:
            text: Content to validate
            environment: Environment context
            mode: application|professional|casual
        
        Returns:
            Dict with overall_pass, score, violations, suggestions
        """
        
        lines = text.split('\n')
        
        results = {
            'overall_pass': False,
            'score': 0.0,
            'checks': {},
            'violations': [],
            'suggestions': []
        }
        
        # Check 1: Contraction rate
        contraction_check = self._check_contraction_rate(text, lines, environment)
        results['checks']['contraction_rate'] = contraction_check
        
        # Check 2: Dash density
        dash_check = self._check_dash_density(text, lines)
        results['checks']['dash_density'] = dash_check
        
        # Check 3: Forbidden patterns
        forbidden_check = self._check_forbidden_patterns(text, lines)
        results['checks']['forbidden_patterns'] = forbidden_check
        
        # Check 4: Rhetorical questions
        rhetorical_check = self._check_rhetorical_questions(text, lines, mode)
        results['checks']['rhetorical_questions'] = rhetorical_check
        
        # Check 5: Expert audience (no condescension)
        expert_check = self._check_expert_audience(text, lines)
        results['checks']['expert_audience'] = expert_check
        
        # Check 6: Third-person self-references
        third_person_check = self._check_third_person(text, lines)
        results['checks']['third_person'] = third_person_check
        
        # Check 7: Weak verbs (career only, warning)
        if environment == 'career':
            weak_verb_check = self._check_weak_verbs(text, lines)
            results['checks']['weak_verbs'] = weak_verb_check
        
        # Check 8: Voice profile alignment (centrifuge)
        centrifuge_check = self._check_centrifuge(text, environment)
        results['checks']['voice_profile'] = centrifuge_check
        
        # Calculate score
        checks = [contraction_check, dash_check, forbidden_check, 
                 rhetorical_check, expert_check, third_person_check,
                 centrifuge_check]
        passed = sum(1 for c in checks if c['pass'])
        total = len(checks)
        
        results['score'] = passed / total
        results['overall_pass'] = all(c['pass'] for c in checks)
        
        # Collect violations and suggestions
        for check_name, check in results['checks'].items():
            if not check['pass']:
                for v in check.get('violations', []):
                    results['violations'].append({
                        'check': check_name,
                        **v
                    })
                if 'suggestion' in check:
                    results['suggestions'].append({
                        'check': check_name,
                        'suggestion': check['suggestion']
                    })
        
        return results
    
    def _check_contraction_rate(self, text: str, lines: List[str], environment: str) -> Dict:
        """Check if contraction rate meets minimum."""
        targets = {
            'dev': 0.40,
            'research': 0.40,
            'career': 0.60,
            'work': 0.60,
            'personal': 0.70
        }
        
        minimum = targets.get(environment, 0.40)
        
        text_lower = text.lower()
        count = sum(1 for c in self.contractions if c in text_lower)
        
        words = len(text.split())
        opportunities = max(1, words / 10)
        rate = count / opportunities
        
        passed = rate >= minimum
        
        return {
            'pass': passed,
            'measured': round(rate, 2),
            'minimum': minimum,
            'suggestion': f"Add more contractions (measured: {rate:.0%}, minimum: {minimum:.0%})" if not passed else None
        }
    
    def _check_dash_density(self, text: str, lines: List[str]) -> Dict:
        """Check dash density ≤3 per page."""
        em_dashes = text.count('—')
        en_dashes = text.count('–')
        pause_hyphens = text.count(' - ')
        
        total_dashes = em_dashes + en_dashes + pause_hyphens
        words = len(text.split())
        pages = max(1, words / 500)
        density = total_dashes / pages
        
        passed = density <= 3.0
        
        violations = []
        if not passed:
            # Find lines with dashes
            for i, line in enumerate(lines, 1):
                if '—' in line or '–' in line or ' - ' in line:
                    violations.append({
                        'line': i,
                        'excerpt': line[:80] + '...' if len(line) > 80 else line
                    })
        
        return {
            'pass': passed,
            'measured': round(density, 1),
            'limit': 3.0,
            'violations': violations[:5],  # Show first 5
            'suggestion': f"Reduce dash usage ({density:.1f} per page, limit: 3.0)" if not passed else None
        }
    
    def _check_forbidden_patterns(self, text: str, lines: List[str]) -> Dict:
        """Check for forbidden patterns."""
        text_lower = text.lower()
        violations = []
        
        # Check blocking patterns
        for pattern in self.forbidden_blocking:
            if pattern.lower() in text_lower:
                # Find lines
                for i, line in enumerate(lines, 1):
                    if pattern.lower() in line.lower():
                        violations.append({
                            'line': i,
                            'pattern': pattern,
                            'severity': 'blocking',
                            'excerpt': line[:80] + '...' if len(line) > 80 else line
                        })
        
        # Check warning patterns
        for pattern in self.forbidden_warning:
            if pattern.lower() in text_lower:
                for i, line in enumerate(lines, 1):
                    if pattern.lower() in line.lower():
                        violations.append({
                            'line': i,
                            'pattern': pattern,
                            'severity': 'warning',
                            'excerpt': line[:80] + '...' if len(line) > 80 else line
                        })
        
        passed = len([v for v in violations if v['severity'] == 'blocking']) == 0
        
        return {
            'pass': passed,
            'violations': violations[:10],  # Show first 10
            'suggestion': "Remove forbidden patterns" if not passed else None
        }
    
    def _check_rhetorical_questions(self, text: str, lines: List[str], mode: str) -> Dict:
        """Check rhetorical questions (max 1 if opening hook)."""
        if mode == 'casual':
            # Allowed in casual mode
            return {'pass': True}
        
        # Find question marks
        violations = []
        for i, line in enumerate(lines, 1):
            if '?' in line:
                # Check if rhetorical (doesn't end in quoted text)
                if not re.search(r'["\'].*\?["\']', line):
                    violations.append({
                        'line': i,
                        'excerpt': line[:80] + '...' if len(line) > 80 else line
                    })
        
        # Allow 1 rhetorical question at start (opening hook)
        if len(violations) == 1 and violations[0]['line'] <= 3:
            passed = True
        else:
            passed = len(violations) == 0
        
        return {
            'pass': passed,
            'violations': violations,
            'suggestion': "Remove rhetorical questions (or limit to 1 opening hook)" if not passed else None
        }
    
    def _check_expert_audience(self, text: str, lines: List[str]) -> Dict:
        """Check for condescending language."""
        condescending = [
            'simply put', 'as you can see', 'obviously', 'clearly',
            'it goes without saying', 'needless to say', 'of course',
            'as everyone knows', 'to be honest'
        ]
        
        text_lower = text.lower()
        violations = []
        
        for pattern in condescending:
            if pattern in text_lower:
                for i, line in enumerate(lines, 1):
                    if pattern in line.lower():
                        violations.append({
                            'line': i,
                            'pattern': pattern,
                            'excerpt': line[:80] + '...' if len(line) > 80 else line
                        })
        
        passed = len(violations) == 0
        
        return {
            'pass': passed,
            'violations': violations[:5],
            'suggestion': "Remove condescending language" if not passed else None
        }
    
    def _check_third_person(self, text: str, lines: List[str]) -> Dict:
        """Check for third-person self-references."""
        patterns = [
            r"\bdavid'?s\b", r"\bhis\s+\w+", r"\bhe\s+\w+"
        ]
        
        violations = []
        for i, line in enumerate(lines, 1):
            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append({
                        'line': i,
                        'pattern': pattern,
                        'excerpt': line[:80] + '...' if len(line) > 80 else line
                    })
        
        passed = len(violations) == 0
        
        return {
            'pass': passed,
            'violations': violations[:5],
            'suggestion': "Use first-person (I/my) not third-person (David's/his)" if not passed else None
        }
    
    def _check_weak_verbs(self, text: str, lines: List[str]) -> Dict:
        """Check for weak verbs (career mode, warning only)."""
        violations = []
        
        text_lower = text.lower()
        for weak, strong in self.weak_verbs.items():
            if weak in text_lower:
                for i, line in enumerate(lines, 1):
                    if weak in line.lower():
                        violations.append({
                            'line': i,
                            'weak': weak,
                            'suggested': strong,
                            'excerpt': line[:80] + '...' if len(line) > 80 else line
                        })
        
        # Warning only, not blocking
        return {
            'pass': True,  # Never fails
            'violations': violations[:5],
            'suggestion': "Consider stronger verbs (warning only)" if violations else None
        }


    def _check_centrifuge(self, text: str, environment: str) -> Dict:
        """Check 8: Voice profile alignment via centrifuge scoring."""
        if not self._centrifuge:
            return {
                'pass': True,
                'skipped': True,
                'suggestion': 'Centrifuge not available (wordfreq/nltk missing?)'
            }
        
        register = self.ENV_REGISTER_MAP.get(environment, 'TECH')
        result = self._centrifuge.score(text, register)
        overall = result['overall_score']
        
        if overall >= 0.65:
            passed = True
            severity = None
        elif overall >= 0.50:
            passed = True  # WARN but still passes
            severity = 'warning'
        else:
            passed = False
            severity = 'fail'
        
        violations = []
        for flag in result.get('flags', []):
            violations.append({
                'line': 0,
                'pattern': flag.get('type', ''),
                'excerpt': flag.get('suggestion', ''),
                'severity': severity or 'info'
            })
        
        suggestion = None
        if severity == 'warning':
            suggestion = f"Voice profile WARN ({overall:.2f}) - review centrifuge flags"
        elif severity == 'fail':
            suggestion = f"Voice profile FAIL ({overall:.2f}) - rewrite with flag adjustments"
        
        return {
            'pass': passed,
            'measured': round(overall, 2),
            'sub_scores': {
                'rarity': result['rarity_score'],
                'rhythm': result['rhythm_score'],
                'style': result['style_score'],
            },
            'register': register,
            'violations': violations,
            'suggestion': suggestion,
        }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run quality gates on file")
    parser.add_argument('file', help="File to validate")
    parser.add_argument('--env', default='personal', 
                       choices=['dev', 'research', 'career', 'work', 'personal'])
    parser.add_argument('--mode', default='application',
                       choices=['application', 'professional', 'casual'])
    
    args = parser.parse_args()
    
    # Read file
    with open(args.file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Validate
    gate = QualityGate()
    result = gate.validate(text, args.env, args.mode)
    
    # Display
    print("\n[GATE] QUALITY GATE RESULTS")
    print("=" * 60)
    print(f"\nOverall: {'[OK] PASS' if result['overall_pass'] else '[FAIL] FAIL'}")
    print(f"Score: {result['score']:.0%} ({sum(1 for c in result['checks'].values() if c['pass'])}/{len(result['checks'])} checks passed)")

    print("\n[LIST] Check Results:")
    for check_name, check in result['checks'].items():
        status = "[OK]" if check['pass'] else "[FAIL]"
        print(f"   {status} {check_name}")

    if result['violations']:
        print(f"\n[WARN] Violations ({len(result['violations'])}):")
        for v in result['violations'][:10]:
            print(f"\n   Line {v['line']} ({v['check']}):")
            print(f"      {v['excerpt']}")

    if result['suggestions']:
        print(f"\n[INFO] Suggestions:")
        for s in result['suggestions']:
            print(f"   - {s['suggestion']}")
