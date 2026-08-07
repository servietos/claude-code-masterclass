# Notes CLI: Project State

## Goal
Add FTS5 full-text search to notes-cli.

## Decisions
- Full-text search on the note body only
- SQLite FTS5; no external dependencies beyond Typer (pytest for tests)
- `ORDER BY bm25(notes_fts) ASC` for ranking (bm25() returns negative values, so ascending puts the most relevant first)
- Non-destructive migration: the `notes` table is untouched, the FTS index is external-content and rebuilt idempotently
- New command: `search "query"` prints matching notes ranked by relevance

## Status
- [x] FTS5 migration
- [x] search command
- [x] tests

## Next Action
None. The feature is complete.

## Done Criteria
- `python notes.py search "hello"` returns matching notes ranked by BM25
- `python notes.py list` still works and returns all notes
- Existing seed notes survive the migration

## Open Questions
