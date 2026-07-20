"""
Environment Detector - Auto-detect appropriate environment from context
"""

import re
from typing import Dict, List, Tuple

class EnvironmentDetector:
    """Detect which Ghost Writer environment to use based on context clues."""
    
    def __init__(self):
        # Keywords that strongly indicate each environment
        self.indicators = {
            'career': [
                'cover letter', 'resume', 'job application', 'hiring manager',
                'interviewing for', 'position', 'recruiter', 'career',
                'applying for', 'role at', 'opportunity at'
            ],
            'personal': [
                'linkedin post', 'social media', 'facebook', 'twitter',
                'instagram', 'personal email', 'family', 'friend',
                'wedding', 'birthday', 'celebration'
            ],
            'dev': [
                'readme', 'documentation', 'api', 'code', 'function',
                'class', 'module', 'repository', 'github', 'technical doc',
                'architecture', 'implementation', 'pull request'
            ],
            'research': [
                'paper', 'study', 'research', 'analysis', 'hypothesis',
                'methodology', 'literature review', 'findings', 'conclusion',
                'academic', 'journal', 'publication'
            ],
            'work': [
                'proposal', 'business', 'client', 'stakeholder', 'meeting',
                'presentation', 'strategy', 'quarterly', 'revenue',
                'partnership', 'contract', 'vendor'
            ]
        }
    
    def detect(self, query: str, context: Dict = None) -> Tuple[str, float]:
        """
        Detect environment from user query and optional context.
        
        Args:
            query: User's request (e.g., "write a cover letter")
            context: Optional context dict with hints (file_path, previous_env, etc.)
        
        Returns:
            Tuple of (environment, confidence) where confidence is 0.0-1.0
        """
        
        query_lower = query.lower()
        
        # Score each environment
        scores = {}
        for env, keywords in self.indicators.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            scores[env] = score
        
        # Check context hints
        if context:
            # File path hints
            if 'file_path' in context:
                path = context['file_path'].lower()
                if 'readme' in path or 'docs' in path:
                    scores['dev'] = scores.get('dev', 0) + 2
                elif 'resume' in path or 'cover' in path:
                    scores['career'] = scores.get('career', 0) + 2
            
            # Previous environment hint
            if 'previous_env' in context:
                prev_env = context['previous_env']
                scores[prev_env] = scores.get(prev_env, 0) + 1
        
        # Find best match
        if max(scores.values()) == 0:
            # No clear match - default to 'personal' with low confidence
            return 'personal', 0.3
        
        best_env = max(scores, key=scores.get)
        best_score = scores[best_env]
        
        # Calculate confidence (0.0-1.0)
        # High confidence if multiple keywords match
        if best_score >= 3:
            confidence = 0.95
        elif best_score == 2:
            confidence = 0.8
        elif best_score == 1:
            confidence = 0.6
        else:
            confidence = 0.3
        
        return best_env, confidence
    
    def should_ask_user(self, confidence: float) -> bool:
        """Determine if we should ask user to confirm environment."""
        return confidence < 0.7


if __name__ == "__main__":
    # Test the detector
    detector = EnvironmentDetector()
    
    test_cases = [
        "write a cover letter for a VP position",
        "create a linkedin post about AI trends",
        "write readme for my new python library",
        "draft a research paper on consciousness",
        "write a business proposal for a new client",
        "help me write an email to my mom",
        "create documentation for the API",
    ]
    
    print("\n[SCAN] ENVIRONMENT DETECTOR TEST")
    print("=" * 60)
    
    for query in test_cases:
        env, confidence = detector.detect(query)
        should_ask = detector.should_ask_user(confidence)
        
        print(f"\nQuery: \"{query}\"")
        print(f"   Environment: {env}")
        print(f"   Confidence: {confidence:.0%}")
        print(f"   Ask user: {'Yes' if should_ask else 'No'}")
