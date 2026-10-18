#!/usr/bin/env python3
import json
import os
import sys
from collections import Counter
from pathlib import Path

# the script sits in hooks/, so two parents up is the project root
DEFAULT_LOG = Path(__file__).resolve().parent.parent / "logs" / "audit.jsonl"
LOG = Path(os.environ.get("HOOK_AUDIT_LOG", DEFAULT_LOG))

payload = json.load(sys.stdin)
session = payload.get("session_id", "unknown")

rows = []
if LOG.exists():
    # one JSON record per line, blank lines skipped
    with LOG.open(encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle if line.strip()]

rows = [row for row in rows if row.get("session_id") == session]

if not rows:
    print(f"[summary] session {session}: no file writes recorded", file=sys.stderr)
    sys.exit(0)

files = sorted({row["file_path"] for row in rows})
total_bytes = sum(row["bytes"] for row in rows)

lines = [f"[summary] session {session}: {len(rows)} writes, {len(files)} files, {total_bytes} bytes"]
# count per tool name, listed alphabetically
tools = Counter(row["tool"] for row in rows)
lines += [f"  {tool} x{count}" for tool, count in sorted(tools.items())]
lines += [f"  {path}" for path in files]

print("\n".join(lines), file=sys.stderr)
sys.exit(0)
