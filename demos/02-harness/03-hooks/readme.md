# Automate Workflows with Hooks

Hooks are shell commands that Claude Code executes automatically at defined lifecycle events. They run in your OS shell, outside the LLM entirely, so they are deterministic, fast, and cannot be reasoned around by Claude. That last property is what makes them valuable: a guardrail that lives in a prompt can be argued with; a hook that exits non-zero cannot.

The three things hooks give you that prompts do not: guaranteed side effects (linting, logging, notifications), pre-execution blocking (stop a dangerous command before it runs), and external system integration (post to Slack, write to a database, trigger a CI job), all without trusting Claude to remember.

## Hook Types

| Event | When it fires | Can block Claude? |
|-------|--------------|-------------------|
| `PreToolUse` | Before any tool call executes | Yes: exit code 2 blocks the call and feeds stderr back to Claude |
| `PostToolUse` | After a tool call completes | No |
| `Notification` | When Claude sends a notification (task done, waiting on user) | No |
| `Stop` | When Claude finishes a turn | Yes: exit code 2 prevents Claude from stopping and continues the conversation |

## Configuration

Hooks live in `.claude/settings.json` under a `hooks` object keyed by event name. Each event holds a list of matcher groups; every group pairs a `matcher` (a regex over the tool name) with a `hooks` array of entries of `type: "command"`. `Stop` and the other non-tool events do not support matchers and always fire, so their groups carry only a `hooks` array; a `matcher` added there is silently ignored.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "python scripts/guardrail.py" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          { "type": "command", "command": "bash scripts/lint-changed.sh" }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          { "type": "command", "command": "bash scripts/session-log.sh" }
        ]
      }
    ]
  }
}
```

Claude Code passes the tool call payload to the hook via stdin as a JSON object. A `PreToolUse` hook for `Bash` receives `{ "hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": { "command": "..." } }` alongside `session_id`, `cwd`, and `transcript_path`. A `PostToolUse` hook for `Write` receives the same fields plus `tool_response`. Exit 0 allows the call and lets Claude Code parse stdout for JSON control fields; exit 2 blocks and feeds stderr back to Claude; any other non-zero code is a non-blocking error.

## Example 1 (PostToolUse): Auto-lint on Write and Edit

This hook fires after every `Write` or `Edit` call and runs ESLint on the changed file. Because it runs after the write, it never blocks Claude; it just enforces formatting as a guaranteed side effect of every file change, with no manual step.

```bash
#!/usr/bin/env bash
# scripts/lint-changed.sh
FILE=$(cat - | python -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))")
[[ "$FILE" == *.ts || "$FILE" == *.tsx ]] && npx eslint --fix "$FILE" --quiet
```

The hook extracts `tool_input.file_path` from the JSON payload on stdin, checks the extension, and only runs ESLint for TypeScript files. Add it to `PostToolUse` with `matcher: "Write|Edit"` and every file Claude touches stays lint-clean without a separate prompt step.

## Example 2 (PreToolUse): Block Writes to Generated Paths

This hook fires before every `Write` or `Edit` call and refuses any path owned by a build step: anything under `docs/generated/` and any `*.lock` file. It is the blocker this topic's own hook pipeline builds, chosen because the exit-code contract is the lesson and a non-destructive rule shows it without borrowing module 09's material.

```python
#!/usr/bin/env python3
import fnmatch
import json
import sys
from pathlib import Path

PROTECTED = ["docs/generated/*", "*.lock"]

payload = json.load(sys.stdin)

if payload.get("tool_name") not in ("Write", "Edit"):
    sys.exit(0)

file_path = payload.get("tool_input", {}).get("file_path", "")
# the payload path is absolute and os-native, this pair makes it repo-relative so a pattern can match
target = Path(file_path).as_posix()
cwd = Path(payload.get("cwd", ".")).as_posix()

if cwd != "." and target.startswith(cwd + "/"):
    target = target[len(cwd) + 1:]

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

Three properties of the contract are visible here. Exit 0 is the pass-through for every payload the hook does not care about, exit 2 is the only code that stops the call, and the stderr text is the entire explanation Claude receives, so a bare `sys.exit(2)` blocks the write and tells the model nothing. The check is also content-aware rather than tool-aware: the permissions allowlist in `settings.json` decides which tools Claude may call, while the hook decides what those tools may touch.

Exit 2 is not the only way to say no. A `PreToolUse` hook can instead exit 0 and print a JSON control object on stdout with `permissionDecision: "deny"` and a reason, which is the form [09-observability: Hook Guardrails and Least Privilege](../../09-observability/02-guardrails/demo-hook-guardrails.md) uses when it applies these same mechanics to destructive Bash commands, alongside a Bash and PowerShell handler pair and an audit log.

## Session Logging: Stop Hook for Continuous Learning

The `Stop` event fires when Claude finishes a turn. That timing makes it the right place to record what happened in a session (what Claude did, what tools it used, what errors it hit) and feed that record into a retrospective loop.

```bash
#!/usr/bin/env bash
# scripts/session-log.sh
TIMESTAMP=$(date +%Y%m%dT%H%M%S)
LOG_DIR=".claude/sessions"
mkdir -p "$LOG_DIR"
cat - > "$LOG_DIR/$TIMESTAMP.json"
```

The hook writes the turn payload to a timestamped file in `.claude/sessions/`. Over days and weeks this builds a corpus of session data that a separate analysis pass can read, extracting patterns in what breaks, what skills underperform, and where agent handoffs fail. The analysis can be triggered manually whenever something stops working well, not on a fixed schedule.

This pattern maps directly to the skill-improvement loop in [Evolve via Metrics](../../../labs/08-optimize/lab-02-evolve-via-metrics.md): record, measure, iterate. The Stop hook is the recording layer; the analysis is a separate Claude invocation run against the log corpus.

## Hands-On Demos

[Build a Three-Event Hook Pipeline](demo-hook-pipeline.md) wires a `PreToolUse` blocker, a `PostToolUse` audit writer, and a `Stop` summarizer in stdlib Python, proving each one by piping a real payload into it and asserting the exit code. The pristine starter is `hook-pipeline/`; the finished reference is `hook-pipeline-solution/`.

[Enforce a Skill Folder Convention with Hooks](demo-skill-guard.md) applies the same mechanics to a real repository rule: a master skill holds exactly one root `SKILL.md` and every leaf is a frontmatter-free `references/<leaf>.md`. A `PreToolUse` blocker refuses a nested subskill before it reaches disk, and a `PostToolUse` hook runs a bash linter over `.claude/skills/` and `.claude/agents/` to catch what the blocker cannot see. The pristine starter is `skill-guard/`; the finished reference is `skill-guard-solution/`.

The two demos show the layering that makes hooks useful: prevention at `PreToolUse`, where a bad write can still be refused, and correction at `PostToolUse`, where exit 2 cannot undo the write but does feed the problem back to Claude for the next turn.

## Helpful Claude Slash Commands

| Command | Usage |
|---------|-------|
| `/update-config` | Add, modify, or debug hook entries and permissions in `settings.json`. |
| `/fewer-permission-prompts` | Scan transcripts and build an allowlist so safe tools bypass approval prompts. |
| `/doctor` | Run a health check to verify hooks are registered and scripts are reachable. |

## Key Topics covered in this module

- [Claude Code Hooks](https://code.claude.com/docs/en/hooks): Event types, stdin payload format, blocking semantics
- [Claude Code Settings](https://code.claude.com/docs/en/settings): Where hooks are configured and how the settings hierarchy applies
- [Evolve via Metrics (lab)](../../../labs/08-optimize/lab-02-evolve-via-metrics.md): Session recording feeds a skill-improvement loop
