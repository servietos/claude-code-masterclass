# Read the Vacancies Planning Record

This folder is the [hr-mcp-server/](../hr-mcp-server) starter plus every file the four planning demos wrote. The server code is unchanged: planning produced documents, and the feature is built later from them.

| File | Written by | What it holds |
| --- | --- | --- |
| [plan-mode-turn-1.md](plan-mode-turn-1.md) | [demo-plan-mode-constraint-ratchet.md](../demo-plan-mode-constraint-ratchet.md), Part A | The plan mode plan file after the vague brief: five copied tools and the assumptions to correct |
| [plan-mode-turn-2.md](plan-mode-turn-2.md) | [demo-plan-mode-constraint-ratchet.md](../demo-plan-mode-constraint-ratchet.md), Part B | The same plan file after the constraint ratchet: four tools and the ranking rule |
| [ledger.md](ledger.md) | [demo-plan-vacancies.md](../demo-plan-vacancies.md), Step 1 | Findings of three parallel subagents under MCP tools, Data and Verification |
| [plan.md](plan.md) | [demo-plan-vacancies.md](../demo-plan-vacancies.md), Steps 1 and 2 | Eight numbered tasks, corrected against the constraints |
| [STATE.md](STATE.md) | [demo-authoring-state.md](../demo-authoring-state.md) | Goal, Decisions, Status, Next Action, Done Criteria and an empty Open Questions |
| [work-packages.md](work-packages.md) | [demo-work-package-decomposition.md](../demo-work-package-decomposition.md), step 1 | Four packages with inputs, outputs, contracts and dependencies |
| [issues.md](issues.md) | [demo-work-package-decomposition.md](../demo-work-package-decomposition.md), step 3 | The parent issue, four sub-issues and the `gh` commands to file them, none of them run |

The record comes from headless runs of Claude Code on `haiku` (`--model haiku`), each prompt sent verbatim from its guide with `claude -p`. Plan mode ran with `--permission-mode plan`, the file-writing steps with `--permission-mode bypassPermissions`, and follow-up prompts resumed their session with `--resume`. The plan mode plan file was written to `~/.claude/plans/` (`i-want-to-add-parsed-minsky.md` in this run) and copied here under its turn name.
