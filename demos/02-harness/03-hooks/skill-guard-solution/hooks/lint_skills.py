#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from pathlib import Path

# derived from the script's own location, since a hook's working directory is not guaranteed
PROJECT = Path(__file__).resolve().parent.parent
LINTER = PROJECT / "scripts" / "lint-claude-config.sh"

payload = json.load(sys.stdin)

if payload.get("tool_name") not in ("Write", "Edit"):
    sys.exit(0)

target = Path(payload.get("tool_input", {}).get("file_path", "")).as_posix()

if ".claude/skills/" not in target and ".claude/agents/" not in target:
    sys.exit(0)

root = Path(os.environ.get("HOOK_LINT_ROOT", PROJECT))
# relative and posix, because the bash shipped with git for windows rejects a drive-letter path with exit 127
linter = Path(os.path.relpath(LINTER, root)).as_posix()
result = subprocess.run(
    ["bash", linter, "."],
    cwd=root,
    capture_output=True,
    text=True,
)

if result.returncode == 0:
    print("[lint] skill and agent config clean", file=sys.stderr)
    sys.exit(0)

# stdout is parsed as json control output, so the linter's report has to be re-emitted on stderr
print(result.stdout.strip(), file=sys.stderr)
# exit 2 cannot undo the write, it hands that report to claude so the next turn repairs it
sys.exit(2)
