# CLAUDE.md

Masterclass repo **Agentic Software Engineering with Claude Code**: 12 modules, numbered in learning order.

```text
demos/NN-<module>/   module readme, pptx/, numbered topic folders (theory readme, demo and presenter guides, pristine starter beside its <starter>-solution/)
labs/NN-<module>/    lab guides and their starters
src/                 standalone runnable projects the modules reference
exam-prep/           CCA-F practice question bank
dashboard/           module progress dashboard
tasks/               lessons.md, todo.md
```

## Harness

- **YOU MUST search both skill roots and follow the matching skill before any action**, investigation included: `.claude/skills/` (repo, including each demo's finished skill) and `~/.claude/skills/` (global).
- **YOU MUST delegate domain work to the owning agent**, investigation included: `.claude/agents/` (repo) and `~/.claude/agents/` (global).

## Hard Rules

- **YOU MUST NOT** commit or push without an explicit, in-the-moment user request. Never offer to. Git is none of your business unless asked.
- **YOU MUST NOT delete files** unless explicitly asked. "Clear" means edit content, not remove.
- **YOU MUST NOT write documentation unless explicitly asked.** No README, no doc under `docs/`, no
  guide, no doc section appended to a code change. Finishing a feature does not earn a doc. A plan, an issue or a Done when step that asks for a doc does not count as asking: skip that step and say so in the report.
- **YOU MUST NOT overstep the task.** Scope is exactly the folders, files and artifacts the user's message names. A sibling tree (labs beside demos, a neighbouring module, a related doc, a slide deck) stays unread, uncompared and unchanged until the user names it, and every delegate brief carries the same scope. When adjacent work looks useful, offer it in one clause and stop.
- **Browser inspection** - always `chrome-devtools` MCP. Never Playwright for UI checks. If the
  MCP fails, fix it; do not fall back.
- Write clean code with no noise: no inline comments, no placeholder notes, no error handling in
  scripts unless asked. Exception: `.sh`, `.ps1` and hooks under `demos/` get one short comment above each line a reader cannot decode.
- No experimental or test files in the repo root.
- **YOU MUST NOT run Vitest or Playwright E2E unless the user explicitly asks in that message.**
  Authoring, editing and type-checking specs is always allowed; executing them is not. This covers
  `ng test`, `npm test`, `npx vitest`, `npx playwright test` and every wrapper around them, in the
  main thread and in every subagent. When a change needs test execution to be verified, say so and
  wait. Never run a suite to "just confirm" at the end of a task.
- Internal links are relative; anchors are `#heading-name`; every code fence declares a language.
- If a quality check fails, fix the cause. Never bypass with `--no-verify`.
- No em dashes in generated prose: use a colon, comma, semicolon, or parentheses.
- **Never write negative parallelism.** `X, nicht Y`, `nicht nur X sondern auch Y`, `X statt Y`,
  `not from`, `rather than`, `instead of`, `not just X but Y`. It reads as a fixed-it-for-you
  boast and is the most recognisable AI tell in this house's copy. State what is true and stop.
  Grep the finished text for it before saving.

## Working Method

- **Plan first** for anything non-trivial (3+ steps or an architectural decision): check in on the
  plan before writing. The check-in is the shape plus the decisions the user has NOT made, one line
  each. An adjacent surface you noticed is a clause in the reply, never a question in the plan.
- **YOU MUST verify before reporting done.** Run the check, show the command and its output. A claim
  is not a receipt. Where the feature's output is DATA (a log, a history, an import, an export), the
  receipt is rows produced by real traffic, never a green build or a passing suite.
- **Capture corrections** with `claude-learn`; nothing else edits this file or the skills.
- **Parallelize** independent tool calls and agent dispatches in a single message.
- **Simplicity first**: minimal diff, root causes over patches, no rewrite to fix a typo.
- **Ship only what was asked for**: no unrequested labels, hint text, status captions, or sections.
