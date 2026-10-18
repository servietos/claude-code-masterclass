#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# the script sits in hooks/, so two parents up is the project root
DEFAULT_LOG = Path(__file__).resolve().parent.parent / "logs" / "audit.jsonl"
LOG = Path(os.environ.get("HOOK_AUDIT_LOG", DEFAULT_LOG))

payload = json.load(sys.stdin)

record = {
    # UTC with seconds precision, e.g. 2026-10-17T19:05:00+00:00
    "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "session_id": payload.get("session_id", "unknown"),
    "tool": payload.get("tool_name"),
    "file_path": payload.get("tool_input", {}).get("file_path", ""),
    # length of the tool's returned content string
    "bytes": len(payload.get("tool_response", {}).get("content", "")),
}

LOG.parent.mkdir(parents=True, exist_ok=True)
with LOG.open("a", encoding="utf-8") as handle:
    handle.write(json.dumps(record) + "\n")

print(f"[audit] logged {record['tool']} {record['file_path']} to {LOG}", file=sys.stderr)
sys.exit(0)
