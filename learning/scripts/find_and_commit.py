"""Find git via node's environment, then commit."""
import subprocess, os, traceback

LOG = r"D:\Projects\SCRVNR\learning\scripts\find_git_log.txt"
def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

log("=== start ===")
REPO = r"D:\Projects\SCRVNR"

# Search common locations including GitHub Desktop
search_paths = [
    r"C:\Program Files\Git\cmd\git.exe",
    r"C:\Program Files\Git\bin\git.exe",
    r"C:\Program Files (x86)\Git\cmd\git.exe",
    r"D:\Programs\Git\cmd\git.exe",
    r"C:\Users\DKdKe\AppData\Local\Programs\Git\cmd\git.exe",
    r"C:\Users\DKdKe\scoop\shims\git.exe",
]

# Also search GitHub Desktop bundled git
gh_desktop_base = r"C:\Users\DKdKe\AppData\Local\GitHubDesktop"
if os.path.isdir(gh_desktop_base):
    log(f"GitHub Desktop dir exists: {gh_desktop_base}")
    for item in os.listdir(gh_desktop_base):
        cand = os.path.join(gh_desktop_base, item, "resources", "app", "git", "cmd", "git.exe")
        search_paths.append(cand)
        cand2 = os.path.join(gh_desktop_base, item, "resources", "app", "git", "mingw64", "bin", "git.exe")
        search_paths.append(cand2)
else:
    log("No GitHub Desktop dir")

# Also check winget / user installs
for d in [r"C:\Users\DKdKe\AppData\Local\Microsoft\WinGet",
          r"C:\Users\DKdKe\AppData\Local"]:
    if os.path.isdir(d):
        for root, dirs, files in os.walk(d):
            if "git.exe" in files:
                fp = os.path.join(root, "git.exe")
                search_paths.append(fp)
                log(f"  found via walk: {fp}")
            # don't recurse too deep
            if root.count(os.sep) - d.count(os.sep) > 4:
                dirs.clear()

# Also try where.exe
try:
    r = subprocess.run(["where.exe", "git"], capture_output=True, text=True, timeout=10)
    if r.returncode == 0 and r.stdout.strip():
        for line in r.stdout.strip().split("\n"):
            search_paths.append(line.strip())
            log(f"  where.exe found: {line.strip()}")
except Exception:
    log("where.exe failed")

# Also check PATH entries
path_dirs = os.environ.get("PATH", "").split(os.pathsep)
for d in path_dirs:
    cand = os.path.join(d, "git.exe")
    if os.path.exists(cand):
        search_paths.append(cand)
        log(f"  PATH found: {cand}")

git = None
for p in search_paths:
    if os.path.exists(p):
        git = p
        log(f"FOUND: {p}")
        break
    else:
        log(f"  miss: {p}")

if not git:
    log("!! git not found anywhere")
    log("=== end ===")
    exit(1)

def run(*args):
    r = subprocess.run([git, "-C", REPO] + list(args), capture_output=True, text=True, timeout=120)
    log(f"$ git {' '.join(args)}\n  rc={r.returncode}\n  out={r.stdout.strip()[:500]}\n  err={r.stderr.strip()[:500]}")
    return r

try:
    run("status", "--porcelain")
    run("add", "-A")
    run("status", "--porcelain")
    run("commit", "-m", "feat(voice): By Any Means v5 final + Voice Doctrine codification - rhythm doctrine, patterns #31-33, guillotine principle, 11 correction pairs")
    run("log", "--oneline", "-3")
except Exception:
    log("EXCEPTION:\n" + traceback.format_exc())
log("=== end ===")
