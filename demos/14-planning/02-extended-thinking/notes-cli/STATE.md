# Notes CLI Project State

## Goal
Add FTS5 full-text search to notes-cli.

## Decisions
- Full-text search on the note body only
- Use SQLite FTS5; no external dependencies beyond Typer
- Non-destructive migration; existing notes.db rows must survive
- New command: `search "query"` prints matching notes ranked by relevance

## Status
- [x] Starter scaffolded
- [x] Plan produced and constraints locked
- [ ] Ranking approach decided
- [ ] FTS5 migration
- [ ] search command
- [ ] tests

## Next Action
Decide the ranking expression, then run the FTS5 migration.

## Done Criteria
- `python notes.py search "hello"` returns matching notes ranked by BM25
- `python notes.py list` still works and returns all notes
- Existing seed notes survive the migration

## Open Questions
- Ranking expression: `ORDER BY bm25(notes_fts) ASC` or `ORDER BY rank`?
