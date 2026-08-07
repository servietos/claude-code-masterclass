---
description: Lint every slash command file in this project for missing frontmatter fields and argument placeholders
argument-hint: [strict|report]
allowed-tools: Read, Glob, Bash(ls .claude/commands)
---

# Audit Commands

Mode: $ARGUMENTS

Command files on disk:

!`ls .claude/commands`

Read every `.md` file in `.claude/commands/` and check each one against these rules:

- Frontmatter exists and is the first thing in the file.
- `description` is present and states what the command does, not just its name.
- `argument-hint` is present and its bracket count matches the highest positional placeholder used in the body.
- `allowed-tools` is present and lists only tools the body actually needs.
- The body references at least one of `$ARGUMENTS`, `$ARGUMENTS[N]`, or `$N`.

Report one table row per command file with columns: command name, missing fields, verdict (pass or fail).

In `strict` mode, also fail any command whose `allowed-tools` grants a bare `Bash` with no argument pattern. In `report` mode, note it as a warning instead.

Do not modify any command file. Propose the fix in prose.
