# Audit a Harness for Dated Instructions

A harness keeps every instruction written for the models it has outlived: shouting, step scripts, word caps, workarounds for retired models, and references to files that were renamed long ago. You run the prompt audit over a small harness, read which findings are verifiable facts and which are judgement, narrow the audit to one skill, apply the proposed diff, and re-audit until nothing reaches the diff. You end up with a harness of five files whose re-audit proposes no edits, plus the three reports that got it there.

------

Nothing to install. Work in [prompt-audit/](prompt-audit/); the finished harness and all three reports are beside it in [prompt-audit-solution/](prompt-audit-solution/).

```bash
cd demos/08-optimize/05-prompt-audit/prompt-audit
claude
```

## Demo Files

| File | What it represents |
|---|---|
| `CLAUDE.md` | Project instructions with caps emphasis, a step-by-step incantation, a word cap, a claude-3-5-sonnet workaround, and a Jest rule |
| `.claude/rules/testing.md` | A rule file that says Vitest, contradicting CLAUDE.md |
| `.claude/skills/release-notes/SKILL.md` | A skill with a `STEP 1 ... STEP 6` script, a `<scratchpad>` instruction, a pinned tag and nine trigger synonyms |
| `.claude/agents/order-reviewer.md` | A subagent told it is graded on how many issues it finds |
| `.claude/commands/changelog.md` | A command that calls `/release-notes-v1`, which does not exist |
| `package.json`, `src/` | The project the harness describes: Vitest, a `lint` script, no `typecheck` script, no `docs/` folder |

## Part A: Audit the Whole Harness

Run the audit over the project. The `.` path keeps it on this folder; without a path it also reads everything under `~/.claude/`.

```text
/doctor prompt-audit .
```

The report opens with its assumptions, and its summary closes with the counts:

```text
**Assumptions.** Scope is the whole working directory: `CLAUDE.md`, `.claude/rules/testing.md`, `.claude/agents/order-reviewer.md`, `.claude/commands/changelog.md` and `.claude/skills/release-notes/SKILL.md`. Settings files and `~/.claude` were not read. The target model is Claude Opus 5.5, the model running this audit, because nothing in the repo names one. Provenance could not be checked because the files are untracked in git. Nothing was applied; the diff below is a proposal.

Counts: Group 1 has 14 findings, Group 2 has 7, Group 3 does not apply (no tool definitions), and Group 4 does not apply (`src/` has no request code; the one-agent roster has no redundancy).
```

Expected result: a findings table of 25 rows and a proposed diff covering four files, with no file changed on disk. The full report is [audit-report.md](prompt-audit-solution/audit-report.md). Your counts and wording will differ between runs; the missing files, the missing script and the Jest contradiction are facts, and every run finds them.

## Part B: Separate Facts from Judgement

The report is ordered by confidence. The top six rows are checkable against the repository, so verify one before trusting the rest:

| # | Location | Evidence | Why obsolete | Conf. |
|---|---|---|---|---|
| 1 | `CLAUDE.md:15` | "Always write tests with Jest" | `rules/testing.md:3` says Vitest, as do `package.json` (`vitest run`) and `orders.test.ts` | High |
| 2 | `CLAUDE.md:11` | "`npm run typecheck`" | `package.json` has no `typecheck` script | High |
| 3 | `CLAUDE.md:13` | "Read docs/architecture.md" | `docs/` does not exist | High |
| 5 | `.claude/commands/changelog.md:5` | "/release-notes-v1 command" | The only definition is the `release-notes` skill | High |

Check row 2 from the Claude Code prompt; the `!` prefix runs it in your shell:

```text
! cat package.json
```

Expected result: `scripts` holds `test` and `lint` only, confirming row 2. The rows below them are pattern matches against the target model (row 7 "think step by step", row 12 the 50-word cap, row 15 the no-narration rule), and the last three are `flag` items that stay out of the diff:

| # | Location | Evidence | Conf. | Action |
|---|---|---|---|---|
| 23 | `SKILL.md:19` | "Do not hallucinate." | Low | flag |
| 24 | `CLAUDE.md:3`, `order-reviewer.md:7` | "You are a helpful assistant." | Low | flag |
| 25 | `CLAUDE.md:25` | "/deploy-staging" | Low | flag |

Row 25 is low because `/deploy-staging` may be a user-level command the audit did not read, so absence in the project is not proof.

## Part C: Narrow the Audit to One Skill

A harness-wide pass spreads its attention across every file. Pointing the same audit at one skill reads it line by line:

```text
/claude-api prompt-audit .claude/skills/release-notes
```

Expected result: 11 findings for one file, including one the harness-wide pass missed. The full report is [audit-skill-report.md](prompt-audit-solution/audit-skill-report.md).

```text
| 2 | SKILL.md:10 | `Think step by step inside <scratchpad> tags` | 1b scaffold replaced by API feature | Thinking is always on in Opus 5.5 and depth is set by `effort`. Asking for reasoning in the output can trigger a `reasoning_extraction` refusal. | High | replace-with-API-feature (`effort` frontmatter if wanted) |
| 5 | SKILL.md:12 | `Read CHANGELOG.md.` | 2 volatile specifics | There is no `CHANGELOG.md` in the project. | High | rewrite (proposed only) |
| 6 | SKILL.md:11 | `git log --oneline v1.2.0..HEAD` | 2 volatile specifics | The repo has no `v1.2.0` tag. | High | rewrite (proposed only) |
```

It also lists what it kept: the one-line role statement, `Do not invent commits` as a real constraint, and the Features/Fixes/Chores grouping as the author's own format.

## Part D: Apply the Diff

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

The deploy rule shows the other shape of a fix, a rewrite that keeps the live purpose instead of deleting the line:

```markdown
To ship a change, run /deploy-staging and wait for the smoke test to pass before reporting it shipped.
```

## Part E: Re-Audit

Run the same command on the edited harness:

```text
/doctor prompt-audit .
```

Expected result: no proposed diff, and three low-confidence flags. The full report is [re-audit-report.md](prompt-audit-solution/re-audit-report.md).

```text
The surface is essentially clean. None of the dated patterns the starter had are left in the solution folder. No finding reaches medium or high confidence, so there is no proposed diff.
```

| Location | Evidence | Confidence | Action |
|---|---|---|---|
| `CLAUDE.md:19` | "run /deploy-staging and wait for the smoke test" | Low | flag: add the command to the project or drop the section |
| `.claude/commands/changelog.md:5`, `.claude/skills/release-notes/SKILL.md:10` | "Read CHANGELOG.md first" | Low | flag |
| `.claude/skills/release-notes/SKILL.md:12` | "Do not hallucinate." | Low | flag |

The missing `CHANGELOG.md` that Part C rated high is now a low flag: the command appends to that file, so the audit reads it as not created yet rather than stale. Deciding which flags to act on stays with you.
