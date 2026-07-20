"""Scrub all corpus JSONL files on disk. One-time cleanup."""
import glob
import sys
sys.path.insert(0, r"D:\Projects\SCRVNR")
from research.voice_fingerprint.secret_scrubber import scrub_file

files = glob.glob(r"D:\Projects\SCRVNR\research\voice_fingerprint\*.jsonl")
print(f"Found {len(files)} JSONL files to scrub")

for f in files:
    result = scrub_file(f)
    print(f"  {result['input'].split('voice_fingerprint\\\\')[-1] if 'voice_fingerprint' in result['input'] else result['input']}: "
          f"{result['redacted_lines']} lines scrubbed, {result['total_redactions']} secrets removed")

print("Done. All corpus files on disk are now clean.")
