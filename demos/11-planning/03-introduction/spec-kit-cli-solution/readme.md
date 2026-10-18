# Solution: Spec Kit CLI for Claude Code, Verified

The commands on [the topic page](../readme.md) were run on 2026-10-17. This folder records what they actually did, so you can tell a broken install from a changed tool.

Environment: Windows 11, Claude Code 2.1.302, `uv` 0.9.18, Python 3.12.10, Spec Kit `specify` 1.2.1.

## Install

The topic page installs the latest release, and the demo's setup scripts pin the version this module was recorded against. On 2026-10-17 both resolve to the same build:

```bash
uv tool install specify-cli --reinstall
```

```text
Resolved 43 packages in 325ms
Prepared 43 packages in 6ms
Uninstalled 43 packages in 513ms
Installed 43 packages in 272ms
...
 ~ specify-cli==1.2.1
```

```bash
uv tool install specify-cli==1.2.1 --reinstall
```

```text
Resolved 43 packages in 323ms
Prepared 43 packages in 7ms
Uninstalled 43 packages in 676ms
Installed 43 packages in 314ms
...
 ~ specify-cli==1.2.1
...
Installed 1 executable: specify
```

```bash
specify --version
```

```text
specify 1.2.1
```

The install commands above were not re-run in the verification pass, because they replace a global tool on the machine. The output is the one recorded earlier on the same day; `specify --version` was checked again and printed `specify 1.2.1`.

The command is identical in PowerShell. `--reinstall` replaces whatever `specify-cli` the machine already carries; without it, `uv tool install` leaves an older version in place and you end up typing a command name the installed skills no longer use.

## Initialize for Claude Code

```bash
specify init meeting-cost --integration claude --script py --non-interactive
```

```text
Selected coding agent integration: claude
Selected script type: py
Initialize Specify Project
├── ● Check required tools (ok)
├── ● Select coding agent integration (claude)
├── ● Select script type (py)
├── ● Install integration (Claude Code)
├── ● Install shared infrastructure (scripts (py) + templates)
├── ○ Ensure scripts executable
├── ● Constitution setup (copied from template)
├── ● Install bundled workflow (speckit installed)
└── ● Finalize (project ready)
Project ready.
```

The closing banner names where the commands went and what they are called:

```text
│  2. Start Claude in this project directory; spec-kit skills were installed  │
│  to .claude/skills                                                          │
│  3. Start using skills with your coding agent:                              │
│     3.1 /speckit-constitution - Establish project principles                │
│     3.2 /speckit-specify - Create baseline specification                    │
│     3.3 /speckit-plan - Create implementation plan                          │
│     3.4 /speckit-tasks - Generate actionable tasks                          │
│     3.5 /speckit-implement - Execute implementation                         │
│     3.6 /speckit-converge - Assess the codebase and append remaining work   │
│  as tasks                                                                   │
```

The generated project contains ten skill folders, one per command, and the hyphen separator is written next to the integration that owns the files:

```bash
ls meeting-cost/.claude/skills
```

```text
speckit-analyze
speckit-checklist
speckit-clarify
speckit-constitution
speckit-converge
speckit-implement
speckit-plan
speckit-specify
speckit-tasks
speckit-taskstoissues
```

```bash
cat meeting-cost/.specify/integration.json
```

```json
{
  "version": "1.2.1",
  "integration_state_schema": 1,
  "installed_integrations": [
    "claude"
  ],
  "integration_settings": {
    "claude": {
      "script": "py",
      "invoke_separator": "-"
    }
  },
  "integration": "claude",
  "default_integration": "claude"
}
```

## The integration flag is not optional in a script

`specify init` asks for the coding agent when it has a terminal to ask in. In a script, a CI job or any run with `--non-interactive`, it picks a default, and the default is not Claude Code:

```bash
specify init init-default --non-interactive
```

```text
Non-interactive session detected: defaulting to 'copilot'. Use --integration to
Selected coding agent integration: copilot
Selected script type: ps
├── ● Install integration (GitHub Copilot)
```

The result is a `.github/` folder with a `skills/` subfolder and no `.claude/` folder, so Claude Code finds no `speckit-*` skills. Always pass `--integration claude`.

## What the flags accept

`specify init` takes `--script`, `--ignore-agent-tools`, `--here`, `--force`, `--allow-symlinks`, `--non-interactive`, `--preset`, `--integration`, `--integration-options`, `--commands-dir`, `--skills`, `--extension`, `--trust-extension-urls` and `--trust-integration`. The top-level subcommands are `init`, `check`, `version`, `mcp`, `self`, `extension`, `integration`, `event`, `preset`, `artifact`, `bundle` and `workflow`.

`init` needs no network. The templates ship inside the package, which is also why the generated project always matches the installed CLI version.

## Slash commands in the generated project

The skills were run headlessly from the generated folder, one prompt per command, in fresh sessions.

`/speckit-constitution` with six principles wrote `.specify/memory/constitution.md` at version 1.0.0, dated 2026-10-17. The file carries the six principle sections, and the reply notes that the template has five principle slots and that a sixth was added.

`/speckit-specify` with the calculator brief wrote `specs/001-meeting-cost-calculator/spec.md` and `checklists/requirements.md`, with no `[NEEDS CLARIFICATION]` markers.

## If the version has moved on

Re-run the commands above. If `specify --version` reports something newer and the closing banner prints different command names, correct the topic page; your install is fine.

[← Back to Why Spec-Driven Development](../readme.md)
