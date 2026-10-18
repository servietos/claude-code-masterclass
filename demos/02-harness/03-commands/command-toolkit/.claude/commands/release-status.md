---
description: Summarize the commit fixture and report which commit types the changelog CLI does not group yet
argument-hint: [version]
allowed-tools: Read, Glob, Bash(node src/notes.mjs *)
---

# Release Status

Target version: $ARGUMENTS

Read `data/commits.json` and `src/notes.mjs`, then report:

1. How many commits are in the fixture.
2. The distinct commit types present, with a count for each.
3. Which of those types are missing from the `GROUPS` map in `src/notes.mjs` and would therefore land in `Other Changes`.

Answer in a single markdown table plus one closing sentence. Do not modify any files.
