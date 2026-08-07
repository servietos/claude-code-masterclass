# Apply Extended Thinking to Hard Design Decisions

Extended thinking is on by default, `ultrathink` is the one phrase the CLI matches as a request for deeper reasoning on a single turn, and `/effort` raises the level for the whole session. You spend that one deep turn on the open BM25 ranking question in the notes-cli starter and judge the reasoning chain rather than the verdict. You end with the ranking decision moved out of Open Questions and into Decisions in STATE.md.

------

The [notes-cli/](notes-cli/) folder is the starting point for this demo. It contains the same app as topic 01 plus a pre-written `STATE.md` that captures the constraints locked during the Plan Mode session, with the ranking decision left open as the one remaining question. Open Claude Code inside it and follow the prompts below.

Press `Shift+Tab` until the input pill reads `plan mode on`. You are in Plan Mode with the FTS5 constraints locked. The open question is which ranking approach to use for BM25 results; spend the session's one deep-reasoning turn on it.

## The Prompt

Still in Plan Mode, submit:

```text
ultrathink about this:

FTS5 BM25 in SQLite is available via the bm25() function in a match expression,
but it returns negative values, where more negative means more relevant.

Compare two approaches for the ranking sort:
  A. ORDER BY bm25(notes_fts) ASC (ascending, so most-negative first)
  B. ORDER BY rank (the undocumented rank hidden column)

For each: write the SQL, explain the gotchas on a ~10k-row notes table, and recommend one.
```

## What to Watch in the Response

The thinking block appears before the final answer. Read it. The recommendation itself is model-dependent, so judge the reasoning rather than the verdict. A useful chain will:

- Write both SQL variants with the full query, not just the ORDER BY clause
- Name the sign-convention issue on `bm25()`: negative values, so ASC is correct but counterintuitive
- Treat `rank` as undocumented and therefore risky to depend on in portable code
- Reject one option with a stated reason instead of a preference

If the block is two sentences and jumps straight to a recommendation, the question was easy enough to resolve in the first draft. Rephrase: name both alternatives explicitly, ask for predicted query plans, and add "explain why the other one loses".

## What to Do With the Output

The recommendation from this turn becomes a locked decision. Move it out of Open Questions before authoring the rest of STATE.md:

```text
Move the ranking question from Open Questions into Decisions in STATE.md, written as the
expression you just recommended plus the one-line reason. Flip "Ranking approach decided" to [x].
```

That one line closes the last open architectural question before the statefile is finalized.

The completed reference version of this demo, with the migration, the ranked `search` command, tests, and a fully checked STATE.md, lives in [notes-cli-solution/](notes-cli-solution/).
