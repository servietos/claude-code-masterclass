## Prompt audit: `prompt-audit-solution`

**Assumptions.** Scope is the whole working directory: `CLAUDE.md`, `.claude/rules/testing.md`, `.claude/agents/order-reviewer.md`, `.claude/commands/changelog.md` and `.claude/skills/release-notes/SKILL.md`. Settings files and `~/.claude` were not read. The target model is Claude Opus 5.5, the model running this audit, because nothing in the repo names one. Provenance could not be checked because the files are untracked in git. Nothing was applied; the diff below is a proposal.

**Summary.** The biggest problems:
- `CLAUDE.md` requires Jest, but the project and the rule file both use Vitest.
- Four references point at things that don't exist: `docs/architecture.md`, `docs/review-checklist.md`, `npm run typecheck` and `/release-notes-v1`.
- The release-notes skill is a stack of workarounds from the claude-3 era: a scratchpad, word caps, a no-narration rule and a pinned-model note.

Counts: Group 1 has 14 findings, Group 2 has 7, Group 3 does not apply (no tool definitions), and Group 4 does not apply (`src/` has no request code; the one-agent roster has no redundancy).

### Findings

| # | Location | Evidence | Pattern | Why obsolete | Conf. | Action |
|---|---|---|---|---|---|---|
| 1 | `CLAUDE.md:15` | "Always write tests with Jest" | G2 conflict / stale fact | `rules/testing.md:3` says Vitest, as do `package.json` (`vitest run`) and `orders.test.ts` | High | rewrite (proposed only) |
| 2 | `CLAUDE.md:11` | "`npm run typecheck`" | G2 volatile specific | `package.json` has no `typecheck` script | High | rewrite |
| 3 | `CLAUDE.md:13` | "Read docs/architecture.md" | G2 volatile specific | `docs/` does not exist | High | remove |
| 4 | `.claude/agents/order-reviewer.md:13` | "docs/review-checklist.md" | G2 volatile specific | `docs/` does not exist | High | rewrite |
| 5 | `.claude/commands/changelog.md:5` | "/release-notes-v1 command" | G2 volatile specific | The only definition is the `release-notes` skill | High | rewrite |
| 6 | `SKILL.md:11` | "`v1.2.0..HEAD`" | G2 volatile specific | The repo's only tag is `1.0.0`; `changelog.md` already says "since the last tag" | High | rewrite |
| 7 | `CLAUDE.md:9` | "IMPORTANT: You MUST ALWAYS think step by step... Take a deep breath" | 1b scaffold | Thinking is always on in Opus 5.5; depth is set by `effort`, not prose | High | remove |
| 8 | `SKILL.md:10` | "Think step by step inside <scratchpad> tags" | 1b scaffold | Same as #7 | High | remove |
| 9 | `CLAUDE.md:11` | "CRITICAL: NEVER skip... Be thorough. Do not be lazy. Do not stop early." | 1a pressure | Current models are proactive; caps emphasis causes over-triggering | High | rewrite |
| 10 | `order-reviewer.md:9` | "CRITICAL: Be thorough. Do not be lazy. Do not stop early." | 1a pressure | Same as #9 | High | remove |
| 11 | `order-reviewer.md:11` | "If in doubt, flag it. You will be graded on how many issues you find." | 1a default-to + 1c grader vocabulary | Rewards volume, so it invites false positives | High | rewrite |
| 12 | `CLAUDE.md:19` | "Never use bullet points or headers... under 50 words" | 1d anti-formatting + 1f numeric cap | Opus 5.5 already formats sparingly; the caps starve answers | High | rewrite |
| 13 | `CLAUDE.md:21` | "Remember, you tend to be too verbose, so don't be too chatty." | 1a trait claim, 1c repetition | Duplicates line 19 in anxious form | High | remove |
| 14 | `CLAUDE.md:25` | "known issue with claude-3-5-sonnet... ALWAYS wait!!" | 1d model workaround | Written for a retired model | High | rewrite |
| 15 | `SKILL.md:17` | "Hold all findings until the very end. Do not narrate. No interim updates." | 1d update suppressor | Opus 5.5 under-narrates when this is present | High | remove |
| 16 | `SKILL.md:21` | "This format was tuned for claude-3-opus, which padded its answers." | 1d fossil / G2 history narrative | The tuning target is retired | High | remove |
| 17 | `changelog.md:5` | "IMPORTANT: ALWAYS read CHANGELOG.md first!!!" | 1a pressure | Emphasis with no reason | High | rewrite |
| 18 | `SKILL.md:10-16` | "STEP 1: ... STEP 6:" | 1c choreography | A script for a judgment task; only the order "log, then read" matters | Medium | rewrite |
| 19 | `SKILL.md:15` | "at most 100 words per group" | 1b/1f numeric cap | Caps are removed together with the choreography | Medium | remove |
| 20 | `SKILL.md:19` | "Do not use emojis. Do not use bold. Avoid marketing words." | 1e style prohibitions | No stated reason; better restated positively | Medium | rewrite |
| 21 | `SKILL.md:3` | Nine near-synonym trigger phrases | G2 trigger enumeration | Grows one phrase per miss and generalizes poorly | Medium | rewrite |
| 22 | `order-reviewer.md:3` | "You MUST use this agent for EVERY change, no matter how small." | G3/G2 trigger | "Every change" contradicts the agent's own `src/orders.ts` scope, so it triggers on unrelated edits | Medium | rewrite |
| 23 | `SKILL.md:19` | "Do not hallucinate." | 1c | Needs a re-test; no documented harm | Low | flag |
| 24 | `CLAUDE.md:3`, `order-reviewer.md:7` | "You are a helpful assistant." | 1d identity stub | The only product context `CLAUDE.md` gives; consider adding what the Orders Service does | Low | flag |
| 25 | `CLAUDE.md:25` | "/deploy-staging" | G2 | Not defined in the project; it may be user-level, so this isn't a contradiction | Low | flag |

### Proposed diff

Line 11 carries findings #2 and #9, so they share one hunk.

```diff
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -1,25 +1,19 @@
 # Orders Service
 
 You are a helpful assistant.
 
 ## Workflow
 
-IMPORTANT: You MUST ALWAYS think step by step before answering ANY question. Take a deep breath first.
-
-CRITICAL: NEVER skip the checks. Before every commit run `npm run typecheck` and `npm run lint`. Be thorough. Do not be lazy. Do not stop early.
-
-Read docs/architecture.md before touching anything in src/.
+Before every commit run `npm run lint`.
 
 ## Testing
 
-Always write tests with Jest. Put every test next to the file it covers as `<name>.test.ts`.
+Put every test next to the file it covers as `<name>.test.ts`.
 
 ## Style
 
-Never use bullet points or headers in your replies. Keep every answer under 50 words.
-
-Remember, you tend to be too verbose, so don't be too chatty.
+Keep replies to the length the question needs; use lists only for genuinely list-shaped content.
 
 ## Deploying
 
-To ship a change, run /deploy-staging and wait for the smoke test. This is a known issue with claude-3-5-sonnet: it sometimes forgets to wait, so ALWAYS wait!!
+To ship a change, run /deploy-staging and wait for the smoke test to pass before reporting it shipped.
```

```diff
--- a/.claude/agents/order-reviewer.md
+++ b/.claude/agents/order-reviewer.md
@@ -1,13 +1,11 @@
 ---
 name: order-reviewer
-description: Reviews changes to src/orders.ts. You MUST use this agent for EVERY change, no matter how small.
+description: Reviews changes to src/orders.ts. Use it after any edit to that file.
 tools: Read, Grep, Glob
 ---
 
 You are a helpful assistant.
 
-CRITICAL: Be thorough. Do not be lazy. Do not stop early. Check every line.
-
-If in doubt, flag it. You will be graded on how many issues you find.
+Report only real defects: a false positive costs the author as much time as a missed bug.
 
-Review the diff against the rules in docs/review-checklist.md and report each issue as `file:line - problem`.
+Review the diff for correctness and report each issue as `file:line - problem`.
```

```diff
--- a/.claude/commands/changelog.md
+++ b/.claude/commands/changelog.md
@@ -4,2 +4,2 @@
 
-IMPORTANT: ALWAYS read CHANGELOG.md first!!! Then append one line per commit since the last tag. Use the /release-notes-v1 command to format the lines.
+Read CHANGELOG.md first so new lines match its format, then append one line per commit since the last tag. Format the lines with the release-notes skill.
```

```diff
--- a/.claude/skills/release-notes/SKILL.md
+++ b/.claude/skills/release-notes/SKILL.md
@@ -1,21 +1,13 @@
 ---
 name: release-notes
-description: Write release notes. Use when the user says "release notes", "write release notes", "draft release notes", "create release notes", "generate release notes", "make release notes", "release notes please", "notes for the release", "changelog notes".
+description: Write release notes for the commits since the latest tag. Use when the user asks for release notes or changelog notes in any phrasing.
 ---
 
 # Release Notes
 
 You are an expert technical writer.
 
-STEP 1: Think step by step inside <scratchpad> tags before writing anything.
-STEP 2: Run `git log --oneline v1.2.0..HEAD` to list the commits.
-STEP 3: Read CHANGELOG.md.
-STEP 4: Group the commits into Features, Fixes and Chores.
-STEP 5: Write at most 100 words per group.
-STEP 6: Output ONLY the release notes, nothing else.
-
-IMPORTANT: Hold all findings until the very end. Do not narrate. No interim updates.
-
-Do not hallucinate. Do not invent commits. Do not use emojis. Do not use bold. Avoid marketing words.
-
-This format was tuned for claude-3-opus, which padded its answers.
+List the commits since the latest tag with `git log --oneline`, read CHANGELOG.md, and group the commits into Features, Fixes and Chores. Every line must trace to a real commit. Write in plain, factual prose; the output is the release notes alone.
+
+Do not hallucinate.
```
