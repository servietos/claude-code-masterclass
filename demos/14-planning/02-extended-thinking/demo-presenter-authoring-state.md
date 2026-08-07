---
presents: demo-authoring-state.md
budget: 4 min
beats: 4
---

# Present: Capture a Planning Session in STATE.md

STATE.md is dictated section by section, and its Done Criteria are commands rather than intentions. An empty Open Questions is the gate for leaving Plan Mode. Four beats: the dictated sections, the executable pair, the ban on invented decisions, the update rule.

------

## Beats

### Beat 1: you dictate the sections, Claude fills only the content (1 min)

**Open:** [Dictate the Statefile Sections](demo-authoring-state.md#dictate-the-statefile-sections) · [Canonical Sections](readme.md#canonical-sections)
**Say:** The structure is yours to fix and only the content is Claude's to supply. Ask for a statefile in the abstract and every session returns a differently organised essay.

```text
Rewrite STATE.md in the project root with:

## Goal
Add FTS5 full-text search to notes-cli.

## Decisions
[everything we just locked in: FTS5, the ranking expression we chose, no external deps beyond
Typer, non-destructive migration, the search command surface]
```

**Result:** the headings came back literally, in the dictated order, in [`notes-cli-solution/STATE.md`](notes-cli-solution/STATE.md)

```markdown
# Notes CLI Project State

## Goal
Add FTS5 full-text search to notes-cli.

## Decisions
- Full-text search on the note body only
- Use SQLite FTS5; no external dependencies beyond Typer
```

**Gotcha:** the bracketed text is an instruction, not content to copy; a Goal that needs a paragraph is describing two features.

### Beat 2: Status and Next Action make the file executable (1 min)

**Open:** [`notes-cli/STATE.md`](notes-cli/STATE.md) · the `Status` and `Next Action` sections
**Say:** A record of what was decided is a memo. What makes it executable is one named next step plus criteria that are commands rather than intentions.

```text
## Status
- [ ] FTS5 migration
...
## Next Action
FTS5 migration

## Done Criteria
- python notes.py search "hello" returns matching notes ranked by BM25
- python notes.py list still works and returns all notes
```

**Result:** Next Action came back as one line, and Done Criteria as runnable commands, in [`notes-cli-solution/STATE.md`](notes-cli-solution/STATE.md)

```markdown
## Next Action
None. The feature is complete; the next change starts a new planning session.

## Done Criteria
- `python notes.py search "hello"` returns matching notes ranked by BM25
- `python notes.py list` still works and returns all notes
- Existing seed notes survive the migration
```

**Gotcha:** "user can search notes by keyword" is an acceptance criterion; if Claude has to interpret whether a criterion is met, it is not specific enough.

### Beat 3: no invented decisions, and an empty Open Questions is the exit gate (1 min)

**Open:** [Verify the Decisions and Exit Plan Mode](demo-authoring-state.md#verify-the-decisions-and-exit-plan-mode) · [`notes-cli/STATE.md`](notes-cli/STATE.md) · the `Decisions` section
**Say:** A model asked to write up a conversation will fill its gaps, and a plausible filling is indistinguishable from an agreement once written down. So the file is checked against the transcript, not read for sense.

```text
## Open Questions
[empty]

Use the conversation we just had as the source of truth. Do not invent new decisions.
```

**Result:** the finished [`notes-cli-solution/STATE.md`](notes-cli-solution/STATE.md) ends on the heading with nothing under it

```markdown
## Open Questions
```

**Gotcha:** a question left open in the plan costs one more turn; the same question found in code costs everything built on top of it.

### Beat 4: a statefile stays true only if a rule keeps it updated (1 min)

**Open:** [The Update Discipline](readme.md#the-update-discipline) · `CLAUDE.md` (the learner adds it in the [notes-cli/](notes-cli/) starter, which ships none)
**Say:** Discipline you have to remember under deadline is not discipline. The read and the update belong in the project's own instructions, where every session inherits them.

```text
Read STATE.md before any non-trivial change. Update STATE.md after any non-trivial change.
```

**Result:** not shipped, and deliberately so. Neither the starter nor the solution folder carries a CLAUDE.md; the rule is the learner's to add.

**Gotcha:** one skipped update starts the drift, and a quietly stale statefile is worse than none, because the next session has no reason to doubt it.

## If the room asks

| Question | Answer |
|---|---|
| Is STATE.md a spec by another name? | No. A spec is the desired end state written once; STATE.md is the current state, updated after every session. |
| Who is the reader? | The next Claude invocation, which resumes without re-deriving the plan. |
| What if Claude invents a decision nobody made? | Reject that bullet and point at the transcript; the source-of-truth clause exists because the model fills gaps plausibly. |
| Can I exit Plan Mode with one open question? | Not in this pattern. One more constraint turn is cheaper than discovering the gap in code. |
| Where do the Status items come from? | The work packages; the next demo splits this file into three packages whose names match these checkboxes. |
