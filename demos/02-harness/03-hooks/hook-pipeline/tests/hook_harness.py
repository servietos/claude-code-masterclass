import json
import os
import subprocess
import sys
from pathlib import Path

# derived from this file's own location, so the suite runs from any working directory
HOOKS_DIR = Path(__file__).resolve().parent.parent / "hooks"


def run_hook(script, payload, env=None):
    # subprocess env= replaces the whole environment rather than extending it, so start from a copy
    merged = dict(os.environ)
    merged.update(env or {})
    result = subprocess.run(
        [sys.executable, str(HOOKS_DIR / script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=merged,
    )
    return result.returncode, result.stdout, result.stderr
