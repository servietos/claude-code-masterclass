# Proposal 1

Target metric: sections present (`version-heading`, `features-heading`, `fixes-heading`), 1 of 9
heading checks passed across the three v0 runs.

Change (one variable only): step 3 of the skill names the output structure. Nothing else changes.

Prediction: all three heading graders reach 3 of 3. `no-merge` and `read-commits` stay at 3 of 3,
and no run errors.

Proposed SKILL.md:

```markdown
---
name: release-notes
description: Generate release notes from recent git commits
---

# Release Notes

## When to use

When the user asks for a changelog, release notes, or a summary of recent commits.

## Steps

1. Read `commits.txt`, the output of `git log --oneline -10`.
2. Summarise the commits as user-facing release notes.
3. Return the notes as markdown with exactly this structure: a `# Version` heading, then `## Features` for `feat:` commits and `## Fixes` for `fix:` commits.
```
