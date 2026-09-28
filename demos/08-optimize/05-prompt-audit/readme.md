# Audit the Harness for Dated Instructions

Every CLAUDE.md, rule, skill, agent and command in a harness was written against the model of its day. Emphasis added because an older model under-triggered, step-by-step scripts added because it planned poorly, and a word cap added because it rambled all stay in the file after that model is retired. Current models follow instructions closely and literally, so the leftover text over-applies: shouting causes over-triggering, choreography causes over-planning, and a cap starves answers that need the room.

A prompt audit finds those specific dated instructions and proposes their removal. It is not a length pass: caveman compression in [02-caveman-compression](../02-caveman-compression/readme.md) keeps every rule and shortens the wrapper, while the audit decides which rules should exist at all. Run the audit first, then compress what survives.

## Two entry points, one audit

Both commands run the same audit procedure from the bundled `/claude-api` skill:

| Command | Default scope | Leads with |
|---|---|---|
| `/doctor prompt-audit [path]` | CLAUDE.md, CLAUDE.local.md and AGENTS.md, plus the rules, skills, commands, subagents and output styles under `.claude/` and `~/.claude/` | References to files or commands that do not exist, and files that contradict each other |
| `/claude-api prompt-audit [path]` | The prompt surface of the working directory, including system prompts and tool descriptions in application code | Dated prompt text and API scaffolds |

`/doctor prompt-audit` is the Claude Code entry point for a harness; `/checkup prompt-audit` is its alias. Pass a path to audit one file or folder instead of everything, for example `/doctor prompt-audit .claude/skills/release-notes`. It requires Claude Code v2.1.283 or later, and it is unavailable when the bundled `/claude-api` skill is turned off through `skillOverrides` or `disableBundledSkills`.

## What the audit looks for

The audit states two assumptions before it reads anything: the scope, and the target model it judges against. It takes the target from the request, else from a documented migration, else from the newest model the repository names, else the current flagship. Cruft is relative to that model, so the same line can be load-bearing on one generation and dead weight on the next.

| Family | Pattern | Example in a harness |
|---|---|---|
| Pressure language | Caps emphasis, `!!`, "do not be lazy", hedges on real requirements | `CRITICAL: NEVER skip the checks` |
| Replaced scaffolds | "Think step by step", `<scratchpad>` tags, numeric word caps | `Keep every answer under 50 words` |
| Over-specification | `STEP 1 ... STEP 6` scripts for judgement work, prohibition lists, grader vocabulary | `You will be graded on how many issues you find` |
| Fossils | Retired model names, update suppressors, anti-formatting rules, identity stubs | `known issue with claude-3-5-sonnet` |
| Brittle skill files | Stale paths, flags and tags; trigger phrases that grow one synonym per miss | `git log v1.2.0..HEAD` when no such tag exists |
| Harness integrity | A path, script or command that does not exist; two files that disagree | CLAUDE.md says Jest, `.claude/rules/testing.md` says Vitest |

The keep list binds as tightly as the patterns. Context only the author knows (audience, environment facts, the reason behind a constraint) is never cruft, exact scripts stay where only one sequence is safe, and a prohibition stays when its failure still reproduces. Trigger text in a skill `description` may keep calibrated urgency, because routing text and behavioural text do different jobs. An audit that finds nothing proposes nothing.

## Read the report

The audit produces two deliverables and changes no file until you ask:

| Deliverable | Content |
|---|---|
| Findings table | `file:line`, the quoted evidence, the pattern it matches, why it is obsolete for the target model, a confidence level, and an action |
| Proposed diff | One hunk per finding at high or medium confidence, so you can take hunks selectively |

| Confidence | Meaning | Lands in the diff |
|---|---|---|
| High | Documented in current Claude docs, errors on the target model, or a verifiable fact such as a missing file | Yes |
| Medium | Consistent, widely observed behaviour such as example over-indexing | Yes |
| Low | Heuristic or idiom-dating | No, reported as `flag` |

Actions are `remove`, `rewrite` (with the replacement text), `move`, `replace-with-API-feature`, `add` (an under-described tool gets more text, not less) and `flag`.

## Apply and re-audit

Take the diff hunk by hunk: a rewrite that keeps the live purpose of an instruction ("wait for the smoke test to pass") beats a bare deletion. Then run the same audit again on the edited harness. The second report is the check that the removals did not introduce new stale references, and its remaining findings should be the `flag` items you chose to keep.

Removal is a hypothesis. For an instruction whose purpose still matters, probe the behaviour before and after on a scratch copy; asking the model whether it needs the line is not a measurement. Re-run the audit at every model release, because prompts are per-model artifacts.

## Helpful Claude Slash Commands

| Command | Usage |
|---|---|
| `/doctor` | Run `/doctor prompt-audit` over the whole harness, or pass a path to audit one file or folder |
| `/memory` | Open the CLAUDE.md files the audit flagged and apply the accepted hunks |
| `/context` | Confirm the always-loaded share of the context window after the cleanup |
| `/rewind` | Restore the harness files from before the hunks were applied, if a probe regresses |

## Key Topics Covered in This Module

- [Write effective instructions](https://code.claude.com/docs/en/memory#write-effective-instructions): what `/doctor prompt-audit` reads, its path argument, and its version requirement
- [Commands reference](https://code.claude.com/docs/en/commands): the `/doctor [prompt-audit [path]]` entry and its `/checkup` alias
- [Claude API skill](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/claude-api-skill): the bundled skill that runs the audit
- [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices): the current-model behaviour the audit judges against
