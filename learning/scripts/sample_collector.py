"""
Sample Collector - Auto-save Ghost Writer outputs
Called after each generation to save output for learning
"""

from pathlib import Path
from datetime import datetime
import hashlib
import re
import sys

sys.path.append(str(Path(__file__).parent))
from db_manager import VoiceDatabase

class SampleCollector:
    """Collect and save Ghost Writer outputs."""
    
    def __init__(self):
        self.db = VoiceDatabase()
        self.samples_dir = Path(__file__).parent.parent / "samples"
    
    def collect(self, content: str, environment: str, context_type: str,
               quality_score: float, context_tags: list) -> dict:
        """Collect a sample and save to filesystem + database."""
        
        # Calculate metrics
        word_count = len(content.split())
        contraction_rate = self.calculate_contraction_rate(content)
        dash_density = self.calculate_dash_density(content)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        first_words = self.extract_first_words(content, max_words=5)
        filename = f"{timestamp}_{environment}_{context_type}_{first_words}.md"
        
        # Save to filesystem
        env_dir = self.samples_dir / f"from_{environment}"
        env_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = env_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Saved sample: {file_path}")
        
        # Add to database
        sample_id = self.db.add_sample(
            content=content,
            environment=environment,
            context_type=context_type,
            file_path=str(file_path),
            word_count=word_count,
            contraction_rate=contraction_rate,
            dash_density=dash_density,
            quality_score=quality_score,
            context_tags=context_tags
        )
        
        if sample_id:
            print(f"✅ Added to database: Sample ID {sample_id}")
        else:
            print(f"ℹ️  Sample already exists in database (duplicate)")
        
        return {
            'file_path': str(file_path),
            'sample_id': sample_id,
            'word_count': word_count,
            'contraction_rate': contraction_rate,
            'dash_density': dash_density
        }
    
    def calculate_contraction_rate(self, text: str) -> float:
        """Calculate percentage of contractions used."""
        contractions = [
            "it's", "you'll", "here's", "that's", "don't", "won't", "can't",
            "isn't", "aren't", "wasn't", "weren't", "haven't", "hasn't",
            "hadn't", "I'm", "you're", "we're", "they're", "I've", "we've",
            "they've", "I'd", "you'd", "we'd", "they'd", "what's", "where's",
            "when's", "who's", "how's", "there's", "let's"
        ]
        
        text_lower = text.lower()
        count = sum(1 for c in contractions if c in text_lower)
        
        # Estimate opportunities (simplified)
        words = len(text.split())
        opportunities = words / 10  # Rough estimate
        
        if opportunities == 0:
            return 0.0
        
        rate = min(1.0, count / opportunities)
        return round(rate, 3)
    
    def calculate_dash_density(self, text: str) -> float:
        """Calculate dashes per page."""
        em_dashes = text.count('—')
        en_dashes = text.count('–')
        
        # Don't count hyphens in compound words, only pause hyphens
        # (simplified - just count all hyphens for now)
        pause_hyphens = text.count(' - ')
        
        total_dashes = em_dashes + en_dashes + pause_hyphens
        
        # Estimate pages (500 words per page)
        word_count = len(text.split())
        pages = max(1, word_count / 500)
        
        dashes_per_page = total_dashes / pages
        return round(dashes_per_page, 2)
    
    def extract_first_words(self, text: str, max_words: int = 5) -> str:
        """Extract first few words for filename."""
        # Remove markdown headers, strip whitespace
        text = re.sub(r'^#+\s*', '', text)
        text = text.strip()
        
        words = text.split()[:max_words]
        
        # Clean words for filename (alphanumeric only)
        clean_words = []
        for word in words:
            clean = re.sub(r'[^a-zA-Z0-9]', '', word)
            if clean:
                clean_words.append(clean.lower())
        
        return '_'.join(clean_words[:5])


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Collect Ghost Writer sample")
    parser.add_argument('file', help="File to collect")
    parser.add_argument('--environment', required=True, 
                       choices=['dev', 'research', 'career', 'work', 'personal'])
    parser.add_argument('--context', required=True, 
                       help="Context type (e.g., cover_letter, linkedin_post)")
    parser.add_argument('--quality', type=float, default=0.8, 
                       help="Quality score (0.0-1.0)")
    parser.add_argument('--tags', nargs='*', default=['generated'], 
                       help="Context tags")
    
    args = parser.parse_args()
    
    # Read file
    with open(args.file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Collect
    collector = SampleCollector()
    result = collector.collect(
        content=content,
        environment=args.environment,
        context_type=args.context,
        quality_score=args.quality,
        context_tags=args.tags
    )
    
    print(f"\n✅ Sample collected successfully!")
    print(f"   File: {result['file_path']}")
    print(f"   Sample ID: {result['sample_id']}")
    print(f"   Word count: {result['word_count']}")
    print(f"   Contraction rate: {result['contraction_rate']:.1%}")
    print(f"   Dash density: {result['dash_density']:.1f} per page")
