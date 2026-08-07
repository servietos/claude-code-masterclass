# Run the Finished FTS5 Search Feature

The completed reference for the Plan Mode walkthrough in [../notes-cli/readme.md](../notes-cli/readme.md). It carries the result of the locked plan: a non-destructive FTS5 migration, a `search` command ranked with `ORDER BY bm25(notes_fts) ASC`, the filled-in [STATE.md](STATE.md), and tests for every Done Criteria bullet.

Work in the starter, compare against this folder.

## Run It

```bash
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt
.venv/Scripts/python notes.py add "hello from notes-cli"
.venv/Scripts/python notes.py add "second note"
.venv/Scripts/python notes.py list
.venv/Scripts/python notes.py search hello
```

On macOS and Linux use `.venv/bin/pip` and `.venv/bin/python`.

`list` prints both notes newest first; `search hello` prints only the matching note:

```text
1  2026-07-22 20:36:00  hello from notes-cli
```

## Run the Tests

```bash
.venv/Scripts/python -m pytest -q
```

Four tests pass: `list` after `add`, `search` matching one note only, BM25 ranking putting the denser match first, and a legacy `notes.db` without an FTS index surviving the migration.

## What Changed Against the Starter

| File | Change |
|---|---|
| `db.py` | `notes_fts` virtual table over the existing `notes` table, an after-insert trigger, and an idempotent `rebuild` that backfills rows written before the migration |
| `notes.py` | `search` command joining `notes_fts` to `notes`, ordered by `bm25(notes_fts)` ascending |
| `test_notes.py` | One test per Done Criteria bullet, each running against a temporary database |
| `STATE.md` | Decisions, Status, Done Criteria and an empty Open Questions section |
| `requirements.txt` | `typer==0.27.0` and `pytest==8.3.3` |
