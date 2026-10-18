import json
import os
import subprocess
import sys

payload = json.load(sys.stdin)
if payload.get("tool_name") not in ("Write", "Edit"):
    sys.exit(0)

path = payload["tool_input"]["file_path"].replace("\\", "/")
if ".claude/skills/" not in path and ".claude/agents/" not in path:
    sys.exit(0)

project = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
root = os.environ.get("HOOK_LINT_ROOT", project)
linter = os.path.join(project, "scripts", "lint-claude-config.sh")

# bash on Windows rejects drive-letter paths, so the script is addressed relative to the lint root
linter_rel = os.path.relpath(linter, root).replace("\\", "/")
result = subprocess.run(
    ["bash", linter_rel, "."],
    cwd=root,
    capture_output=True,
    text=True,
)

if result.returncode == 0:
    print("[lint] skill and agent config clean", file=sys.stderr)
    sys.exit(0)

# exit 2 makes Claude Code refuse the write and show stderr to Claude
print(result.stdout, file=sys.stderr)
sys.exit(2)
