---
description: Run notes-extract then notes-prioritise to produce a prioritised .notes/extracted.md
---

# Notes Flow

Run the notes toolkit end to end.

1. Run the `notes-extract` skill. It scans the project for `TODO`, `FIXME` and `NOTE` comments and writes `.notes/extracted.md`.
2. Run the `notes-prioritise` skill. It rewrites `.notes/extracted.md` into `Now`, `Next` and `Later` sections.
3. Report the counts per bucket and the path of the report.

Stop after step 2 if `.notes/extracted.md` was not produced, and say why.
