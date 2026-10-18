# Audit a Harness for Dated Instructions

Audit a small invoice-service harness with `/doctor prompt-audit`, check the high-confidence findings against the repository before trusting them, apply the proposed diff, and re-audit until nothing reaches the diff. Budget 45 minutes.

A harness collects instructions the way a house collects boxes: each one made sense when it was packed. This one carries shouting, step scripts, a word cap, the name of a retired model, a command that does not exist and a file that was renamed. You will find all of it with one command, learn which findings you can prove from the shell and which are judgement, and finish with a harness whose second audit proposes nothing. The deliverables are four files you write: `pointers.md`, `audit-report.md`, `verification.md` and `reaudit.md`.

Each step follows the same pattern:

- **Overview:** what this step achieves
- **Research / Planning / Discussion:** an open prompt to reason through the problem before acting
- **Finding:** what to read and evaluate in Claude's response before moving on
- **Recipe:** a complete prompt you can use as-is or adapt from your own findings
- **Expected Outcome:** observable artefacts that confirm success

The teaching behind this lab is in [Audit the Harness for Dated Instructions](../../demos/07-optimize-observability/01-prompt-audit/readme.md).

---

## Where to Open Claude Code

The audit reads `CLAUDE.md` and `.claude/` from the directory you launch in, so open Claude Code inside the lab project. A session opened at the repo root audits this repo's own harness and never sees the starter. The command needs Claude Code v2.1.283 or later and the bundled `/claude-api` skill turned on.

```bash
cd labs/07-optimize-observability/audit-dated-instructions
claude
```

If you start Claude Code with the Claude Terminal extension, it opens in the VS Code workspace folder, so open `audit-dated-instructions` as the workspace folder first.

---

## Running the Lab Starter

The starter is a complete small harness: `CLAUDE.md`, one rule, one agent, one command, one skill, a three-line `docs/`, a `scripts/smoke.sh` and a tiny `src/`. It contains no audit report and no re-audit record. Install the dependencies once, because the closing `/ship` run executes the tests. Time budget for the lab is 45 minutes.

```bash
npm install
```

A successful start is a Claude Code session whose prompt shows the `audit-dated-instructions` folder, and a folder holding `CLAUDE.md`, `package.json`, `docs/`, `scripts/`, `src/` and `.claude/` with `agents/`, `commands/`, `rules/` and `skills/` inside.

---

## Step 1: Map What the Harness Points At (6 minutes)

**Overview:** Most of the audit's top findings are claims about whether something exists. Collect those claims yourself first, so that Step 2's report has something to be checked against.

**Research / Planning / Discussion:**

```text
Read CLAUDE.md and every file under .claude/. List each place where an instruction points at something outside its own file: a script, an npm command, a document, another command, a test framework. For each, say which file mentions it and whether the target exists in this folder right now. Output a markdown table. Do not change any file.
```

**Finding:** A good table has one row per pointer and a yes or no for each, and the no rows are the interesting ones. Look for `npm run verify`, `docs/review-rules.md` and the test framework named in two different places. Push back if a row says "exists" without naming where Claude looked.

**Recipe:**

```text
Create pointers.md in this folder with the table you just produced: one row per pointer, columns file, pointer, exists. Mark each row yes or no from what is on disk, and add no commentary.
```

**Expected Outcome:** A `pointers.md` with a row for every pointer. Rows for `scripts/smoke.sh` read yes; rows for `npm run verify` and `docs/review-rules.md` read no. You will compare the audit against this table in Step 3.

---

## Step 2: Run the Audit and Save the Report (10 minutes)

**Overview:** The audit judges every instruction against a target model and produces a findings table plus a proposed diff, and it edits nothing. The `.` path keeps it on this folder; without a path it also reads everything under `~/.claude/`.

**Research / Planning / Discussion:**

```text
/doctor prompt-audit .
```

**Finding:** The report opens by stating its scope and its target model, and the target is the model running the audit. Read the table from the top: High rows are documented or verifiable, Medium rows are consistent observed behaviour, and Low rows appear under `Flags` and stay out of the diff. Check that the Money line (integer cents) and the `npm publish` prohibition are not proposed for removal; both carry a reason only the author knew. If either is proposed for removal, say so in the next prompt.

**Recipe:**

```text
Save the full audit report from the previous turn to audit-report.md in this folder: the assumptions, the findings table, the proposed diff and the flags, unchanged. Change no other file.
```

**Expected Outcome:** `audit-report.md` exists and holds the findings table, a proposed diff covering `CLAUDE.md`, the rule, the agent, the command and the skill, and a flags list. Counts differ from run to run; the missing `verify` script, the Jest and Vitest contradiction and the stale `docs/review-rules.md` reference appear in every run. No other file has changed.

---

## Step 3: Verify Two High Rows from the Shell (8 minutes)

**Overview:** A High row for a missing file or script is a claim about the disk, so you can prove it without asking a model. Verify two, one for a missing command and one for a contradiction, before you apply anything. The `!` prefix runs the line in your own shell and adds its output to the conversation, so the prompts in this step can quote it. Every line below works in bash and PowerShell.

Missing command: the audit says `npm run verify` has no script behind it.

```text
! npm run verify
```

Expected result: npm exits with an error that names the missing script `verify`. Then list what the project does define:

```text
! cat package.json
```

Expected result: `scripts` holds `test` and `lint` only.

Contradiction: the audit says `CLAUDE.md` and `.claude/rules/testing.md` disagree about the test framework.

```text
! git grep -n --untracked -i -E "jest|vitest" -- .
```

Expected result: `CLAUDE.md` and `package.json` name Vitest, `src/invoices.test.ts` imports from `vitest`, and `.claude/rules/testing.md` names Jest. The search also matches your own `audit-report.md` and `pointers.md` from Steps 1 and 2, and `package-lock.json` after `npm install`; those matches are expected. The disk sides with Vitest, so the rule is the stale file.

**Research / Planning / Discussion:**

```text
Open audit-report.md and pointers.md. For each High row, say whether my shell checks confirm it, and list any row in the report that my shell checks cannot settle, with the reason. Change no file.
```

**Finding:** Every High row about a missing path or script should be settled by `pointers.md` and the shell output. Rows that cannot be settled, such as "the word cap is obsolete", are judgement and belong to the Medium tier in spirit. A report whose High row you could not reproduce is a report to distrust for the remaining rows.

**Recipe:**

```text
Create verification.md in this folder with two sections. Section one: the claim from audit-report.md for the missing verify script, the command I ran, and what it returned. Section two: the claim for the Jest and Vitest contradiction, the command I ran, which file the disk supports, and which file is stale. Quote the shell output I saw in this session and invent none.
```

**Expected Outcome:** `verification.md` holds two sections, each with a claim, a command and a result that matches your terminal, and the second section names `.claude/rules/testing.md` as the stale file.

---

## Step 4: Audit One Skill with the API Entry Point (8 minutes)

**Overview:** Both entry points run the same procedure, but `/claude-api prompt-audit` leads with dated prompt text and API scaffolds, while `/doctor prompt-audit` leads with missing references and conflicts. A skill is mostly prompt text, so the second command shows the findings the first one ranks lower.

**Research / Planning / Discussion:**

```text
/claude-api prompt-audit .claude/skills/invoice-summary
```

**Finding:** Expect the scratchpad tag, the numbered STEP script, the word cap, the retired model name and the "hold all findings" instruction. Compare with the skill rows in `audit-report.md`: the two reports should agree on what is dated and may differ on order and wording. The `description` field carries many trigger phrases; the audit may flag the growing synonym list as Low confidence, which is a `flag` and stays out of the diff.

**Recipe:**

```text
Append a section titled Skill-only audit to audit-report.md. Under it, list each finding from the /claude-api prompt-audit run on .claude/skills/invoice-summary, and mark each one as also found by /doctor prompt-audit or found only here. Change no other file.
```

**Expected Outcome:** `audit-report.md` ends with a `Skill-only audit` section whose rows are each marked `also found` or `only here`. Most rows are `also found`; the section shows both entry points reach the same conclusions about the same file.

---

## Step 5: Apply the Diff and Re-audit (12 minutes)

**Overview:** The audit proposes and never edits. Apply the hunks, then audit the edited harness again, because the second report is the check that your removals did not leave a new stale reference behind.

**Research / Planning / Discussion:**

```text
Read the proposed diff in audit-report.md. For each hunk, say whether it removes an instruction or rewrites it, and whether the rewrite keeps the live purpose of the instruction (for example waiting for the smoke test). Name any hunk where a bare deletion would lose something the harness still needs. Change no file.
```

**Finding:** Two hunks need a judgement. The pressure around the smoke test in `.claude/commands/ship.md` has a live purpose, so the command should keep "run `scripts/smoke.sh` and wait for it" in plain words. The agent's reference to `docs/review-rules.md` should point at `docs/review-checklist.md`, where that content lives now, and the stale rule should be rewritten to say Vitest.

**Recipe:**

```text
Apply the proposed diff from audit-report.md. Apply every hunk. For the references the audit could not repair, use these: the review rules live in docs/review-checklist.md, the test framework is Vitest with explicit imports from vitest, and the verify step in CLAUDE.md becomes npm test. Leave the flag items and the Money and Publishing sections unchanged.
```

**Expected Outcome:** Five files change: `CLAUDE.md`, `.claude/rules/testing.md`, `.claude/agents/invoice-reviewer.md`, `.claude/commands/ship.md` and `.claude/skills/invoice-summary/SKILL.md`. The `Workflow` section of `CLAUDE.md` shrinks to one line:

```markdown
Before every commit run `npm test` and `npm run lint`.
```

Check the edits against the disk with a search for every stale token the report named:

```text
! git grep -n --untracked -i -E "jest|review-rules|npm run verify|claude-3|scratchpad" -- . ":!audit-report.md" ":!verification.md" ":!reaudit.md" ":!pointers.md"
```

Expected result: no output, because every stale token is gone from the harness files.

Run the same audit again on the edited harness:

```text
/doctor prompt-audit .
```

Read the result. If the diff still has hunks, apply them and run the audit once more; repeat until the diff is empty. The report may still list Low rows under `Flags`, and those are the items you chose to keep. Then record the outcome:

```text
Create reaudit.md in this folder. Record how many audit runs it took to reach an empty proposed diff, the count of findings in each run, and the flag items that remain with a one-line reason to keep each. Quote the last run's summary line exactly.
```

Expected result: `reaudit.md` states the number of runs, the findings per run falling to a diff with no hunks, and the remaining flags. The final run states that no finding reaches the diff.

---

## Wrap (1 minute)

You hold four files that were not there at the start (`pointers.md`, `audit-report.md`, `verification.md` and `reaudit.md`) and a harness whose five files state only what the current model needs. Run the `/ship` command once to confirm the rewritten harness still works:

```text
/ship
```

A successful end state: Claude runs `scripts/smoke.sh`, waits for the test run to finish, and answers ready or not ready in one sentence.
