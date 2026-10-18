# Labs - Module 06: Subagents and Agent Teams

| Lab | Topic | Title | Track | Level | Time | Description |
|-----|-------|-------|-------|-------|------|-------------|
| 01 | Docs Agent | [Build a specialized documentation agent with brand-voice enforcement](lab-01-specialized-agents.md) | Core | Intermediate | 50m | Build a documentation sub-agent by reasoning through tools, model choice, MCP wiring, and brand-voice enforcement in conversation with Claude. |
| 02 | Unit Testing Agent | [Build a scoped unit-testing agent with minimal permissions](lab-02-unit-testing-agent.md) | Optional | Intermediate | 50m | Build a unit-testing sub-agent scoped to one catalog-api stack, with minimal Bash permissions and interface-only mocking rules, then run it against real source code and evaluate the test quality. |
| 03 | Agentic Team | [Orchestrate an agentic team to deliver customer data persistence](lab-03-agentic-team.md) | Optional | Advanced | 1h 20m | Coordinate the dotnet-expert and angular-expert as a team to add customer data persistence to the food-shop checkout page. |
| 04 | Review Team | [Spawn a review team and steer it](lab-04-spawn-a-review-team.md) | Core | Intermediate | 30m | Enable agent teams, spawn three named reviewers on one unreviewed service, watch them claim tasks off the shared list, redirect one by messaging it directly, and gate the single fix behind plan approval. |
| 05 | Review Loop | [Converge a review loop with a stopping rule](lab-05-converge-a-review-loop.md) | Optional | Advanced | 1h 30m | Harden the catalog-service write path with a writer and a read-only reviewer, triage every finding against the project's real configuration, stop the loop on a round cap, then optionally rerun the split as a workflow graph with the vote in code. |
| 06 | Debate a Root Cause | [Debate a root cause with a team](lab-06-debate-a-root-cause.md) | Optional | Advanced | 1h 20m | Spawn five teammates that each defend one hypothesis about a billing bug, falsify each other with one-variable control experiments run outside the project, and record every refuted theory in a consensus findings file. |

**Core** labs teach this module's central capabilities, one for sub-agents and one for agent teams; run them if you run nothing else. **Optional** labs go deeper, cover a second tool, or need an account you may not have. **Level** rates the lab itself: Beginner needs no prior Claude Code experience, Intermediate assumes you have configured a harness before, Advanced assumes you are comfortable with hooks, subagents, or headless scripting.

Core path: 1h 20m. All labs: 6h 20m.

Lab 03 is the module's most rewarding lab and also its heaviest, because it runs the .NET API and the Angular app together and applies an EF Core migration; budget the extra install time before choosing it.

Agent teams are experimental and need Claude Code 2.1.178 or newer, and three teammates bill roughly three times a single-session review of the same code. Check `claude --version` before the clock starts on Lab 04.

Each lab has a starter you work in, and a finished counterpart beside it named `<starter>-solution/`: `01-docs-agent/docs-agent/` with `01-docs-agent/docs-agent-solution/` for Lab 01, the `catalog-service-*-solution/` copy you make in Lab 02, `src/food-app/catalog-api/catalog-service-cs-lab03-solution/` plus `src/food-app/shop-ui/food-shop-ng-solution/` for Lab 03, and for Lab 04 the starter `04-review/notes-api-py` with the `notes-api-py-solution/` copy you make in Step 0. The starter stays pristine (no dependencies, no build output, no generated test files, no findings); install, run and generate only inside the solution folder, and use it as the completed reference when you want to compare. In Lab 04 the review file the team writes and the one approved fix land in the solution folder, while the agent-teams flag goes into your global harness at `~/.claude/settings.json`.
