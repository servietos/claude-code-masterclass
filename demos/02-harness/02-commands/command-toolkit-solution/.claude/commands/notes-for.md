---
description: Render the changelog for a given version and review it for gaps before release
argument-hint: [version]
allowed-tools: Read, Bash(node src/notes.mjs *)
model: claude-sonnet-5
---

# Notes For Version

Requested version: $0

Generated changelog:

!`node src/notes.mjs`

Using the changelog above:

1. Rewrite it with `$0` as the version in the `# Release` heading.
2. Add a one-paragraph summary at the top, at most three sentences, describing the theme of this release.
3. List any entries that landed under `Other Changes` and say which grouping key would fix each one.

Print the result as markdown in your reply. Do not write files.
