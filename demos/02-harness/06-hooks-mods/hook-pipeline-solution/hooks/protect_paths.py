#!/usr/bin/env python3
import fnmatch
import json
import sys
from pathlib import Path

PROTECTED = ["docs/generated/*", "*.lock"]

payload = json.load(sys.stdin)

if payload.get("tool_name") not in ("Write", "Edit"):
    sys.exit(0)

file_path = payload.get("tool_input", {}).get("file_path", "")
# the payload path is absolute and os-native, this pair makes it repo-relative so a pattern can match
target = Path(file_path).as_posix()
cwd = Path(payload.get("cwd", ".")).as_posix()

if cwd != "." and target.startswith(cwd + "/"):
    target = target[len(cwd) + 1:]

for pattern in PROTECTED:
    # fnmatch * spans slashes too, so docs/generated/* also matches anything nested below it
    if fnmatch.fnmatch(target, pattern):
        print(
            f"Blocked: {target} matches the protected pattern '{pattern}'. "
            "Generated output is owned by the build step, so edit the generator input instead.",
            file=sys.stderr,
        )
        # exit 2 is the only code that blocks the call, any other non-zero code just warns
        sys.exit(2)

sys.exit(0)
