"""VFP-03 Task 2: Extract quantitative linguistic features from tagged corpus."""
import json
import re
import time
import statistics
from collections import Counter
from wordfreq import zipf_frequency
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords

INPUT = r"D:\Projects\SCRVNR\research\voice_fingerprint\tagged_corpus_v2.jsonl"
OUTPUT = r"D:\Projects\SCRVNR\research\voice_fingerprint\features.jsonl"
PROGRESS_INTERVAL = 5000

# Pre-cache stopwords
STOPWORDS = set(stopwords.words("english"))

# Acronym exclusion set for caps emphasis detection
ACRONYMS = {
    "I","API","URL","HTML","CSS","JSON","SQL","MCP","KERNL","SCRVNR","VIGIL",
    "TESSRYX","AEGIS","ASURIQ","COVOS","GPT","LLM","NER","FTS","RLS","RPC",
    "YAML","PDF","SMS","MMS","OK","ID","UI","UX","CLI","SDK","NPM","GIT",
    "SSH","TCP","HTTP","REST","CRUD","AWS","GCP","ETA","CEO","COO","LLC",
    "DBA","EIN","IRS","SEC","FEC","DOJ","FBI","CIA","NSA","FOIA","PAC",
    "AIPAC","NATO","IMF","UN","EU","USA","CA","BSOD","SSD","HDD","RAM",
    "CPU","GPU","USB","HDMI","OG","TDC","PCV","ATF","FWD",
}

# Pre-compiled regexes
RE_WORD = re.compile(r"[a-zA-Z''\-]+")
RE_PUNCT_STRIP = re.compile(r"^[^a-zA-Z]+|[^a-zA-Z]+$")
RE_CONTRACTION = re.compile(r"\b\w+(n't|'re|'ll|'ve|'m|'d)\b", re.IGNORECASE)
RE_POSSESSIVE = re.compile(r"\b\w+'s\b", re.IGNORECASE)
RE_CAPS_WORD = re.compile(r"\b([A-Z]{2,})\b")
RE_PROFANITY = re.compile(
    r"\b(fuck|shit|damn|hell|ass|bullshit|wtf|stfu|lmao)\b", re.IGNORECASE
)
RE_DOUBLE_PERIOD = re.compile(r"\.\.(?!\.)")
RE_HYPHEN = re.compile(r" - ")
RE_EM_DASH = re.compile(r"—| — ")
RE_ELLIPSIS = re.compile(r"\.\.\.")
RE_FILE_PATH = re.compile(r"[A-Z]:\\|/mnt/|/home/|~/")
RE_URL = re.compile(r"https?://|www\.")
RE_DOLLAR = re.compile(r"\$\d+")
RE_NAMED_ENTITY = re.compile(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b")
RE_NUMBER = re.compile(r"\b\d+(?:\.\d+)?\b")

PROFANITY_SET = {"fuck","shit","damn","hell","ass","bullshit","wtf","stfu","lmao",
                 "fucking","fucked","shitty","damned","asses"}

def extract_features(text):
    """Compute all feature groups for a single message."""
    if not text or not text.strip():
        return empty_features()

    # === A. Word-Level Features ===
    words_raw = text.split()
    word_count = len(words_raw)
    if word_count == 0:
        return empty_features()

    # Clean words for vocabulary analysis
    words_lower = [w.lower() for w in words_raw]
    unique_words = len(set(words_lower))
    ttr = unique_words / word_count if word_count > 0 else 0
    mean_word_length = sum(len(w) for w in words_raw) / word_count

    # === B. Vocabulary Rarity Features ===
    # Strip punctuation from word boundaries, filter stopwords and short words
    content_words = []
    for w in words_lower:
        cleaned = RE_PUNCT_STRIP.sub("", w)
        if cleaned and len(cleaned) >= 3 and cleaned not in STOPWORDS:
            content_words.append(cleaned)

    if word_count >= 3 and len(content_words) >= 1:
        zipf_scores = []
        for cw in content_words:
            z = zipf_frequency(cw, "en")
            zipf_scores.append(z)

        nonzero_zipf = [z for z in zipf_scores if z > 0]
        mean_zipf = statistics.mean(zipf_scores) if zipf_scores else None
        median_zipf = statistics.median(zipf_scores) if zipf_scores else None
        min_zipf = min(nonzero_zipf) if nonzero_zipf else None
        pct_rare = sum(1 for z in zipf_scores if 0 < z < 3.0) / len(zipf_scores) * 100 if zipf_scores else None
        pct_very_rare = sum(1 for z in zipf_scores if 0 < z < 2.0) / len(zipf_scores) * 100 if zipf_scores else None
        pct_unknown = sum(1 for z in zipf_scores if z == 0) / len(zipf_scores) * 100 if zipf_scores else None

        # Rarest word (lowest nonzero zipf)
        if nonzero_zipf:
            min_z = min(nonzero_zipf)
            rarest_idx = next(i for i, z in enumerate(zipf_scores) if z == min_z)
            rarest_word = content_words[rarest_idx]
        else:
            rarest_word = None
    else:
        mean_zipf = median_zipf = min_zipf = None
        pct_rare = pct_very_rare = pct_unknown = None
        rarest_word = None

    # === C. Sentence-Level Features ===
    sentences = sent_tokenize(text)
    sentence_count = len(sentences)
    sent_lengths = [len(s.split()) for s in sentences]

    if sent_lengths:
        mean_sent_len = statistics.mean(sent_lengths)
        median_sent_len = statistics.median(sent_lengths)
        max_sent_len = max(sent_lengths)
        min_sent_len = min(sent_lengths)
        std_sent_len = statistics.pstdev(sent_lengths) if len(sent_lengths) > 1 else 0
        if len(sent_lengths) >= 3:
            from scipy.stats import skew as scipy_skew
            sent_len_skew = float(scipy_skew(sent_lengths))
        else:
            sent_len_skew = None
    else:
        mean_sent_len = median_sent_len = max_sent_len = min_sent_len = 0
        std_sent_len = 0
        sent_len_skew = None

    question_count = sum(1 for s in sentences if s.strip().endswith("?"))
    question_density = question_count / sentence_count if sentence_count > 0 else 0

    # === D. Character-Level / Style Features ===
    contraction_matches = RE_CONTRACTION.findall(text)
    contraction_count = len(contraction_matches)
    contraction_rate = contraction_count / word_count * 100 if word_count > 0 else 0

    # Caps emphasis: ALL-CAPS words mid-sentence, excluding acronyms
    caps_matches = RE_CAPS_WORD.findall(text)
    caps_emphasis_count = sum(1 for c in caps_matches if c not in ACRONYMS)
    caps_emphasis_rate = caps_emphasis_count / word_count * 1000 if word_count > 0 else 0

    profanity_matches = RE_PROFANITY.findall(text)
    profanity_count = len(profanity_matches)
    profanity_rate = profanity_count / word_count * 1000 if word_count > 0 else 0

    double_period_count = len(RE_DOUBLE_PERIOD.findall(text))
    hyphen_count = len(RE_HYPHEN.findall(text))
    em_dash_count = len(RE_EM_DASH.findall(text))
    exclamation_count = text.count("!")
    ellipsis_count = len(RE_ELLIPSIS.findall(text))

    # === E. Specificity Features ===
    has_file_path = bool(RE_FILE_PATH.search(text))
    has_url = bool(RE_URL.search(text))
    has_dollar_amount = bool(RE_DOLLAR.search(text))
    has_named_entity = bool(RE_NAMED_ENTITY.search(text))
    number_tokens = len(RE_NUMBER.findall(text))
    number_density = number_tokens / word_count if word_count > 0 else 0

    return {
        # A. Word-Level
        "word_count": word_count,
        "unique_words": unique_words,
        "type_token_ratio": round(ttr, 4),
        "mean_word_length": round(mean_word_length, 2),
        # B. Vocabulary Rarity
        "mean_zipf": round(mean_zipf, 3) if mean_zipf is not None else None,
        "median_zipf": round(median_zipf, 3) if median_zipf is not None else None,
        "min_zipf": round(min_zipf, 3) if min_zipf is not None else None,
        "pct_rare": round(pct_rare, 2) if pct_rare is not None else None,
        "pct_very_rare": round(pct_very_rare, 2) if pct_very_rare is not None else None,
        "pct_unknown": round(pct_unknown, 2) if pct_unknown is not None else None,
        "rarest_word": rarest_word,
        # C. Sentence-Level
        "sentence_count": sentence_count,
        "mean_sentence_len": round(mean_sent_len, 2),
        "median_sentence_len": round(median_sent_len, 1),
        "max_sentence_len": max_sent_len,
        "min_sentence_len": min_sent_len,
        "std_sentence_len": round(std_sent_len, 2),
        "sentence_len_skew": round(sent_len_skew, 3) if sent_len_skew is not None else None,
        "question_count": question_count,
        "question_density": round(question_density, 3),
        # D. Character-Level / Style
        "contraction_count": contraction_count,
        "contraction_rate": round(contraction_rate, 3),
        "caps_emphasis_count": caps_emphasis_count,
        "caps_emphasis_rate": round(caps_emphasis_rate, 2),
        "profanity_count": profanity_count,
        "profanity_rate": round(profanity_rate, 2),
        "double_period_count": double_period_count,
        "hyphen_count": hyphen_count,
        "em_dash_count": em_dash_count,
        "exclamation_count": exclamation_count,
        "ellipsis_count": ellipsis_count,
        # E. Specificity
        "has_file_path": has_file_path,
        "has_url": has_url,
        "has_dollar_amount": has_dollar_amount,
        "has_named_entity": has_named_entity,
        "number_density": round(number_density, 4),
    }


def empty_features():
    """Return a feature dict with all values as None/0 for empty messages."""
    return {
        "word_count": 0, "unique_words": 0, "type_token_ratio": 0,
        "mean_word_length": 0,
        "mean_zipf": None, "median_zipf": None, "min_zipf": None,
        "pct_rare": None, "pct_very_rare": None, "pct_unknown": None,
        "rarest_word": None,
        "sentence_count": 0, "mean_sentence_len": 0, "median_sentence_len": 0,
        "max_sentence_len": 0, "min_sentence_len": 0, "std_sentence_len": 0,
        "sentence_len_skew": None, "question_count": 0, "question_density": 0,
        "contraction_count": 0, "contraction_rate": 0,
        "caps_emphasis_count": 0, "caps_emphasis_rate": 0,
        "profanity_count": 0, "profanity_rate": 0,
        "double_period_count": 0, "hyphen_count": 0, "em_dash_count": 0,
        "exclamation_count": 0, "ellipsis_count": 0,
        "has_file_path": False, "has_url": False, "has_dollar_amount": False,
        "has_named_entity": False, "number_density": 0,
    }


def main():
    start = time.time()
    total = 0
    feature_count = 0

    with open(INPUT, "r", encoding="utf-8") as fin, \
         open(OUTPUT, "w", encoding="utf-8") as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            msg = json.loads(line)
            total += 1

            text = msg.get("text", "")
            features = extract_features(text)
            feature_count = len(features)

            # F. Metadata (pass-through)
            record = {
                "source": msg.get("source"),
                "register": msg.get("register"),
                "timestamp": msg.get("timestamp"),
                "conversation_id": msg.get("conversation_id"),
                "word_count_original": msg.get("word_count"),
            }
            record.update(features)
            fout.write(json.dumps(record, ensure_ascii=False) + "\n")

            if total % PROGRESS_INTERVAL == 0:
                elapsed = time.time() - start
                rate = total / elapsed if elapsed > 0 else 0
                print(f"  [{total:,} messages] {elapsed:.1f}s ({rate:.0f} msg/s)")

    elapsed = time.time() - start
    print(f"\n=== Feature Extraction Complete ===")
    print(f"Total messages: {total:,}")
    print(f"Features per message: {feature_count}")
    print(f"Processing time: {elapsed:.1f}s ({total/elapsed:.0f} msg/s)")

if __name__ == "__main__":
    main()
