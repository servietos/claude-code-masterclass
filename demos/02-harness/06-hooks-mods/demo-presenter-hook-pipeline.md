---
presents: demo-hook-pipeline.md
budget: 6 min
beats: 6
---

# Present: Build a Three-Event Hook Pipeline

Three hooks on three events, each shown with the test that pins its exit code. A room walks away knowing which exit code does what on which event, and why a hook that reports must never exit 2.

------

## Beats

### Beat 1: the wiring is four levels deep, and `Stop` has no matcher (1 min)

**Open:** [`hook-pipeline/.claude/settings.json`](hook-pipeline/.claude/settings.json) · the single `PreToolUse` group the starter ships
**Say:** A hook is a plain program, so the only thing between it and running is the shape of its settings entry. A wrong shape is not rejected: the file parses, the session starts, the hook never fires.

```json
    "PreToolUse": [
      {
        "matcher": "Write|Edit|Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python \"$CLAUDE_PROJECT_DIR/hooks/inspect_payload.py\""
          }
        ]
      }
    ]
```

**Result:** [`hook-pipeline-solution/.claude/settings.json`](hook-pipeline-solution/.claude/settings.json), one group grown to four across three events, and the `Stop` group carries no matcher at all

```json
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python \"$CLAUDE_PROJECT_DIR/hooks/session_summary.py\""
          }
        ]
      }
    ]
```

**Gotcha:** a flat array with a top-level `event` key is the obsolete shape and silently never fires, and `$CLAUDE_PROJECT_DIR` is there because a hook's working directory is not guaranteed to be the project root.

### Beat 2: exit 2 is the only code that blocks, and stderr is the whole message (1 min)

**Open:** [`protect_paths.py`](hook-pipeline-solution/hooks/protect_paths.py) · the match loop and both `sys.exit` calls · [`tests/test_protect_paths.py`](hook-pipeline-solution/tests/test_protect_paths.py)
**Say:** A hook's entire interface with the harness is an exit code plus whatever it wrote to stderr. That puts the whole burden of explanation on one string, read by someone who has to act on it next turn.

```python
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
```

**Result:** no file, only a refusal: piping a protected path in produces this exact pair

```text
Blocked: docs/generated/api.md matches the protected pattern 'docs/generated/*'. Generated output is owned by the build step, so edit the generator input instead.
exit=2
```

**Gotcha:** exit 2 stops the tool call and feeds stderr back to Claude; any other non-zero code is a non-blocking error that logs a warning and lets the tool run.

### Beat 3: a hook defends its own preconditions, and the payload path is absolute (1 min)

**Open:** [`protect_paths.py`](hook-pipeline-solution/hooks/protect_paths.py) · the `tool_name` guard and the `cwd` strip · [`hook-pipeline-solution/.claude/settings.json`](hook-pipeline-solution/.claude/settings.json)
**Say:** A matcher belongs to the wiring, not the script, so a hook that trusts it is correct only until someone edits settings. The payload hands over an absolute path while conventions are written relative to the project root.

```python
if payload.get("tool_name") not in ("Write", "Edit"):
    sys.exit(0)

file_path = payload.get("tool_input", {}).get("file_path", "")
# the payload path is absolute and os-native, this pair makes it repo-relative so a pattern can match
target = Path(file_path).as_posix()
cwd = Path(payload.get("cwd", ".")).as_posix()

if cwd != "." and target.startswith(cwd + "/"):
    target = target[len(cwd) + 1:]
```

**Result:** no file again, and the absence is the point: `/repo/src/app.py` through the same hook produces no output and `exit=0`

**Gotcha:** the room will call the `tool_name` check redundant since the matcher already limits this to `Write|Edit`; point at the test harness, which invokes the script directly with a `Bash` payload.

### Beat 4: `PostToolUse` cannot prevent anything, so its value is the guaranteed record (1 min)

**Open:** [`audit_write.py`](hook-pipeline-solution/hooks/audit_write.py) · the `LOG` override and the `entry` record · [`tests/test_audit_write.py`](hook-pipeline-solution/tests/test_audit_write.py)
**Say:** An event that fires after the tool already ran can never gate anything, so what it buys is a record nobody has to remember to write. Each run is a separate short-lived process with no memory of the last.

```python
LOG = Path(os.environ.get("HOOK_AUDIT_LOG", DEFAULT_LOG))
...
entry = {
    "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "session_id": payload.get("session_id", "unknown"),
    "tool": payload.get("tool_name"),
    "file_path": payload.get("tool_input", {}).get("file_path", ""),
    "bytes": len(payload.get("tool_response", {}).get("content", "")),
}
```

**Result:** two payloads, two lines appended to `hook-pipeline-solution/logs/audit.jsonl` (written at run time, gitignored, so no link reaches it)

```text
{"ts": "2026-07-23T05:23:26+00:00", "session_id": "s-1", "tool": "Write", "file_path": "/repo/src/app.py", "bytes": 8}
{"ts": "2026-07-23T05:23:26+00:00", "session_id": "s-1", "tool": "Edit", "file_path": "/repo/src/util.py", "bytes": 5}
```

**Gotcha:** `tool_response` is the one field `PostToolUse` carries that `PreToolUse` does not, and `bytes` is its length, not its content.

### Beat 5: on `Stop`, exit 2 prevents stopping, so a reporting hook always exits 0 (1 min)

**Open:** [`session_summary.py`](hook-pipeline-solution/hooks/session_summary.py) · the two empty-state branches and the session filter · [`audit_write.py`](hook-pipeline-solution/hooks/audit_write.py)
**Say:** Exit codes are not global constants: the code that refuses a tool call means keep going on the event that fires when Claude finishes a turn. A hook that only observes must succeed unconditionally.

```python
if not LOG.exists():
    print(f"[summary] session {session}: no file writes recorded", file=sys.stderr)
    sys.exit(0)

entries = [json.loads(line) for line in LOG.read_text(encoding="utf-8").splitlines() if line.strip()]
mine = [entry for entry in entries if entry.get("session_id") == session]

if not mine:
    print(f"[summary] session {session}: no file writes recorded", file=sys.stderr)
    sys.exit(0)
```

**Result:** no file, only stderr: with the two audit rows on disk, a `Stop` payload for session `s-1` prints exactly this

```text
[summary] session s-1: 2 writes, 2 files, 13 bytes
[summary]   Edit x1
[summary]   Write x1
[summary]   /repo/src/app.py
[summary]   /repo/src/util.py
exit=0
```

**Gotcha:** exit 2 on `Stop` does not block, it prevents Claude from stopping, so a summary hook that exits 2 traps the session in a loop.

### Beat 6: the fixture row that proves the filter is the third one (1 min)

**Open:** [`tests/test_session_summary.py`](hook-pipeline-solution/tests/test_session_summary.py) · the `ROWS` fixture · [`hook-pipeline/tests`](hook-pipeline/tests) · the starter's harness and one test
**Say:** A test for a filter proves nothing unless the fixture contains something the filter has to reject. Counts assert something only when a wrong implementation would produce different ones.

```python
ROWS = [
    {"ts": "2026-01-01T00:00:00+00:00", "session_id": "abc123", "tool": "Write", "file_path": "/repo/src/a.py", "bytes": 3},
    {"ts": "2026-01-01T00:00:01+00:00", "session_id": "abc123", "tool": "Edit", "file_path": "/repo/src/a.py", "bytes": 5},
    {"ts": "2026-01-01T00:00:02+00:00", "session_id": "other", "tool": "Write", "file_path": "/repo/src/z.py", "bytes": 9},
]
...
        self.assertIn("2 writes, 1 files, 8 bytes", stderr)
...
        self.assertNotIn("/repo/src/z.py", stderr)
```

**Result:** three test modules the starter has no counterpart for, in [`hook-pipeline-solution/tests`](hook-pipeline-solution/tests), and the whole suite green

```text
----------------------------------------------------------------------
Ran 15 tests in 0.558s

OK
```

**Gotcha:** without the `other` row the filter is untested, and a hook that ignores `session_id` entirely passes every assertion.

## If the room asks

| Question | Answer |
|---|---|
| Why stderr and not stdout for the reason? | On exit 2 stdout is discarded, and on exit 0 stdout is parsed as JSON control output; diagnostics survive only on stderr. |
| Does a `matcher` on a `Stop` group work? | No, and it is not an error either: non-tool events ignore the field silently and the hook always fires. |
| Do two matching `PreToolUse` groups both run? | Yes, both run; they are independent checks over the same call. |
