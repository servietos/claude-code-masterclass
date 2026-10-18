import json
import os
import re
import sys


def block(reason):
    # exit 2 makes Claude Code refuse the tool call and show stderr to Claude
    print(reason, file=sys.stderr)
    sys.exit(2)


def has_identity_frontmatter(content):
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return False
    # the frontmatter block closes on the next bare --- line
    closing = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if closing is None:
        return False
    # a name or description key at the start of a line makes the file discoverable as a skill
    return any(re.match(r"(name|description)\s*:", line) for line in lines[1:closing])


payload = json.load(sys.stdin)
if payload.get("tool_name") not in ("Write", "Edit"):
    sys.exit(0)

tool_input = payload.get("tool_input", {})
path = tool_input["file_path"].replace("\\", "/")

# strip the cwd prefix so the path is repo-relative
root = os.getcwd().replace("\\", "/").rstrip("/") + "/"
if path.lower().startswith(root.lower()):
    path = path[len(root):]

segments = [s for s in path.split("/") if s]

# the tail is everything after the first .claude/skills pair
start = next(
    (i + 2 for i in range(len(segments) - 1) if segments[i:i + 2] == [".claude", "skills"]),
    None,
)
if start is None:
    sys.exit(0)

tail = segments[start:]
if len(tail) < 2:
    sys.exit(0)

skill = tail[0]
nested = tail[1]
name = tail[-1]

if name.lower() == "skill.md" and len(tail) > 2:
    block(
        f"nested subskill manifest {path}: write .claude/skills/{skill}/references/{nested}.md instead, "
        f"or promote it to a top-level skill folder"
    )

# the exact-case check comes second, so only a two-segment lowercase manifest reaches it
if name == "skill.md" and len(tail) == 2:
    block(f"{path}: a lowercase skill.md is invisible on case-sensitive filesystems, name the manifest SKILL.md")

if nested == "references" and name.endswith(".md") and has_identity_frontmatter(tool_input.get("content", "")):
    block(
        f"{path}: a reference must stay a plain document, because frontmatter with a name or description "
        f"makes it get discovered as its own skill"
    )

sys.exit(0)
