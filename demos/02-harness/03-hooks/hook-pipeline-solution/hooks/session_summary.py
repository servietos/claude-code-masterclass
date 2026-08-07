#!/usr/bin/env python3
import json
import os
import sys
from collections import Counter
from pathlib import Path

# derived from the script's own location, since a hook's working directory is not guaranteed
DEFAULT_LOG = Path(__file__).resolve().parent.parent / "logs" / "audit.jsonl"
LOG = Path(os.environ.get("HOOK_AUDIT_LOG", DEFAULT_LOG))

payload = json.load(sys.stdin)
session = payload.get("session_id", "unknown")

if not LOG.exists():
    print(f"[summary] session {session}: no file writes recorded", file=sys.stderr)
    sys.exit(0)

entries = [json.loads(line) for line in LOG.read_text(encoding="utf-8").splitlines() if line.strip()]
mine = [entry for entry in entries if entry.get("session_id") == session]

if not mine:
    print(f"[summary] session {session}: no file writes recorded", file=sys.stderr)
    sys.exit(0)

tools = Counter(entry["tool"] for entry in mine)
files = sorted({entry["file_path"] for entry in mine})
total_bytes = sum(entry.get("bytes", 0) for entry in mine)

print(f"[summary] session {session}: {len(mine)} writes, {len(files)} files, {total_bytes} bytes", file=sys.stderr)
for tool, count in sorted(tools.items()):
    print(f"[summary]   {tool} x{count}", file=sys.stderr)
for path in files:
    print(f"[summary]   {path}", file=sys.stderr)

# on Stop exit 2 does not block, it stops claude from stopping, so a reporting hook always exits 0
sys.exit(0)
