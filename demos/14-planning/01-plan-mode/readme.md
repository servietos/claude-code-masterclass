# Enter Plan Mode for Complex Tasks

Plan Mode is a harness constraint that prevents Claude from writing or editing files. It is not a different model; it is a tool-use restriction applied to Edit, Write, and shell write operations. Claude can still read files, run read-only commands, and reason across the full conversation.

Activate with `Shift+Tab` until the input pill reads `plan mode on`. Exit the same way.

## Why Plan Mode Changes Output Quality

Without a write restriction, Claude resolves ambiguity silently: it picks the most likely interpretation and starts producing code. That guess is free to make and expensive to undo.

With Plan Mode active, the model cannot act, so its behavior shifts. It asks clarifying questions it would otherwise skip. It proposes structure before filling it in. It surfaces assumptions as explicit flags rather than implicit choices in the first committed file.

Plan Mode makes Claude's assumptions visible before they become code. That is its only purpose, and it is sufficient.

## The Vague-Brief Failure Mode

Submitting an under-specified request in Plan Mode produces a question list, not a plan. That is the intended outcome.

```text
Prompt: I want to add search to notes-cli.
```

Claude responds with questions: What kind of search? Full-text or tag-based? Body only or metadata too? SQLite FTS5 or an external library?

That question list is the planning session's first deliverable.

The failure mode this replaces: sending the same prompt outside Plan Mode. Claude starts coding immediately, picks a schema and a query strategy, and two hours later you discover it made the wrong choice on both.

## The Constraint-First Pattern

Constraints submitted after Claude has proposed a plan arrive as negotiation. Constraints submitted before the ask arrive as specification. The order is not cosmetic; it changes what Claude plans against.

```text
Constraints (non-negotiable):
  1. Full-text search on the note body only.
  2. Use SQLite FTS5. No external dependencies beyond Typer.
  3. Results ranked by BM25 relevance (FTS5 native).
  4. Existing notes.db rows must survive. No destructive migration.
  5. New command: search "query" (prints matching notes ranked by relevance).

Revise the plan. Tell me what is still ambiguous.
```

Constraint ratchets do two things: they lock decisions that are already made and they expose what is still open. The last sentence matters; "tell me what is still ambiguous" invites Claude to identify its own gaps rather than hide them.

## Iterating the Plan

A single Plan Mode turn rarely produces a complete plan. Two or three turns is the expected pattern.

Turn 1: submit the feature request. Claude produces a provisional plan with an open questions section. Turn 2: answer the questions with constraint ratchets. Claude revises the plan and narrows ambiguity.

Turn 3 (if needed): close remaining open questions with one final constraint batch.

If the planning session requires more than five turns, the brief is fundamentally unclear. The right move is to stop, clarify what you actually know, and restart with that clarity written down before you submit.

## When to Use Plan Mode and When to Skip It

Use Plan Mode for: new features with architectural choices, tasks spanning multiple files, anything a senior engineer would spec before coding.

Skip it for: one-file edits with obvious scope, bug fixes with a clear reproduction, documentation updates.

The cost of entering Plan Mode on a simple task is one extra turn. The cost of skipping it on a complex task is often several hours of reversal.

## Demo

See [demo-plan-mode-constraint-ratchet.md](demo-plan-mode-constraint-ratchet.md). The starter project is [notes-cli/](notes-cli/); the finished, runnable reference is [notes-cli-solution/](notes-cli-solution/).

## Helpful Claude Slash Commands

| Command | Usage |
|---|---|
| `/model` | Switch to a stronger model before a planning session; plan quality is where model choice pays off most |
| `/compact` | Compress conversation history when a long planning iteration is filling the context window |
| `/clear` | Drop a planning session that went sideways and restart from a written brief |

## Key Topics Covered in This Module

- [Claude Code overview](https://code.claude.com/docs/en/overview): entry point for harness architecture and tool-use model
- [Claude Code memory (CLAUDE.md)](https://code.claude.com/docs/en/memory): where to encode STATE.md rules and planning discipline
- [Extended thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking): budgeted reasoning chains and token cost guidance
