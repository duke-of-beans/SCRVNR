"""Add Cultural Stab signature move to voice_description.md"""
p = open(r"D:\Projects\SCRVNR\voice_description.md", "r", encoding="utf-8").read()

new_move = """- **The Cultural Stab**: embeds exact quotes from public figures mid-sentence as dependent clauses that invert the original meaning. 3-8 exact words, no attribution, sentence survives without it, original moment carried public emotion. Reader recognizes it and feels the knife, or the sentence reads clean. Seven rules: (1) exact words not paraphrase, (2) 3-8 words, (3) no attribution, (4) meaning inverts in context, (5) placed at apex of claim, (6) original moment carried emotion, (7) sentence survives without it. All seven must pass."""

p = p.replace("## Anti-Patterns", new_move + "\n\n## Anti-Patterns")
open(r"D:\Projects\SCRVNR\voice_description.md", "w", encoding="utf-8").write(p)
print("Added Cultural Stab to Signature Moves")
