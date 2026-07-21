"""Commit via python subprocess - bypass flaky shell launcher. Verify STATUS.md state first."""
import subprocess, shutil, os, traceback

LOG = r"D:\Projects\SCRVNR\learning\scripts\commit_log.txt"
def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

log("=== commit start ===")
REPO = r"D:\Projects\SCRVNR"

# find git
git = shutil.which("git")
if not git:
    for cand in [r"C:\Program Files\Git\cmd\git.exe", r"C:\Program Files\Git\bin\git.exe",
                 r"C:\Program Files (x86)\Git\cmd\git.exe"]:
        if os.path.exists(cand):
            git = cand
            break
log(f"git: {git}")

def run(*args):
    r = subprocess.run([git, "-C", REPO] + list(args), capture_output=True, text=True, timeout=120)
    log(f"$ git {' '.join(args)}\n  rc={r.returncode}\n  out={r.stdout.strip()[:800]}\n  err={r.stderr.strip()[:800]}")
    return r

try:
    # verify STATUS.md really changed on disk
    with open(os.path.join(REPO, "STATUS.md"), "r", encoding="utf-8") as f:
        head = f.readline().strip() + " | " + f.readline().strip()
    log(f"STATUS.md head: {head}")

    run("add", "-A")
    run("commit", "-m", "feat(voice): By Any Means v5 final + Voice Doctrine codification - rhythm doctrine, patterns #31-33, guillotine principle, 11 correction pairs")
    run("log", "--oneline", "-3")
    run("status", "--porcelain")
except Exception:
    log("EXCEPTION:\n" + traceback.format_exc())
log("=== commit end ===")
