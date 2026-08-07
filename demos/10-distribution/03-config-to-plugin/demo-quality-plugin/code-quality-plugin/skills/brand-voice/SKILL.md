---
name: brand-voice
description: 'Audit and fix Markdown files for brand-voice quality: em dashes in prose, Mermaid label syntax, paragraph length, and slash command tables. Trigger phrases: brand voice check, quality check, fix em dashes, check this readme.'
license: MIT
allowed-tools: Read, Edit, Glob, Grep
---

# Brand Voice Quality Check

Enforce the writing and formatting rules below against one or more Markdown files. The skill ships with the plugin so any installer gets the same rules without copying a config.

## Inputs

A file, a folder, or a glob. If no target is given, ask before proceeding.

## Rules

### Rule 1: No Em Dashes in Prose

Em dashes are banned in body text. Replace based on role:

| Em dash role | Replace with |
|---|---|
| Parenthetical aside | `(...)` |
| Clause continuation | `,` or `;` |
| Explanation or amplification | `:` |
| Simple pause | `;` |

Exceptions: em dashes inside link text (`[01 — Intro]`) and inside fenced code are intentional and stay.

### Rule 2: Mermaid Node Labels

`\n` does not render inside Mermaid node labels. Use `<br/>` and wrap the label in double quotes.

```text
Before: O[Orchestrator] --> R[Research Agent\nfinds facts]
After:  O[Orchestrator] --> R["Research Agent<br/>finds facts"]
```

### Rule 3: Paragraph Length

No paragraph may exceed four sentences. Start a new paragraph at the fifth. Do not count sentences inside fenced code, blockquotes, table cells, or list items.

### Rule 4: Slash Command Tables

Slash command tables must list commands specific to the document's topic. Do not paste the same generic set into every file. If the topic is unclear, flag it rather than guessing.

## Steps

1. Resolve the target to a list of Markdown files using Glob.
2. For each file: read, scan for every rule, collect violations.
3. Apply all fixes in a single Edit per file where possible.
4. Print a per-file violation report.

## Output Format

```text
FILE: <path>
  [em-dash]   line 12 — fixed
  [mermaid]   line 29 — \n replaced with <br/>
  [paragraph] line 84 — split after sentence 4

SUMMARY: N files checked, M changed
```
