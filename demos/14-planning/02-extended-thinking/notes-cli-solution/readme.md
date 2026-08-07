# Read the Finished Notes CLI Search Feature

This is the completed reference for the [notes-cli/](../notes-cli/) starter: the FTS5 migration, the `search` command ranked with `bm25()`, the test file, and a `STATE.md` with every Status box checked. Use it to compare against your own run, not as the folder you work in.

## Run it

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python test_notes.py
python notes.py add "hello world"
python notes.py add "second note"
python notes.py add "hello again hello"
python notes.py search hello
python notes.py list
```

On macOS or Linux, activate with `source .venv/bin/activate`.

Expected output of `python test_notes.py`:

```text
PASS migration keeps existing rows
PASS search ranks by bm25
PASS cli search and list
```

Expected output of `python notes.py search hello`, with the two-occurrence note first because its BM25 score is the most negative:

```text
3  2026-07-22 20:38:07  hello again hello
1  2026-07-22 20:38:07  hello world
```

## What the migration does

`db.py` creates an external-content FTS5 table (`content='notes'`, `content_rowid='id'`) plus three triggers that keep the index in sync on insert, update and delete. Rows written before the migration are backfilled with a single `'rebuild'` command.

The backfill guard is the part worth reading: `SELECT count(*) FROM notes_fts` on an external-content table counts the content table, so it reports the right number even when the index is empty and can never detect a missing backfill. The guard therefore checks `sqlite_master` for the `notes_fts` table before creating it and rebuilds only on the run that created it.
