# Skill Guard Starter

A stdlib-only Python project for enforcing the master-skill folder convention with hooks: a `PreToolUse` blocker that refuses a nested subskill before it is written, and a `PostToolUse` hook that runs a shipped bash linter over `.claude/skills/` and `.claude/agents/` after every change.

Nothing needs installing. Python 3.9 or newer and a `bash` on PATH (Git Bash on Windows) are the only requirements.

## The convention being enforced

A master skill holds exactly one `SKILL.md` at its root. Every leaf is a plain `references/<leaf>.md` with no frontmatter, because a `name` or `description` is what makes a file get discovered as its own skill and shadow the master. A capability that genuinely needs to be discoverable on its own becomes a top-level peer skill folder, never a nested one.

## What ships here

| Path | Purpose |
|------|---------|
| `scripts/lint-claude-config.sh` | Finished reference linter: walks `.claude/skills/` and `.claude/agents/`, reports defects, exits 1 when any are found |
| `fixtures/clean/` | A correct skill tree: one root manifest, three frontmatter-free references, one described agent |
| `fixtures/broken/` | The same tree carrying one instance of each defect the linter catches |
| `.claude/settings.json` | Empty `hooks` object, wired in Step 4 |
| `tests/hook_harness.py` | Pipes a real JSON payload into a hook script, and runs the linter against a fixture root |
| `tests/test_lint_script.py` | Asserts the linter's exit codes and the four defects it finds in `fixtures/broken` |

## What you build

Two hooks plus their tests:

1. `hooks/block_nested_skill.py`, a `PreToolUse` hook that blocks a nested `SKILL.md`, a lowercase `skill.md`, and a reference carrying frontmatter, each with exit 2 and a reason on stderr.
2. `hooks/lint_skills.py`, a `PostToolUse` hook that runs the shipped linter whenever a skill or agent file changes and feeds the issue list back to Claude.

## Run the tests

```bash
python -m unittest discover -s tests -v
```

## Run the linter by hand

```bash
bash scripts/lint-claude-config.sh fixtures/clean
bash scripts/lint-claude-config.sh fixtures/broken
```

The guide for this project is [../demo-skill-guard.md](../demo-skill-guard.md).
