"""Final commit: STATUS.md + handoff doc."""
import subprocess
REPO = r"D:\Projects\SCRVNR"
GIT = r"d:\Program Files\Git\cmd\git.exe"
LOG = r"D:\Projects\SCRVNR\learning\scripts\commit_final_log.txt"
def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
def run(*args):
    r = subprocess.run([GIT, "-C", REPO] + list(args), capture_output=True, text=True, timeout=120)
    log(f"$ git {' '.join(args)} -> rc={r.returncode} | {r.stdout.strip()[:300]} | {r.stderr.strip()[:300]}")
    return r
log("=== start ===")
run("add", "-A")
run("commit", "-m", "docs: session close — STATUS.md + publish handoff for davidkirsch.me")
run("log", "--oneline", "-5")
log("=== end ===")
