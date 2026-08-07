---
presents: demo-plan-mode-constraint-ratchet.md
budget: 4 min
beats: 4
---

# Present: Lock design decisions incrementally with Plan Mode

A question list is a planning deliverable, not a session that failed to start. Constraints sent before the ask are read as specification, not negotiation. Four beats: the vague brief, the ratchet, the auditable decisions, the stop rule.

------

## Beats

### Beat 1: a vague brief in Plan Mode returns questions, not code (1 min)

**Open:** [`notes-cli/notes.py`](notes-cli/notes.py) · [Part A: Vague Brief](demo-plan-mode-constraint-ratchet.md#part-a-vague-brief)
**Say:** Outside Plan Mode an under-specified request gets resolved silently, and that guess is free to make and expensive to undo. Removing the ability to write pushes the ambiguity back to whoever owns it.

```text
I want to add search to notes-cli.
```

**Result:** nothing written. A question list comes back covering search type, scope, dependencies and query semantics, and the starter's `notes.py` still ends at `list_notes`.

**Gotcha:** Plan Mode restricts Edit, Write and shell writes only; reads, greps and read-only commands still run.

### Beat 2: constraints before the ask arrive as specification (1 min)

**Open:** [Part B: Constraint Ratchet](demo-plan-mode-constraint-ratchet.md#part-b-constraint-ratchet) · [`notes-cli/db.py`](notes-cli/db.py)
**Say:** The same five lines read as negotiation after a plan exists and as specification before the ask. They do not narrow the solution, they clarify the problem.

```text
Constraints (non-negotiable):
  1. Full-text search on the note body only.
  2. Use SQLite FTS5. No external dependencies beyond Typer.
  3. Results ranked by BM25 relevance (FTS5 native).
  4. Existing notes.db rows must survive. No destructive migration.
  5. New command: search "query" (prints matching notes ranked by relevance).

Revise the plan. Tell me what is still ambiguous.
```

**Result:** constraints 2 and 4 are legible in [`notes-cli-solution/db.py`](notes-cli-solution/db.py), which the starter has nothing of

```diff
+    conn.execute("""
+        CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts
+        USING fts5(body, content='notes', content_rowid='id')
+    """)
...
+    conn.execute("INSERT INTO notes_fts(notes_fts) VALUES ('rebuild')")
     conn.commit()
     conn.close()
```

**Gotcha:** the closing sentence is load-bearing; "tell me what is still ambiguous" makes Claude name its own gaps instead of hiding them.

### Beat 3: the ratchet's output is auditable, one bullet per constraint (1 min)

**Open:** [`notes-cli-solution/STATE.md`](notes-cli-solution/STATE.md) · the `Decisions` section · [The Constraint-First Pattern](readme.md#the-constraint-first-pattern)
**Say:** A plan is worth locking only if a reader who was not in the conversation can check it against the brief. A bullet with no line behind it is a choice the model made for you.

```markdown
## Decisions
- Full-text search on the note body only
- SQLite FTS5; no external dependencies beyond Typer (pytest for tests)
- `ORDER BY bm25(notes_fts) ASC` for ranking (bm25() returns negative values, so ascending puts the most relevant first)
- Non-destructive migration: the `notes` table is untouched, the FTS index is external-content and rebuilt idempotently
- New command: `search "query"` prints matching notes ranked by relevance
```

**Result:** constraint 2 outlived the plan into [`notes-cli-solution/requirements.txt`](notes-cli-solution/requirements.txt), which gains only the test runner

```diff
 typer==0.27.0
+pytest==8.3.3
```

**Gotcha:** the ranking bullet is the one tracing to no constraint.

### Beat 4: more than five turns means the brief is broken, not the plan (1 min)

**Open:** [Iterating the Plan](readme.md#iterating-the-plan)
**Say:** Two or three turns each narrow the ambiguity measurably; past five they stop, because the missing clarity sits on your side of the conversation.

```markdown
A single Plan Mode turn rarely produces a complete plan. Two or three turns is the expected pattern.

Turn 1: submit the feature request. Claude produces a provisional plan with an open questions section. Turn 2: answer the questions with constraint ratchets. Claude revises the plan and narrows ambiguity.

Turn 3 (if needed): close remaining open questions with one final constraint batch.

If the planning session requires more than five turns, the brief is fundamentally unclear. The right move is to stop, clarify what you actually know, and restart with that clarity written down before you submit.
```

**Result:** this session closed inside the rule; [`notes-cli-solution/STATE.md`](notes-cli-solution/STATE.md) ends on an empty Open Questions

```markdown
## Next Action
None. The feature is complete.
...
## Open Questions
```

**Gotcha:** the stop rule is the beat people forget; past five turns you rewrite the brief, you do not run another turn.

## If the room asks

| Question | Answer |
|---|---|
| Is Plan Mode a different model? | No, a harness restriction on Edit, Write and shell writes. The model is unchanged. |
| Why two turns, not constraints first? | In real work send them first. The two-turn shape shows the room what Claude assumes when you do not tell it. |
| Do constraints not just limit what Claude can propose? | They remove decisions you had already made, which frees the turn for the ones you had not. |
| Where did constraints 3 and 5 land? | In [`notes-cli-solution/notes.py`](notes-cli-solution/notes.py): a `search` command ordered by `bm25(notes_fts) ASC`. |
| Do I need the venv and seeded notes? | Only to execute the result; the planning session just reads `db.py` and `notes.py`. |
