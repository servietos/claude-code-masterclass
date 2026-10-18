---
name: notes-extract
description: Scan the project for TODO, FIXME and NOTE comments and write a structured markdown report to .notes/extracted.md. Use when asked to extract todos, collect fixmes, inventory code notes, or build a notes report.
---

# Notes Extract

Scan the project and produce a structured inventory of every `TODO`, `FIXME` and `NOTE` comment.

## Steps

1. Search the tracked source tree for the three markers. Use a content search over `src/`, `tests/` and the project root, skipping `.git/`, `node_modules/`, `.venv/` and `.notes/`.
2. For every hit record: marker kind, file path relative to the project root, line number, and the comment text with the marker prefix stripped.
3. Group the hits by marker kind in the order `FIXME`, `TODO`, `NOTE`.
4. Write `.notes/extracted.md`. Create the `.notes/` directory if it does not exist.

## Output format

```markdown
# Extracted Notes

Generated from a scan of the project source.

## FIXME

| File | Line | Note |
|---|---|---|
| src/parser.py | 12 | handle empty input |

## TODO

| File | Line | Note |
|---|---|---|

## NOTE

| File | Line | Note |
|---|---|---|
```

## Rules

- Never edit the source files. This skill only reads them.
- Keep one table row per hit, in file-then-line order.
- If a marker kind has no hits, keep its heading and write `_none_` under it.
- Write only to `.notes/extracted.md`.
