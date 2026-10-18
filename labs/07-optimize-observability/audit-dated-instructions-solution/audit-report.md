## Prompt audit: `labs/07-optimize-observability/audit-dated-instructions-solution`

**Assumptions (Step 0).** Scope is this folder's prompt surface: `CLAUDE.md`, `.claude/rules/testing.md`, `.claude/agents/invoice-reviewer.md`, `.claude/commands/ship.md`, `.claude/skills/invoice-summary/SKILL.md`, and `docs/review-checklist.md`, which the reviewer reads. Target model is `claude-haiku-5-5`, the model running this audit, since the repo has no migration notes and no model IDs. Skipped: the ancestor `CLAUDE.md` at the repo root (not named in the request), `pointers.md` and `scripts/smoke.sh` (not prompt text), and `src/` (no model calls, so Group 4 is not applicable). The folder is untracked (`??`), so there is no git history and no blame; direction comes from the repo's own contents. No files were changed.

**Highest-impact findings**

1. **Two retired-model fossils.** `ship.md:5` and `SKILL.md:20` both attribute their text to `claude-3-opus`. Each is a workaround for a model no longer in use.
2. **The testing rule contradicts the repo.** `.claude/rules/testing.md` says "Use Jest" and "rely on the global `describe`, `it` and `expect`". `package.json` has `vitest` and no `jest`, and `src/invoices.test.ts` imports from `'vitest'`.
3. **Two stale pointers.** The reviewer agent cites `docs/review-rules.md`, which does not exist (the file is `docs/review-checklist.md`). `CLAUDE.md` requires `npm run verify`, which is not in `package.json` scripts.

**Counts:** Group 1: 10 findings. Group 2: 3 findings, plus the stale `verify` fact on `CLAUDE.md:9`. Group 3: none; the reviewer's `description` is routing text and is kept. Group 4: not applicable (no request code), except one low flag. Sub-agent roster: one agent, nothing to merge.

### Findings

| # | Location | Pattern | Confidence | Action |
|---|---|---|---|---|
| 1 | `.claude/commands/ship.md:5` | 1d retired-model workaround + 1a pressure | High | rewrite |
| 2 | `.claude/skills/invoice-summary/SKILL.md:20` | 1d pinned retired model | High | remove |
| 3 | `.claude/skills/invoice-summary/SKILL.md:10-14` | 1b `<scratchpad>` scaffold (High); 1c STEP choreography (Medium) | High / Medium | rewrite |
| 4 | `CLAUDE.md:7` | 1b "think step by step", 1a "Do not be lazy" | High | remove |
| 5 | `CLAUDE.md:9` | 1a pressure + stale fact (`npm run verify` missing) | High | rewrite |
| 6 | `.claude/rules/testing.md:1-3` | Group 2 stale fact (Jest, globals) | High | rewrite |
| 7 | `.claude/agents/invoice-reviewer.md:9` | 1a "CRITICAL / be thorough" | High | rewrite |
| 8 | `.claude/agents/invoice-reviewer.md:11` | 1c grader vocabulary + 1a "if in doubt" | High | rewrite |
| 9 | `.claude/agents/invoice-reviewer.md:13` | Group 2 stale path | High | rewrite |
| 10 | `.claude/skills/invoice-summary/SKILL.md:16` | 1d update suppressor | Medium | remove |
| 11 | `.claude/skills/invoice-summary/SKILL.md:18` | 1e prohibitions with no provenance | Medium | rewrite |
| 12 | `CLAUDE.md:21` | 1f numeric word cap + 1d anti-formatting | Medium | rewrite |
| 13 | `.claude/skills/invoice-summary/SKILL.md:3` | Group 2 trigger-case enumeration | Medium | rewrite |

### Flags (no edit proposed)

- **F1, low, Group 4:** `invoice-summary` has the model sum amounts per customer. That is deterministic, and `src/invoices.ts` already exports `totalCents`. Consider a code step, with the model keeping the summary wording.
- **F2, low:** `SKILL.md:18` "Do not hallucinate" restates a trained default. The diff keeps it because the signal is weak.
- **F3, decision for you:** Finding 12 removes the 40-word cap. If the cap is a limit of the chat surface this assistant runs in, keep it and add the reason beside it.
- **F4, decision for you:** Finding 5 drops `npm run verify`. If a `verify` script is meant to exist, add it to `package.json` and restore the line.
- **F5, assumption:** Finding 9 assumes `docs/review-checklist.md` is the intended rules file. Confirm before applying.

### Proposed diff

```diff
--- a/.claude/commands/ship.md
+++ b/.claude/commands/ship.md
@@ -5 +5 @@ (finding 1)
-IMPORTANT!!! ALWAYS run `scripts/smoke.sh` first and WAIT for it to finish. This is a known issue with claude-3-opus: it sometimes reports done before the script returns, so NEVER skip the wait!!
+Run `scripts/smoke.sh` first and wait for it to finish.

--- a/.claude/skills/invoice-summary/SKILL.md
+++ b/.claude/skills/invoice-summary/SKILL.md
@@ -3 +3 @@ (finding 13)
-description: Summarise invoices. Use when the user says "invoice summary", "summarise invoices", "summarize invoices", "invoice totals", "total the invoices", "monthly invoice report", "invoice overview", "billing summary".
+description: Summarise invoices and their totals per customer. Use when the user asks for a summary, totals, a periodic report, or an overview of invoices.
@@ -10,5 +10,2 @@ (finding 3)
-STEP 1: Think step by step inside <scratchpad> tags before writing anything.
-STEP 2: Read every invoice in the file the user names.
-STEP 3: Total the amounts per customer.
-STEP 4: Write at most 80 words per customer.
-STEP 5: Output ONLY the summary, nothing else.
+Read every invoice in the file the user names and total the amounts per customer. Keep each customer's summary short, and reply with the summary only.
@@ -16 +13 @@ (finding 10)
-IMPORTANT: Hold all findings until the very end. Do not narrate. No interim updates.
@@ -18 +15 @@ (finding 11)
-Do not hallucinate. Do not invent invoices. Do not use emojis. Avoid marketing words.
+Do not hallucinate. Do not invent invoices. Write plain, factual prose.
@@ -20 +17 @@ (finding 2)
-This format was tuned for claude-3-opus, which padded its answers.

--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -7 +6 @@ (finding 4)
-IMPORTANT: You MUST think step by step before every answer. Be extremely thorough. Do not be lazy.
@@ -9 +8 @@ (finding 5)
-CRITICAL: NEVER skip the checks. Before every commit run `npm run verify` and `npm run lint`. Do not stop early.
+Before every commit run `npm run lint`.
@@ -21 +20 @@ (finding 12)
-Never use headers or bullet points in your replies. Keep every answer under 40 words.
+Keep replies short and answer only what was asked. Use headers or bullet points only when they help the reader scan the reply.

--- a/.claude/rules/testing.md
+++ b/.claude/rules/testing.md
@@ -3 +3 @@ (finding 6)
-Use Jest for every test. Rely on the global `describe`, `it` and `expect`.
+Use Vitest for every test. Import `describe`, `it` and `expect` from `vitest`.

--- a/.claude/agents/invoice-reviewer.md
+++ b/.claude/agents/invoice-reviewer.md
@@ -9 +9 @@ (finding 7)
-CRITICAL: Be thorough. Do not be lazy. Check every single line.
+Check every changed line.
@@ -11 +11 @@ (finding 8)
-You will be graded on how many issues you find, so if in doubt, flag it.
+Report an issue when the change breaks a rule in the review checklist.
@@ -13 +13 @@ (finding 9)
-Review the diff against the rules in docs/review-rules.md and report each issue as `file:line - problem`.
+Review the diff against the rules in docs/review-checklist.md and report each issue as `file:line - problem`.
```

Nothing was applied, and no command was run. Tell me which hunks to apply (or say "apply all"), and I'll apply them and check the result with `npm run lint` and `npm test`. The testing check would need your explicit request.

## Skill-only audit

Source: `/claude-api prompt-audit .claude/skills/invoice-summary`, run on `.claude/skills/invoice-summary/SKILL.md` alone, target `claude-haiku-5-5`. Each finding is matched to the `/doctor prompt-audit` finding above that covers the same location and pattern.

**Findings**

| # | Location | Finding | Found by |
|---|---|---|---|
| 1 | `SKILL.md:20` | Pinned retired model (`claude-3-opus`) | Also found by /doctor prompt-audit (finding 2) |
| 2 | `SKILL.md:10` | "Think step by step" inside `<scratchpad>` tags | Also found by /doctor prompt-audit (finding 3, lines 10-14) |
| 3 | `SKILL.md:11-14` | STEP choreography and 80-word cap | Also found by /doctor prompt-audit (finding 3, lines 10-14) |
| 4 | `SKILL.md:16` | Update suppressor ("Hold all findings", "No interim updates") | Also found by /doctor prompt-audit (finding 10) |
| 5 | `SKILL.md:18` | Style prohibitions with no provenance (emojis, marketing words) | Also found by /doctor prompt-audit (finding 11) |
| 6 | `SKILL.md:3` | Trigger-case enumeration in the description | Also found by /doctor prompt-audit (finding 13) |

**Flags**

| # | Location | Flag | Found by |
|---|---|---|---|
| F1 | `SKILL.md:13` vs `CLAUDE.md:21` | 80-word cap conflicts with the 40-word reply cap; no history to order them | Found only here |
| F2 | `SKILL.md:18` | "Do not hallucinate" restates a trained default (low) | Also found by /doctor prompt-audit (flag F2) |
| F3 | `SKILL.md:6-14` | Deterministic totals done by the model; `totalCents` already exists (low) | Also found by /doctor prompt-audit (flag F1) |

All six findings and two of the three flags also appear in the /doctor run. The 80-word vs 40-word conflict (F1) appears only in the /claude-api run, because the /doctor run looked at the 40-word cap in `CLAUDE.md` without comparing it to the skill's 80-word cap.
