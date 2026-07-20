"""
Centrifuge CLI - Command-line voice profile scoring.

Usage:
  python tools\\centrifuge_cli.py score output.md --register TECH
  echo "some text" | python tools\\centrifuge_cli.py score - --register PERSONAL
  python tools\\centrifuge_cli.py compare original.md revised.md --register INVESTIGATE
  python tools\\centrifuge_cli.py profiles
  python tools\\centrifuge_cli.py profile TECH
"""

import sys
import os
import argparse

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from core.centrifuge import VoiceCentrifuge


# ANSI color codes (graceful fallback)
try:
    _test = sys.stdout.isatty()
    GREEN = '\033[92m' if _test else ''
    RED = '\033[91m' if _test else ''
    YELLOW = '\033[93m' if _test else ''
    CYAN = '\033[96m' if _test else ''
    BOLD = '\033[1m' if _test else ''
    RESET = '\033[0m' if _test else ''
except Exception:
    GREEN = RED = YELLOW = CYAN = BOLD = RESET = ''


def score_label(score):
    """Color-coded score label."""
    if score >= 0.65:
        return f"{GREEN}PASS{RESET}"
    elif score >= 0.50:
        return f"{YELLOW}WARN{RESET}"
    else:
        return f"{RED}FAIL{RESET}"


def print_result(result, label=""):
    """Print a score result with formatting."""
    prefix = f"{BOLD}{label}{RESET} " if label else ""
    overall = result['overall_score']
    print(f"\n{prefix}{BOLD}Overall: {overall:.2f}{RESET} [{score_label(overall)}]")
    print(f"  Register: {CYAN}{result['register']}{RESET}")
    print(f"  Words:    {result['word_count']}")
    print(f"  Time:     {result['processing_ms']:.1f}ms")
    print(f"\n  Rarity:   {result['rarity_score']:.2f} [{score_label(result['rarity_score'])}]")
    print(f"  Rhythm:   {result['rhythm_score']:.2f} [{score_label(result['rhythm_score'])}]")
    print(f"  Style:    {result['style_score']:.2f} [{score_label(result['style_score'])}]")

    if result['flags']:
        print(f"\n  {YELLOW}Flags ({len(result['flags'])}):{RESET}")
        for flag in result['flags']:
            ftype = flag.get('type', '?')
            suggestion = flag.get('suggestion', '')
            detail = ''
            if 'words' in flag:
                detail = f" [{', '.join(flag['words'][:5])}]"
            elif 'count' in flag:
                detail = f" (count: {flag['count']})"
            print(f"    - {ftype}{detail}: {suggestion}")
    print()

def cmd_score(args, centrifuge):
    """Score a file or stdin."""
    if args.file == '-':
        text = sys.stdin.read()
    else:
        with open(args.file, 'r', encoding='utf-8') as f:
            text = f.read()
    if not text.strip():
        print(f"{RED}Error: empty input{RESET}")
        sys.exit(1)
    result = centrifuge.score(text, args.register)
    print_result(result)


def cmd_compare(args, centrifuge):
    """Compare two texts."""
    with open(args.file1, 'r', encoding='utf-8') as f:
        text1 = f.read()
    with open(args.file2, 'r', encoding='utf-8') as f:
        text2 = f.read()
    r1 = centrifuge.score(text1, args.register)
    r2 = centrifuge.score(text2, args.register)

    print(f"\n{BOLD}Comparison ({args.register}):{RESET}")
    print(f"{'':>20} {'File 1':>10} {'File 2':>10} {'Delta':>10}")
    print(f"  {'Overall':>18} {r1['overall_score']:>10.2f} {r2['overall_score']:>10.2f} {r2['overall_score']-r1['overall_score']:>+10.2f}")
    print(f"  {'Rarity':>18} {r1['rarity_score']:>10.2f} {r2['rarity_score']:>10.2f} {r2['rarity_score']-r1['rarity_score']:>+10.2f}")
    print(f"  {'Rhythm':>18} {r1['rhythm_score']:>10.2f} {r2['rhythm_score']:>10.2f} {r2['rhythm_score']-r1['rhythm_score']:>+10.2f}")
    print(f"  {'Style':>18} {r1['style_score']:>10.2f} {r2['style_score']:>10.2f} {r2['style_score']-r1['style_score']:>+10.2f}")
    print(f"  {'Words':>18} {r1['word_count']:>10} {r2['word_count']:>10}")
    print()

    if r2['overall_score'] > r1['overall_score']:
        print(f"  {GREEN}File 2 is closer to David's voice.{RESET}")
    elif r1['overall_score'] > r2['overall_score']:
        print(f"  {YELLOW}File 1 is closer to David's voice.{RESET}")
    else:
        print(f"  Both files score equally.")
    print()

def cmd_profiles(args, centrifuge):
    """Show all register profiles summary."""
    print(f"\n{BOLD}Register Profiles:{RESET}")
    print(f"  {'Register':<22} {'Msgs':>7} {'Words':>10} {'Zipf':>6} {'Rare%':>7} {'Contr':>6} {'Bimodal':>8}")
    print("  " + "-" * 70)
    for reg in centrifuge.available_registers():
        p = centrifuge.get_profile(reg)
        if not p:
            continue
        bimod = "yes" if p.get('is_bimodal') else "no"
        print(f"  {reg:<22} {p.get('n_messages',0):>7} {p.get('n_words',0):>10} "
              f"{p.get('mean_zipf',0):>6.2f} {p.get('pct_rare',0):>6.1f}% "
              f"{p.get('contraction_rate',0):>5.2f} {bimod:>8}")
    print()


def cmd_profile(args, centrifuge):
    """Show a specific register's profile."""
    reg = args.register.upper()
    p = centrifuge.get_profile(reg)
    t = centrifuge.get_target(reg)
    if not p:
        print(f"{RED}Unknown register: {reg}{RESET}")
        print(f"Available: {', '.join(centrifuge.available_registers())}")
        sys.exit(1)

    print(f"\n{BOLD}{CYAN}{reg}{RESET} {BOLD}Register Profile{RESET}")
    print(f"  Messages: {p.get('n_messages',0):,}  |  Words: {p.get('n_words',0):,}")
    print(f"\n  {BOLD}Vocabulary:{RESET}")
    print(f"    Mean Zipf:     {p.get('mean_zipf',0):.4f}")
    print(f"    Median Zipf:   {p.get('median_zipf',0):.4f}")
    print(f"    Std Zipf:      {p.get('std_zipf',0):.4f}")
    print(f"    % Rare:        {p.get('pct_rare',0):.2f}%")
    print(f"    Kite Skew:     {p.get('kite_skew',0):.4f}")
    print(f"\n  {BOLD}Rhythm:{RESET}")
    print(f"    Mean sent len:  {p.get('mean_sentence_len',0):.2f}")
    print(f"    Std sent len:   {p.get('std_sentence_len',0):.2f}")
    print(f"    Bimodal:        {'yes' if p.get('is_bimodal') else 'no'} (coeff: {p.get('bimodality_coefficient',0):.4f})")

    print(f"\n  {BOLD}Style:{RESET}")
    print(f"    Contraction:    {p.get('contraction_rate',0):.4f}")
    print(f"    Caps emphasis:  {p.get('caps_emphasis_rate',0):.4f}")
    print(f"    Profanity:      {p.get('profanity_rate',0):.4f}")
    print(f"    Em-dash:        {p.get('em_dash_rate',0):.4f}")
    print(f"    Exclamation:    {p.get('exclamation_rate',0):.4f}")

    if t:
        print(f"\n  {BOLD}Targets (centrifuge):{RESET}")
        print(f"    Target Zipf:       {t.get('target_mean_zipf',0):.4f} (+/- {t.get('tolerance_zipf',0):.2f})")
        print(f"    Target % rare:     {t.get('target_pct_rare',0):.2f}% (+/- {t.get('tolerance_rare',0):.1f})")
        print(f"    Target contraction:{t.get('target_contraction_rate',0):.4f} (+/- {t.get('tolerance_contraction',0):.2f})")
        print(f"    Target sent len:   {t.get('target_sentence_len_mean',0):.2f} (+/- {t.get('tolerance_sentence',0):.1f})")
    print()


def main():
    parser = argparse.ArgumentParser(
        description='Centrifuge - Voice profile scoring CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest='command')

    # score
    p_score = sub.add_parser('score', help='Score a file against voice profile')
    p_score.add_argument('file', help='File to score (use - for stdin)')
    p_score.add_argument('--register', '-r', default='TECH', help='Target register')

    # compare
    p_cmp = sub.add_parser('compare', help='Compare two files')
    p_cmp.add_argument('file1', help='First file')
    p_cmp.add_argument('file2', help='Second file')
    p_cmp.add_argument('--register', '-r', default='TECH', help='Target register')

    # profiles
    sub.add_parser('profiles', help='Show all register profiles')

    # profile
    p_prof = sub.add_parser('profile', help='Show a specific register profile')
    p_prof.add_argument('register', help='Register name')

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    centrifuge = VoiceCentrifuge()

    if args.command == 'score':
        cmd_score(args, centrifuge)
    elif args.command == 'compare':
        cmd_compare(args, centrifuge)
    elif args.command == 'profiles':
        cmd_profiles(args, centrifuge)
    elif args.command == 'profile':
        cmd_profile(args, centrifuge)


if __name__ == "__main__":
    main()
