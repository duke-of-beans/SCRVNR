"""Commit subtitle fix."""
import subprocess
REPO = r"D:\Projects\SCRVNR"
GIT = r"d:\Program Files\Git\cmd\git.exe"
LOG = r"D:\Projects\SCRVNR\learning\scripts\commit2_log.txt"
def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
def run(*args):
    r = subprocess.run([GIT, "-C", REPO] + list(args), capture_output=True, text=True, timeout=120)
    log(f"$ git {' '.join(args)} -> rc={r.returncode} | {r.stdout.strip()[:300]} | {r.stderr.strip()[:300]}")
    return r
log("=== start ===")
run("add", "-A")
run("commit", "-m", "fix(voice): move subtitle to essay level - On hollow wills and sharp receipts")
run("log", "--oneline", "-3")
log("=== end ===")
