# Capture a Planning Session in STATE.md

A statefile is dictated section by section: you name the headings and Claude fills only content the session actually produced. You rewrite STATE.md in the notes-cli starter with Goal, Decisions, Status, Next Action, Done Criteria and Open Questions, then check that every decision traces back to something said. You leave Plan Mode holding a statefile whose Done Criteria are runnable commands and whose Open Questions section is empty.

------

## Dictate the Statefile Sections

Run this in the [notes-cli/](notes-cli/) starter, still in Plan Mode after the constraint ratchet from topic 01 and the ranking decision from [demo-extended-thinking.md](demo-extended-thinking.md). Submit:

```text
Rewrite STATE.md in the project root with:

## Goal
Add FTS5 full-text search to notes-cli.

## Decisions
[everything we just locked in: FTS5, the ranking expression we chose, no external deps beyond
Typer, non-destructive migration, the search command surface]

## Status
- [ ] FTS5 migration
- [ ] search command
- [ ] tests

## Next Action
FTS5 migration

## Done Criteria
- python notes.py search "hello" returns matching notes ranked by BM25
- python notes.py list still works and returns all notes
- existing seed notes survive the migration

## Open Questions
[empty]

Use the conversation we just had as the source of truth. Do not invent new decisions.
```

## Verify the Decisions and Exit Plan Mode

Read the result before moving on: every bullet under Decisions must trace back to something said in the session, and Open Questions must be empty. Exit Plan Mode with `Shift+Tab` once both hold.

The finished statefile for this feature, with every Status box checked, is in [notes-cli-solution/STATE.md](notes-cli-solution/STATE.md).
