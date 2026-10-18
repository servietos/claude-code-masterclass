# Audit a Harness for Dated Instructions

A harness keeps every instruction written for the models it has outlived: shouting, step scripts, word caps, workarounds for retired models, and references to files that were renamed long ago. You run the prompt audit over a small harness, read which findings are verifiable facts and which are judgement, and apply the proposed diff.

------

Nothing to install. Work in [prompt-audit/](prompt-audit); the finished harness and all three reports are beside it in [prompt-audit-solution/](prompt-audit-solution).

## Part A: Audit the Whole Harness

Run the audit over the project. The `.` path keeps it on this folder; without a path it also reads everything under `~/.claude/`.

```text
/doctor prompt-audit .
```

The report opens with its assumptions, and its summary closes with the counts. The target model is the model that runs the audit, so the name in your report is the model you ran:

```text
- **Target model:** `claude-haiku-5-5`, the model running this audit. The request names none, and `CLAUDE.md`'s `claude-3-5-sonnet` is a finding to remove.

**Counts:** Group 1 (dated prompt text): 13. Group 2 (brittle config, stale facts, conflicts): 7. Group 3 (tool descriptions): 1. Group 4 (request config and architecture): not applicable, because there is no request-building code and `src/orders.ts` is plain arithmetic. The sub-agent roster has one agent, so there is nothing to merge.
```

Expected result: a findings table with one row per finding and a proposed diff covering four files, with no file changed on disk. The full report is [audit-report.md](prompt-audit-solution/audit-report.md); your counts will differ, but the missing files, the missing script and the Jest contradiction are facts every run finds.

## Part B: Separate Facts from Judgement

The report is ordered by confidence. The top rows are checkable against the repository, so verify one before trusting the rest:

| # | Location | Evidence | Why obsolete | Conf. |
|---|---|---|---|---|
| 1 | `CLAUDE.md:11` | "Read docs/architecture.md before touching anything in src/." | `docs/` does not exist | High |
| 2 | `CLAUDE.md:9` | "`npm run typecheck`" | `package.json` has no `typecheck` script | High |
| 3 | `CLAUDE.md:15` | "Always write tests with Jest" | `rules/testing.md:3` says Vitest, as do `package.json` (`vitest run`) and `orders.test.ts` | High |
| 15 | `.claude/commands/changelog.md:5` | "Use the /release-notes-v1 command" | The only definition is the `release-notes` skill | High |

Check row 2 from the Claude Code prompt; the `!` prefix runs it in your shell:

```text
! cat package.json
```

Expected result: `scripts` holds `test` and `lint` only, confirming row 2.

The rows below the facts are pattern matches, and the report's `Flags` section lists items that stay out of the diff. `/deploy-staging` is one of them: it may be a user-level command the audit did not read, so absence in the project is not proof.

## Part C: Apply the Diff

The report proposes and never edits. Apply the harness-wide diff from Part A in the same session:

```text
Apply the proposed diff from the audit. Apply every hunk; leave the flag items as they are.
```

Expected result: four files change and `.claude/rules/testing.md` does not. The CLAUDE.md `Workflow` section before and after:

```markdown
IMPORTANT: You MUST ALWAYS think step by step before answering ANY question. Take a deep breath first.

CRITICAL: NEVER skip the checks. Before every commit run `npm run typecheck` and `npm run lint`. Be thorough. Do not be lazy. Do not stop early.

Read docs/architecture.md before touching anything in src/.
```

```markdown
Before every commit run `npm run lint`.
```

The one real rule inside the pressure survives, and it names the script the project actually has.
