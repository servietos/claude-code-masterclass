# Ship a Code-Quality Bundle as One Plugin

This demo ships a four-piece bundle as a single installable plugin: a `/create-docs` slash command, a `brand-voice` skill, a `code-reviewer` skill, and a `PostToolUse` metrics hook. The pieces are deliberately the kind of artifacts a team would otherwise scatter across personal `.claude/` folders, and the plugin is what turns "everyone has their own version" into "everyone has the same version, pinned to a sha".

## Prerequisites

Hook commands default to bash, which on Windows means Git Bash, and the wired command calls `bash` explicitly. The script uses `jq` to build each record, so install `jq` before the run (`winget install jqlang.jq` on Windows). The bundled `hooks/metrics.ps1` is the PowerShell equivalent for a machine without `jq` or without Git Bash: wire it by setting the hook command to `pwsh -NoProfile -File "${CLAUDE_PLUGIN_ROOT}/hooks/metrics.ps1"` and adding `"shell": "powershell"` to the hook entry.

## Folder Layout

```text
demo-quality-plugin/
├── quality-review-plugin/                # the plugin
│   ├── .claude-plugin/plugin.json      # manifest
│   ├── commands/create-docs.md         # /create-docs slash command
│   ├── skills/
│   │   ├── brand-voice/SKILL.md        # writing-quality skill
│   │   └── code-reviewer/SKILL.md      # code-review skill
│   └── hooks/
│       ├── hooks.json                  # PostToolUse wire-up
│       ├── metrics.ps1                 # PowerShell hook
│       └── metrics.sh                  # Git Bash hook (default)
├── project-settings.json               # project-level model and permissions
└── sample-code/
    └── inventory.py                    # target for /create-docs
```

## What Each Piece Does

The `/create-docs` command reads a source file at a path the user provides, generates a sibling `.md` document with purpose, public surface, behavior notes, and usage, then chains the bundled skills. It calls `brand-voice` against the generated documentation to enforce em-dash, paragraph length, and Mermaid label rules, and it calls `code-reviewer` against the original source to surface critical findings in a "Review Notes" section.

The `brand-voice` skill applies the same four rules already used elsewhere in this masterclass repo, packaged so any installer gets them without copying a config. The `code-reviewer` skill is the existing repo skill bundled verbatim, which is exactly the artifact the demo claims to be packaging from `.claude/` into a plugin.

The `PostToolUse` metrics hook fires after every tool call and appends a JSONL record to `${CLAUDE_PLUGIN_DATA}/tool-usage.jsonl`. Each record carries timestamp, session id, tool name, input snapshot, duration, error flag, and current working directory. The hook is one of the clearest cases where `${CLAUDE_PLUGIN_DATA}` matters: the data path is the same across machines even though the install path differs.

Model and permission defaults do not travel inside a plugin. `project-settings.json` in this folder is that project-level file, kept next to the plugin for comparison.

## Running the Demo

### Step 1: Local load with `--plugin-dir`

```bash
claude --plugin-dir ./quality-review-plugin
```

The init message should list `quality-review-plugin` and its components. Verify the namespaced command appears with `/quality-review-plugin:create-docs` and the skills are visible under the plugin namespace.

### Step 2: Run `/create-docs` against the sample

```text
/quality-review-plugin:create-docs sample-code/inventory.py
```

The command produces `sample-code/inventory.py.md` with the documentation, then chains the brand-voice and code-reviewer passes. Findings on `inventory.py` are model-dependent; expect notes around `Inventory.value()` summing a generator with a `Decimal` start value, the mutation path in `adjust`, and the non-internationalized `InventoryError` messages.

### Step 3: Inspect metrics

The hook writes to `${CLAUDE_PLUGIN_DATA}`, which Claude Code exports to hook processes only, not to your terminal. Read the log from its resolved location instead, which is `~/.claude/plugins/data/<plugin-id>/tool-usage.jsonl`. A plugin loaded with `--plugin-dir` carries the id `<name>-inline`:

```bash
cat ~/.claude/plugins/data/quality-review-plugin-inline/tool-usage.jsonl
```

```powershell
Get-Content $env:USERPROFILE\.claude\plugins\data\quality-review-plugin-inline\tool-usage.jsonl
```

Each line is one tool invocation:

```json
{"timestamp":"2026-07-22T20:55:18Z","session_id":"d10342a8","tool_name":"Read","tool_input":{"file_path":"sample-code/inventory.py"},"duration_ms":2,"is_error":false,"cwd":"D:\\demo"}
```

Aggregate by `tool_name` for a per-tool count, by `session_id` for per-session totals, or by `duration_ms` to find the slow tools.

### Step 4: Edit and reload

Tighten the `/create-docs` description in `commands/create-docs.md`, then `/reload-plugins`. Re-invoke the command and confirm the new behavior appears without restarting Claude Code. That hot-reload loop is what makes plugin authoring no slower than `.claude/` authoring; only publishing carries extra cost.

### Step 5: Validate before publishing

```bash
claude plugin validate --strict ./quality-review-plugin
claude --plugin-dir ./quality-review-plugin plugin details quality-review-plugin
```

`validate` takes a path and catches manifest, skill, and hook errors that would otherwise become silent no-loads at install time; a skill whose YAML frontmatter fails to parse loads with empty metadata and never triggers. `details` resolves a plugin by name, so a plugin that is not installed yet needs the `--plugin-dir` flag in front of the subcommand. It prints the component inventory (3 skills, 1 hook) and the projected token cost, which is the number you want students worrying about before they ship a plugin that loads every skill on every turn.

## Hook Choice and Why

A `PostToolUse` metrics hook is the right kind to bundle in a quality plugin for two reasons. First, it is read-only and additive, and `PostToolUse` cannot block a call the way a `PreToolUse` guardrail can: the tool has already run, so exit code 2 only feeds stderr back to Claude. Second, it produces the telemetry teams actually want when they adopt a shared plugin: which tools fire, how often, how long, and from which sessions. Plugins that ship guardrail-style `PreToolUse` hooks should do so under a clearly named plugin so installers know what they are signing up for; this one is observability, not enforcement.

## Pointers

- Plugin anatomy: [../../02-plugin-anatomy/readme.md](../../02-plugin-anatomy/readme.md)
- Presenter script for the publishing path: [../readme.md](../readme.md)
- Marketplace distribution next steps: [../../04-marketplaces/readme.md](../../04-marketplaces/readme.md)
- Completed reference including the validated catalog: [../demo-quality-plugin-solution/](../demo-quality-plugin-solution/readme.md)
