# Proposal 2

Target metric: notes only (`notes-only`), 0 of 3 runs at the v1b baseline. Every v1 answer ended
with a `---` rule and a paragraph explaining which commits were left out.

Change (one variable only): a new step 4 tells the skill to return the notes and nothing around
them. Nothing else changes.

Prediction: `notes-only` reaches 3 of 3. The three heading graders, `no-merge` and `read-commits`
stay at 3 of 3, and no run errors.

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
4. Return only the notes: nothing before the `# Version` heading and nothing after the last section.
```
