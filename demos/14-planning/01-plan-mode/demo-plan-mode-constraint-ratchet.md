# Lock design decisions incrementally with Plan Mode

Plan Mode answers a vague brief with a question list instead of code, and a numbered constraint block submitted before the ask is read as specification rather than as negotiation. You submit both against the notes-cli starter and compare the two plans that come back. You end holding a plan whose schema, migration strategy and command surface are pinned by constraints you wrote.

------

The [notes-cli/](notes-cli/) folder contains the starter app used in this demo. Prepare it with:

```bash
cd notes-cli
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt
.venv/Scripts/python notes.py add "hello from notes-cli"
.venv/Scripts/python notes.py list
```

On macOS and Linux use `.venv/bin/pip` and `.venv/bin/python`.

Expected output is one line per note: id, timestamp, body.

## Part A: Vague Brief

Press `Shift+Tab` until the input pill reads `plan mode on`. Submit:

```text
I want to add search to notes-cli.
```

Claude responds with a question list covering search type, scope, dependency constraints, and query semantics. It produces a provisional plan marked as such.

## Part B: Constraint Ratchet

Stay in Plan Mode. Submit:

```text
Constraints (non-negotiable):
  1. Full-text search on the note body only.
  2. Use SQLite FTS5. No external dependencies beyond Typer.
  3. Results ranked by BM25 relevance (FTS5 native).
  4. Existing notes.db rows must survive. No destructive migration.
  5. New command: search "query" (prints matching notes ranked by relevance).

Revise the plan. Tell me what is still ambiguous.
```

The plan changes concretely when constraints precede the ask. The schema section shows an FTS5 virtual table, the migration strategy is non-destructive, and the ambiguity section is now small enough to close in one more turn.

The finished, runnable result of this planning session (FTS5 migration, `search` command, STATE.md, tests) lives in [notes-cli-solution/](notes-cli-solution/).
