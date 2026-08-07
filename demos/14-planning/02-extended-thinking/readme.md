# Reason deeply with Extended Thinking and persist decisions in STATE.md

## Extended Thinking

Extended thinking is Claude reasoning before it answers. The reasoning appears in the transcript as a thinking block; the answer follows it. In Claude Code it is enabled by default, so the question is not how to switch it on but how much depth a given turn deserves.

Spend the depth on decisions that are genuinely architectural: comparing implementation approaches with non-obvious costs, checking whether a plan's assumptions are internally consistent, selecting a query strategy under mixed constraints. Explaining code, writing a test, or renaming a symbol does not need it.

### How to Control the Depth

Three controls do the work, and one popular myth does not.

| Control | What it does |
|---|---|
| `ultrathink` anywhere in the prompt | Requests deeper reasoning for that one turn. The CLI matches the word and adds an in-context instruction |
| `/effort` (also the slider in `/model`, or the `--effort` flag) | Sets the reasoning effort level for the session on models that support it |
| `Alt+T` (`Option+T` on macOS) | Toggles extended thinking on or off |

The myth is the keyword ladder. Phrases such as "think", "think hard", and "think step by step" are passed through as ordinary prompt text; they are not recognized as budget keywords. They still shape the answer the way any instruction does, but they do not buy more reasoning. Verified against Claude Code 2.1.217, whose binary matches `ultrathink` and contains no "think hard" keyword.

```text
ultrathink about this:

FTS5 BM25 in SQLite is available via the bm25() function in a match expression,
but it returns negative values, where more negative means more relevant.

Compare two approaches for the ranking sort:
  A. ORDER BY bm25(notes_fts) ASC (ascending, so most-negative first)
  B. ORDER BY rank (the undocumented rank hidden column)

For each: show the query, explain the gotchas, recommend one.
```

### What to Look for in the Output

The quality signal is the reasoning chain, not the conclusion. What the model recommends varies from run to run; how it got there is what you can audit. A useful chain considers trade-offs the quick answer would have skipped, quantifies assumptions with concrete numbers, and rejects alternatives with a stated reason rather than a preference.

If the chain is short and conclusory, the question was easy enough to resolve in the first draft. Rephrase with an explicit comparison structure: name the alternatives, ask for predicted query plans or cost estimates, and ask which one loses and why.

### Thinking Budget vs. Token Cost

Thinking tokens are billed as output tokens, and the budget ceiling is the model's max output tokens minus one. That is the whole cost argument: a deep turn on a decision you will live with for months is cheap, and the same depth on every turn is not.

On models with a fixed thinking budget, `MAX_THINKING_TOKENS` caps it. On adaptive-reasoning models a nonzero budget is ignored and the effort level is the control instead. The rule of thumb stays simple: one or two deep turns per planning session, on the hardest decision in the plan.

## Demo: Extended Thinking on the Hard Decision

See [demo-extended-thinking.md](demo-extended-thinking.md).

## STATE.md: The Rolling Handoff Document

STATE.md is not a spec. A spec describes the desired end state and is written once. STATE.md describes the current state: what has been decided, what is done, what comes next, and what is still open. It is written before work begins and updated after every meaningful session.

Its purpose is session continuity. Any future Claude invocation that reads STATE.md first can resume where the last one left off without re-deriving the whole plan.

### Canonical Sections

```markdown
# <Project> Project State

## Goal
[one sentence: the thing being built]

## Decisions
[bullet list of every locked-in choice: schema, query strategy, CLI surface, constraints]

## Status
- [x] Step completed
- [ ] Step remaining

## Next Action
[the single next concrete thing to do, specific enough for Claude to act on without asking]

## Done Criteria
[verifiable bullet list: commands you can run and outputs you can read]

## Open Questions
[anything still ambiguous, empty when the plan is locked]
```

### The Update Discipline

Add one rule to CLAUDE.md and enforce it without exceptions:

```text
Read STATE.md before any non-trivial change. Update STATE.md after any non-trivial change.
```

The update is minimal: flip a status checkbox, rewrite the Next Action line. If done consistently, the file is always accurate. One skipped update starts the drift that makes the file useless.

### Demo: Authoring STATE.md

See [demo-authoring-state.md](demo-authoring-state.md).

## Sub-Agent Decomposition

A sub-agent package is a unit of work that one Claude session can complete without further clarification. It has four required fields.

| Field | Description |
|---|---|
| Name | Short, lowercase, hyphenated (`schema-migration`) |
| Input | Files it may read and the STATE.md section governing it |
| Output | Files it creates or modifies and the contract it must satisfy |
| Depends on | Which other package must finish first, if any |

The contract is the critical part: a runnable command and expected output, not a description of intent. The contract is what you check mechanically after execution.

### Decomposition Rules

Each package targets one concern, not one file. Packages that can run in parallel have no declared dependency on each other. Each package's contract must be checkable without reading the source code. Aim for three to five packages total; more than seven means the decomposition is too fine-grained.

### Demo: Decomposing Into Independently Executable Work Packages

See [demo-work-package-decomposition.md](demo-work-package-decomposition.md).

## Done Criteria and the Self-Critique Loop

Done criteria are mechanically verifiable statements about what must be true when a package finishes. They are different from acceptance criteria.

Acceptance criteria describe user-visible outcomes: "User can search notes by keyword." Done criteria are specific enough for Claude to run and report unambiguously: "`python notes.py search hello` returns only notes containing `hello`, ranked by BM25 with the most relevant note first."

If Claude has to interpret whether a criterion is met, it is not specific enough.

### The Self-Critique Prompt

After execution, before declaring done, ask Claude to walk through each Done Criteria bullet and produce evidence rather than a verdict:

```text
Execute the three packages from STATE.md in dependency order. After each package finishes:
  1. Update STATE.md: flip the matching Status checkbox to [x] and update Next Action.
  2. Run the package's contract command and paste the output below.

When all three are done, self-critique:
  - Walk through every bullet in the Done Criteria section.
  - For each, run the check and report PASS or FAIL with the actual command output.
  - If anything fails, fix it, re-run, and update STATE.md.

Do not declare the feature complete until every Done Criteria bullet is PASS.
```

The PASS/FAIL structure is what you audit. If Claude produces evidence that all criteria pass, you verify a sample. If something is FAIL, the self-critique loop catches it before you declare the feature done.

## Starter and Solution Folders

Work in `notes-cli/`; the finished result is beside it in `notes-cli-solution/`.

## Helpful Claude Slash Commands

| Command | Usage |
|---|---|
| `/effort` | Raise or lower the reasoning effort level for the session before a hard planning turn |
| `/memory` | Open `CLAUDE.md` to add the STATE.md read and update rule once, so every session inherits it |
| `/cost` | Track token spend across a planning session, where thinking tokens are billed as output tokens |

## Key Topics Covered in This Module

- [Effort levels and ultrathink](https://code.claude.com/docs/en/model-config#adjust-effort-level): how reasoning depth is actually controlled in Claude Code
- [Extended thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking): thinking budgets and how thinking tokens are billed
- [Claude Code memory (CLAUDE.md)](https://code.claude.com/docs/en/memory): where to encode the STATE.md read and update rule
- [Reduce token usage](https://code.claude.com/docs/en/costs#reduce-token-usage): `MAX_THINKING_TOKENS`, effort levels, and subagent delegation
