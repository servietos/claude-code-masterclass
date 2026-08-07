# Notes CLI: Project State

## Goal
Add tags and pinning to notes-cli so notes can be filtered by multiple tags with AND semantics and pinned notes sort to the top of `list`.

## Decisions
- Tags are normalised: `tags(id, name UNIQUE)` plus a `note_tags(note_id, tag_id)` junction table with a composite primary key. No JSON columns.
- Pinning is global per note: an integer `pinned` column on `notes`, default 0.
- `list` sorts by `pinned DESC, id DESC`; the printed line stays `id  created_at  body`.
- `--tag` on `list` is repeatable and means AND (a note must carry every named tag).
- Multi-tag AND uses `GROUP BY n.id HAVING COUNT(DISTINCT nt.tag_id) = N` (Option B): one parameterised statement covers any number of tags, and at CLI scale the cost difference is under a millisecond. Measured on 10k notes and 30k note_tags (SQLite 3.49.1, best of 50 runs, two tags): self-join 0.139 ms, INTERSECT 0.202 ms, GROUP BY HAVING 0.507 ms. Option B is the slowest of the three because its plan adds three temp b-trees (GROUP BY, count(DISTINCT), ORDER BY); switch to the self-join chain if the tag count is fixed and the table grows.
- Migration is non-destructive: `init_db()` runs `CREATE TABLE IF NOT EXISTS` plus a guarded `ALTER TABLE notes ADD COLUMN pinned` only when the column is absent. Existing rows keep their ids and bodies.
- Indexes: `idx_note_tags_tag ON note_tags(tag_id, note_id)` for tag lookup, `idx_notes_pinned ON notes(pinned DESC, id DESC)` for the default ordering.
- CLI surface: `tag add <id> <name>`, `tag remove <id> <name>`, `pin <id>`, `unpin <id>`, `list [--tag NAME]...`.
- No dependency beyond Typer; `sqlite3` comes from the stdlib.

## Status
- [x] Starter scaffolded
- [x] Schema migration written
- [x] Tag/pin commands implemented
- [x] List filter implemented
- [x] Done criteria validated

## Next Action
None. The feature is complete and every Done Criteria bullet passes.

## Done Criteria
- `python notes.py tag add 1 work` exits 0 and prints `tagged note 1 with work`.
- `python notes.py list --tag work --tag urgent` prints only notes carrying both tags.
- `python notes.py pin 1` followed by `python notes.py list` prints note 1 first, then the rest by id descending.
- `python notes.py unpin 1` followed by `python notes.py list` restores plain id-descending order.
- `python notes.py tag remove 1 urgent` removes the note from the `--tag work --tag urgent` result.
- The two seed notes created before the migration are still present with their original ids after the new schema is applied.
- `python -c "import sqlite3; print(sqlite3.connect('notes.db').execute('select name from sqlite_master where type=?', ('table',)).fetchall())"` lists `notes`, `tags` and `note_tags`.

## Open Questions
None.
