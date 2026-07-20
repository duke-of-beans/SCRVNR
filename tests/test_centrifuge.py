#!/usr/bin/env python3
"""
Integration test for VoiceCentrifuge.
VFP-05 Task 8: 5 good strings (David-like) + 3 bad strings (Claude-like).
Good must score > 0.5, bad must score < 0.5.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.centrifuge import VoiceCentrifuge

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "learning", "voice.db")

# --- David-like strings (one per major register) ---
# These must have: varied sentence lengths (bimodal registers need short+long),
# domain-specific vocabulary (lower zipf), and David's punctuation patterns.
GOOD_STRINGS = {
    "TECH": (
        "OK so here's the issue. The WebSocket reconnection handler isn't catching "
        "the TypeError when you pass null params to the PowerShell cmdlet. "
        "I've traced it through the async stack and the devtools console shows "
        "the ERRNO getting swallowed before the orchestration layer even sees it. "
        "Fix: wrap the init callback in a try/catch, check for null before "
        "passing to the cmdlet. Already tested locally. Works."
    ),
    "PROFESSIONAL": (
        "Hit 340% ROAS on Q3. "
        "Ran the full ops stack with 12 direct reports and grew retention "
        "from 61% to 89% in 8 months by rebuilding the onboarding pipeline "
        "that was completely broken when I got there. "
        "Cut vendor costs 23%. "
        "KPIs improved across the board because I restructured the sprint "
        "cycle around deliverables and stopped letting things slip past QA. "
        "Happy people make more products."
    ),
    "PERSONAL": (
        "OK here's the thing. "
        "The AUTONOMIC lifelog timestamps from the SHIM layer keep telling "
        "the same story every single time I pull the orchestration data. "
        "The KERNL doesn't lie. "
        "It's not about money and it never was about that at all. "
        "The real question is whether the triangulation between what we SAY "
        "and what we ACTUALLY ship holds up to any serious scrutiny whatsoever. "
        "LIFELOG says no."
    ),
    "ACADEMIC": (
        "Three competing frameworks explain the bimodality coefficient. "
        "First: contraction rate doesn't correlate linearly with formality. "
        "That's falsifiable. PROVISIONAL at best. "
        "Evidence from the corpus shows register detection can't be purely "
        "lexical because we'd observe consistent kite skew within registers "
        "and we DON'T, which means there's a latent variable driving the "
        "triangulation between vocabulary rarity and sentence rhythm "
        "that the HIRM framework hasn't accounted for. Speculative but testable."
    ),
    "CASUAL": (
        "yeah that works. nice! wait hold on. "
        "lol I just realized the whole thing's broken. "
        "ok let's do it tomorrow. "
        "sounds good!"
    ),
}

# --- Claude-like strings (should score low) ---
BAD_STRINGS = {
    "claude_formal": (
        "I would be happy to help you with that. It is important to note "
        "that there are several considerations to keep in mind. First and "
        "foremost, one should carefully evaluate the various options "
        "available. Furthermore, it is worth mentioning that the "
        "implementation — while straightforward — requires careful "
        "attention to detail. I hope this helps clarify the situation."
    ),
    "claude_listy": (
        "Here are the key points to consider: First, the architecture "
        "should be modular and extensible. Second, the implementation "
        "needs to be robust and well-tested. Third, the documentation "
        "should be comprehensive and up-to-date. Additionally, it is "
        "essential to ensure that the codebase remains maintainable "
        "and that best practices are followed throughout the process."
    ),
    "claude_hedged": (
        "That is an excellent question. There are indeed multiple "
        "perspectives to consider here. On one hand, the approach "
        "you have described could potentially yield positive results. "
        "On the other hand, it might be worth exploring alternative "
        "strategies that could perhaps offer additional benefits. "
        "Ultimately, the decision depends on your specific requirements."
    ),
}

def main():
    print("=" * 60)
    print("VFP-05 INTEGRATION TEST: VoiceCentrifuge")
    print("=" * 60)
    
    centrifuge = VoiceCentrifuge(DB_PATH)
    print(f"\nLoaded registers: {centrifuge.available_registers()}")
    
    passed = 0
    failed = 0
    total = len(GOOD_STRINGS) + len(BAD_STRINGS)
    
    # Test good strings (David-like) — should score > 0.5
    print("\n--- GOOD STRINGS (expect > 0.5) ---")
    for register, text in GOOD_STRINGS.items():
        result = centrifuge.score(text, register)
        status = "PASS" if result["overall_score"] > 0.5 else "FAIL"
        if status == "PASS":
            passed += 1
        else:
            failed += 1
        print(f"  {register:20s} -> {result['overall_score']:.3f}  [{status}]"
              f"  (rarity={result['rarity_score']:.2f} rhythm={result['rhythm_score']:.2f}"
              f" style={result['style_score']:.2f})")
    
    # Test bad strings (Claude-like) — should score < 0.5
    print("\n--- BAD STRINGS (expect < 0.5) ---")
    for label, text in BAD_STRINGS.items():
        # Score against TECH as default register
        result = centrifuge.score(text, "TECH")
        status = "PASS" if result["overall_score"] < 0.5 else "FAIL"
        if status == "PASS":
            passed += 1
        else:
            failed += 1
        print(f"  {label:20s} -> {result['overall_score']:.3f}  [{status}]"
              f"  (rarity={result['rarity_score']:.2f} rhythm={result['rhythm_score']:.2f}"
              f" style={result['style_score']:.2f})")
        if result.get("flags"):
            flag_types = [f['type'] for f in result['flags']]
            print(f"    flags: {', '.join(flag_types)}")
    
    # Summary
    print(f"\n{'=' * 60}")
    print(f"RESULT: {passed}/{total} passed, {failed}/{total} failed")
    if failed == 0:
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
    print(f"{'=' * 60}")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
