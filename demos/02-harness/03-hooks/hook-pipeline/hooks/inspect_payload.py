#!/usr/bin/env python3
import json
import sys

# claude sends the whole hook payload as one json object on stdin
payload = json.load(sys.stdin)

event = payload.get("hook_event_name", "unknown")
tool = payload.get("tool_name", "-")
session = payload.get("session_id", "-")
input_keys = ",".join(sorted(payload.get("tool_input", {}))) or "-"

# stderr, because on exit 0 claude parses a hook's stdout as json control output
print(f"[inspect] event={event} session={session} tool={tool} tool_input_keys={input_keys}", file=sys.stderr)
sys.exit(0)
