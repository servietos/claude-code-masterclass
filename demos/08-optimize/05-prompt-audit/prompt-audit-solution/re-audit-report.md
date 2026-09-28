Assumptions: scope is `prompt-audit-solution/` (CLAUDE.md, `.claude/rules/testing.md`, the `order-reviewer` agent, the `changelog` command, the `release-notes` skill). Nothing outside the project was read, and there are no settings or `.mcp.json` files. The target model is Claude Opus 5.5, because no model was named and that is the model running this audit.

The surface is essentially clean. None of the dated patterns the starter had are left in the solution folder. No finding reaches medium or high confidence, so there is no proposed diff.

Counts: Group 1 has 1 finding, Group 2 has 2, and Groups 3 and 4 don't apply (no tool definitions, no request code, and the only subagent has no duplicate).

| Location | Evidence | Pattern | Why | Confidence | Action |
|---|---|---|---|---|---|
| `CLAUDE.md:19` | "run /deploy-staging and wait for the smoke test" | Group 2, command that doesn't exist in the project | There is no `.claude/commands/deploy-staging.md` and no deploy script in `package.json`. It may be a user-level command, which I didn't check because it's outside the project. | Low | flag: add the command to the project or drop the section |
| `.claude/commands/changelog.md:5`, `.claude/skills/release-notes/SKILL.md:10` | "Read CHANGELOG.md first" | Group 2, file that doesn't exist | The project has no `CHANGELOG.md`. The command appends to it, so it may just not have been created yet. | Low | flag |
| `.claude/skills/release-notes/SKILL.md:12` | "Do not hallucinate." | Group 1c, a "do not hallucinate" line | Line 10 already says the same thing ("Every line must trace to a real commit"). A one-line recap at the end is on the keep list. | Low | flag |
