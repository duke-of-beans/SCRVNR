"""
Pattern Extractor - Extract voice patterns from samples
Analyzes text samples and extracts patterns for voice.db
"""

import re
from typing import List, Dict, Set
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))
from db_manager import VoiceDatabase

class PatternExtractor:
    """Extract voice patterns from text samples."""
    
    def __init__(self):
        self.db = VoiceDatabase()
        
        # Common contraction patterns
        self.contractions = [
            "it's", "you'll", "here's", "that's", "don't", "won't", "can't",
            "isn't", "aren't", "wasn't", "weren't", "haven't", "hasn't",
            "hadn't", "I'm", "you're", "we're", "they're", "I've", "we've",
            "they've", "I'd", "you'd", "we'd", "they'd", "what's", "where's",
            "when's", "who's", "how's", "there's", "let's"
        ]
        
        # Transition patterns to look for
        self.transition_patterns = [
            r"here'?s how",
            r"here'?s what",
            r"the way (?:this|it|I) (?:works?|see)",
            r"what'?s interesting",
            r"the thing is",
            r"under the hood",
            r"the trick (?:here|is)",
            r"this lets you",
            r"you'?ll want to",
            r"if you need"
        ]
    
    def extract_from_sample(self, sample_id: int, content: str, environment: str) -> Dict:
        """Extract all patterns from a sample."""
        
        patterns_found = {
            'contractions': self.extract_contractions(content),
            'transitions': self.extract_transitions(content),
            'sentence_structures': self.extract_sentence_structures(content),
            'imperatives': self.extract_imperatives(content)
        }
        
        # Add patterns to database
        patterns_added = 0
        
        # Add contractions
        for contraction in patterns_found['contractions']:
            self.db.add_pattern(
                pattern_type='contraction',
                pattern_text=contraction,
                environment=environment,
                confidence=0.8,  # High confidence for contractions
                source_sample_id=sample_id
            )
            patterns_added += 1
        
        # Add transitions
        for transition in patterns_found['transitions']:
            self.db.add_pattern(
                pattern_type='transition',
                pattern_text=transition,
                environment=environment,
                confidence=0.7,
                source_sample_id=sample_id
            )
            patterns_added += 1
        
        # Add sentence structures (first 5 unique)
        for structure in list(patterns_found['sentence_structures'])[:5]:
            self.db.add_pattern(
                pattern_type='sentence_structure',
                pattern_text=structure,
                environment=environment,
                confidence=0.6,
                source_sample_id=sample_id
            )
            patterns_added += 1
        
        # Add imperatives
        for imperative in patterns_found['imperatives']:
            self.db.add_pattern(
                pattern_type='imperative',
                pattern_text=imperative,
                environment=environment,
                confidence=0.7,
                source_sample_id=sample_id
            )
            patterns_added += 1
        
        return {
            'sample_id': sample_id,
            'patterns_added': patterns_added,
            'patterns_found': patterns_found
        }
    
    def extract_contractions(self, text: str) -> Set[str]:
        """Find all contractions used."""
        text_lower = text.lower()
        found = set()
        
        for contraction in self.contractions:
            if contraction in text_lower:
                found.add(contraction)
        
        return found
    
    def extract_transitions(self, text: str) -> Set[str]:
        """Find transition phrases."""
        found = set()
        text_lower = text.lower()
        
        for pattern in self.transition_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                found.add(match.group(0))
        
        return found
    
    def extract_sentence_structures(self, text: str) -> Set[str]:
        """Extract common sentence structures (simplified)."""
        sentences = text.split('.')
        structures = set()
        
        for sentence in sentences[:10]:  # First 10 sentences
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Extract pattern: first 3-4 words
            words = sentence.split()[:4]
            if len(words) >= 3:
                structure = ' '.join(words)
                structures.add(structure)
        
        return structures
    
    def extract_imperatives(self, text: str) -> Set[str]:
        """Find imperative sentence patterns."""
        sentences = text.split('.')
        imperatives = set()
        
        # Common imperative verbs
        imperative_verbs = [
            'use', 'run', 'call', 'set', 'get', 'add', 'remove',
            'create', 'delete', 'update', 'read', 'write', 'load',
            'save', 'check', 'verify', 'test', 'try', 'see'
        ]
        
        for sentence in sentences:
            sentence = sentence.strip().lower()
            words = sentence.split()
            
            if words and words[0] in imperative_verbs:
                # First 3-4 words of imperative
                imperative = ' '.join(words[:4])
                imperatives.add(imperative)
        
        return imperatives
    
    def process_unextracted(self, limit: int = 10):
        """Process samples that haven't been extracted yet."""
        samples = self.db.get_unextracted_samples(limit)
        
        print(f"Processing {len(samples)} unextracted samples...")
        
        for sample in samples:
            print(f"\nProcessing sample {sample['id']} ({sample['environment']})...")
            
            result = self.extract_from_sample(
                sample['id'],
                sample['content'],
                sample['environment']
            )
            
            print(f"  Added {result['patterns_added']} patterns")
            
            # Mark as extracted
            self.db.mark_sample_extracted(sample['id'])
        
        print(f"\n✅ Processed {len(samples)} samples")


if __name__ == "__main__":
    extractor = PatternExtractor()
    
    # Process all unextracted samples
    extractor.process_unextracted(limit=100)
