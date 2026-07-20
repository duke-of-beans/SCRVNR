"""
Secret Scrubber — Strip API keys and secrets from text BEFORE it enters the corpus.

Called by the corpus extraction pipeline (extract_corpus.py) on every message.
Also usable standalone to scrub any text.

This is the FIRST line of defense. The pre-commit hook is the LAST.
.gitignore is the middle layer. All three must hold.

Usage:
    from research.voice_fingerprint.secret_scrubber import scrub
    clean_text = scrub(raw_text)
"""

import re
from typing import List, Tuple

# Each pattern: (compiled regex, replacement string, description)
SECRET_PATTERNS: List[Tuple[re.Pattern, str, str]] = [
    # Anthropic
    (re.compile(r'sk-ant-api\S{20,}'), '[REDACTED_ANTHROPIC_KEY]', 'Anthropic API key'),

    # OpenAI
    (re.compile(r'sk-proj-\S{20,}'), '[REDACTED_OPENAI_KEY]', 'OpenAI project key'),

    # GitHub
    (re.compile(r'ghp_[A-Za-z0-9]{36}'), '[REDACTED_GITHUB_PAT]', 'GitHub PAT'),
    (re.compile(r'github_pat_[A-Za-z0-9_]{60,}'), '[REDACTED_GITHUB_PAT]', 'GitHub fine-grained PAT'),
    (re.compile(r'gho_[A-Za-z0-9]{36}'), '[REDACTED_GITHUB_OAUTH]', 'GitHub OAuth token'),
    (re.compile(r'ghs_[A-Za-z0-9]{36}'), '[REDACTED_GITHUB_APP]', 'GitHub App token'),

    # npm
    (re.compile(r'npm_[A-Za-z0-9]{36}'), '[REDACTED_NPM_TOKEN]', 'npm access token'),

    # Vercel
    (re.compile(r'vcp_[A-Za-z0-9]{50,}'), '[REDACTED_VERCEL_TOKEN]', 'Vercel PAT'),
    (re.compile(r'vck_[A-Za-z0-9]{50,}'), '[REDACTED_VERCEL_KEY]', 'Vercel API key'),

    # Supabase
    (re.compile(r'sbp_[a-f0-9]{40}'), '[REDACTED_SUPABASE_PAT]', 'Supabase PAT'),
    (re.compile(r'sb_secret_[A-Za-z0-9_-]{30,}'), '[REDACTED_SUPABASE_SECRET]', 'Supabase secret key'),
    (re.compile(r'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\.[A-Za-z0-9_-]{50,}\.[A-Za-z0-9_-]{20,}'), '[REDACTED_JWT]', 'JWT token'),

    # Resend
    (re.compile(r're_[A-Za-z0-9]{8}_[A-Za-z0-9]{20,}'), '[REDACTED_RESEND_KEY]', 'Resend API key'),

    # Google
    (re.compile(r'AIzaSy[A-Za-z0-9_-]{33}'), '[REDACTED_GOOGLE_API_KEY]', 'Google API key'),
    (re.compile(r'GOCSPX-[A-Za-z0-9_-]{28,}'), '[REDACTED_GOOGLE_OAUTH_SECRET]', 'Google OAuth secret'),
    (re.compile(r'\d{12}-[a-z0-9]{32}\.apps\.googleusercontent\.com'), '[REDACTED_GOOGLE_CLIENT_ID]', 'Google OAuth client ID'),

    # Stripe
    (re.compile(r'sk_live_[A-Za-z0-9]{24,}'), '[REDACTED_STRIPE_LIVE_KEY]', 'Stripe live secret key'),
    (re.compile(r'sk_test_[A-Za-z0-9]{24,}'), '[REDACTED_STRIPE_TEST_KEY]', 'Stripe test secret key'),
    (re.compile(r'pk_live_[A-Za-z0-9]{24,}'), '[REDACTED_STRIPE_LIVE_PK]', 'Stripe live publishable key'),

    # DeepSeek
    (re.compile(r'sk-[a-f0-9]{32}'), '[REDACTED_DEEPSEEK_KEY]', 'DeepSeek API key'),

    # xAI
    (re.compile(r'xai-[A-Za-z0-9]{60,}'), '[REDACTED_XAI_KEY]', 'xAI API key'),

    # OpenRouter
    (re.compile(r'sk-or-v1-[a-f0-9]{64}'), '[REDACTED_OPENROUTER_KEY]', 'OpenRouter API key'),

    # Railway
    (re.compile(r'railway_[a-f0-9]{32,}'), '[REDACTED_RAILWAY_TOKEN]', 'Railway token'),

    # OpenAI legacy (broader catch - run after more specific patterns)
    (re.compile(r'sk-[a-zA-Z0-9]{40,}'), '[REDACTED_OPENAI_KEY]', 'OpenAI legacy key'),

    # Generic patterns (catch-all, run last)
    (re.compile(r'(?:api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token)\s*[=:]\s*["\']([A-Za-z0-9_-]{20,})["\']', re.IGNORECASE), '[REDACTED_GENERIC_SECRET]', 'Generic secret assignment'),

    # AWS (proactive)
    (re.compile(r'AKIA[A-Z0-9]{16}'), '[REDACTED_AWS_KEY]', 'AWS access key'),
]


def scrub(text: str) -> str:
    """
    Remove all known API key patterns from text.
    Returns the cleaned text with secrets replaced by [REDACTED_*] tags.
    """
    for pattern, replacement, _desc in SECRET_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def scan(text: str) -> List[dict]:
    """
    Scan text for secrets WITHOUT modifying it. Returns list of findings.
    Useful for auditing existing corpus files.
    """
    findings = []
    for pattern, _replacement, desc in SECRET_PATTERNS:
        matches = pattern.findall(text)
        if matches:
            findings.append({
                'type': desc,
                'count': len(matches),
            })
    return findings


def scrub_file(input_path: str, output_path: str = None) -> dict:
    """
    Scrub an entire file line by line. Returns stats.
    If output_path is None, overwrites the input file.
    """
    if output_path is None:
        output_path = input_path

    total_redactions = 0
    total_lines = 0
    redacted_lines = 0

    lines = []
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            total_lines += 1
            cleaned = scrub(line)
            if cleaned != line:
                redacted_lines += 1
                total_redactions += sum(
                    len(p.findall(line)) for p, _, _ in SECRET_PATTERNS
                )
            lines.append(cleaned)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    return {
        'total_lines': total_lines,
        'redacted_lines': redacted_lines,
        'total_redactions': total_redactions,
        'input': input_path,
        'output': output_path,
    }


if __name__ == "__main__":
    # Self-test with synthetic patterns (NOT real keys — those trigger GitHub push protection)
    test_cases = [
        ("sk-ant-api03-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX-XXXX", True, "Anthropic"),
        ("ghp_" + "A" * 36, True, "GitHub PAT"),
        ("npm_" + "B" * 36, True, "npm"),
        ("vcp_" + "C" * 55, True, "Vercel"),
        ("sbp_" + "a" * 40, True, "Supabase PAT"),
        ("re_XXXXXXXX_" + "Y" * 25, True, "Resend"),
        ("AIzaSy" + "X" * 33, True, "Google API"),
        ("sk-" + "a" * 32, True, "DeepSeek"),
        ("xai-" + "Z" * 65, True, "xAI"),
        ("No secrets in this message at all", False, "Clean"),
    ]

    passed = 0
    for text, should_redact, label in test_cases:
        cleaned = scrub(text)
        was_redacted = "[REDACTED" in cleaned
        if was_redacted == should_redact:
            passed += 1
            print(f"  [PASS] {label}")
        else:
            print(f"  [FAIL] {label}: expected redact={should_redact}, got {was_redacted}")

    print(f"\n{passed}/{len(test_cases)} patterns caught")
