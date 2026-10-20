# CLAUDE.md

Masterclass repo **Agentic Software Engineering with Claude Code**: 11 modules, numbered in learning order.

## Layout

```text
demos/NN-<module>/   module readme, pptx/, numbered topic folders (theory readme, demo and presenter guides, pristine starter beside its <starter>-solution/)
labs/NN-<module>/    lab guides and their starters
src/                 standalone runnable projects the modules reference
exam-prep/           CCA-F practice question bank
dashboard/           module progress dashboard
tasks/               lessons.md, todo.md
```

## Harness

Orchestration runs in the integrations-marketplace mods (`D:\git-projects\integrations-marketplace`), and the house rules in `~/.claude/CLAUDE.md` apply as they stand; this file repeats neither.

- `subagent-delegation-plugin`: routes work to the owning agent (owners in `.claude/rules/`), sends fact gathering to the Haiku fact-gatherer, bounds every brief, keeps the agent ledger.
- `learn-loop-plugin`: runs `claude-learn` once a session goes idle.
- `report-plugin`: starts a status cron when an agent or workflow runs long.
- `intent-guard-plugin`: holds destructive commands nobody asked for.
- `ask-check-plugin`: stops questions the conversation already settled and unrequested findings.
- `write-gate-plugin`: holds a writer's finish until the humanize and marketing-psychology passes ran.
- `harness-plugin`: guards this file's shape, halts a run on `AGENT_STOP`, redirects it with `STEER.md`; `fix-constitution` realigns the repo.

## Hard Rules

- **YOU MUST NOT overstep the task.** Scope is exactly the folders, files and artifacts the user's message names. A sibling tree (labs beside demos, a neighbouring module, a related doc, a slide deck) stays unread, uncompared and unchanged until the user names it, and every delegate brief carries the same scope. When adjacent work looks useful, offer it in one clause and stop.
- **Browser inspection** - always `chrome-devtools` MCP. Never Playwright for UI checks. If the MCP fails, fix it; do not fall back.
- Write clean code with no noise: no inline comments, no placeholder notes, no error handling in scripts unless asked. Exception: `.sh`, `.ps1` and hooks under `demos/` get one short comment above each line a reader cannot decode.
- No experimental or test files in the repo root.
- **YOU MUST NOT run Vitest or Playwright E2E unless the user explicitly asks in that message.** Authoring, editing and type-checking specs is always allowed; executing them is not. This covers `ng test`, `npm test`, `npx vitest`, `npx playwright test` and every wrapper around them, in the main thread and in every subagent. When a change needs test execution to be verified, say so and wait. Never run a suite to "just confirm" at the end of a task.
- Internal links are relative; anchors are `#heading-name`; every code fence declares a language.
- If a quality check fails, fix the cause. Never bypass with `--no-verify`.
- **Never write negative parallelism.** `X, nicht Y`, `nicht nur X sondern auch Y`, `X statt Y`, `not from`, `rather than`, `instead of`, `not just X but Y`. It reads as a fixed-it-for-you boast and is the most recognisable AI tell in this house's copy. State what is true and stop. Grep the finished text for it before saving.

## Working Method

- **Plan first** for anything non-trivial (3+ steps or an architectural decision): write it to `tasks/todo.md`, check in, then track progress there.
- **Verify before reporting done.** Run the check, show the command and its output. A claim is not a receipt.
- **Review `tasks/lessons.md`** at session start; `claude-learn`'s `instruction-audit` gate prunes it and this file.
- **Simplicity first**: minimal diff, root causes over patches, no rewrite to fix a typo.
- **Plan check-in** is the shape plus the decisions the user has NOT made, one line each. An adjacent surface you noticed is a clause in the reply, never a question in the plan.
- **Data receipts**: where the feature's output is DATA (a log, a history, an import, an export), the receipt is rows produced by real traffic, never a green build or a passing suite.
