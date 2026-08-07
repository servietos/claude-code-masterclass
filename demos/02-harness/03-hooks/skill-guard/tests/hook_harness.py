import json
import os
import subprocess
import sys
from pathlib import Path

# derived from this file's own location, so the suite runs from any working directory
PROJECT = Path(__file__).resolve().parent.parent
HOOKS_DIR = PROJECT / "hooks"
LINTER = PROJECT / "scripts" / "lint-claude-config.sh"


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


def run_linter(root):
    target = PROJECT / "fixtures" / root
    # relative and posix, because the bash shipped with git for windows rejects a drive-letter path with exit 127
    linter = Path(os.path.relpath(LINTER, target)).as_posix()
    result = subprocess.run(
        ["bash", linter, "."],
        cwd=target,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr
