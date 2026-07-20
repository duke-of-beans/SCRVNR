import sys, subprocess
result = subprocess.run(
    [r'D:\Programs\Python312\python.exe', r'D:\Projects\SCRVNR\tools\quality_gate.py',
     r'D:\Projects\SCRVNR\research\voice_fingerprint\test_crazy_in_tents.md', '--env', 'research'],
    capture_output=True, text=True, cwd=r'D:\Projects\SCRVNR'
)
with open(r'D:\Projects\SCRVNR\research\voice_fingerprint\quality_gate_results.txt', 'w', encoding='utf-8') as f:
    f.write(f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}\n\nRETURN CODE: {result.returncode}")
print(f"Done. Return code: {result.returncode}")
