---
presents: demo-extended-thinking.md
budget: 4 min
beats: 4
---

# Present: Apply Extended Thinking to Hard Design Decisions

`ultrathink` is the one phrase the CLI actually matches. A deep turn is judged by its reasoning chain, not by the verdict. Four beats: the three real controls, the prompt shape, the chain, the question the starter leaves open.

------

## Beats

### Beat 1: three controls are real and the keyword ladder is not (1 min)

**Open:** [How to Control the Depth](readme.md#how-to-control-the-depth) · the control table
**Say:** Extended thinking already runs on every turn, so nothing here switches it on. The only question is how much depth one turn deserves.

```markdown
| Control | What it does |
|---|---|
| `ultrathink` anywhere in the prompt | Requests deeper reasoning for that one turn. The CLI matches the word and adds an in-context instruction |
| `/effort` (also the slider in `/model`, or the `--effort` flag) | Sets the reasoning effort level for the session on models that support it |
| `Alt+T` (`Option+T` on macOS) | Toggles extended thinking on or off |
```

**Result:** no file; the check is on the binary, verified against Claude Code 2.1.217, which matches `ultrathink` and contains no "think hard" keyword.

**Gotcha:** "think", "think hard" and "think step by step" pass through as ordinary prompt text; they shape the answer like any instruction but buy no reasoning.

### Beat 2: the prompt shape is what earns the depth (1 min)

**Open:** [The Prompt](demo-extended-thinking.md#the-prompt) · [`notes-cli/notes.py`](notes-cli/notes.py)
**Say:** Depth only pays on a question with somewhere to go: named alternatives, the counterintuitive fact stated up front, a deliverable fixed in advance.

```text
ultrathink about this:

FTS5 BM25 in SQLite is available via the bm25() function in a match expression,
but it returns negative values, where more negative means more relevant.

Compare two approaches for the ranking sort:
  A. ORDER BY bm25(notes_fts) ASC (ascending, so most-negative first)
  B. ORDER BY rank (the undocumented rank hidden column)

For each: write the SQL, explain the gotchas on a ~10k-row notes table, and recommend one.
```

**Result:** option A shipped verbatim in the `search` command of [`notes-cli-solution/notes.py`](notes-cli-solution/notes.py)

```python
        WHERE notes_fts MATCH ?
        ORDER BY bm25(notes_fts) ASC
```

**Gotcha:** point at the row count; "~10k rows" is what turns a preference question into a cost question.

### Beat 3: judge the chain, not the verdict (1 min)

**Open:** [What to Watch in the Response](demo-extended-thinking.md#what-to-watch-in-the-response) · [What to Look for in the Output](readme.md#what-to-look-for-in-the-output)
**Say:** The recommendation varies between runs, so it is the one part you cannot audit. The argument is auditable: quantified assumptions, and a losing option rejected for a stated reason.

```markdown
- Write both SQL variants with the full query, not just the ORDER BY clause
- Name the sign-convention issue on `bm25()`: negative values, so ASC is correct but counterintuitive
- Treat `rank` as undocumented and therefore risky to depend on in portable code
- Reject one option with a stated reason instead of a preference

If the block is two sentences and jumps straight to a recommendation, the question was easy enough to resolve in the first draft. Rephrase: name both alternatives explicitly, ask for predicted query plans, and add "explain why the other one loses".
```

**Result:** the rejection carried its reason into the Decisions bullet of [`notes-cli-solution/STATE.md`](notes-cli-solution/STATE.md)

```markdown
- ORDER BY bm25(notes_fts) ASC for ranking (bm25() returns negative values, so ASC puts the most relevant row first; the rank hidden column is undocumented and its sign convention is not portable)
```

**Gotcha:** a thin chain is feedback about the question, not about the model; rephrase it rather than re-running and hoping.

### Beat 4: the starter ships the question already open (1 min)

**Open:** [`notes-cli/STATE.md`](notes-cli/STATE.md) · the `Open Questions` entry
**Say:** One or two deep turns is a planning session's whole budget, so the target is chosen before the turn starts. A statefile with exactly one thing unresolved is that choice made explicit.

```markdown
## Done Criteria
- `python notes.py search "hello"` returns matching notes ranked by BM25
- `python notes.py list` still works and returns all notes
- Existing seed notes survive the migration

## Open Questions
- Ranking expression: `ORDER BY bm25(notes_fts) ASC` or `ORDER BY rank`?
```

**Result:** the deep turn banked; in [`notes-cli-solution/STATE.md`](notes-cli-solution/STATE.md) the box is checked and Open Questions is empty

```markdown
- [x] Ranking approach decided (deep reasoning turn)
...
## Open Questions
```

**Gotcha:** depth that closes no named question is thinking you paid for and cannot bank.

## If the room asks

| Question | Answer |
|---|---|
| Does "think hard" buy more than "think"? | Neither is a budget keyword. Only `ultrathink` is matched by the CLI. |
| How are thinking tokens billed? | As output tokens, with the ceiling at the model's max output tokens minus one. |
| Does `MAX_THINKING_TOKENS` always apply? | Only on fixed-budget models; on adaptive-reasoning models a nonzero budget is ignored and effort level is the control. |
| So is option A or option B correct? | The solution locks `ORDER BY bm25(notes_fts) ASC` because the sign convention is documented and `rank` is not. |
| What if the thinking block is short? | The question was easy enough for the first draft. Rephrase with explicit alternatives and ask which option loses and why. |
