"""
Voice Analyzer - Calculate voice authenticity and identify drift
Implements voice-confidence-scorer.md specification
"""

import sys
from pathlib import Path
from typing import Dict, List

sys.path.append(str(Path(__file__).parent.parent / "learning" / "scripts"))
from db_manager import VoiceDatabase

class VoiceAnalyzer:
    """Analyze voice authenticity of text."""
    
    def __init__(self):
        self.db = VoiceDatabase()
    
    def analyze(self, text: str, environment: str) -> Dict:
        """
        Calculate voice confidence score.
        
        Returns score breakdown with specific concerns and suggestions.
        """
        
        # Load environment calibration
        calibration = self._load_calibration(environment)
        
        # Calculate metrics
        formality_score = self._score_formality(text, calibration)
        directness_score = self._score_directness(text, calibration)
        contraction_score = self._score_contractions(text, calibration)
        authenticity_score = self._score_authenticity_markers(text, environment)
        forbidden_score = self._score_forbidden_patterns(text, environment)
        
        # Overall confidence (weighted average)
        overall = (
            formality_score['normalized'] * 0.20 +
            directness_score['normalized'] * 0.20 +
            contraction_score['normalized'] * 0.25 +
            authenticity_score['normalized'] * 0.25 +
            forbidden_score['normalized'] * 0.10
        )
        
        # Generate concerns
        concerns = self._generate_concerns(
            formality_score, directness_score, contraction_score,
            authenticity_score, forbidden_score
        )
        
        # Determine confidence level
        if overall >= 0.8:
            level = "high"
        elif overall >= 0.6:
            level = "good"
        else:
            level = "needs_work"
        
        return {
            'overall_confidence': round(overall, 2),
            'confidence_level': level,
            'breakdown': {
                'formality': formality_score,
                'directness': directness_score,
                'contraction_rate': contraction_score,
                'authenticity_markers': authenticity_score,
                'forbidden_patterns': forbidden_score
            },
            'concerns': concerns
        }
    
    def _load_calibration(self, environment: str) -> Dict:
        """Load environment calibration targets."""
        defaults = {
            'dev': {'formality': 6, 'directness': 8, 'contraction_target': 0.65},
            'research': {'formality': 8, 'directness': 7, 'contraction_target': 0.50},
            'career': {'formality': 7, 'directness': 9, 'contraction_target': 0.75},
            'work': {'formality': 7, 'directness': 8, 'contraction_target': 0.75},
            'personal': {'formality': 4, 'directness': 8, 'contraction_target': 0.85},
        }
        return defaults.get(environment, defaults['dev'])
    
    def _score_formality(self, text: str, calibration: Dict) -> Dict:
        """Score formality (simplified estimation)."""
        # Count formality indicators
        formal_indicators = ['however', 'therefore', 'furthermore', 'moreover', 'nevertheless']
        casual_indicators = ["it's", "you're", "gonna", "wanna"]
        
        text_lower = text.lower()
        formal_count = sum(1 for word in formal_indicators if word in text_lower)
        casual_count = sum(1 for word in casual_indicators if word in text_lower)
        
        # Estimate formality 1-10
        if casual_count > formal_count:
            measured = 5 - min(3, casual_count - formal_count)
        else:
            measured = 5 + min(3, formal_count - casual_count)
        
        target = calibration['formality']
        delta = measured - target
        
        # Normalize (1.0 = on target, 0.0 = 5+ away)
        normalized = max(0.0, 1.0 - abs(delta) / 5.0)
        
        return {
            'score': measured,
            'target': target,
            'delta': delta,
            'normalized': normalized
        }
    
    def _score_directness(self, text: str, calibration: Dict) -> Dict:
        """Score directness (simplified estimation)."""
        # Count hedging vs direct language
        hedging = ['perhaps', 'maybe', 'possibly', 'might', 'I think', 'I believe']
        direct = ['must', 'should', 'need to', 'use', 'run', 'call']
        
        text_lower = text.lower()
        hedging_count = sum(1 for word in hedging if word in text_lower)
        direct_count = sum(1 for word in direct if word in text_lower)
        
        # Estimate directness 1-10
        if direct_count > hedging_count:
            measured = 6 + min(4, direct_count - hedging_count)
        else:
            measured = 6 - min(4, hedging_count - direct_count)
        
        target = calibration['directness']
        delta = measured - target
        
        normalized = max(0.0, 1.0 - abs(delta) / 5.0)
        
        return {
            'score': measured,
            'target': target,
            'delta': delta,
            'normalized': normalized
        }
    
    def _score_contractions(self, text: str, calibration: Dict) -> Dict:
        """Score contraction usage."""
        contractions = [
            "it's", "you'll", "here's", "that's", "don't", "won't", "can't",
            "isn't", "aren't", "wasn't", "weren't", "haven't", "hasn't",
            "i'm", "you're", "we're", "they're"
        ]
        
        text_lower = text.lower()
        count = sum(1 for c in contractions if c in text_lower)
        
        # Estimate opportunities
        words = len(text.split())
        opportunities = max(1, words / 10)
        
        measured = min(1.0, count / opportunities)
        target = calibration['contraction_target']
        delta = measured - target
        
        # Normalize (±30% tolerance)
        normalized = max(0.0, 1.0 - abs(delta) / 0.3)
        
        return {
            'measured': round(measured, 2),
            'target': target,
            'delta': round(delta, 2),
            'count': count,
            'opportunities': int(opportunities),
            'normalized': normalized
        }
    
    def _score_authenticity_markers(self, text: str, environment: str) -> Dict:
        """Score presence of authentic voice patterns."""
        # Query database for expected patterns
        patterns = self.db.get_patterns(environment, min_confidence=0.7, limit=20)
        
        # Check which are present
        text_lower = text.lower()
        present = []
        missing = []
        
        for pattern in patterns:
            if pattern['pattern_text'].lower() in text_lower:
                present.append(pattern['pattern_text'])
            else:
                missing.append(pattern['pattern_text'])
        
        # Normalize
        total_expected = len(patterns)
        normalized = len(present) / total_expected if total_expected > 0 else 0.0
        
        return {
            'present': present[:5],  # First 5 for display
            'missing': missing[:3],  # First 3 for display
            'count': len(present),
            'total_expected': total_expected,
            'normalized': normalized
        }
    
    def _score_forbidden_patterns(self, text: str, environment: str) -> Dict:
        """Check for forbidden patterns."""
        forbidden = self.db.get_forbidden_patterns(environment, severity='blocking')
        
        violations = []
        text_lower = text.lower()
        
        for pattern in forbidden:
            if pattern['pattern'].lower() in text_lower:
                violations.append({
                    'pattern': pattern['pattern'],
                    'reason': pattern['reason']
                })
        
        # Binary: 1.0 if clean, 0.0 if violations
        normalized = 1.0 if len(violations) == 0 else 0.0
        
        return {
            'violations': violations,
            'count': len(violations),
            'normalized': normalized
        }
    
    def _generate_concerns(self, formality, directness, contractions,
                          authenticity, forbidden) -> List[Dict]:
        """Generate specific concerns with suggestions."""
        concerns = []
        
        # Formality concerns
        if abs(formality['delta']) >= 2:
            direction = "too formal" if formality['delta'] > 0 else "too casual"
            concerns.append({
                'description': f"Formality is {direction}",
                'severity': 'moderate' if abs(formality['delta']) < 3 else 'major',
                'suggestion': f"Target: {formality['target']}/10, measured: {formality['score']}/10"
            })
        
        # Directness concerns
        if abs(directness['delta']) >= 2:
            direction = "too direct" if directness['delta'] > 0 else "too hedged"
            concerns.append({
                'description': f"Directness is {direction}",
                'severity': 'moderate',
                'suggestion': f"Target: {directness['target']}/10, measured: {directness['score']}/10"
            })
        
        # Contraction concerns
        if contractions['delta'] < -0.15:
            concerns.append({
                'description': f"Contraction rate too low ({contractions['measured']:.0%})",
                'severity': 'moderate',
                'suggestion': f"Target: {contractions['target']:.0%}. Add contractions like: it's, you'll, here's"
            })
        
        # Authenticity concerns
        if authenticity['count'] < 5:
            concerns.append({
                'description': f"Missing authentic patterns ({authenticity['count']}/{authenticity['total_expected']})",
                'severity': 'moderate',
                'suggestion': f"Consider: {', '.join(authenticity['missing'][:3])}"
            })
        
        # Forbidden pattern concerns
        for violation in forbidden['violations']:
            concerns.append({
                'description': f"Forbidden pattern: '{violation['pattern']}'",
                'severity': 'major',
                'suggestion': f"Remove or rephrase: {violation['reason']}"
            })
        
        return concerns


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze voice authenticity")
    parser.add_argument('file', help="File to analyze")
    parser.add_argument('environment', choices=['dev', 'research', 'career', 'work', 'personal'])
    
    args = parser.parse_args()
    
    # Read file
    with open(args.file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Analyze
    analyzer = VoiceAnalyzer()
    result = analyzer.analyze(text, args.environment)
    
    # Display
    print(f"\n[ANALYZE] VOICE ANALYSIS")
    print("=" * 60)
    print(f"\n[TARGET] Overall Confidence: {result['overall_confidence']:.0%} ({result['confidence_level']})")

    print(f"\n[STATS] Breakdown:")
    for metric, scores in result['breakdown'].items():
        print(f"\n   {metric}:")
        for key, value in scores.items():
            if key != 'normalized':
                print(f"      {key}: {value}")

    if result['concerns']:
        print(f"\n[WARN] Concerns ({len(result['concerns'])}):")
        for concern in result['concerns']:
            print(f"\n   [{concern['severity']}] {concern['description']}")
            print(f"   -> {concern['suggestion']}")
    else:
        print(f"\n[OK] No concerns - voice is authentic!")
