#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# derived from the script's own location, since a hook's working directory is not guaranteed
DEFAULT_LOG = Path(__file__).resolve().parent.parent / "logs" / "audit.jsonl"
LOG = Path(os.environ.get("HOOK_AUDIT_LOG", DEFAULT_LOG))

payload = json.load(sys.stdin)

if payload.get("tool_name") not in ("Write", "Edit"):
    sys.exit(0)

entry = {
    "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "session_id": payload.get("session_id", "unknown"),
    "tool": payload.get("tool_name"),
    "file_path": payload.get("tool_input", {}).get("file_path", ""),
    "bytes": len(payload.get("tool_response", {}).get("content", "")),
}

LOG.parent.mkdir(parents=True, exist_ok=True)
with LOG.open("a", encoding="utf-8") as handle:
    handle.write(json.dumps(entry) + "\n")

print(f"[audit] recorded {entry['tool']} {entry['file_path']}", file=sys.stderr)
sys.exit(0)
