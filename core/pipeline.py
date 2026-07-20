"""
Generation Pipeline — SCRVNR v2.0 Full Loop (Sprint V2-05)

Wires all 6 subsystems into the complete generation pipeline defined in
SCRVNR_V2_ARCHITECTURE.md §2:

    1. DETECT REGISTER
    2. LOAD CONTEXT (register_profiles, voice_description, forbidden, auto-fix subs)
    3. RETRIEVE EXAMPLES (embedding similarity, register-scoped)
    4. GENERATE (LLM with voice context)
    5. AUTO-CORRECT (binary fixes + rate fixes + substitutions, <10ms)
    6. SCORE (centrifuge, <3ms)
    7. REWRITE (targeted, only if score < 0.50)
    8. LEARN (async — correction capture when David corrects)

Usage:
    from core.pipeline import VoicePipeline
    pipe = VoicePipeline()

    # Score-only mode (no generation, just evaluate existing text)
    result = pipe.evaluate(text, register='TECH')

    # Full correct + score pass (no LLM generation)
    result = pipe.process(text, register='TECH')

    # Build the generation context for prompt injection
    context = pipe.build_generation_context("write about websocket config", register='TECH')

    # Record a correction (learning loop)
    pipe.learn(original_text, corrected_text, register='TECH')
"""

import time
from pathlib import Path
from typing import Dict, List, Optional


class VoicePipeline:
    """
    Complete SCRVNR v2.0 generation pipeline.

    Composes: centrifuge + autocorrect + retrieval + preference description + correction capture
    """

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = str(Path(__file__).parent.parent / 'learning' / 'voice.db')
        self.db_path = db_path

        # Lazy-loaded subsystems
        self._centrifuge = None
        self._autocorrector = None
        self._retriever = None
        self._pref_gen = None
        self._correction_capture = None

    # ------------------------------------------------------------------
    # Subsystem access (lazy-loaded)
    # ------------------------------------------------------------------

    @property
    def centrifuge(self):
        if self._centrifuge is None:
            from core.centrifuge import VoiceCentrifuge
            self._centrifuge = VoiceCentrifuge(self.db_path)
        return self._centrifuge

    @property
    def autocorrector(self):
        if self._autocorrector is None:
            from core.autocorrect import AutoCorrector
            self._autocorrector = AutoCorrector(self.db_path)
        return self._autocorrector

    @property
    def retriever(self):
        if self._retriever is None:
            from core.retrieval import VoiceRetriever
            self._retriever = VoiceRetriever(self.db_path)
        return self._retriever

    @property
    def pref_gen(self):
        if self._pref_gen is None:
            from core.preference_description import PreferenceDescriptionGenerator
            self._pref_gen = PreferenceDescriptionGenerator(self.db_path)
        return self._pref_gen

    @property
    def correction_capture(self):
        if self._correction_capture is None:
            from core.correction_capture import CorrectionCapture
            self._correction_capture = CorrectionCapture(self.db_path)
        return self._correction_capture

    # ------------------------------------------------------------------
    # Step 6: SCORE (centrifuge wrapper with confidence bands)
    # ------------------------------------------------------------------

    def evaluate(self, text: str, register: str = 'TECH') -> Dict:
        """
        Score text with confidence banding.

        Bands:
            >= 0.75: HIGH — ship without review
            0.65-0.75: GOOD — ship with auto-fix applied
            0.50-0.65: MARGINAL — ship with suggestions visible
            < 0.50: LOW — trigger rewrite recommendation
        """
        result = self.centrifuge.score(text, register)
        score = result['overall_score']

        if score >= 0.75:
            band = 'HIGH'
            recommendation = 'ship'
        elif score >= 0.65:
            band = 'GOOD'
            recommendation = 'ship_with_autofix'
        elif score >= 0.50:
            band = 'MARGINAL'
            recommendation = 'ship_with_suggestions'
        else:
            band = 'LOW'
            recommendation = 'rewrite_flagged_sections'

        result['band'] = band
        result['recommendation'] = recommendation
        return result

    # ------------------------------------------------------------------
    # Steps 5+6: AUTO-CORRECT + SCORE (the fast path)
    # ------------------------------------------------------------------

    def process(self, text: str, register: str = 'TECH') -> Dict:
        """
        Run auto-correct then score. The main workhorse for post-generation.

        Returns:
            {
                'text': corrected text,
                'original_text': input text,
                'score': centrifuge result with band,
                'fixes': list of fixes applied,
                'suggestions': list of suggestions,
                'processing_ms': total time
            }
        """
        start = time.perf_counter()

        # Step 5: Auto-correct
        ac_result = self.autocorrector.correct(text, register)

        # Step 6: Score the corrected text
        score_result = self.evaluate(ac_result['text'], register)

        elapsed_ms = (time.perf_counter() - start) * 1000

        return {
            'text': ac_result['text'],
            'original_text': text,
            'score': score_result,
            'fixes': ac_result['fixes'],
            'suggestions': ac_result['suggestions'],
            'fix_count': ac_result['fix_count'],
            'band': score_result['band'],
            'overall_score': score_result['overall_score'],
            'processing_ms': round(elapsed_ms, 2),
        }

    # ------------------------------------------------------------------
    # Steps 2+3: BUILD GENERATION CONTEXT
    # ------------------------------------------------------------------

    def build_generation_context(self, prompt: str,
                                   register: str = 'TECH',
                                   k: int = 3) -> Dict:
        """
        Build the complete generation context for prompt injection.

        Combines:
            - Voice description (register-specific)
            - Retrieved corpus examples
            - Calibration constraints

        Returns:
            {
                'voice_context': formatted string for system/user prompt,
                'examples_retrieved': count,
                'retrieval_confidence': float,
                'register': str
            }
        """
        # Get voice description context
        voice_desc = self.pref_gen.get_prompt_context(register=register)

        # Retrieve examples
        examples = self.retriever.retrieve(prompt, register=register, k=k)
        formatted_examples = self.retriever.format_for_prompt(
            examples, register=register, voice_description=voice_desc
        )

        # Compute retrieval confidence
        if examples:
            avg_similarity = sum(e['similarity'] for e in examples) / len(examples)
            confidence = 'high' if avg_similarity > 0.5 else 'medium' if avg_similarity > 0.3 else 'low'
        else:
            avg_similarity = 0.0
            confidence = 'none'

        # Build calibration constraints
        target = self.centrifuge.get_target(register)
        constraints = []
        if target:
            constraints.append(f"Target contraction rate: {target.get('target_contraction_rate', 0.4)}")
            constraints.append(f"Target em-dash rate: {target.get('target_em_dash_rate', 0.0)} (use hyphens instead)")
            constraints.append(f"Target mean Zipf: {target.get('target_mean_zipf', 4.3)}")

        # Assemble full context
        parts = [formatted_examples]
        if constraints:
            parts.append("")
            parts.append("<voice_constraints>")
            for c in constraints:
                parts.append(f"- {c}")
            parts.append("</voice_constraints>")

        voice_context = '\n'.join(parts)

        return {
            'voice_context': voice_context,
            'examples_retrieved': len(examples),
            'retrieval_confidence': confidence,
            'avg_similarity': round(avg_similarity, 4),
            'register': register,
            'context_chars': len(voice_context),
            'context_tokens_approx': len(voice_context) // 4,
        }

    # ------------------------------------------------------------------
    # Step 8: LEARN (correction capture)
    # ------------------------------------------------------------------

    def learn(self, original: str, corrected: str,
              register: str = None, source: str = 'session') -> Optional[str]:
        """
        Record a correction and propagate learning.

        Args:
            original: The AI-generated text that was corrected
            corrected: David's corrected version
            register: Target register
            source: Origin of the correction

        Returns:
            Correction pair ID
        """
        return self.correction_capture.capture(
            original, corrected,
            register=register,
            source=source,
            score_both=True
        )

    # ------------------------------------------------------------------
    # Pipeline stats
    # ------------------------------------------------------------------

    def get_stats(self) -> Dict:
        """Get comprehensive pipeline statistics."""
        stats = {
            'registers': self.centrifuge.available_registers(),
            'register_count': len(self.centrifuge.available_registers()),
        }

        # Correction capture stats
        try:
            cc_stats = self.correction_capture.get_stats()
            stats['corrections'] = cc_stats
        except Exception:
            stats['corrections'] = {'error': 'unavailable'}

        # Retrieval index stats
        try:
            ret_stats = self.retriever.get_index_stats()
            stats['retrieval'] = ret_stats
        except Exception:
            stats['retrieval'] = {'error': 'unavailable'}

        # Promoted substitutions
        try:
            promoted = self.correction_capture.get_promoted_substitutions()
            stats['promoted_substitutions'] = len(promoted)
        except Exception:
            stats['promoted_substitutions'] = 0

        return stats


if __name__ == "__main__":
    pipe = VoicePipeline()
    print("VoicePipeline initialized")
    print(f"  Registers: {', '.join(pipe.centrifuge.available_registers())}")

    # Demo: process Claude-style text
    test = (
        "The system utilizes a comprehensive framework \u2014 leveraging robust APIs \u2014 "
        "to facilitate seamless data processing across the ecosystem. "
        "It is not complicated but you will need to verify that the endpoint "
        "does not collide with the existing configuration."
    )

    print(f"\n--- Process Demo ---")
    result = pipe.process(test, register='TECH')
    print(f"Band: {result['band']} (score: {result['overall_score']:.3f})")
    print(f"Fixes: {result['fix_count']} applied in {result['processing_ms']:.1f}ms")
    for f in result['fixes']:
        print(f"  [{f['category']}] {f['type']}")
    print(f"Suggestions: {len(result['suggestions'])}")
    print(f"\nOriginal: {test[:80]}...")
    print(f"Corrected: {result['text'][:80]}...")

    # Demo: build generation context
    print(f"\n--- Generation Context Demo ---")
    ctx = pipe.build_generation_context("debug the websocket reconnection handler", register='TECH')
    print(f"Context: {ctx['context_chars']} chars (~{ctx['context_tokens_approx']} tokens)")
    print(f"Examples: {ctx['examples_retrieved']} (confidence: {ctx['retrieval_confidence']})")

    # Stats
    print(f"\n--- Pipeline Stats ---")
    stats = pipe.get_stats()
    print(f"Registers: {stats['register_count']}")
    print(f"Promoted subs: {stats['promoted_substitutions']}")
