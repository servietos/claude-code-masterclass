#!/usr/bin/env python3
import json
import sys
from pathlib import Path

payload = json.load(sys.stdin)

if payload.get("tool_name") not in ("Write", "Edit"):
    sys.exit(0)

tool_input = payload.get("tool_input", {})
# the payload path is absolute and os-native, this pair makes it repo-relative so the segments line up
target = Path(tool_input.get("file_path", "")).as_posix()
cwd = Path(payload.get("cwd", ".")).as_posix()

if cwd != "." and target.startswith(cwd + "/"):
    target = target[len(cwd) + 1:]

parts = target.split("/")

if ".claude" not in parts:
    sys.exit(0)

root = parts.index(".claude")

# a slice rather than an index, so a path that simply ends at .claude cannot raise
if parts[root + 1:root + 2] != ["skills"]:
    sys.exit(0)

tail = parts[root + 2:]

if len(tail) < 2:
    sys.exit(0)

skill = tail[0]
leaf = tail[-1]

if leaf.lower() == "skill.md" and len(tail) > 2:
    nested = "/".join(tail[1:-1])
    print(
        f"Blocked: {target} is a nested subskill manifest. A master skill holds exactly one "
        f"SKILL.md at its root, so write .claude/skills/{skill}/references/{nested}.md as a plain "
        "reference instead, or promote the capability to its own top-level skill folder.",
        file=sys.stderr,
    )
    # exit 2 is the only code that blocks the write, any other non-zero code just warns
    sys.exit(2)

# an exact compare, unlike the .lower() above, so only the lowercase spelling reaches this branch
if leaf == "skill.md" and len(tail) == 2:
    print(
        f"Blocked: {target} must be named SKILL.md. A lowercase manifest is invisible to skill "
        "discovery on case-sensitive filesystems, so the skill works locally and vanishes in CI.",
        file=sys.stderr,
    )
    sys.exit(2)

if tail[1:2] == ["references"] and leaf.endswith(".md"):
    content = tool_input.get("content", "")
    lines = content.splitlines()
    if lines[:1] == ["---"]:
        block = lines[1:]
        end = block.index("---") if "---" in block else len(block)
        keys = [line.split(":", 1)[0].strip().lower() for line in block[:end] if ":" in line]
        found = [key for key in ("name", "description") if key in keys]
        if found:
            print(
                f"Blocked: {target} carries {' and '.join(found)} frontmatter. A reference is a "
                "plain document the master routes to; frontmatter makes it get discovered as its "
                "own skill, which shadows the master.",
                file=sys.stderr,
            )
            sys.exit(2)

sys.exit(0)
