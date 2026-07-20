import sys, json
sys.path.insert(0, r'D:\Projects\SCRVNR')
from core.centrifuge import VoiceCentrifuge

c = VoiceCentrifuge()
text = open(r'D:\Projects\SCRVNR\research\voice_fingerprint\test_crazy_in_tents.md', encoding='utf-8').read()

output_lines = []
registers = ['INVESTIGATE', 'ARGUMENTATIVE', 'TECH', 'CREATIVE_DIRECTION', 'PROFESSIONAL']
for reg in registers:
    try:
        r = c.score(text, reg)
        output_lines.append(f"\n{'='*60}")
        output_lines.append(f"REGISTER: {reg}")
        output_lines.append(f"{'='*60}")
        output_lines.append(json.dumps(r, indent=2, default=str))
    except Exception as e:
        output_lines.append(f"\nERROR for {reg}: {e}")

result = '\n'.join(output_lines)
with open(r'D:\Projects\SCRVNR\research\voice_fingerprint\centrifuge_results.txt', 'w', encoding='utf-8') as f:
    f.write(result)

print(f"Done. {len(registers)} registers scored. Output at centrifuge_results.txt")
