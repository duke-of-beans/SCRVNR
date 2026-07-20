import sys, json, shutil
sys.path.insert(0, r'D:\Projects\SCRVNR')

# First, copy the v2 file - read from outputs location
# The v2 content needs to come from the rewrite
# Since the file is on the container, let's just score the v1 against itself
# and note the comparison needs the v2 file transferred

# Actually - let's score the ORIGINAL (v1) which we already have on disk
from core.centrifuge import VoiceCentrifuge
c = VoiceCentrifuge()

text_v1 = open(r'D:\Projects\SCRVNR\research\voice_fingerprint\test_crazy_in_tents_v1.md', encoding='utf-8').read()

output = []
output.append("ORIGINAL ESSAY SCORES (v1)\n")
output.append(f"Word count: {len(text_v1.split())}\n")

registers = ['INVESTIGATE', 'ARGUMENTATIVE', 'CREATIVE_DIRECTION', 'PROFESSIONAL']
for reg in registers:
    r = c.score(text_v1, reg)
    output.append(f"{reg}: overall={r['overall_score']:.4f} rarity={r['rarity_score']:.4f} rhythm={r['rhythm_score']:.4f} style={r['style_score']:.4f}")

# Count contractions in v1
import re
contractions = len(re.findall(r"(?i)\b\w+(?:'(?:t|s|re|ve|ll|m|d))\b", text_v1))
words = len(text_v1.split())
output.append(f"\nContraction count: {contractions}")
output.append(f"Contraction rate: {contractions/words*100:.1f}%")

# Count em-dashes
em_dashes = text_v1.count('\u2014') + text_v1.count(' \u2014 ')
output.append(f"Em-dash count: {em_dashes}")

# Sentence length stats
import nltk
sents = nltk.sent_tokenize(text_v1)
lens = [len(s.split()) for s in sents]
output.append(f"Sentence count: {len(sents)}")
output.append(f"Mean sentence length: {sum(lens)/len(lens):.1f}")
output.append(f"Min/Max: {min(lens)}/{max(lens)}")
import statistics
output.append(f"Std: {statistics.stdev(lens):.1f}")

# Short sentences (<=6 words)
short = sum(1 for l in lens if l <= 6)
output.append(f"Short sentences (<=6 words): {short} ({short/len(sents)*100:.1f}%)")
long_s = sum(1 for l in lens if l >= 25)
output.append(f"Long sentences (>=25 words): {long_s} ({long_s/len(sents)*100:.1f}%)")

result = '\n'.join(output)
with open(r'D:\Projects\SCRVNR\research\voice_fingerprint\v1_detailed_scores.txt', 'w', encoding='utf-8') as f:
    f.write(result)
print(result)
