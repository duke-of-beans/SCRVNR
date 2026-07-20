"""
Install git hooks for SCRVNR.

Copies the pre-commit hook that blocks secrets from being committed.
Run once after cloning, or after any hook update.

    D:\\Programs\\Python312\\python.exe D:\\Projects\\SCRVNR\\hooks\\install_hooks.py
"""
import shutil
import stat
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
HOOKS_SRC = PROJECT_ROOT / "hooks"
HOOKS_DST = PROJECT_ROOT / ".git" / "hooks"

def install():
    if not HOOKS_DST.exists():
        print(f"ERROR: .git/hooks not found at {HOOKS_DST}")
        return False

    hook = HOOKS_SRC / "pre-commit"
    if not hook.exists():
        print(f"ERROR: pre-commit hook not found at {hook}")
        return False

    dst = HOOKS_DST / "pre-commit"
    shutil.copy2(str(hook), str(dst))

    # Make executable
    dst.chmod(dst.stat().st_mode | stat.S_IEXEC)

    print(f"Installed: {dst}")
    print("Pre-commit hook will block secrets and forbidden file types.")
    return True

if __name__ == "__main__":
    install()
