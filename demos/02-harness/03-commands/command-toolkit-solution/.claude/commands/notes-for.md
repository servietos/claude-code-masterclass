---
description: Render the changelog for a given version and review it for gaps before release
argument-hint: [version]
allowed-tools: Read, Bash(node src/notes.mjs *)
---

# Notes For Version

Requested version: $0

Generated changelog:

!`node src/notes.mjs`

Using the changelog above:

1. Rewrite it with `$0` as the version in the `# Release` heading.
2. Prepend a summary of at most three sentences describing the theme of this release.
3. List every entry currently under `Other Changes` and name the grouping key that would fix each one: the commit type to add to `GROUPS` in `src/notes.mjs`.
