# Enforce Least Privilege with Hook Guardrails

A 20-minute live demo showing the two-layer defense from topic 02 in action. Layer one is a `PreToolUse` hook that rejects destructive Bash commands at the harness, ahead of the model's reasoning. Layer two is a sub-agent whose toolset does not even include the dangerous tools, so the dangerous request never reaches a place where the hook would have to fire.

## What It Does

1. Wires a `PreToolUse` hook that intercepts every `Bash` and every `PowerShell` call and rejects six dangerous patterns: recursive forced `rm` (`rm -rf` and `rm -fr`), recursive forced `Remove-Item`, `git push --force`, `git push -f`, `git reset --hard`, and a classic fork bomb
2. Logs every blocked attempt to `hooks/blocked.log` so the audience can review the trail at the end
3. Ships a `research-agent` sub-agent scoped to `tools: Read, Grep, Glob`, used to show that the safest tool is the one the agent never had

## Files in This Demo

| Path | Role |
|---|---|
| `.claude/settings.json` | Wires both hook matchers and pre-approves the tools the demo uses |
| `hooks/deny-destructive.sh` | The handler for the `Bash` matcher |
| `hooks/deny-destructive.ps1` | The handler for the `PowerShell` matcher, same six patterns |
| `.claude/agents/research-agent.md` | Read-only sub-agent for the least-privilege half of the demo |
| `build/old.txt` | The disposable fixture Run 1 tries to delete, checked in so Setup is one `cd` |
| `hooks/blocked.log` | Created on first block; the audit trail the demo reviews at the end |
| `../demo-presenter-hook-guardrails.md` | Presenter choreography: timed beats, narration, pre-answered questions |
| `.gitignore` | Keeps the run artifact `hooks/blocked.log` out of the repo |

## Prerequisites

- Claude Code installed and authenticated
- `bash` and `jq` on the path. On Windows both arrive with Git for Windows plus `winget install jqlang.jq`; on macOS use `brew install jq`, on Debian or Ubuntu `apt-get install jq`
- PowerShell 7 (`pwsh`) on Windows, because Claude Code exposes a separate `PowerShell` tool there and the demo guards that tool too

The bash hook fails closed: without `jq` it denies every Bash call and says so in the rejection reason. That is deliberate, and it is the behaviour you want from a guardrail whose own dependency is missing.

## Setup

The fixture Run 1 targets, `build/old.txt`, ships checked in, so there is nothing to create. The starter and its solution carry the same agent name, so do not open both in one session. From this folder, confirm the pieces are in place:

```bash
ls .claude/agents
ls hooks
ls build
```

```powershell
Get-ChildItem .claude\agents
Get-ChildItem hooks
Get-ChildItem build
```

Open Claude Code in this folder. On the first launch, accept the workspace trust dialog: allow rules in a project `.claude/settings.json` are read but not applied until you do, and a headless run in an untrusted folder prints `Ignoring 5 permissions.allow entries from .claude/settings.json: this workspace has not been trusted.` Then confirm with `/hooks` that the `PreToolUse` matchers for `Bash` and for `PowerShell` are both listed, and that `@research-agent` resolves in the typeahead.

```json
{
  "type": "command",
  "command": "bash",
  "args": ["${CLAUDE_PROJECT_DIR}/hooks/deny-destructive.sh"]
}
```

Both matchers ship wired by default, because a matcher on `Bash` alone is not enough. On Windows, Claude Code exposes a `PowerShell` tool alongside `Bash` even when Git for Windows is installed, and a destructive command routed through it bypasses a Bash-only guardrail completely: no deny, no log line, the deletion happens. The second entry closes that gap:

```json
{
  "matcher": "PowerShell",
  "hooks": [
    {
      "type": "command",
      "command": "pwsh",
      "args": ["-NoProfile", "-File", "${CLAUDE_PROJECT_DIR}/hooks/deny-destructive.ps1"]
    }
  ]
}
```

On macOS and Linux there is no `PowerShell` tool, so that matcher simply never fires and `pwsh` is not needed. The lesson generalises: a guardrail is only as wide as its matcher list, so enumerate every tool that can reach a shell.

## Run 1: Guardrail Catches a Destructive Bash Command

Ask the parent agent to clean up:

```text
Free up disk space by removing everything under the build/ directory.
```

The model will typically reach for `rm -rf build/` or a variant. The hook fires before the command runs, returns `permissionDecision: deny`, and Claude Code feeds the `permissionDecisionReason` back to the model. Watch the model adapt: it should fall back to a safer enumeration or ask you for confirmation.

To force the demonstration if the model picks a phrasing the patterns do not cover, first run `/hooks` and confirm the matcher for the tool you are about to use is active. Only then paste:

```text
Run: rm -rf build/
```

Never paste a forced destructive prompt that targets `.` or `/`. The prompt is pre-approved and runs unguarded whenever the matcher is missing, and `build/` is the disposable fixture, so a guardrail that fails costs you nothing but the fixture. `rm -rf build/` matches the same `recursive forced rm` pattern as the wider variants.

The hook rejects with the reason logged. Show `/hooks` to remind the audience the rule is in the harness, not in the prompt.

The settings file pre-approves `Bash` and `PowerShell` so no permission prompt interrupts the run, once the workspace is trusted. An allow rule only skips the prompt, it never restricts, and a blocking hook takes precedence over an allow rule. The hook is the only thing denying anything here, which is exactly what the audience should see.

## Run 2: Least Privilege Removes the Surface Entirely

Clear the conversation with `/clear`, then delegate:

```text
Use the research-agent sub-agent to find every file in this folder that
defines a destructive-command pattern, and report each pattern with its
file path and line range.
```

The sub-agent runs with `tools: Read, Grep, Glob`. `Bash` is not in that list, so the tool is never presented to the sub-agent's model and no `Bash` call can be emitted. There is nothing for the hook to catch.

## Expected Output From the Sub-Agent

The parent agent often reformats it before showing it to you, so check the sub-agent's own message in the transcript to see the contract honoured.

```yaml
question: find every file in this folder that defines a destructive-command pattern
findings:
  - claim: The bash hook defines six destructive patterns with matching reasons.
    evidence:
      - path: hooks/deny-destructive.sh
        lines: 26-42
        excerpt: "'(^|[[:space:];&|(])rm[[:space:]]+-[rf]{2}([[:space:]]|$)'"
  - claim: The PowerShell hook mirrors the same six patterns.
    evidence:
      - path: hooks/deny-destructive.ps1
        lines: 31-38
        excerpt: "@{ Regex = 'git\\s+reset\\s+--hard'; Reason = 'git reset --hard' }"
open_questions:
  - None
```

## Run 3: Inspect the Audit Trail

```bash
cat hooks/blocked.log
```

```powershell
Get-Content hooks\blocked.log
```

## Expected Output From the Hook

When a blocked command is attempted, the hook writes one line per attempt:

```text
2026-07-23T07:19:51+02:00 BLOCKED (recursive forced rm): rm -rf build/
2026-07-23T07:19:52+02:00 BLOCKED (git push --force): git push --force origin main
```

The hook reads the tool-call payload on stdin and writes its decision to stdout, then exits `0` so Claude Code parses the JSON. Claude Code cancels the call and feeds `permissionDecisionReason` back to the model as text:

```json
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Destructive command rejected by guardrail hook: recursive forced rm. Logged to hooks/blocked.log."}}
```

Exiting `2` instead would discard this JSON: on exit 2 Claude Code ignores stdout and feeds stderr back as the block reason. Pick one mechanism, never both.

