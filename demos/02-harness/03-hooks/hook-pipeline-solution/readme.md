# Hook Pipeline Solution

The completed reference for [../hook-pipeline/](../hook-pipeline/readme.md): four hooks, their wiring, and 15 passing tests.

## Hooks

| Script | Event | Exit codes it produces |
|--------|-------|------------------------|
| `hooks/inspect_payload.py` | `PreToolUse` | 0 always, prints the contract fields to stderr |
| `hooks/protect_paths.py` | `PreToolUse` | 2 for `docs/generated/*` and `*.lock`, 0 otherwise |
| `hooks/audit_write.py` | `PostToolUse` | 0 always, appends one JSONL line per write |
| `hooks/session_summary.py` | `Stop` | 0 always, prints a per-session rollup to stderr |

Both log-reading hooks honour `HOOK_AUDIT_LOG` so the tests can point them at a temporary file instead of `logs/audit.jsonl`.

## Verified run

```bash
python -m unittest discover -s tests
```

```text
...............
----------------------------------------------------------------------
Ran 15 tests in 0.558s

OK
```

```bash
echo '{"session_id":"s-1","cwd":"/repo","hook_event_name":"PreToolUse","tool_name":"Write","tool_input":{"file_path":"/repo/docs/generated/api.md"}}' | python hooks/protect_paths.py; echo "exit=$?"
```

```powershell
'{"session_id":"s-1","cwd":"/repo","hook_event_name":"PreToolUse","tool_name":"Write","tool_input":{"file_path":"/repo/docs/generated/api.md"}}' | python hooks/protect_paths.py; "exit=$LASTEXITCODE"
```

```text
Blocked: docs/generated/api.md matches the protected pattern 'docs/generated/*'. Generated output is owned by the build step, so edit the generator input instead.
exit=2
```

`logs/audit.jsonl` is generated at runtime and is covered by `.gitignore`.
