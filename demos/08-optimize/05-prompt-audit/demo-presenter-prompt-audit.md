---
presents: demo-prompt-audit.md
budget: 5 min
beats: 5
---

# Present: Audit a Harness for Dated Instructions

Instructions written for an older model do not just waste tokens; the current model follows them literally and over-applies them. Five beats: the harness-wide audit, facts versus judgement in the report, a narrowed audit that goes deeper, the applied diff, and the re-audit that proposes nothing.

------

## Beats

### Beat 1: One command reads the whole harness and changes nothing (1 min)

**Open:** [`CLAUDE.md`](prompt-audit/CLAUDE.md) · [Part A: Audit the Whole Harness](demo-prompt-audit.md#part-a-audit-the-whole-harness)
**Say:** Every line in this file was reasonable for the model it was written against. The audit judges it against the model you run today, and it states that target model before it reads anything.

```text
/doctor prompt-audit .
```

**Result:** [`audit-report.md`](prompt-audit-solution/audit-report.md), 25 findings and a proposed diff across four files, nothing applied

```text
The target model is Claude Opus 5.5, the model running this audit, because nothing in the repo names one.

Counts: Group 1 has 14 findings, Group 2 has 7, Group 3 does not apply (no tool definitions), and Group 4 does not apply (`src/` has no request code; the one-agent roster has no redundancy).
```

**Gotcha:** without the `.` the audit also reads everything under `~/.claude/`, and on a presenter laptop that is your whole personal harness on the projector.

### Beat 2: The top of the report is facts you can check (1 min)

**Open:** [Part B: Separate Facts from Judgement](demo-prompt-audit.md#part-b-separate-facts-from-judgement) · [`package.json`](prompt-audit/package.json)
**Say:** A missing file or a missing script is not an opinion about prompting. Verify one of those rows live, and the room trusts the rest of the report for the right reason.

```text
! cat package.json
```

**Result:** rows 1 to 3 of [`audit-report.md`](prompt-audit-solution/audit-report.md), all high confidence

```text
| 1 | `CLAUDE.md:15` | "Always write tests with Jest" | G2 conflict / stale fact | `rules/testing.md:3` says Vitest, as do `package.json` (`vitest run`) and `orders.test.ts` | High | rewrite (proposed only) |
| 2 | `CLAUDE.md:11` | "`npm run typecheck`" | G2 volatile specific | `package.json` has no `typecheck` script | High | rewrite |
| 3 | `CLAUDE.md:13` | "Read docs/architecture.md" | G2 volatile specific | `docs/` does not exist | High | remove |
```

**Gotcha:** row 25, `/deploy-staging`, is only a flag because the command may live in a user-level folder the audit did not read; absence in the project is not proof.

### Beat 3: Narrow the scope and the audit reads deeper (1 min)

**Open:** [`SKILL.md`](prompt-audit/.claude/skills/release-notes/SKILL.md) · [Part C: Narrow the Audit to One Skill](demo-prompt-audit.md#part-c-narrow-the-audit-to-one-skill)
**Say:** A harness-wide pass spreads attention across every file. The same audit pointed at one skill found 11 findings in one file, including one the wide pass missed.

```text
/claude-api prompt-audit .claude/skills/release-notes
```

**Result:** [`audit-skill-report.md`](prompt-audit-solution/audit-skill-report.md)

```text
| 5 | SKILL.md:12 | `Read CHANGELOG.md.` | 2 volatile specifics | There is no `CHANGELOG.md` in the project. | High | rewrite (proposed only) |
| 6 | SKILL.md:11 | `git log --oneline v1.2.0..HEAD` | 2 volatile specifics | The repo has no `v1.2.0` tag. | High | rewrite (proposed only) |
```

**Gotcha:** it also lists what it kept (the role line, `Do not invent commits`, the Features/Fixes/Chores grouping); an audit that only says delete is the one to distrust.

### Beat 4: Six lines of pressure become one rule (1 min)

**Open:** [Part D: Apply the Diff](demo-prompt-audit.md#part-d-apply-the-diff) · [`CLAUDE.md` after](prompt-audit-solution/CLAUDE.md)
**Say:** Caps, "take a deep breath" and "do not be lazy" carried no rule, and the one real rule inside them named a script that does not exist. What survives is the check the project can actually run.

```text
Apply the proposed diff from the audit. Apply every hunk; leave the flag items as they are.
```

**Result:** the `Workflow` section of [`CLAUDE.md`](prompt-audit-solution/CLAUDE.md), against three paragraphs in the starter

```markdown
Before every commit run `npm run lint`.
```

**Gotcha:** the deploy line was rewritten, not deleted, because waiting for the smoke test is still a live purpose once the claude-3-5-sonnet excuse is gone.

### Beat 5: The re-audit is the finish line (1 min)

**Open:** [Part E: Re-Audit](demo-prompt-audit.md#part-e-re-audit)
**Say:** Removal is a hypothesis, and the edits themselves can introduce stale references. The same command on the edited harness decides when you are done.

```text
/doctor prompt-audit .
```

**Result:** [`re-audit-report.md`](prompt-audit-solution/re-audit-report.md)

```text
The surface is essentially clean. None of the dated patterns the starter had are left in the solution folder. No finding reaches medium or high confidence, so there is no proposed diff.
```

**Gotcha:** three low flags remain, and they are yours to decide; the missing `CHANGELOG.md` that was high in Beat 3 is now low because the command appends to it.

## If the room asks

| Question | Answer |
|---|---|
| Is this caveman compression again? | No. Caveman keeps every rule and cuts the wrapper; the audit decides which rules should exist. Audit first, then compress what survives. |
| What is the difference between `/doctor prompt-audit` and `/claude-api prompt-audit`? | Same audit from the bundled `/claude-api` skill. `/doctor` is the Claude Code entry point and leads with stale paths, stale commands and contradicting files. |
| Will my run show 25 findings? | No. Counts and wording vary; the missing files, the missing script and the Jest contradiction are facts every run finds. |
| Did any file change before Part D? | No. The audit proposes a diff and applies nothing until asked. |
| When do I run it again? | At every model release, since a line load-bearing on one generation is cruft on the next. |
| Which version do I need? | Claude Code v2.1.283 or later, with the bundled `/claude-api` skill enabled. |
