---
name: notes-prioritise
description: Read .notes/extracted.md and rewrite it into Now, Next and Later sections based on inferred urgency. Use after notes-extract, or when asked to prioritise todos, triage notes, or rank code comments by urgency.
---

# Notes Prioritise

Read `.notes/extracted.md` and rewrite it as a prioritised plan.

## Steps

1. Read `.notes/extracted.md`. If it does not exist, stop and say that `notes-extract` has to run first.
2. Assign every row exactly one bucket using the rules below.
3. Rewrite `.notes/extracted.md` in place with the prioritised layout. Keep every original row: no row is dropped, no row is duplicated.

## Bucket rules

| Bucket | Assign when |
|---|---|
| Now | Marker is `FIXME`, or the text mentions a crash, data loss, security, a leak, or a correctness bug |
| Next | Marker is `TODO`, or the text describes missing behaviour, validation, or a test gap |
| Later | Marker is `NOTE`, or the text is an observation, a refactor idea, or a future-version remark |

A `TODO` whose text describes a correctness or security problem moves up to Now. A `FIXME` that is a stylistic remark moves down to Next.

## Output format

```markdown
# Prioritised Notes

## Now

| File | Line | Marker | Note |
|---|---|---|---|

## Next

| File | Line | Marker | Note |
|---|---|---|---|

## Later

| File | Line | Marker | Note |
|---|---|---|---|
```

## Rules

- Rewrite `.notes/extracted.md` only. Do not create a second report file.
- Every row from the extracted report appears exactly once in the prioritised report.
- If a bucket is empty, keep its heading and write `_none_` under it.
