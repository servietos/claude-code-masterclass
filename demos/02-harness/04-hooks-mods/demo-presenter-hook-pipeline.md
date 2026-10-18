---
presents: demo-hook-pipeline.md
budget: 4 min
beats: 4
---

# Present: Build a Three-Event Hook Pipeline

Three hooks on three events, each shown with the test that pins its exit code. A room walks away knowing which exit code does what on which event, and why a hook that reports must never exit 2.

------

## Beats

### Beat 1: exit 2 is the only code that blocks, and stderr is the whole message (1 min)

**Open:** [`protect_paths.py`](hook-pipeline-solution/hooks/protect_paths.py) · the match loop and both `sys.exit` calls · [`tests/test_protect_paths.py`](hook-pipeline-solution/tests/test_protect_paths.py)
**Say:** A hook's entire interface with the harness is an exit code plus whatever it wrote to stderr. That puts the whole burden of explanation on one string, read by someone who has to act on it next turn.

```python
for pattern in PROTECTED:
    # fnmatch * also crosses slashes, so docs/generated/* also matches anything nested below it
    if fnmatch.fnmatch(target, pattern):
        print(
            f"Blocked: {target} matches the protected pattern '{pattern}'. "
            "Generated output is owned by the build step, so edit the generator input instead.",
            file=sys.stderr,
        )
        # exit 2 is the only code that blocks the call, any other non-zero code just warns
        sys.exit(2)

sys.exit(0)
```

**Result:** no file, only a refusal: piping a protected path in produces this exact pair

```text
Blocked: docs/generated/api.md matches the protected pattern 'docs/generated/*'. Generated output is owned by the build step, so edit the generator input instead.
exit=2
```

**Gotcha:** exit 2 stops the tool call and feeds stderr back to Claude; any other non-zero code is a non-blocking error that logs a warning and lets the tool run.

### Beat 2: `PostToolUse` cannot prevent anything, so its value is the guaranteed record (1 min)

**Open:** [`audit_write.py`](hook-pipeline-solution/hooks/audit_write.py) · the `LOG` override and the `record` dict · [`tests/test_audit_write.py`](hook-pipeline-solution/tests/test_audit_write.py)
**Say:** An event that fires after the tool already ran can never gate anything, so what it buys is a record nobody has to remember to write. Each run is a separate short-lived process with no memory of the last.

```python
LOG = Path(os.environ.get("HOOK_AUDIT_LOG", DEFAULT_LOG))
...
record = {
    "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "session_id": payload.get("session_id", "unknown"),
    "tool": payload.get("tool_name"),
    "file_path": payload.get("tool_input", {}).get("file_path", ""),
    "bytes": len(payload.get("tool_response", {}).get("content", "")),
}
```

**Result:** two payloads, two lines appended to `hook-pipeline-solution/logs/audit.jsonl` (written at run time, gitignored, so no link reaches it)

```text
{"ts": "2026-10-17T17:08:23+00:00", "session_id": "s-1", "tool": "Write", "file_path": "/repo/src/app.py", "bytes": 8}
{"ts": "2026-10-17T17:08:23+00:00", "session_id": "s-1", "tool": "Edit", "file_path": "/repo/src/util.py", "bytes": 5}
```

**Gotcha:** `tool_response` is the one field `PostToolUse` carries that `PreToolUse` does not, and `bytes` is the length of that `content` string.

### Beat 3: on `Stop`, exit 2 prevents stopping, so a reporting hook always exits 0 (1 min)

**Open:** [`session_summary.py`](hook-pipeline-solution/hooks/session_summary.py) · the empty-state check and the session filter · [`audit_write.py`](hook-pipeline-solution/hooks/audit_write.py)
**Say:** Exit codes are not global constants: the code that refuses a tool call means keep going on the event that fires when Claude finishes a turn. A hook that only observes must succeed unconditionally.

```python
rows = []
if LOG.exists():
    # one JSON record per line, blank lines skipped
    with LOG.open(encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle if line.strip()]

rows = [row for row in rows if row.get("session_id") == session]

if not rows:
    print(f"[summary] session {session}: no file writes recorded", file=sys.stderr)
    sys.exit(0)
```

**Result:** no file, only stderr: with the two audit rows on disk, a `Stop` payload for session `s-1` prints exactly this

```text
[summary] session s-1: 2 writes, 2 files, 13 bytes
  Edit x1
  Write x1
  /repo/src/app.py
  /repo/src/util.py
exit=0
```

**Gotcha:** exit 2 on `Stop` does not block, it prevents Claude from stopping, so a summary hook that exits 2 traps the session in a loop.

### Beat 4: the fixture row that proves the filter is the third one (1 min)

**Open:** [`tests/test_session_summary.py`](hook-pipeline-solution/tests/test_session_summary.py) · the `ROWS` fixture · [`hook-pipeline/tests`](hook-pipeline/tests) · the starter's harness and one test
**Say:** A test for a filter proves nothing unless the fixture contains something the filter has to reject. Counts assert something only when a wrong implementation would produce different ones.

```python
ROWS = [
    {"ts": "2026-10-17T10:00:00+00:00", "session_id": "abc123", "tool": "Write", "file_path": "src/a.py", "bytes": 3},
    {"ts": "2026-10-17T10:01:00+00:00", "session_id": "abc123", "tool": "Edit", "file_path": "src/a.py", "bytes": 5},
    {"ts": "2026-10-17T10:02:00+00:00", "session_id": "other", "tool": "Write", "file_path": "other.md", "bytes": 99},
]
...
        self.assertIn("[summary] session abc123: 2 writes, 1 files, 8 bytes", self.run_summary())
...
        self.assertNotIn("other.md", stderr)
```

**Result:** three test modules the starter has no counterpart for, in [`hook-pipeline-solution/tests`](hook-pipeline-solution/tests), and the whole suite green

```text
----------------------------------------------------------------------
Ran 10 tests in 0.455s

OK
```

**Gotcha:** without the `other` row the filter is untested, and a hook that ignores `session_id` entirely passes every assertion.

## If the room asks

| Question | Answer |
|---|---|
| Why stderr and not stdout for the reason? | On exit 2 stdout is discarded, and on exit 0 stdout is parsed as JSON control output; diagnostics survive only on stderr. |
| Does a `matcher` on a `Stop` group work? | No, and it is not an error either: non-tool events ignore the field silently and the hook always fires. |
| Do two matching `PreToolUse` groups both run? | Yes, both run; they are independent checks over the same call. |
