# Hook Guardrails, Completed Reference

This is the finished counterpart to [`../demo-hook-guardrails/`](../demo-hook-guardrails/readme.md). Work through the starter; come here to compare against a run that actually happened. Everything in this folder was produced by executing the hook.

## What Is Different From the Starter

| Path | Why it is here |
|---|---|
| `hooks/blocked.log` | A real audit trail, written by the two hook scripts during the verification run below |
| `build/old.txt` | The Run 1 fixture, pre-created so the demo has a plausible target |
| `verification.md` | Every pattern test with its literal command, exit code, and output, plus the live Claude Code runs |
| `.gitignore` | Same list as the starter, minus the `hooks/blocked.log` entry, because here that file is the deliverable |

The hook scripts, `.claude/settings.json`, and `.claude/agents/research-agent.md` are byte-identical to the starter. The guardrail is the artifact, so there is nothing to complete in it. The presenter guide is not duplicated here; it stays at [`../demo-presenter-hook-guardrails.md`](../demo-presenter-hook-guardrails.md) so the two copies cannot drift.

## The Audit Trail This Folder Ships

```text
2026-10-17T19:22:56+02:00 BLOCKED (recursive forced rm): rm -rf /
2026-10-17T19:22:56+02:00 BLOCKED (recursive forced rm): rm -fr /
2026-10-17T19:22:56+02:00 BLOCKED (recursive forced rm): rm -rf .
2026-10-17T19:22:57+02:00 BLOCKED (recursive forced rm): rm -rf build/
2026-10-17T19:22:57+02:00 BLOCKED (recursive forced rm): rm  -rf  /
2026-10-17T19:22:57+02:00 BLOCKED (git push --force): git push --force origin main
2026-10-17T19:22:58+02:00 BLOCKED (git push --force): git push origin main --force
2026-10-17T19:22:58+02:00 BLOCKED (git push -f): git push -f origin main
```

The file holds one line per blocked attempt from both scripts; the full file is the trail for the whole verification run. `hooks/deny-destructive.sh` and `hooks/deny-destructive.ps1` emit the same line format, so the log reads as one trail regardless of platform.

## Reproduce It

Delete `hooks/blocked.log`, then feed the hook a `PreToolUse` payload directly. No Claude Code session is needed to test a hook:

```bash
jq -nc '{tool_name:"Bash",tool_input:{command:"rm -rf /"}}' | bash hooks/deny-destructive.sh
```

```powershell
'{"tool_name":"Bash","tool_input":{"command":"rm -rf /"}}' | pwsh -NoProfile -File hooks/deny-destructive.ps1
```

Both print the deny JSON, exit `0`, and append one line to `hooks/blocked.log`. The full matrix, including the benign commands that must pass, is in [`verification.md`](verification.md).

`hooks/blocked.log` and `build/old.txt` are committed evidence, which is why this folder's `.gitignore` does not list them. Reproducing changes both, so restore them afterwards and `git status` goes clean again:

```bash
git checkout -- hooks/blocked.log build/old.txt
```

## Model-Dependent Parts

The hook decision is deterministic; the model's reaction to it is not. In the forced `rm -rf build/` run the model reported the block, named the reason, and did not retry through another command. On the free-disk prompt the same model deleted `build/old.txt` with `find build -mindepth 1 -delete`, a command no pattern matches, so the hook never fired. The pattern list covers the phrasings it names, and a different model or a later version may adapt differently. Treat the transcript excerpts in `verification.md` as observed outcomes that a later run can change.
