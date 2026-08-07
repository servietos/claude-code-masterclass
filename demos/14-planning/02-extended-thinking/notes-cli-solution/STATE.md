# Notes CLI Project State

## Goal
Add FTS5 full-text search to notes-cli.

## Decisions
- Full-text search on the note body only
- Use SQLite FTS5; no external dependencies beyond Typer
- ORDER BY bm25(notes_fts) ASC for ranking (bm25() returns negative values, so ASC puts the most relevant row first; the rank hidden column is undocumented and its sign convention is not portable)
- External-content FTS5 table (content='notes', content_rowid='id') kept in sync by insert, update and delete triggers
- Non-destructive migration: the rebuild runs once, only when notes_fts did not exist yet
- New command: `search "query"` prints matching notes ranked by relevance

## Status
- [x] Starter scaffolded
- [x] Plan produced and constraints locked
- [x] Ranking approach decided (deep reasoning turn)
- [x] FTS5 migration
- [x] search command
- [x] tests

## Next Action
None. The feature is complete; the next change starts a new planning session.

## Done Criteria
- `python notes.py search "hello"` returns matching notes ranked by BM25
- `python notes.py list` still works and returns all notes
- Existing seed notes survive the migration
- `python test_notes.py` prints three PASS lines and exits 0

## Open Questions
