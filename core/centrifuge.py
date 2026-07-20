"""
Rarity Centrifuge — Score generated text against David's measured voice profile.

Scores text on three axes:
  - Rarity: vocabulary frequency alignment with David's kite shape
  - Rhythm: sentence length distribution alignment
  - Style: contraction/punctuation/emphasis alignment

Overall score = weighted average: rarity(0.4) + rhythm(0.3) + style(0.3)

All data read from voice.db (register_profiles + rarity_targets tables).
No network calls. No writes during scoring. Read-only.

Usage:
    from centrifuge import VoiceCentrifuge
    c = VoiceCentrifuge(db_path='path/to/voice.db')
    result = c.score(text, register='TECH')
    if c.passes(text, register='TECH', threshold=0.65):
        print("Voice match")
"""

import json
import re
import sqlite3
import time
from typing import Dict, List, Optional


# Lazy imports — only loaded on first use
_wordfreq = None
_nltk_sent_tokenize = None


def _get_zipf(word: str) -> float:
    """Get Zipf frequency for a word. Lazy-loads wordfreq."""
    global _wordfreq
    if _wordfreq is None:
        from wordfreq import zipf_frequency
        _wordfreq = zipf_frequency
    return _wordfreq(word.lower(), 'en')


def _sent_tokenize(text: str) -> List[str]:
    """Sentence tokenize. Lazy-loads nltk."""
    global _nltk_sent_tokenize
    if _nltk_sent_tokenize is None:
        from nltk.tokenize import sent_tokenize
        _nltk_sent_tokenize = sent_tokenize
    return _nltk_sent_tokenize(text)


# Stopwords — small inline set to avoid nltk download dependency
STOPWORDS = frozenset([
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you',
    'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself',
    'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them',
    'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this',
    'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been',
    'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
    'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
    'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
    'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from',
    'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
    'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
    'how', 'all', 'both', 'each', 'few', 'more', 'most', 'other', 'some',
    'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
    'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now', 'd',
    'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', 'couldn', 'didn',
    'doesn', 'hadn', 'hasn', 'haven', 'isn', 'ma', 'mightn', 'mustn',
    'needn', 'shan', 'shouldn', 'wasn', 'weren', 'won', 'wouldn'
])

CONTRACTION_PATTERN = re.compile(
    r"\b(?:i'm|you're|we're|they're|it's|that's|here's|there's|"
    r"what's|where's|when's|who's|how's|let's|"
    r"can't|won't|don't|didn't|doesn't|isn't|aren't|wasn't|weren't|"
    r"haven't|hasn't|hadn't|couldn't|wouldn't|shouldn't|mightn't|mustn't|"
    r"i've|you've|we've|they've|i'd|you'd|we'd|they'd|"
    r"i'll|you'll|we'll|they'll|he'll|she'll|it'll|"
    r"he's|she's)\b",
    re.IGNORECASE
)


WORD_PATTERN = re.compile(r"[a-zA-Z']+")
EM_DASH_PATTERN = re.compile(r'[—–]')  # em-dash and en-dash
CAPS_WORD_PATTERN = re.compile(r'\b[A-Z]{2,}\b')


class VoiceCentrifuge:
    """Score generated text against David's measured voice profile."""

    def __init__(self, db_path: str = None):
        if db_path is None:
            from pathlib import Path
            db_path = str(Path(__file__).parent.parent / 'learning' / 'voice.db')
        self.db_path = db_path
        self._profiles = {}
        self._targets = {}
        self._load_data()
        # Warmup wordfreq and nltk to avoid cold-start penalty on first score()
        _get_zipf('the')
        _sent_tokenize('Hello world.')

    def _load_data(self):
        """Load register profiles and rarity targets from voice.db."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            cur = conn.cursor()
            # Load register profiles
            cur.execute("SELECT * FROM register_profiles")
            for row in cur.fetchall():
                self._profiles[row['register']] = dict(row)

            # Load rarity targets
            cur.execute("SELECT * FROM rarity_targets")
            for row in cur.fetchall():
                self._targets[row['register']] = dict(row)
        finally:
            conn.close()

    def _tokenize_words(self, text: str) -> List[str]:
        """Extract content words (non-stopwords)."""
        words = WORD_PATTERN.findall(text.lower())
        return [w for w in words if w not in STOPWORDS and len(w) > 1]

    def _compute_rarity(self, words: List[str]) -> Dict:
        """Compute vocabulary rarity metrics."""
        if not words:
            return {'mean_zipf': 0.0, 'pct_rare': 0.0}
        zipfs = [_get_zipf(w) for w in words]
        mean_z = sum(zipfs) / len(zipfs)
        rare_count = sum(1 for z in zipfs if z < 3.0)
        pct_rare = (rare_count / len(zipfs)) * 100
        return {'mean_zipf': mean_z, 'pct_rare': pct_rare, 'zipfs': zipfs}

    def _compute_rhythm(self, text: str) -> Dict:
        """Compute sentence length distribution metrics."""
        sentences = _sent_tokenize(text)
        if not sentences:
            return {'mean_len': 0.0, 'std_len': 0.0, 'count': 0}
        lengths = [len(s.split()) for s in sentences]
        n = len(lengths)
        mean_len = sum(lengths) / n
        if n > 1:
            variance = sum((l - mean_len) ** 2 for l in lengths) / (n - 1)
            std_len = variance ** 0.5
        else:
            std_len = 0.0
        return {'mean_len': mean_len, 'std_len': std_len, 'count': n, 'lengths': lengths}

    def _compute_style(self, text: str, word_count: int) -> Dict:
        """Compute style metrics: contractions, em-dashes, caps, etc."""
        if word_count == 0:
            return {}
        contractions = len(CONTRACTION_PATTERN.findall(text))
        # Rate per 100 words to match profile format
        contraction_rate = contractions / max(1, word_count / 100)

        em_dashes = len(EM_DASH_PATTERN.findall(text))
        em_dash_rate = (em_dashes / word_count) * 1000

        caps_words = len(CAPS_WORD_PATTERN.findall(text))
        caps_rate = (caps_words / word_count) * 1000

        exclamations = text.count('!')
        exclamation_rate = (exclamations / word_count) * 1000

        return {
            'contraction_rate': contraction_rate,
            'em_dash_rate': em_dash_rate,
            'em_dash_count': em_dashes,
            'caps_rate': caps_rate,
            'exclamation_rate': exclamation_rate,
        }

    def _score_rarity(self, rarity: Dict, target: Dict) -> float:
        """Score vocabulary rarity alignment. Returns 0-1."""
        if not target:
            return 0.5
        t_zipf = target.get('target_mean_zipf', 4.3)
        tol = target.get('tolerance_zipf', 0.8)
        actual = rarity.get('mean_zipf', 0.0)
        if actual == 0.0:
            return 0.0
        diff = abs(actual - t_zipf)
        # Use generous tolerance: 1.5x the stored tolerance for graceful degradation
        effective_tol = max(tol * 1.5, 0.5)
        score = max(0.0, 1.0 - (diff / effective_tol))

        # Also factor in pct_rare alignment
        t_rare = target.get('target_pct_rare', 6.0)
        tol_rare = target.get('tolerance_rare', 3.0)
        diff_rare = abs(rarity.get('pct_rare', 0.0) - t_rare)
        rare_score = max(0.0, 1.0 - (diff_rare / max(tol_rare, 2.0)))

        return score * 0.6 + rare_score * 0.4

    def _score_rhythm(self, rhythm: Dict, profile: Dict, target: Dict) -> float:
        """Score sentence length distribution alignment. Returns 0-1."""
        if not target or not profile:
            return 0.5
        t_mean = target.get('target_sentence_len_mean', 15.0)
        tol = target.get('tolerance_sentence', 5.0)
        actual_mean = rhythm.get('mean_len', 0.0)
        diff = abs(actual_mean - t_mean)
        mean_score = max(0.0, 1.0 - (diff / max(tol, 1.0)))

        # Check std alignment
        t_std = target.get('target_sentence_len_std', 10.0)
        actual_std = rhythm.get('std_len', 0.0)
        std_diff = abs(actual_std - t_std)
        std_score = max(0.0, 1.0 - (std_diff / max(t_std * 0.5, 3.0)))

        return mean_score * 0.6 + std_score * 0.4

    def _score_style(self, style: Dict, profile: Dict, target: Dict) -> float:
        """Score style alignment. Returns 0-1."""
        if not target or not profile:
            return 0.5
        sub_scores = []

        # Contraction rate
        t_cont = target.get('target_contraction_rate', 0.4)
        tol_cont = target.get('tolerance_contraction', 0.15)
        actual_cont = style.get('contraction_rate', 0.0)
        # Normalize: profile stores per-100-words, we compute per-100-words
        diff_cont = abs(actual_cont - t_cont)
        cont_score = max(0.0, 1.0 - (diff_cont / max(tol_cont, 0.05)))
        sub_scores.append(cont_score * 0.3)

        # Em-dash penalty: David uses ~0 em-dashes. Any em-dash is a penalty.
        em_count = style.get('em_dash_count', 0)
        if em_count == 0:
            em_score = 1.0
        elif em_count <= 2:
            em_score = 0.4
        else:
            em_score = 0.0
        sub_scores.append(em_score * 0.4)

        # Caps emphasis — presence is Davidian
        caps = style.get('caps_rate', 0.0)
        profile_caps = profile.get('caps_emphasis_rate', 10.0)
        if profile_caps > 5.0:
            # David uses caps; having some is good
            caps_score = min(1.0, caps / max(profile_caps * 0.3, 1.0))
        else:
            caps_score = 0.8
        sub_scores.append(caps_score * 0.3)

        return sum(sub_scores)

    def _generate_flags(self, text: str, style: Dict, rarity: Dict,
                        rhythm: Dict, profile: Dict, target: Dict) -> List[Dict]:
        """Generate specific actionable flags."""
        flags = []

        # Em-dash flag
        em_count = style.get('em_dash_count', 0)
        if em_count > 0:
            flags.append({
                'type': 'em_dash',
                'count': em_count,
                'suggestion': 'Replace em-dashes with hyphens - David never uses em-dashes'
            })

        # Low rarity vocabulary flag
        if rarity.get('zipfs'):
            common_words = []
            all_words = WORD_PATTERN.findall(text.lower())
            content_words = [w for w in all_words if w not in STOPWORDS and len(w) > 1]
            for w in content_words:
                z = _get_zipf(w)
                if z > 5.5:
                    common_words.append(w)
            # Deduplicate
            common_unique = list(dict.fromkeys(common_words))[:5]
            if common_unique:
                flags.append({
                    'type': 'low_rarity',
                    'words': common_unique,
                    'suggestion': f"Words too common for David's {profile.get('register', 'UNKNOWN')} register"
                })

        # Sentence uniformity flag (bimodal registers)
        is_bimodal = profile.get('is_bimodal', 0)
        if is_bimodal and rhythm.get('std_len', 0) < 3.0 and rhythm.get('count', 0) > 3:
            flags.append({
                'type': 'sentence_too_uniform',
                'mean': round(rhythm.get('mean_len', 0), 1),
                'target_std': round(profile.get('std_sentence_len', 10.0), 1),
                'suggestion': 'Mix short directives with longer explanations'
            })

        # Claude-tell words
        claude_tells = ['utilize', 'facilitate', 'leverage', 'comprehensive',
                        'robust', 'seamless', 'streamline', 'synergy',
                        'holistic', 'paradigm', 'ecosystem']
        found_tells = [w for w in WORD_PATTERN.findall(text.lower()) if w in claude_tells]
        if found_tells:
            flags.append({
                'type': 'claude_vocabulary',
                'words': list(dict.fromkeys(found_tells)),
                'suggestion': 'Replace with David-authentic vocabulary'
            })

        return flags

    def score(self, text: str, register: str = 'TECH') -> Dict:
        """
        Score text against David's measured voice profile for a register.

        Args:
            text: The generated text to score
            register: Target register (TECH, CASUAL, PERSONAL, etc.)

        Returns:
            Dict with overall_score, rarity_score, rhythm_score, style_score,
            flags, register, word_count, processing_ms
        """
        start = time.perf_counter()

        profile = self._profiles.get(register, self._profiles.get('TECH', {}))
        target = self._targets.get(register, self._targets.get('TECH', {}))

        # Tokenize
        all_words = WORD_PATTERN.findall(text)
        word_count = len(all_words)
        content_words = self._tokenize_words(text)

        # Compute metrics
        rarity = self._compute_rarity(content_words)
        rhythm = self._compute_rhythm(text)
        style = self._compute_style(text, word_count)

        # Score each axis
        rarity_score = self._score_rarity(rarity, target)
        rhythm_score = self._score_rhythm(rhythm, profile, target)
        style_score = self._score_style(style, profile, target)

        # Weighted overall
        overall = rarity_score * 0.4 + rhythm_score * 0.3 + style_score * 0.3

        # Generate flags
        flags = self._generate_flags(text, style, rarity, rhythm, profile, target)

        elapsed_ms = (time.perf_counter() - start) * 1000

        return {
            'overall_score': round(overall, 4),
            'rarity_score': round(rarity_score, 4),
            'rhythm_score': round(rhythm_score, 4),
            'style_score': round(style_score, 4),
            'flags': flags,
            'register': register,
            'word_count': word_count,
            'processing_ms': round(elapsed_ms, 1),
        }

    def passes(self, text: str, register: str = 'TECH',
               threshold: float = 0.65) -> bool:
        """Quick pass/fail check."""
        result = self.score(text, register)
        return result['overall_score'] >= threshold

    def available_registers(self) -> List[str]:
        """List all registers with loaded profiles."""
        return sorted(self._profiles.keys())

    def get_profile(self, register: str) -> Optional[Dict]:
        """Get the raw profile data for a register."""
        return self._profiles.get(register)

    def get_target(self, register: str) -> Optional[Dict]:
        """Get the rarity targets for a register."""
        return self._targets.get(register)


if __name__ == "__main__":
    import time as _t
    t0 = _t.perf_counter()
    c = VoiceCentrifuge()
    init_ms = (_t.perf_counter() - t0) * 1000
    print(f"Init: {init_ms:.0f}ms (includes wordfreq warmup)")
    print(f"Loaded {len(c.available_registers())} registers: {', '.join(c.available_registers())}")

    test = "Here's how this works - you'll want to check the endpoint first, then run the tests. It's not complicated but you'll need to verify the websocket config doesn't collide with the existing shim."
    result = c.score(test, 'TECH')
    print(f"\nTest score: {result['overall_score']:.2f} ({result['processing_ms']:.1f}ms)")
    print(f"  Rarity: {result['rarity_score']:.2f}")
    print(f"  Rhythm: {result['rhythm_score']:.2f}")
    print(f"  Style:  {result['style_score']:.2f}")
    if result['flags']:
        print(f"  Flags: {len(result['flags'])}")
        for f in result['flags']:
            print(f"    - {f['type']}: {f.get('suggestion', '')}")

    # Performance test — second call should be fast
    long_text = (test + " ") * 15  # ~500 words
    result2 = c.score(long_text, 'TECH')
    print(f"\nPerformance (warm, ~{result2['word_count']} words): {result2['processing_ms']:.1f}ms")
    target = "PASS" if result2['processing_ms'] < 50 else "FAIL"
    print(f"  < 50ms target: {target}")
