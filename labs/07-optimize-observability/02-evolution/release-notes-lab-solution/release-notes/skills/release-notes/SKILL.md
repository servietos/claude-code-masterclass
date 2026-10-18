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
