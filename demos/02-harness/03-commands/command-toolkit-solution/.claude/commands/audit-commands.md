---
description: Lint every slash command file in this project for missing frontmatter fields and argument placeholders
argument-hint: [strict|report]
allowed-tools: Read, Glob, Bash(ls .claude/commands)
---

# Audit Commands

Mode: $ARGUMENTS

Command directory listing:

!`ls .claude/commands`

Required frontmatter fields: `description`, `argument-hint`, `allowed-tools`.

For each `.md` file in `.claude/commands`:

1. Read the file and check that all three required fields are present in the frontmatter block.
2. If the frontmatter has an `argument-hint`, the body must use at least one argument placeholder (`$ARGUMENTS`, `$0`, `$1`, ...). Record `argument placeholder` as missing when it does not.
3. If the body uses an argument placeholder, the frontmatter must have an `argument-hint`. Record `argument-hint` as missing when it does not.

Verdict per file:

- `strict`: `FAIL` when anything is missing, otherwise `PASS`.
- `report`, or an empty or other mode: `WARN` when anything is missing, otherwise `PASS`.

Answer with one markdown table with the columns `Command`, `Missing`, `Verdict`, and one row per command file. Write `none` in `Missing` when nothing is missing. Close with one sentence giving the number of files checked and the number of `FAIL` or `WARN` verdicts. Do not modify any files.
