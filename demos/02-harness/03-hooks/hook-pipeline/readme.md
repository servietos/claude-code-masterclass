# Hook Pipeline Starter

A stdlib-only Python project for learning the Claude Code hook contract end to end: the `.claude/settings.json` wiring shape, the stdin JSON payload, the exit-code semantics, and a three-event pipeline built from `PreToolUse`, `PostToolUse`, and `Stop`.

Nothing needs installing. Python 3.9 or newer is the only requirement.

## What ships here

| Path | Purpose |
|------|---------|
| `hooks/inspect_payload.py` | Finished reference hook: reads the payload from stdin, reports the contract fields on stderr, exits 0 |
| `.claude/settings.json` | Wires the reference hook to `PreToolUse` |
| `tests/hook_harness.py` | Pipes a real JSON payload into a hook script and returns exit code, stdout, stderr |
| `tests/test_inspect_payload.py` | Asserts the reference hook's exit code and stderr contract |

## What you build

Three more hooks plus their tests:

1. `hooks/protect_paths.py`, a `PreToolUse` hook that blocks `Write` and `Edit` to generated paths with exit 2 and a reason on stderr.
2. `hooks/audit_write.py`, a `PostToolUse` hook that appends one JSONL line per file write.
3. `hooks/session_summary.py`, a `Stop` hook that reads the JSONL and prints a per-session summary.

## Run the tests

```bash
python -m unittest discover -s tests -v
```

## Pipe a payload by hand

Bash:

```bash
echo '{"session_id":"s-1","cwd":"/repo","hook_event_name":"PreToolUse","tool_name":"Write","tool_input":{"file_path":"/repo/src/app.py","content":"print(1)"}}' | python hooks/inspect_payload.py; echo "exit=$?"
```

PowerShell:

```powershell
'{"session_id":"s-1","cwd":"/repo","hook_event_name":"PreToolUse","tool_name":"Write","tool_input":{"file_path":"/repo/src/app.py","content":"print(1)"}}' | python hooks/inspect_payload.py; "exit=$LASTEXITCODE"
```

The guide for this project is [../demo-hook-pipeline.md](../demo-hook-pipeline.md).
