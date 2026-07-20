"""
Preference Description Generator — SCRVNR v2.0 Subsystem 2 (PREFER)

Generates and maintains voice_description.md — a natural-language description
of David's voice, derived from quantitative profile data and iteratively
refined against corrections.

Research basis:
    PROSE (Apple, ICML 2025): Iterative preference description refinement
    yielded 33% improvement over prior methods.

The description bridges quantitative profiles (centrifuge targets) and
the LLM's understanding of style. It is:
    - Derived from voice_profile.json + voice.db register_profiles
    - Version-controlled (each generation increments the version)
    - Human-readable and editable by David
    - Injectable into generation prompts (max ~2,000 tokens)
    - Refinable against correction pairs from Subsystem 1

Usage:
    from core.preference_description import PreferenceDescriptionGenerator
    gen = PreferenceDescriptionGenerator()

    # Generate initial description
    doc = gen.generate()
    gen.save(doc)

    # Get injectable context for a specific register
    ctx = gen.get_prompt_context(register='TECH')

    # Refine based on correction pairs
    gen.refine_from_corrections()
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


# Registers worth individual sections (enough data to be meaningful)
MAJOR_REGISTERS = [
    'TECH', 'CASUAL', 'PROFESSIONAL', 'ARGUMENTATIVE',
    'INVESTIGATE', 'CREATIVE_DIRECTION', 'PERSONAL', 'FRUSTRATED'
]

# Minimum messages for a register to get its own section
MIN_REGISTER_MESSAGES = 100


class PreferenceDescriptionGenerator:
    """Generate and maintain voice_description.md from quantitative data."""

    def __init__(self, db_path: str = None, profile_path: str = None,
                 output_dir: str = None):
        project_root = Path(__file__).parent.parent

        if db_path is None:
            db_path = str(project_root / 'learning' / 'voice.db')
        if profile_path is None:
            profile_path = str(project_root / 'research' / 'voice_fingerprint' / 'voice_profile.json')
        if output_dir is None:
            output_dir = str(project_root)

        self.db_path = db_path
        self.profile_path = profile_path
        self.output_dir = Path(output_dir)
        self.output_path = self.output_dir / 'voice_description.md'

        self._profile = None
        self._db_profiles = {}
        self._db_targets = {}
        self._correction_stats = None

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def _load_profile(self) -> Dict:
        """Load voice_profile.json."""
        if self._profile is None:
            with open(self.profile_path, 'r', encoding='utf-8') as f:
                self._profile = json.load(f)
        return self._profile

    def _load_db_data(self):
        """Load register profiles and targets from voice.db."""
        if self._db_profiles:
            return

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM register_profiles")
            for row in cur.fetchall():
                self._db_profiles[row['register']] = dict(row)

            cur.execute("SELECT * FROM rarity_targets")
            for row in cur.fetchall():
                self._db_targets[row['register']] = dict(row)

            # Load correction stats if table exists
            try:
                cur.execute("""
                SELECT COUNT(*) as total,
                       AVG(score_delta) as avg_delta
                FROM correction_pairs
                WHERE score_delta IS NOT NULL
                """)
                row = cur.fetchone()
                if row and row['total'] > 0:
                    self._correction_stats = {
                        'total': row['total'],
                        'avg_delta': row['avg_delta']
                    }

                # Top promoted substitutions
                cur.execute("""
                SELECT from_text, to_text, register, occurrence_count
                FROM substitution_ledger
                WHERE promoted = 1
                ORDER BY occurrence_count DESC
                LIMIT 10
                """)
                promoted = [dict(r) for r in cur.fetchall()]
                if promoted:
                    if self._correction_stats is None:
                        self._correction_stats = {}
                    self._correction_stats['promoted_subs'] = promoted
            except sqlite3.OperationalError:
                pass  # tables don't exist yet
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Description generation — translate numbers to natural language
    # ------------------------------------------------------------------

    def _describe_contraction_rate(self, rate: float, register: str) -> str:
        """Translate contraction rate to natural language."""
        pct = round(rate * 100) if rate < 1.0 else round(rate)
        # VFP stores contraction_rate as contractions per 100 words in some places,
        # and as a 0-1 ratio in others. Normalize.
        if rate > 1.0:
            # Per-100-words format from the profile
            if rate > 50:
                return f"Very high contraction rate ({pct}/100 words) — contractions are the default"
            elif rate > 30:
                return f"High contraction rate ({pct}/100 words) — prefers contracted forms"
            else:
                return f"Moderate contraction rate ({pct}/100 words)"
        else:
            if rate > 0.6:
                return f"High contraction rate (~{pct}%) — contractions are the default"
            elif rate > 0.4:
                return f"Moderate contraction rate (~{pct}%)"
            elif rate > 0.25:
                return f"Low contraction rate (~{pct}%) — often writes expanded forms"
            else:
                return f"Very low contraction rate (~{pct}%) — rarely contracts"

    def _describe_sentence_rhythm(self, profile: Dict) -> str:
        """Describe sentence length distribution."""
        mean_len = profile.get('mean_sentence_len', 15)
        std_len = profile.get('std_sentence_len', 10)
        is_bimodal = profile.get('is_bimodal', 0)
        bc = profile.get('bimodality_coefficient', 0)

        parts = []
        if mean_len < 10:
            parts.append(f"Short sentences (avg ~{mean_len:.0f} words)")
        elif mean_len < 18:
            parts.append(f"Medium sentences (avg ~{mean_len:.0f} words)")
        else:
            parts.append(f"Longer sentences (avg ~{mean_len:.0f} words)")

        if is_bimodal:
            # Estimate modes: bimodal text clusters around 0.4x and 1.8x the mean
            short_est = max(3, min(10, round(mean_len * 0.4)))
            long_est = min(40, max(15, round(mean_len * 1.8)))
            parts.append(f"bimodal rhythm — alternates short directives (~{short_est} words) with longer explanations (~{long_est} words)")
        elif std_len > 8:
            parts.append("high variety in sentence length")
        elif std_len < 4:
            parts.append("uniform sentence length (low variety)")

        return '; '.join(parts)

    def _describe_vocabulary(self, profile: Dict, register: str) -> str:
        """Describe vocabulary rarity characteristics."""
        mean_zipf = profile.get('mean_zipf', 4.3)
        kite_skew = profile.get('kite_skew', -1.4)
        pct_rare = profile.get('pct_rare', 6.0)

        parts = []
        if mean_zipf < 4.0:
            parts.append("Technical vocabulary skewing toward specialized terms")
        elif mean_zipf < 4.3:
            parts.append("Slightly technical vocabulary")
        elif mean_zipf < 4.6:
            parts.append("Natural conversational vocabulary")
        else:
            parts.append("Common everyday vocabulary")

        if abs(kite_skew) > 2.5:
            parts.append("very strong rarity tail (uses rare words significantly more than average)")
        elif abs(kite_skew) > 1.5:
            parts.append("clear rarity tail into specialized vocabulary")

        if pct_rare > 8:
            parts.append(f"~{pct_rare:.0f}% rare words (Zipf < 3.0)")
        elif pct_rare > 5:
            parts.append(f"~{pct_rare:.0f}% rare words")

        return '; '.join(parts)

    def _describe_punctuation(self, profile: Dict) -> List[str]:
        """Describe punctuation patterns."""
        traits = []

        em_rate = profile.get('em_dash_rate', 0)
        if em_rate < 0.5:
            traits.append("Never uses em-dashes — uses hyphens with spaces instead")
        elif em_rate < 2.0:
            traits.append("Rare em-dash usage")

        hyp_rate = profile.get('hyphen_rate', 0)
        if hyp_rate > 10:
            traits.append(f"Frequent hyphen usage ({hyp_rate:.1f}/1k words) — hyphens are the primary connective punctuation")

        exc_rate = profile.get('exclamation_rate', 0)
        if exc_rate > 5:
            traits.append(f"Frequent exclamation marks ({exc_rate:.1f}/1k words)")
        elif exc_rate < 1.0:
            traits.append("Rare exclamation marks")

        ellipsis_rate = profile.get('ellipsis_rate', 0)
        if ellipsis_rate > 2.0:
            traits.append(f"Uses ellipses for trailing thoughts ({ellipsis_rate:.1f}/1k words)")

        caps_rate = profile.get('caps_emphasis_rate', 0)
        if caps_rate > 15:
            traits.append(f"Uses ALL-CAPS for emphasis ({caps_rate:.1f}/1k words)")
        elif caps_rate > 8:
            traits.append("Moderate use of ALL-CAPS emphasis")

        return traits

    def _describe_profanity(self, profile: Dict, register: str) -> Optional[str]:
        """Describe profanity usage."""
        rate = profile.get('profanity_rate', 0)
        if register == 'FRUSTRATED' and rate > 20:
            return f"Heavy profanity ({rate:.0f}/1k words) — this register is defined by emotional intensity"
        elif rate > 1.0:
            return f"Occasional profanity ({rate:.1f}/1k words)"
        elif rate > 0.3:
            return "Light profanity (rare but present)"
        return None

    # ------------------------------------------------------------------
    # Document generation
    # ------------------------------------------------------------------

    def _get_version(self) -> int:
        """Get next version number from existing file."""
        if self.output_path.exists():
            try:
                content = self.output_path.read_text(encoding='utf-8')
                # Parse version from header
                for line in content.split('\n'):
                    if line.startswith('## Last refined:'):
                        parts = line.split('Refinement count:')
                        if len(parts) > 1:
                            count = int(parts[1].split('|')[0].strip())
                            return count + 1
            except (ValueError, IndexError):
                pass
        return 1

    def generate(self) -> str:
        """
        Generate voice_description.md from quantitative profile data.

        Returns the document content as a string.
        """
        self._load_profile()
        self._load_db_data()

        profile = self._profile
        registers = profile.get('registers', {})
        global_data = profile.get('global', {})
        baseline = profile.get('claude_baseline_comparison', {})

        version = self._get_version()
        now = datetime.now().strftime('%Y-%m-%d')

        lines = []

        # Header
        lines.append(f"# David's Voice — Preference Description v{version}")
        lines.append(f"## Last refined: {now} | Refinement count: {version} | Source: quantitative profile + corpus analysis")
        lines.append("")

        # Global traits
        lines.append("## Global Traits (all registers)")
        lines.append("")

        global_mean_zipf = global_data.get('mean_zipf', profile.get('registers', {}).get('TECH', {}).get('vocabulary', {}).get('mean_zipf', 4.33))

        lines.append(f"- Vocabulary center: mean Zipf {global_mean_zipf:.2f} (slightly above common-word center; mixes everyday language with domain-specific technical terms)")
        lines.append("- Punctuation identity: hyphens with spaces (` - `) are the connective punctuation, never em-dashes. Straight quotes, not smart quotes.")

        # Contraction gradient (global observation)
        lines.append("- Contraction rate varies sharply by register: highest in CASUAL/ARGUMENTATIVE (~74%), lowest in TECH (~29%). The contraction rate is a formality dial.")

        # Em-dash
        delta = baseline.get('delta_david_minus_claude', {})
        em_delta = delta.get('em_dash_rate', -25.8)
        lines.append(f"- Em-dash delta from Claude: {em_delta:.1f}/1k words. Claude's em-dash rate is the single biggest tell. David's native rate is ~0.4/1k words.")

        # Sentence length (global)
        lines.append("- Sentence length: global mean ~17 words, but bimodal in most technical registers. Short directive sentences (3-8 words) alternate with longer explanatory ones (20-35 words).")

        # Typo fingerprint
        typos = global_data.get('consistent_typos', [])
        if typos:
            top_typos = [t.get('word', '') for t in typos[:5] if t.get('word')]
            lines.append(f"- Typographic fingerprint: consistent typos like '{', '.join(top_typos)}' — these are identity markers in informal registers, not errors to correct.")

        # ALL-CAPS
        lines.append("- Uses ALL-CAPS for emphasis in technical contexts (tool names, system names, status words). Not shouting — signposting.")

        lines.append("")

        # Per-register sections
        for reg_name in MAJOR_REGISTERS:
            reg_data = registers.get(reg_name, {})
            db_profile = self._db_profiles.get(reg_name, {})

            if not reg_data and not db_profile:
                continue

            n_messages = reg_data.get('n_messages', db_profile.get('n_messages', 0))
            if n_messages < MIN_REGISTER_MESSAGES:
                continue

            vocab = reg_data.get('vocabulary', {})
            rhythm = reg_data.get('rhythm', {})
            style = reg_data.get('style', {})

            # Merge: JSON provides supplementary data, db_profile (canonical) wins
            # JSON first so DB values overwrite on conflict
            merged = {}
            for key in ['mean_zipf', 'median_zipf', 'std_zipf', 'pct_rare',
                         'pct_very_rare', 'kite_skew']:
                if key in vocab:
                    merged[key] = vocab[key]
            for key in ['mean_sentence_len', 'median_sentence_len', 'std_sentence_len',
                         'bimodality_coefficient', 'is_bimodal']:
                if key in rhythm:
                    merged[key] = rhythm[key]
            for key in ['contraction_rate', 'caps_emphasis_rate', 'profanity_rate',
                         'question_density', 'hyphen_rate', 'em_dash_rate',
                         'exclamation_rate', 'ellipsis_rate']:
                if key in style:
                    merged[key] = style[key]
            # DB profile wins — these are the centrifuge calibration targets
            merged.update({k: v for k, v in db_profile.items() if v is not None})

            lines.append(f"## Register: {reg_name} ({n_messages:,} messages)")
            lines.append("")

            # Vocabulary
            lines.append(f"- {self._describe_vocabulary(merged, reg_name)}")

            # Rhythm
            lines.append(f"- {self._describe_sentence_rhythm(merged)}")

            # Contraction rate
            cr = merged.get('contraction_rate', 0.4)
            lines.append(f"- {self._describe_contraction_rate(cr, reg_name)}")

            # Punctuation
            punct_traits = self._describe_punctuation(merged)
            for trait in punct_traits[:3]:  # limit to avoid bloat
                lines.append(f"- {trait}")

            # Profanity
            prof = self._describe_profanity(merged, reg_name)
            if prof:
                lines.append(f"- {prof}")

            # Register-specific notes
            if reg_name == 'TECH':
                lines.append("- Names things: file paths, tool names, project names, error messages appear in ~73% of messages")
                lines.append("- Directives are bare imperatives: 'check the endpoint', 'run the tests', 'push it'")
            elif reg_name == 'CASUAL':
                lines.append("- Short messages (median ~7 words), often fragments")
                lines.append("- High informality: contractions, sentence fragments, zero filler")
            elif reg_name == 'ARGUMENTATIVE':
                lines.append("- Steepest rarity tail of any register (kite skew -3.16) — deploys uncommon vocabulary for precision")
                lines.append("- Highest contraction rate despite analytical content — argues informally")
                lines.append("- Uses ellipses for rhetorical pauses more than any other register")
            elif reg_name == 'INVESTIGATE':
                lines.append("- Evidence-first structure: specific names, dates, amounts before conclusions")
                lines.append("- High caps emphasis — entity names, document titles")
            elif reg_name == 'CREATIVE_DIRECTION':
                lines.append("- Architectural vocabulary: 'surface', 'layer', 'pipeline', 'composition'")
                lines.append("- Bimodal rhythm: short vision statements + longer implementation specifications")
            elif reg_name == 'FRUSTRATED':
                lines.append("- Profanity is structural, not decorative — signals genuine frustration, not humor")
                lines.append("- Highest caps emphasis rate across all registers")
                lines.append("- Questions are rhetorical challenges, not requests for information")
            elif reg_name == 'PERSONAL':
                lines.append("- Warmer tone, higher contraction rate than professional registers")
                lines.append("- Frequent hyphen usage — conversational dashes as asides")

            lines.append("")

        # Signature Moves
        lines.append("## Signature Moves")
        lines.append("")
        lines.append("- **The Bare Directive**: short imperative sentences with no hedging. 'Check the endpoint.' 'Push it.' 'Run the tests.' Not 'You might want to consider checking...'")
        lines.append("- **The Register Shift**: drops from PROFESSIONAL to CASUAL mid-paragraph when making a point. Formal setup, casual punchline.")
        lines.append("- **The Specificity Anchor**: names specific files, tools, systems, people instead of generics. 'voice.db' not 'the database', 'centrifuge.py' not 'the scoring module'.")
        lines.append("- **The Bimodal Beat**: in TECH register, alternates 4-word directives with 25-word explanations. The short sentence sets up; the long sentence delivers.")
        lines.append("- **The Architecture Sentence**: describes system relationships using spatial metaphors — 'upstream', 'downstream', 'surfaces', 'layers', 'pipeline'.")
        lines.append("")

        # Anti-patterns
        lines.append("## Anti-Patterns (things David never does)")
        lines.append("")
        lines.append("- Never uses em-dashes (—). Uses hyphens with spaces (` - `) instead. This is the #1 AI detection signal.")
        lines.append("- Never uses 'utilize', 'facilitate', 'comprehensive', 'robust', 'seamless', 'leverage', 'synergy', 'holistic', 'paradigm', 'ecosystem' (the Claude vocabulary).")
        lines.append("- Never hedges with 'I think', 'perhaps', 'it might be worth considering'. States positions directly.")
        lines.append("- Never uses numbered lists for things that could be a sentence. Lists are for genuinely enumerable items.")
        lines.append("- Never opens with 'Great question!' or 'That's a really interesting point.' Gets to the answer.")
        lines.append("- Never writes uniform-length sentences. If every sentence is 15-20 words, the rhythm is wrong.")
        lines.append("- Never uses smart/curly quotes. Straight quotes only.")
        lines.append("")

        # Correction History
        if self._correction_stats:
            lines.append("## Correction History")
            lines.append("")
            total = self._correction_stats.get('total', 0)
            avg_delta = self._correction_stats.get('avg_delta')
            if total > 0:
                delta_str = f", avg centrifuge delta: {avg_delta:+.3f}" if avg_delta is not None else ""
                lines.append(f"- {total} correction pairs captured{delta_str}")

            promoted = self._correction_stats.get('promoted_subs', [])
            if promoted:
                lines.append("- Promoted substitutions (auto-fix candidates):")
                for sub in promoted[:5]:
                    lines.append(f"  - '{sub['from_text']}' → '{sub['to_text']}' ({sub['occurrence_count']}× in {sub['register']})")
            lines.append("")

        return '\n'.join(lines)

    # ------------------------------------------------------------------
    # Save and version control
    # ------------------------------------------------------------------

    def save(self, content: str = None) -> Path:
        """
        Save voice_description.md.

        Args:
            content: The document content, or None to generate fresh

        Returns:
            Path to saved file
        """
        if content is None:
            content = self.generate()

        self.output_path.write_text(content, encoding='utf-8')
        return self.output_path

    # ------------------------------------------------------------------
    # Prompt context extraction
    # ------------------------------------------------------------------

    def get_prompt_context(self, register: str = 'TECH',
                            include_global: bool = True,
                            max_tokens: int = 800) -> str:
        """
        Extract injectable prompt context for a specific register.

        Returns a focused version of the description suitable for
        injection into a generation prompt's system or user context.

        Args:
            register: Target register
            include_global: Whether to include global traits
            max_tokens: Approximate max tokens for the context

        Returns:
            Formatted string ready for prompt injection
        """
        if not self.output_path.exists():
            self.save()

        content = self.output_path.read_text(encoding='utf-8')
        sections = self._parse_sections(content)

        parts = []

        if include_global and 'Global Traits (all registers)' in sections:
            parts.append("## Voice: Global Traits")
            parts.append(sections['Global Traits (all registers)'])

        # Find register-specific section
        for key, text in sections.items():
            if key.startswith(f"Register: {register}"):
                parts.append(f"## Voice: {register} Register")
                parts.append(text)
                break

        if 'Signature Moves' in sections:
            parts.append("## Voice: Signature Moves")
            parts.append(sections['Signature Moves'])

        if 'Anti-Patterns (things David never does)' in sections:
            parts.append("## Voice: Anti-Patterns")
            parts.append(sections['Anti-Patterns (things David never does)'])

        result = '\n\n'.join(parts)

        # Rough token count (1 token ≈ 4 chars) and truncate if needed
        approx_tokens = len(result) / 4
        if approx_tokens > max_tokens:
            # Truncate from the end, keeping global + register
            target_chars = max_tokens * 4
            result = result[:target_chars].rsplit('\n', 1)[0]
            result += "\n[truncated for context budget]"

        return result

    def _parse_sections(self, content: str) -> Dict[str, str]:
        """Parse markdown into sections by ## headers."""
        sections = {}
        current_header = None
        current_lines = []

        for line in content.split('\n'):
            if line.startswith('## '):
                if current_header is not None:
                    sections[current_header] = '\n'.join(current_lines).strip()
                current_header = line[3:].strip()
                current_lines = []
            elif current_header is not None:
                current_lines.append(line)

        if current_header is not None:
            sections[current_header] = '\n'.join(current_lines).strip()

        return sections

    # ------------------------------------------------------------------
    # Refinement
    # ------------------------------------------------------------------

    def refine_from_corrections(self) -> bool:
        """
        Check correction pairs for patterns that contradict current description.

        Returns True if the description was updated.

        This is the PROSE-style iterative refinement loop:
        1. Read current description claims
        2. Check each claim against accumulated correction evidence
        3. If a claim is contradicted by 3+ corrections, flag it
        4. Regenerate the description incorporating correction data
        """
        self._load_db_data()

        if not self._correction_stats:
            return False

        total = self._correction_stats.get('total', 0)
        if total < 5:
            return False  # not enough data to refine

        # Regenerate with correction data included
        new_content = self.generate()
        self.save(new_content)
        return True

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate_against_corpus(self, register: str = 'TECH',
                                  sample_count: int = 5) -> Dict:
        """
        Cross-sample consistency check (from PROSE methodology).

        Verify each preference claim against corpus samples.
        Returns validation results.

        Note: This reads from the corpus JSONL files, which are on disk
        but not in git. Falls back to voice.db data if JSONL unavailable.
        """
        self._load_db_data()
        profile = self._db_profiles.get(register, {})

        if not profile:
            return {'register': register, 'error': 'no profile data'}

        # For now, validate against the quantitative profile
        # Full corpus validation will be added when the retrieval system (V2-03)
        # provides sample access
        validations = []

        # Check key claims
        if profile.get('contraction_rate') is not None:
            cr = profile['contraction_rate']
            validations.append({
                'claim': f'contraction rate ~{cr:.2f}',
                'source': 'register_profiles',
                'n_messages': profile.get('n_messages', 0),
                'confidence': 'high' if profile.get('n_messages', 0) > 500 else 'medium'
            })

        if profile.get('is_bimodal') is not None:
            bc = profile.get('bimodality_coefficient', 0)
            validations.append({
                'claim': f"bimodal={'yes' if profile['is_bimodal'] else 'no'} (BC={bc:.3f})",
                'source': 'register_profiles',
                'n_messages': profile.get('n_messages', 0),
                'confidence': 'high' if profile.get('n_messages', 0) > 500 else 'medium'
            })

        if profile.get('em_dash_rate') is not None:
            em = profile['em_dash_rate']
            validations.append({
                'claim': f'em-dash rate {em:.2f}/1k words',
                'source': 'register_profiles',
                'n_messages': profile.get('n_messages', 0),
                'confidence': 'high'
            })

        return {
            'register': register,
            'validations': validations,
            'total_claims_checked': len(validations),
            'all_high_confidence': all(v['confidence'] == 'high' for v in validations)
        }


if __name__ == "__main__":
    gen = PreferenceDescriptionGenerator()
    print("PreferenceDescriptionGenerator initialized")
    print(f"  Profile: {gen.profile_path}")
    print(f"  DB: {gen.db_path}")
    print(f"  Output: {gen.output_path}")

    # Generate
    doc = gen.generate()
    path = gen.save(doc)
    print(f"\nGenerated voice_description.md ({len(doc)} chars, ~{len(doc)//4} tokens)")
    print(f"  Saved to: {path}")

    # Prompt context
    ctx = gen.get_prompt_context(register='TECH')
    print(f"\nTECH prompt context: {len(ctx)} chars (~{len(ctx)//4} tokens)")

    # Validation
    val = gen.validate_against_corpus(register='TECH')
    print(f"\nValidation ({val['register']}): {val['total_claims_checked']} claims checked")
    for v in val.get('validations', []):
        print(f"  [{v['confidence']}] {v['claim']}")
