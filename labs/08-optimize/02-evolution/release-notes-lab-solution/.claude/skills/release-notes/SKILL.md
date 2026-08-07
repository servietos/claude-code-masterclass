---
name: release-notes
description: Generate release notes from recent git commits
---

# Release Notes

## When to use

When the user asks for a changelog, release notes, or a summary of recent commits.

## Steps

1. Run `git log --oneline -10` to see recent commits.
2. Summarise the commits as user-facing release notes.
3. Return the notes as markdown.
