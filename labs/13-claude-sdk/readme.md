# Labs - Module 13: Claude Agent SDK

| Lab | Topic | Title | Track | Level | Time | Description |
|-----|-------|-------|-------|-------|------|-------------|
| 01 | Embedding | [Embed Claude in a TypeScript Program](lab-01-embed-claude.md) | Core | Intermediate | 1h | Use the Claude Agent SDK to spawn Claude from inside your own program. One-shot calls, streaming responses, session resume, custom tools, typed output schemas, and wiring into a CI script. |
| 02 | Orchestration | [Run Parallel SDK Agents With Session Isolation](lab-02-parallel-sdk-agents.md) | Optional | Advanced | 1h | Build a code-review pipeline with three parallel SDK sessions (security, performance, style) plus an orchestrator that reconciles their findings. Package as a CI job. |

**Core** is the one lab that teaches this module's central capability; run it if you run nothing else. **Optional** labs go deeper, cover a second tool, or need an account you may not have. **Level** rates the lab itself: Beginner needs no prior Claude Code experience, Intermediate assumes you have configured a harness before, Advanced assumes you are comfortable with hooks, subagents, or headless scripting.

Core path: 1h. All labs: 2h.

Both labs call the Agent SDK with an `ANTHROPIC_API_KEY` and every call is billed to it, so the wall-clock time above excludes the account setup and does not account for spend.

> **Both labs are billed.** They need an `ANTHROPIC_API_KEY` from [the Claude Console](https://platform.claude.com), and every `query()` call in every step is a paid API request against your own account. Lab 02 is the heavier of the two.

Both labs ship their starters, at [`01-embed/sdk-embed/`](01-embed/sdk-embed/) and [`02-parallel/sdk-review-pipeline/`](02-parallel/sdk-review-pipeline/), so there is nothing to scaffold before you begin. Each lab's completed reference sits beside its project: [`01-embed/sdk-embed-solution/`](01-embed/sdk-embed-solution/) and [`02-parallel/sdk-review-pipeline-solution/`](02-parallel/sdk-review-pipeline-solution/). Open a solution when a step will not compile.

> **Naming note:** Alexander's module is titled "Claude Code SDK". Anthropic has renamed it to the **Claude Agent SDK** (npm package `@anthropic-ai/claude-agent-sdk`, repos at [`anthropics/claude-agent-sdk-typescript`](https://github.com/anthropics/claude-agent-sdk-typescript) and [`anthropics/claude-agent-sdk-python`](https://github.com/anthropics/claude-agent-sdk-python)). The labs use the new name and current package; the workflow Alexander described still applies. See the [migration guide](https://code.claude.com/docs/en/agent-sdk/migration-guide) for the rename details.

Anthropic also ships an [`agent-sdk-dev`](https://github.com/anthropics/claude-code/tree/main/plugins/agent-sdk-dev) plugin that scaffolds new SDK projects via `/new-sdk-app` and verifies them with dedicated agents. The labs build the same patterns by hand so you understand the moving parts, then point you at `agent-sdk-dev` as the production accelerant.
