# Labs - Module 06: Subagents

| Lab | Topic | Title | Track | Level | Time | Description |
|-----|-------|-------|-------|-------|------|-------------|
| 01 | Docs Agent | [Build a specialized documentation agent with brand-voice enforcement](lab-01-specialized-agents.md) | Core | Intermediate | 50m | Build a documentation sub-agent by reasoning through tools, model choice, MCP wiring, and brand-voice enforcement in conversation with Claude. |
| 02 | Unit Testing Agent | [Build a scoped unit-testing agent with minimal permissions](lab-02-unit-testing-agent.md) | Optional | Intermediate | 50m | Build a unit-testing sub-agent scoped to one catalog-api stack, with minimal Bash permissions and interface-only mocking rules, then run it against real source code and evaluate the test quality. |
| 03 | Agentic Team | [Orchestrate an agentic team to deliver customer data persistence](lab-03-agentic-team.md) | Optional | Advanced | 1h 20m | Coordinate the dotnet-expert and angular-expert as a team to add customer data persistence to the food-shop checkout page. |

**Core** is the one lab that teaches this module's central capability; run it if you run nothing else. **Optional** labs go deeper, cover a second tool, or need an account you may not have. **Level** rates the lab itself: Beginner needs no prior Claude Code experience, Intermediate assumes you have configured a harness before, Advanced assumes you are comfortable with hooks, subagents, or headless scripting.

Core path: 50m. All labs: 3h.

Lab 03 is the module's most rewarding lab and also its heaviest, because it runs the .NET API and the Angular app together and applies an EF Core migration; budget the extra install time before choosing it.

Each lab has a starter you work in, and a finished counterpart beside it named `<starter>-solution/`: `01-docs-agent/docs-agent/` with `01-docs-agent/docs-agent-solution/` for Lab 01, the `catalog-service-*-solution/` copy you make in Lab 02, and `src/food-app/catalog-api/catalog-service-cs-lab03-solution/` plus `src/food-app/shop-ui/food-shop-ng-solution/` for Lab 03. The starter stays pristine (no dependencies, no build output, no generated test files); install, run and generate only inside the solution folder, and use it as the completed reference when you want to compare.
