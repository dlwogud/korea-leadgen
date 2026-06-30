"""Convenience runner: source from Saramin, then score.  `python scripts/run.py`"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

for step in ("source_saramin.py", "score_leads.py"):
    print(f"\n=== {step} ===")
    result = subprocess.run([sys.executable, str(HERE / step)])
    if result.returncode != 0:
        sys.exit(f"step failed: {step}")
