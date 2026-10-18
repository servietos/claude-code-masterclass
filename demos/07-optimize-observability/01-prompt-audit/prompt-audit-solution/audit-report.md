## Prompt audit: `prompt-audit-solution/` (proposal only, nothing applied)

**Assumptions (Step 0)**
- **Scope:** the working directory's prompt surface: `CLAUDE.md`, `.claude/agents/order-reviewer.md`, `.claude/commands/changelog.md`, `.claude/skills/release-notes/SKILL.md`, `.claude/rules/testing.md`. I also checked `package.json`, `src/`, and the paths the files name. Skipped: the parent repo's `CLAUDE.md` and the sibling `demos/08-optimize/05-prompt-audit` tree in git history (outside the working directory). No settings, MCP, or credential files exist here.
- **Target model:** `claude-haiku-5-5`, the model running this audit. The request names none, and `CLAUDE.md`'s `claude-3-5-sonnet` is a finding to remove.
- **Audited text:** the working-tree files. Git has one committed revision for this folder (`9e12b08`) and the four prompt files have uncommitted edits, so `git blame` cannot order the Jest/Vitest conflict. That finding rests on the repo's current code instead.

**Highest impact**
1. `CLAUDE.md` names a test framework the repo does not use. It says Jest; `package.json`, `src/orders.test.ts`, and `.claude/rules/testing.md` all use Vitest.
2. Three references point at things that do not exist: `docs/architecture.md`, `docs/review-checklist.md`, and `/release-notes-v1`. The release-notes skill also cites tag `v1.2.0`, but the only tags are `1.0.0` and `2.0.0`. The `npm run typecheck` script is not defined.
3. The release-notes skill is a `claude-3-opus` era scaffold: `<scratchpad>` thinking, a six-step script, word caps, and a "no interim updates" rule.

**Counts:** Group 1 (dated prompt text): 13. Group 2 (brittle config, stale facts, conflicts): 7. Group 3 (tool descriptions): 1. Group 4 (request config and architecture): not applicable, because there is no request-building code and `src/orders.ts` is plain arithmetic. The sub-agent roster has one agent, so there is nothing to merge.

### Report (ordered by confidence)

| # | Location | Evidence (abridged) | Pattern | Confidence | Action |
|---|---|---|---|---|---|
| 1 | CLAUDE.md:11 | `Read docs/architecture.md before touching anything in src/.` | 2 volatile path; `docs/` absent | High | remove |
| 2 | CLAUDE.md:9 | `npm run typecheck`; scripts are only `test` and `lint` | 2 volatile command | High | rewrite (with #5) |
| 3 | CLAUDE.md:15 | `Always write tests with Jest.` | 2 conflict with rules/testing.md and package.json | High | rewrite |
| 4 | CLAUDE.md:7 | `IMPORTANT: You MUST ALWAYS think step by step ... Take a deep breath first.` | 1b scaffold | High | remove |
| 5 | CLAUDE.md:9 | `CRITICAL: NEVER skip the checks. ... Be thorough. Do not be lazy. Do not stop early.` | 1a, 1d | High | rewrite |
| 6 | CLAUDE.md:25 | `This is a known issue with claude-3-5-sonnet ... ALWAYS wait!!` | 1d retired-model fossil, 1a | High | rewrite |
| 7 | CLAUDE.md:21 | `Remember, you tend to be too verbose, so don't be too chatty.` | 1a trait claim | High | remove |
| 8 | CLAUDE.md:19 | `Keep every answer under 50 words.` | 1f numeric cap | Medium | rewrite (with #9) |
| 9 | CLAUDE.md:19 | `Never use bullet points or headers in your replies.` | 1d anti-formatting | Medium | rewrite (with #8) |
| 10 | order-reviewer.md:9 | `CRITICAL: Be thorough. Do not be lazy. Do not stop early. Check every line.` | 1a, 1d | High | remove |
| 11 | order-reviewer.md:11 | `If in doubt, flag it. You will be graded on how many issues you find.` | 1a, 1e grader vocabulary | High | rewrite |
| 12 | order-reviewer.md:13 | `docs/review-checklist.md` | 2 missing path | High | rewrite |
| 13 | order-reviewer.md:3 | `You MUST use this agent for EVERY change, no matter how small.` | 3 over-steered routing text | Medium | rewrite |
| 14 | changelog.md:3 | `IMPORTANT: ALWAYS read CHANGELOG.md first!!!` | 1a | High | rewrite (with #15) |
| 15 | changelog.md:3 | `Use the /release-notes-v1 command` | 2 command does not exist; the skill is `release-notes` | High | rewrite (with #14) |
| 16 | SKILL.md:11 | `git log --oneline v1.2.0..HEAD` | 2 tag does not exist | High | rewrite (with #17, #18) |
| 17 | SKILL.md:10,13-15 | `<scratchpad>` line and STEP 1 to 6 | 1b scaffold, 1c choreography | High | rewrite |
| 18 | SKILL.md:14 | `Write at most 100 words per group.` | 1f numeric cap | Medium | rewrite |
| 19 | SKILL.md:17 | `Hold all findings until the very end. Do not narrate. No interim updates.` | 1d update suppressor | Medium | remove |
| 20 | SKILL.md:21 | `This format was tuned for claude-3-opus, which padded its answers.` | 1d fossil | High | remove |
| 21 | SKILL.md:3 | Description lists nine near-synonym trigger phrases | 2 trigger enumeration | Medium | rewrite |

**Flags (no edit proposed)**
- `CLAUDE.md:25` `/deploy-staging`: no such command exists in this folder. It may come from a user-level or plugin command, which I did not probe outside the project. Confirm before keeping or removing that line.
- `changelog.md:3` and `SKILL.md:12` read `CHANGELOG.md`, which does not exist here. Creating it or dropping the step is your decision.
- `SKILL.md:19` `Do not hallucinate.`: low confidence. Keep it until you re-test.
- Kept on purpose: `You are a helpful assistant.` (a one-line role), the testing rules, `npm test` before done, and `Do not invent commits.` (a real constraint). If the 50-word cap is a display limit, it is product context and should stay (keep-list item 1); say so and I will drop #8.

### Proposed diff

Against the working tree. Hunks #8 and #9 share a line, and #14 and #15 share a line, so each pair is one hunk.

```diff
# CLAUDE.md
@@ line 7-8 (#4)
-IMPORTANT: You MUST ALWAYS think step by step before answering ANY question. Take a deep breath first.
-
@@ line 9 (#2, #5)
-CRITICAL: NEVER skip the checks. Before every commit run `npm run typecheck` and `npm run lint`. Be thorough. Do not be lazy. Do not stop early.
+Before every commit run `npm run lint`.
@@ line 11 (#1)
-Read docs/architecture.md before touching anything in src/.
-
@@ line 15 (#3)
-Always write tests with Jest. Put every test next to the file it covers as `<name>.test.ts`.
+Always write tests with Vitest. Put every test next to the file it covers as `<name>.test.ts`.
@@ line 19 (#8, #9)
-Never use bullet points or headers in your replies. Keep every answer under 50 words.
+Keep replies to the length the question needs. Use bullet points or headers only for list-shaped or sectioned content.
@@ line 21 (#7)
-Remember, you tend to be too verbose, so don't be too chatty.
-
@@ line 25 (#6)
-To ship a change, run /deploy-staging and wait for the smoke test. This is a known issue with claude-3-5-sonnet: it sometimes forgets to wait, so ALWAYS wait!!
+To ship a change, run /deploy-staging and wait for the smoke test to pass before reporting it shipped.

# .claude/agents/order-reviewer.md
@@ line 3 (#13)
-description: Reviews changes to src/orders.ts. You MUST use this agent for EVERY change, no matter how small.
+description: Reviews changes to src/orders.ts. Use it after any edit to that file.
@@ line 9 (#10)
-CRITICAL: Be thorough. Do not be lazy. Do not stop early. Check every line.
-
@@ line 11 (#11)
-If in doubt, flag it. You will be graded on how many issues you find.
+Report only real defects: a false positive costs the author as much time as a missed bug.
@@ line 13 (#12)
-Review the diff against the rules in docs/review-checklist.md and report each issue as `file:line - problem`.
+Review the diff for correctness and report each issue as `file:line - problem`.

# .claude/commands/changelog.md
@@ line 3 (#14, #15)
-IMPORTANT: ALWAYS read CHANGELOG.md first!!! Then append one line per commit since the last tag. Use the /release-notes-v1 command to format the lines.
+Read CHANGELOG.md first so new lines match its format, then append one line per commit since the last tag. Format the lines with the release-notes skill.

# .claude/skills/release-notes/SKILL.md
@@ line 3 (#21)
-description: Write release notes. Use when the user says "release notes", "write release notes", "draft release notes", "create release notes", "generate release notes", "make release notes", "release notes please", "notes for the release", "changelog notes".
+description: Write release notes for the commits since the latest tag. Use when the user asks for release notes or changelog notes in any phrasing.
@@ line 10-15 (#16, #17, #18)
-STEP 1: Think step by step inside <scratchpad> tags before writing anything.
-STEP 2: Run `git log --oneline v1.2.0..HEAD` to list the commits.
-STEP 3: Read CHANGELOG.md.
-STEP 4: Group the commits into Features, Fixes and Chores.
-STEP 5: Write at most 100 words per group.
-STEP 6: Output ONLY the release notes, nothing else.
+List the commits since the latest tag: find the tag with `git describe --tags --abbrev=0`, then run `git log --oneline <tag>..HEAD`.
+Read CHANGELOG.md and group the commits into Features, Fixes and Chores. Keep each group short.
+Output only the release notes.
@@ line 17 (#19)
-IMPORTANT: Hold all findings until the very end. Do not narrate. No interim updates.
-
@@ line 21 (#20)
-This format was tuned for claude-3-opus, which padded its answers.
```

Nothing has been edited. If you want the diff applied, tell me which hunks to take. I would start with hunks 1 to 6 on `CLAUDE.md`, since they carry the stale-fact findings. Note that the Jest-to-Vitest hunk is a proposal under the conflict rule, so confirm it before applying.