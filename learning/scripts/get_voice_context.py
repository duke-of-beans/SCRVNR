"""Quick pipeline context pull for ARGUMENTATIVE register rewrite."""
import sys
sys.path.insert(0, r"D:\Projects\SCRVNR")
from core.pipeline import VoicePipeline

pipe = VoicePipeline()

# Get voice context for ARGUMENTATIVE register
ctx = pipe.build_generation_context(
    "economic policy multiplicative composition austerity trickle-down investment returns at the bottom society",
    register='ARGUMENTATIVE',
    k=5
)

print("=== VOICE CONTEXT ===")
print(ctx['voice_context'][:4000])
print(f"\n=== STATS ===")
print(f"Examples: {ctx['examples_retrieved']}")
print(f"Confidence: {ctx['retrieval_confidence']}")
print(f"Tokens: ~{ctx['context_tokens_approx']}")

# Also get the preference description for ARGUMENTATIVE
from core.preference_description import PreferenceDescriptionGenerator
gen = PreferenceDescriptionGenerator()
desc_ctx = gen.get_prompt_context(register='ARGUMENTATIVE')
print(f"\n=== ARGUMENTATIVE VOICE DESCRIPTION ===")
print(desc_ctx[:2000])

# Get promoted substitutions
from core.correction_capture import CorrectionCapture
cc = CorrectionCapture()
promoted = cc.get_promoted_substitutions(register='ARGUMENTATIVE')
print(f"\n=== PROMOTED SUBSTITUTIONS (ARGUMENTATIVE) ===")
for p in promoted:
    print(f"  '{p['from']}' -> '{p['to']}' ({p['count']}x)")
if not promoted:
    print("  (none yet)")
