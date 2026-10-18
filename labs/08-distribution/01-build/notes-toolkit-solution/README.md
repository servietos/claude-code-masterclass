# notes-toolkit

Reference solution for Lab 01 of Module 08. It is the `notes-toolkit/.claude/` configuration converted into a self-contained Claude Code plugin.

## Overview

The plugin inventories `TODO`, `FIXME` and `NOTE` comments across a project, triages them into `Now` / `Next` / `Later`, and keeps writes fenced to a small set of paths while it works.

## Layout

```text
notes-toolkit/
├── .claude-plugin/
│   └── plugin.json
├── .mcp.json
├── README.md
├── skills/
│   ├── notes-extract/SKILL.md
│   └── notes-prioritise/SKILL.md
├── commands/
│   └── notes-flow.md
├── hooks/
│   ├── hooks.json
│   ├── scope-gate.sh
│   └── scope-gate.ps1
└── mcp-server/
    ├── requirements.txt
    └── server.py
```

The manifest lives at `.claude-plugin/plugin.json`. Every other directory sits at the plugin root. A `plugin.json` at the plugin root is not read by Claude Code.

## Skills

| Skill | Invoked as | What it does |
|---|---|---|
| `notes-extract` | `/notes-toolkit:notes-extract` | Scans the source tree for `TODO`, `FIXME` and `NOTE` and writes `.notes/extracted.md` |
| `notes-prioritise` | `/notes-toolkit:notes-prioritise` | Rewrites `.notes/extracted.md` into `Now`, `Next` and `Later` sections |

## Commands

| Command | Invoked as | What it does |
|---|---|---|
| `notes-flow` | `/notes-toolkit:notes-flow` | Runs `notes-extract` then `notes-prioritise` and reports the per-bucket counts |

## Hooks

`hooks/scope-gate.sh` runs on `PreToolUse` with matcher `Write|Edit`, registered in `hooks/hooks.json`. It reads the hook payload from stdin, normalises the target path (Windows backslashes included), and exits `2` with a stderr message for any write outside `.notes/`, `src/`, `tests/`, `.claude/` and the root `README.md`.

`hooks/scope-gate.ps1` is the same gate for a machine without git-bash or `jq`, where a hook entry defaults to the `powershell` shell and the `bash "…"` command has nothing to execute. Swap the registered entry in `hooks/hooks.json` for this one, and keep exactly one registered:

```json
{ "type": "command", "command": "pwsh -NoProfile -File \"${CLAUDE_PLUGIN_ROOT}/hooks/scope-gate.ps1\"", "shell": "powershell" }
```

## MCP servers

`mcp-server/server.py` is a FastMCP stdio server declared in `.mcp.json` as `notes-mcp`. It exposes one tool.

| Tool | Returns |
|---|---|
| `count_todos(path="")` | `{root, files_scanned, counts: {TODO, FIXME, NOTE}, total}` |

`mcp-server/requirements.txt` is the single dependency declaration. `.mcp.json` launches the server with `uv run --with-requirements`, so `uv` builds and caches the environment from that file at install time, with no interpreter path baked into the plugin.

To work on the server itself, create a local environment beside it:

```bash
cd mcp-server
uv venv --seed .venv
uv pip install --python .venv -r requirements.txt
```

`--seed` puts `pip` inside the venv, so `pip install` after activation targets the venv and never falls through to the system interpreter. `.venv/` is git-ignored.

## Install

Load it for a single session without installing:

```bash
claude --plugin-dir /full/path/to/notes-toolkit
```

Validate the manifest and component frontmatter before you ship it:

```bash
claude plugin validate /full/path/to/notes-toolkit --strict
```

Inside a session, `/reload-plugins` re-reads the plugin after an edit. `/plugin` opens the plugin panel.
