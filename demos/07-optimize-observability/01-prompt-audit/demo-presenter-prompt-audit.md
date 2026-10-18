---
presents: demo-prompt-audit.md
budget: 4 min
beats: 3
---

# Present: Audit a Harness for Dated Instructions

Instructions written for an older model waste tokens, and the current model follows them literally and over-applies them. Three beats: the harness-wide audit, facts versus judgement in the report, and the applied diff.

------

## Beats

### Beat 1: One command reads the whole harness and changes nothing (1.5 min)

**Open:** [`CLAUDE.md`](prompt-audit/CLAUDE.md) · [Part A: Audit the Whole Harness](demo-prompt-audit.md#part-a-audit-the-whole-harness)
**Say:** Every line in this file was reasonable for the model it was written against. The audit judges it against the model you run today, and it states that target model before it reads anything.

```text
/doctor prompt-audit .
```

**Result:** [`audit-report.md`](prompt-audit-solution/audit-report.md), a findings table and a proposed diff across four files, nothing applied

```text
- **Target model:** `claude-haiku-5-5`, the model running this audit. The request names none, and `CLAUDE.md`'s `claude-3-5-sonnet` is a finding to remove.

**Counts:** Group 1 (dated prompt text): 13. Group 2 (brittle config, stale facts, conflicts): 7. Group 3 (tool descriptions): 1. Group 4 (request config and architecture): not applicable, because there is no request-building code and `src/orders.ts` is plain arithmetic. The sub-agent roster has one agent, so there is nothing to merge.
```

**Gotcha:** without the `.` the audit also reads everything under `~/.claude/`, and on a presenter laptop that is your whole personal harness on the projector.

### Beat 2: The top of the report is facts you can check (1 min)

**Open:** [Part B: Separate Facts from Judgement](demo-prompt-audit.md#part-b-separate-facts-from-judgement) · [`package.json`](prompt-audit/package.json)
**Say:** A missing file or a missing script is not an opinion about prompting. Verify one of those rows live, and the room trusts the rest of the report for the right reason.

```text
! cat package.json
```

**Result:** rows 1 to 3 of [`audit-report.md`](prompt-audit-solution/audit-report.md), all high confidence

```markdown
| 1 | CLAUDE.md:11 | `Read docs/architecture.md before touching anything in src/.` | 2 volatile path; `docs/` absent | High | remove |
| 2 | CLAUDE.md:9 | `npm run typecheck`; scripts are only `test` and `lint` | 2 volatile command | High | rewrite (with #5) |
| 3 | CLAUDE.md:15 | `Always write tests with Jest.` | 2 conflict with rules/testing.md and package.json | High | rewrite |
```

**Gotcha:** the `/deploy-staging` line sits in the report's `Flags` section, outside the table, because the command may live in a user-level folder the audit did not read; absence in the project is not proof.

### Beat 3: Six lines of pressure become one rule (1.5 min)

**Open:** [Part C: Apply the Diff](demo-prompt-audit.md#part-c-apply-the-diff) · [`CLAUDE.md` after](prompt-audit-solution/CLAUDE.md)
**Say:** Caps, "take a deep breath" and "do not be lazy" carried no rule, and the one real rule inside them named a script that does not exist. What survives is the check the project can actually run.

```text
Apply the proposed diff from the audit. Apply every hunk; leave the flag items as they are.
```

**Result:** the `Workflow` section of [`CLAUDE.md`](prompt-audit-solution/CLAUDE.md), against three paragraphs in the starter

```markdown
Before every commit run `npm run lint`.
```

**Gotcha:** the deploy line was rewritten to keep its purpose, because waiting for the smoke test is still a live purpose once the claude-3-5-sonnet excuse is gone.

## If the room asks

| Question | Answer |
|---|---|
| Is this caveman compression again? | No. Caveman keeps every rule and cuts the wrapper; the audit decides which rules should exist. Audit first, then compress what survives. |
| Will my run show the same findings? | No. Counts and wording vary; the missing files, the missing script and the Jest contradiction are facts every run finds. |
| Which version do I need? | Claude Code v2.1.283 or later, with the bundled `/claude-api` skill enabled. |
