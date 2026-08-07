# Search and Pin Notes by Tag

Finished reference for the [notes-cli/](../notes-cli/) starter: the tag-search-and-pinning feature that the Spec Kit and BMAD pipelines in [the topic readme](../readme.md) specify. Work through the starter with the frameworks, then compare your result against this folder.

What the pipeline's technical plan asked for and what ships here:

| Plan decision | Implementation |
|---|---|
| Tags in a normalised table plus a junction table, no JSON columns | `tags` and `note_tags` in `db.py` |
| `pinned` integer column on notes, default 0 | added by an idempotent `ALTER TABLE` guarded by `PRAGMA table_info` |
| Multi-tag AND semantics | `GROUP BY note_id HAVING COUNT(DISTINCT tag_id) = N` in the `search` command |
| List order | `ORDER BY pinned DESC, id DESC` |
| Existing rows survive | the migration only adds a column and two tables; an existing `notes.db` keeps every row |

## Run It

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python notes.py add "first note"
.venv/Scripts/python notes.py add "tagged note" -t work -t urgent
.venv/Scripts/python notes.py add "other note" -t work
.venv/Scripts/python notes.py pin 2
.venv/Scripts/python notes.py list
.venv/Scripts/python notes.py search -t work -t urgent
```

On macOS or Linux use `.venv/bin/python` instead of `.venv/Scripts/python`.

Expected output of `list` (the leading `*` marks a pinned note):

```text
* 2  2026-07-22 20:36:40  tagged note  [urgent, work]
  3  2026-07-22 20:36:40  other note  [work]
  1  2026-07-22 20:36:40  first note
```

`search -t work -t urgent` returns only note 2: AND semantics, not OR.

## Verified

Run end to end on Windows with Python 3.12 and `typer==0.27.0`. Copying a `notes.db` written by the untouched starter into this folder and running `list` proves the migration: the pre-existing rows come back unchanged, with `pinned` defaulted to 0.

`typer==0.12.5` (the previous pin) crashes with `TypeError: Parameter.make_metavar() missing 1 required positional argument` against current `click` releases, so both the starter and this folder pin `typer==0.27.0`.
