# Build a Three-Event Hook Pipeline

You write and test `PreToolUse`, `PostToolUse`, and `Stop` hooks in Python and wire them into `.claude/settings.json`. You finish with a three-event pipeline that blocks protected paths, appends an audit record per write, and prints a session summary.

---

Work in `demos/02-harness/04-hooks-mods/hook-pipeline/` (Python 3.9 or newer, standard library only); the completed reference is in [hook-pipeline-solution/](hook-pipeline-solution/readme.md).

## Step 1: Block a Tool Call with Exit Code 2

**Overview:** Every hook reads one JSON object from stdin with `session_id`, `transcript_path`, `cwd` and `hook_event_name` on every event, and on exit 0 its stdout is parsed as JSON control output, which is why diagnostics belong on stderr. Exit code 2 is the only exit code that stops a tool call, and the stderr text is what Claude reads as the reason.

```text
Create hooks/protect_paths.py in demos/02-harness/04-hooks-mods/hook-pipeline/.
Behaviour:
- If tool_name is not Write or Edit, exit 0 immediately.
- Take tool_input.file_path, normalise it with pathlib to POSIX form, and strip the leading cwd prefix so the path is repo-relative.
- Match the result against the patterns ["docs/generated/*", "*.lock"] using fnmatch.
- On a match, print to stderr exactly: Blocked: <relative path> matches the protected pattern '<pattern>'. Generated output is owned by the build step, so edit the generator input instead. Then exit 2.
- Otherwise exit 0 with no output.
```

**Expected Outcome:** Piping a protected path in produces this exact pair, while `/repo/src/app.py` produces no output and `exit=0`:

```text
Blocked: docs/generated/api.md matches the protected pattern 'docs/generated/*'. Generated output is owned by the build step, so edit the generator input instead.
exit=2
```

Wire it in `.claude/settings.json` as a second `PreToolUse` group with matcher `Write|Edit` running `python "$CLAUDE_PROJECT_DIR/hooks/protect_paths.py"`, beside a `PostToolUse` group for `audit_write.py` and a `Stop` group with no `matcher` key for `session_summary.py`; the finished wiring is [hook-pipeline-solution/.claude/settings.json](hook-pipeline-solution/.claude/settings.json).

## Step 2: Summarise the Session on Stop

**Overview:** `PostToolUse` runs after the tool has already executed, so its value is the guaranteed side effect: one JSONL line per file write, sized from `tool_response`, the field a `PreToolUse` payload lacks. `Stop` fires when Claude finishes a turn, and there exit 2 prevents Claude from stopping, so a reporting hook that exits 2 traps the session in a loop.

```text
Create hooks/audit_write.py in demos/02-harness/04-hooks-mods/hook-pipeline/.
Behaviour:
- Resolve the log path from the HOOK_AUDIT_LOG environment variable, defaulting to <project>/logs/audit.jsonl resolved relative to the script file.
- Build a record with these keys exactly: ts (UTC ISO 8601, seconds precision), session_id, tool, file_path, bytes (the length of tool_response.content).
- Create the parent directory if needed, append the record as one JSON line, print a one-line confirmation to stderr, and exit 0.
```

```text
Create hooks/session_summary.py in demos/02-harness/04-hooks-mods/hook-pipeline/.
Behaviour:
- Resolve the log path from HOOK_AUDIT_LOG, defaulting to <project>/logs/audit.jsonl relative to the script file.
- Read the Stop payload from stdin and take session_id.
- If the log is missing, or holds no rows for this session, print "[summary] session <id>: no file writes recorded" to stderr and exit 0.
- Otherwise filter the rows to this session and print to stderr:
  - a header line: "[summary] session <id>: <n> writes, <n> files, <n> bytes" where files is the count of distinct file_path values and bytes is the sum of the bytes field
  - one indented line per tool in the form "  <Tool> x<count>", sorted by tool name
  - one indented line per distinct file_path, sorted
- Always exit 0.
```

**Expected Outcome:** Piping a PostToolUse payload for each of two writes into `hooks/audit_write.py` (a Write with `tool_response.content` of `print(1)` and an Edit with `x = 1`, both session `s-1`) leaves two audit rows on disk. Then a Stop payload for session `s-1` prints `[summary] session s-1: 2 writes, 2 files, 13 bytes`, one line per tool and per file, and `exit=0`.

## Step 3: Prove the Pipeline with Exit-Code Tests

**Overview:** The shipped harness pipes real JSON into a script and returns exit code, stdout, and stderr, so the remaining work is asserting the contract each hook promises. The summary fixture needs a row belonging to a different session, or the filter is untested.

```text
Add three test modules to demos/02-harness/04-hooks-mods/hook-pipeline/tests/, following the style of test_inspect_payload.py and importing run_hook from hook_harness.
tests/test_protect_paths.py:
- a docs/generated/ path blocks with exit 2 and stderr naming both the path and the pattern
- the blocked case writes nothing to stdout
tests/test_audit_write.py (use tempfile.TemporaryDirectory plus the HOOK_AUDIT_LOG env var for isolation):
- two calls append exactly two lines, with the second line's bytes field correct
tests/test_session_summary.py (seed a temp log with two rows for session abc123 and one row for session "other"):
- the summary counts only abc123, reports "2 writes, 1 files, 8 bytes", lists "Write x1" and "Edit x1", and never mentions the other session's file
Constraints: standard library unittest only, no inline comments. Then run: python -m unittest discover -s tests -v
```

**Expected Outcome:** The new modules join the three shipped tests and the run ends in `OK`; without the `other` row, a hook that ignores `session_id` would pass every assertion.
