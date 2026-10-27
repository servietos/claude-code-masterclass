# Automate Workflows with Hooks and Mods

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

This hook fires before every `Write` or `Edit` call and refuses any path owned by a build step: anything under `docs/generated/` and any `*.lock` file. It is the blocker this topic's own hook pipeline builds, chosen because the exit-code contract is the lesson and a non-destructive rule shows it without borrowing module 07's material.

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

Exit 2 is not the only way to say no. A `PreToolUse` hook can instead exit 0 and print a JSON control object on stdout with `permissionDecision: "deny"` and a reason, which is the form [07-optimize-observability: Hook Guardrails and Least Privilege](../../07-optimize-observability/05-guardrails/demo-hook-guardrails.md) uses when it applies these same mechanics to destructive Bash commands, alongside a Bash and PowerShell handler pair and an audit log.

## Example 3 (PostToolUse): Keep CLAUDE.md Short

This repository runs a settings hook of its own on every `Write` and `Edit`: `.claude/hooks/claude-md-guard.sh`, wired under `PostToolUse` with `matcher: "Write|Edit"` and a 5 second timeout. It lets every file through except a `CLAUDE.md` that has grown past 90 lines.

```bash
#!/bin/bash
# PostToolUse hook: keep CLAUDE.md short. Detail belongs in a skill, not here.
# Exit 2 feeds stderr back to the model as blocking feedback; exit 0 stays silent.

MAX_LINES=90

file=$(jq -r '.tool_response.filePath // .tool_input.file_path // empty' 2>/dev/null)
[ -z "$file" ] && exit 0
[ "$(basename "$file")" = "CLAUDE.md" ] || exit 0
[ -f "$file" ] || exit 0

lines=$(wc -l < "$file")

if [ "$lines" -gt "$MAX_LINES" ]; then
  cat >&2 <<EOF
CLAUDE.md is now $lines lines (cap $MAX_LINES). It is a router, not a manual.
Move the detail you just added into the skill that owns it and leave a one-line pointer:
- demo / presenter / lab guide rules -> ~/.claude/skills/create-class/references/create-guide.md
- writing and voice rules            -> .claude/skills/brand-voice-code/references/rules.md
- slide rules                        -> .claude/skills/create-module-pptx/
- anything else procedural           -> a skill under .claude/skills/
Keep only: repo purpose, folder layout, one-line rules, harness delegation.
EOF
  exit 2
fi

exit 0
```

Claude Code starts the script after the write has landed and pipes the tool payload into it. `jq` reads the file path, every file not named `CLAUDE.md` exits 0 at once, and a `CLAUDE.md` over the cap exits 2 with a message that names where the detail belongs. The oversized file is already on disk, so exit 2 cannot undo the write; Claude reads stderr as feedback and moves the detail out in its next step. The script keeps nothing between runs and draws nothing: it is a check, a message and an exit code.

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

This pattern maps directly to the skill-improvement loop in [Evolve via Metrics](../../../labs/07-optimize-observability/lab-02-evolve-via-metrics.md): record, measure, iterate. The Stop hook is the recording layer; the analysis is a separate Claude invocation run against the log corpus.

## Mods: Extend and Customize the Harness

A mod extends and customizes the harness itself. Every other harness file works from outside Claude Code: a settings hook runs a script, a skill adds text, an MCP server adds tools. A mod runs inside Claude Code, as a set of JavaScript or TypeScript functions that Claude Code calls on every event in the session, and each function can watch the event, change it, or take it over, and draw its own interface in the terminal or the Desktop app.

That makes a mod the place to codify what your session history keeps showing: requests that recur, commands that get cancelled or rejected, and reviews that always ask the same question. Mods require Claude Code v2.1.287 or later and are on by default.

## Anatomy of a Mod

A mod is a plugin whose `hooks/hooks.json` names a hooks module under `modules`. That key is what makes the plugin a mod.

```text
first-mod/
├── .claude-plugin/
│   └── plugin.json
└── hooks/
    ├── hooks.json
    └── register.js
```

```json
{
  "description": "The first-mod hooks module",
  "modules": ["./register.js"]
}
```

The hooks module exports `register(on)`. Each call to `on` registers a hook for one event, and the variables at the top of the file are shared by every hook in it. This module counts tool calls and shows the count beside the spinner:

```javascript
let calls = 0

export function register(on) {
  on('tool.call', async ($, e, next) => {
    calls += 1
    $.ui.invalidate('ui.render')
    return next(e)
  })

  on('ui.render', { component: 'Spinner' }, async ($, e, next) => {
    return next({ ...e, props: { ...e.props, suffix: ' · tool calls: ' + calls + '…' } })
  })
}
```

## Observe, Rewrite, Answer

Every hook receives the same three arguments: `$`, the mods API that is the hook's only way to draw, run a process, call a model or touch a file; `e`, the event as plain data; and `next`, which passes the event on to the other mods and then to Claude Code's own behavior. The optional second argument to `on` is a matcher, such as `{ component: 'Spinner' }` or `{ command: 'tally' }`, that limits which events reach the hook.

| Choice | Code | Example |
|---|---|---|
| Observe | `return next(e)` after looking at `e` | Count a tool call, log a prompt |
| Rewrite | `return next({ ...e, ... })` with a changed copy | Add text to the spinner, adjust a tool call's arguments |
| Answer | Return a result without calling `next` | Refuse a command, reply to your own `/command` |

## Events and Surfaces

| Event | Fires when |
|---|---|
| `session.start` | The session starts, and again on every reload of the mod |
| `prompt.submit` | A prompt is submitted |
| `tool.call` | Claude is about to use a tool |
| `command.run` | A `/command` runs, including one the mod registered with `$.command.register` |
| `ui.render` | Claude Code draws a part of its interface |

A mod can draw a band above the prompt, a pane beside the transcript, a status line or a toast, and it can restyle parts Claude Code draws itself, such as a tool call's row or the spinner. Hooks run everywhere the plugin loads, but drawing is narrower: the terminal and the Desktop app's Code tab show it, while the VS Code chat panel and `claude -p` run the hooks and draw nothing.

## Hook Outside, Mod Inside

The hooks above are settings hooks, and Claude Code calls both kinds hooks. The difference is where the code runs. A settings hook attaches to Claude Code from the outside, the same way a skill or an MCP server does: Claude Code starts a separate process for each event, hands it the event as JSON and reads back an exit code. A mod runs inside Claude Code, in the flow from prompt to model to tool call to screen, so it can stop an action before it takes effect and change what appears on the screen.

| | Mod | Settings hook |
|---|---|---|
| Where it runs | Inside Claude Code's own process | In a separate process Claude Code starts for the event |
| What it is | JavaScript or TypeScript functions in a plugin | A shell command, HTTP request or prompt in `settings.json` |
| Lifetime | Loads once and keeps state for the session | Starts fresh on every event and remembers nothing |
| Can it draw | Yes: a band, a pane, a status line, a toast, a question with buttons | No |
| How it ships | A plugin from a marketplace, installed once per machine | A file committed with the repository and wired in `.claude/settings.json` |
| Pick it when | You want a pane, a band, a custom command, or to rewrite an event | You want to block, allow or log an event with a script you already have |

`claude-md-guard.sh` above is the hook side of that table: one script, one rule, one exit code, and nothing it can remember or show. The mod side is `intent-guard`, further below.

## The Build Loop

Ask for a mod in plain words and Claude writes it with the built-in `plugin-authoring` skill, under `~/.claude/dev-mods/<session-id>/`, after you approve hot reloading for the session. To work on a mod you own, load its directory for one session:

```bash
claude --plugin-dir ./first-mod
```

Claude Code hot-reloads the module when a file changes and writes the type declarations for your exact version into `.claude-plugin/types/`; trust them over any page when the two disagree. Two commands close the loop without a session:

```bash
claude plugin validate ./first-mod
claude plugin test
```

`validate` prints a `hooks:` line with every event the module handles and a `calls:` line with every mods API method it calls, so a misspelled event shows up before you run anything. `test` runs the `.test.ts` files under `tests/` against the real runtime, with stubbed tool calls and no sign-in.

## Mods That Keep the Harness Improving

The [integrations.at harness](https://integrations.at/ai-trends/customize-your-agentic-harness-with-mods/) runs four mods, each built from a pattern found in its own session history:

| Mod | What it does |
|---|---|
| `intent-guard` | Checks commands against the team's own prompts: requested work and reads run at once, risky unrequested actions wait for approval |
| `ask-check` | Matches a question Claude is about to ask against earlier prompts and shows the answer already given |
| `learn-queue` | Starts `/claude-learn` after five idle minutes once a session had two prompts, more than three edited files or an agent; a band above the prompt shows the planned time, and key `2` runs it now |
| `report-loop` | Posts a status update every five minutes on any task running longer than five minutes |

The raw material is the transcripts under `~/.claude/projects/`: which requests recur, which commands were cancelled or rejected, and how changes get reviewed. Before shipping a mod that classifies commands or text, replay it over those transcripts and read a sample of every case it fires on.

## A Mod at Work: intent-guard

Claude Code's own permission handling has two ends. The permission classifier can block a command your team asked for, and bypass mode runs every command with nobody checking it. `intent-guard` sits between the two and applies your team's rule: it remembers the last ten prompts you typed and checks every `Bash`, `PowerShell` and MCP delete call against them.

| The command | What intent-guard does |
|---|---|
| A read, or anything that is not risky | Runs at once |
| Risky, and a recent prompt asked for it | Runs at once |
| Risky, and nobody asked for it | Holds it and asks: Proceed or Cancel |

Risky means one of a fixed list of families: deleting files, discarding git work, committing, pushing, merging a pull request, writing to a database, deleting remote resources, changing DNS, killing processes, running tests, and deleting through an MCP tool. Commit, push, merge and test runs count as requested only within the last three prompts. The question names who wants to run what, where, and why it was held:

```text
Claude wants to run `git checkout -- src` in D:\repo, which discards git work. Intent Guard held it because none of your recent prompts asked for that: run it?
```

Proceed lets the command run. Cancel denies it with a message that tells Claude not to retry it or reach the same result another way, and a pane lists every command still waiting. A settings hook starts with an empty memory on every event, so it would have to parse the session transcript again on each call to learn what you asked; the mod keeps the prompts in its own state and draws the waiting commands in its own pane.

## Install Mods from a Marketplace

A mod reaches a machine the way every plugin does: through a marketplace. A marketplace is a git repository or a folder that holds `.claude-plugin/marketplace.json`, a list of plugins with the path to each one. The integrations.at mods live in one such repository, `integrations-marketplace`:

```json
{
  "name": "integrations-marketplace",
  "owner": { "name": "Alexander Kastil" },
  "plugins": [
    { "name": "intent-guard", "source": "./intent-guard" },
    { "name": "learn-queue", "source": "./learn-queue" },
    { "name": "learn-loop", "source": "./learn-loop" }
  ]
}
```

`claude plugin marketplace add` takes four kinds of source: a GitHub `owner/repo`, the `https://` clone URL of any other git host, a local folder, or the URL of a hosted `marketplace.json`. The repository can be private. Claude Code clones it with the git credentials already on the machine and never prompts for a password, so anyone with read access can add it: over HTTPS after `gh auth login` and `gh auth setup-git`, or over SSH with a key loaded in the agent. A folder works too, which is how the author uses a marketplace before pushing it anywhere: plugins from a folder load in place, so an edit shows up at the next session start or after `/reload-plugins`.

```bash
claude plugin marketplace add alexander-kastil/integrations-marketplace
claude plugin install intent-guard@integrations-marketplace
claude plugin list
```

`claude plugin install` from the shell defaults to user scope, and the scope decides which repositories get the mod:

| Scope | Recorded in | Who gets it |
|---|---|---|
| User | `enabledPlugins` in `~/.claude/settings.json` | You, in every repository on this machine |
| Project | `.claude/settings.json`, committed | Everyone in this repository, after each person runs the install once with `--scope project` |
| Local | `.claude/settings.local.json` | You, in this repository only |

So a mod is installed once per machine, not once per repository: install it at user scope and every session in every repository loads it. A second machine repeats the two commands. A mod that needs another plugin names it under `dependencies` in its `plugin.json`, and the install pulls it in from the same marketplace: installing `learn-queue` also installs `learn-loop`, which carries the `claude-learn` skill it starts. A mod with options, such as the five-minute intervals of `report-loop`, takes them with `claude plugin configure report-loop@integrations-marketplace`.

Plugins installed from the shell load in the next session, or in the open one after `/reload-plugins`. Background updates are off for a marketplace you added yourself: run `claude plugin marketplace update integrations-marketplace`, or turn on auto-update for it under Marketplaces in `/plugin`.

## Trust and Off Switches

A mod runs with your permissions and is not sandboxed: it can read and write files, read environment variables, see every prompt and tool call, and approve a tool call before you are asked. Run `claude plugin validate` on a mod's directory before you install it and read its `hooks:` and `calls:` lines.

| Scope | Off switch |
|---|---|
| One mod | Disable or uninstall its plugin in `/plugin` |
| Every installed mod, one session | Start with `--safe-mode` |
| Every installed mod, every session | `"disableAllHooks": true` in `~/.claude/settings.json`, which also stops settings hooks and a custom status line |

Built-in mods such as `/diff` keep running under `--safe-mode` and `disableAllHooks`.

## Hands-On Demos

[Build a Three-Event Hook Pipeline](demo-hook-pipeline.md) wires a `PreToolUse` blocker, a `PostToolUse` audit writer, and a `Stop` summarizer in stdlib Python, proving each one by piping a real payload into it and asserting the exit code. The pristine starter is `hook-pipeline/`; the finished reference is `hook-pipeline-solution/`.

[Enforce a Skill Folder Convention with Hooks](demo-skill-guard.md) applies the same mechanics to a real repository rule: a master skill holds exactly one root `SKILL.md` and every leaf is a frontmatter-free `references/<leaf>.md`. A `PreToolUse` blocker refuses a nested subskill before it reaches disk, and a `PostToolUse` hook runs a bash linter over `.claude/skills/` and `.claude/agents/` to catch what the blocker cannot see. The pristine starter is `skill-guard/`; the finished reference is `skill-guard-solution/`.

The two demos show the layering that makes hooks useful: prevention at `PreToolUse`, where a bad write can still be refused, and correction at `PostToolUse`, where exit 2 cannot undo the write but does feed the problem back to Claude for the next turn.

[Install a Prompt-Cache Meter Mod](demo-cache-meter.md) installs `prompt-cache-control` from the `claude-code-templates` gallery, reviews it with `claude plugin validate` and `claude plugin test`, reads its band and `/cache` pane through a model switch that rewrites the cache, and pins its options in a `--settings` file. The pristine starter is `cache-meter/`; the finished reference is `cache-meter-solution/`.

[Guard Unrequested Commands with a Mod](demo-intent-guard.md) loads `intent-guard` with `--plugin-dir`, watches it hold a `git checkout --` nobody asked for and pass the same command once a prompt asks for it, then adds a `package-publish` family with two tests. The pristine starter is `guard-sandbox/`; the finished reference is `guard-sandbox-solution/`.

## Helpful Claude Slash Commands

| Command | Usage |
|---------|-------|
| `/update-config` | Add, modify, or debug hook entries and permissions in `settings.json`. |
| `/fewer-permission-prompts` | Scan transcripts and build an allowlist so safe tools bypass approval prompts. |
| `/doctor` | Run a health check to verify hooks are registered and scripts are reachable. |
| `/plugin-authoring` | Load the built-in skill Claude uses to write a mod. |
| `/plugin` | See which mods the session loaded and turn one off in the Installed tab. |
| `/reload-plugins` | Load a mod installed from the shell into the open session. |
| `/diff` | Open the diff pane, itself a built-in mod. |

## Key Topics covered in this module

- [Claude Code Hooks](https://code.claude.com/docs/en/hooks): Event types, stdin payload format, blocking semantics
- [Claude Code Settings](https://code.claude.com/docs/en/settings): Where hooks are configured and how the settings hierarchy applies
- [Evolve via Metrics (lab)](../../../labs/07-optimize-observability/lab-02-evolve-via-metrics.md): Session recording feeds a skill-improvement loop
- [Mods overview](https://code.claude.com/docs/en/plugins/mods/overview): what a mod can reach, where mods run, and how they compare to settings hooks, skills and MCP servers
- [Create a mod](https://code.claude.com/docs/en/plugins/mods/create): the tutorial, the reload loop, generated types and `claude plugin validate`
- [React to events](https://code.claude.com/docs/en/plugins/mods/events): tool calls, prompts, turns and the order mods run in
- [Draw in the interface](https://code.claude.com/docs/en/plugins/mods/interface): panes, the band above the prompt, buttons and state
- [Test a mod](https://code.claude.com/docs/en/plugins/mods/test): stubbing events and testing timers and drawings
- [Manage mods for your organization](https://code.claude.com/docs/en/plugins/mods/admin): defaults, managed settings and reviewing a mod
- [Getting started with Claude Code mods](https://claude.dev/blog/getting-started-with-claude-code-mods/): a walkthrough of state, panes and commands
- [Customize your agentic harness with mods](https://integrations.at/ai-trends/customize-your-agentic-harness-with-mods/): the four mods above and how they were derived from session history
- [Sample mods](https://github.com/anthropics/claude-code-playground/tree/main/claude-code/mods): `token-weather`, `blast-radius` and `replay-theater` as complete plugins
