# Labs - Module 10: Claude Agent SDK & Managed Agents

The module runs the same agent loop in two places. Labs 01 and 02 embed it in your own TypeScript program with the Claude Agent SDK, first as single calls and then as parallel reviewer sessions under an orchestrator. Labs 03, 04 and 05 hand the loop to Anthropic's cloud with Managed Agents: Lab 03 walks the three resources (Agent, Environment, Session) end to end on a real debugging task and adds a human approval gate that parks the Session at `requires_action`, Lab 04 coordinates several Agents with outcomes and memory, and Lab 05 extends an Agent with an MCP server and a skill and reads the event log to see which extension served each call.

| Lab | Topic | Title | Track | Level | Time | Description |
|-----|-------|-------|-------|-------|------|-------------|
| 01 | Embedding | [Embed Claude in a TypeScript Program](lab-01-sdk-embed-claude.md) | Core | Intermediate | 1h | Use the Claude Agent SDK to spawn Claude from inside your own program. One-shot calls, streaming responses, session resume, custom tools, typed output schemas, and wiring into a CI script. |
| 02 | Orchestration | [Run Parallel SDK Agents With Session Isolation](lab-02-sdk-parallel-agents.md) | Optional | Advanced | 1h | Build a code-review pipeline with three parallel SDK sessions (security, performance, style) plus an orchestrator that reconciles their findings. Package as a CI job. |
| 03 | Codebase Triage | [Build a Managed Agent for Codebase Triage](lab-03-agent-codebase-triage.md) | Optional | Advanced | 1h | Mount a broken Python repo into a cloud Session and stream the fix loop until the suite is green. Then publish a second Agent version carrying a `commit_changes` custom tool, and resume the parked Session with both an allow and a deny verdict. |
| 04 | Team Memory | [Review Code with Specialist Subagents, a Rubric and Team Memory](lab-04-agent-review-team-memory.md) | Optional | Advanced | 1h 30m | Two read-only reviewer subagents, a graded review, a read-only conventions store and a read-write history a second session recalls. |
| 05 | Extensions | [Extend a Managed Agent with an MCP Server and a Skill](lab-05-agent-mcp-and-skills.md) | Optional | Intermediate | 55m | Attach the Microsoft Learn MCP server and the `docx` skill to one Agent, compare a baseline turn with an extended one, download the document the skill wrote, audit the event log for which extension served each call, then drop the permission policy and watch the Session park at `requires_action`. |

**Core** is the one lab that teaches this module's central capability; run it if you run nothing else. **Optional** labs go deeper, cover a second tool, or need an account you may not have. **Level** rates the lab itself: Beginner needs no prior Claude Code experience, Intermediate assumes you have configured a harness before, Advanced assumes you are comfortable with hooks, subagents, or headless scripting.

Core path: 1h. All labs: 5h 25m.

> **Every lab is billed.** They need an `ANTHROPIC_API_KEY` from [the Claude Console](https://platform.claude.com), and every `query()` call and every Session is a paid API request against your own account. The Managed Agents labs bill session-hours on top of model tokens, so read Lab 03's "Before You Start" table before running anything. The wall-clock times above exclude account setup and do not account for spend. On a Max or Team plan, [claim your monthly API credits](claim-funds.md) first.

All labs ship their starters, so there is nothing to scaffold before you begin. Each completed reference sits beside its project:

| Lab | Starter | Solution |
|-----|---------|----------|
| 01 | [`01-sdk-embed/sdk-embed/`](01-sdk-embed/sdk-embed) | [`01-sdk-embed/sdk-embed-solution/`](01-sdk-embed/sdk-embed-solution) |
| 02 | [`02-sdk-parallel/sdk-review-pipeline/`](02-sdk-parallel/sdk-review-pipeline) | [`02-sdk-parallel/sdk-review-pipeline-solution/`](02-sdk-parallel/sdk-review-pipeline-solution) |
| 03 | [`03-agent-triage/calc-triage/`](03-agent-triage/calc-triage/readme.md) | [`03-agent-triage/calc-triage-solution/`](03-agent-triage/calc-triage-solution/readme.md) |
| 04 | [`04-agent-multiagent/review-team/`](04-agent-multiagent/review-team/readme.md) | [`04-agent-multiagent/review-team-solution/`](04-agent-multiagent/review-team-solution/readme.md) |
| 05 | [`05-agent-extend/docs-agent/`](05-agent-extend/docs-agent/readme.md) | You write the scripts as the lab walks you through them |

Open a solution when a step will not compile. The Lab 03 starter carries the broken Python fixture; you write the two driver scripts.

> **Naming note:** Anthropic renamed the Claude Code SDK to the **Claude Agent SDK** (npm package `@anthropic-ai/claude-agent-sdk`, repos at [`anthropics/claude-agent-sdk-typescript`](https://github.com/anthropics/claude-agent-sdk-typescript) and [`anthropics/claude-agent-sdk-python`](https://github.com/anthropics/claude-agent-sdk-python)). The labs use the new name and current package. See the [migration guide](https://code.claude.com/docs/en/agent-sdk/migration-guide) for the rename details.

Anthropic also ships an [`agent-sdk-dev`](https://github.com/anthropics/claude-code/tree/main/plugins/agent-sdk-dev) plugin that scaffolds new SDK projects via `/new-sdk-app` and verifies them with dedicated agents. Labs 01 and 02 build the same patterns by hand so you understand the moving parts, then point you at `agent-sdk-dev` as the production accelerant.
