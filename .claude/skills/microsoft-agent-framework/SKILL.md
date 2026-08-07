---
name: microsoft-agent-framework
description: >-
  Master skill for Microsoft Agent Framework (Python) development — agent patterns, Foundry deployment,
  evaluation, tools, and .NET↔Python API bridging. Delegates to leaf skills based on task type.
  Use when working on any Agent Framework project in this repo.
  Triggers on: "agent framework", "maf", "magentic", "workflow builder", "hosted agent",
  "foundry agent", "agent deployment", "agent eval".
license: CC-BY-NC-SA-4.0
---

# microsoft-agent-framework — Agent Framework Router

Routes Agent Framework requests to the appropriate leaf skill. Do not implement directly — delegate immediately.

## Delegate Map

| Request type | Leaf skill to invoke |
| --- | --- |
| Add/edit agents, change workflow topology, orchestration | [`agent-framework-workflow`](references/agent-framework-workflow.md) |
| Design workflow architectures, choose patterns, reference topologies | [`agent-framework-orchestration`](references/agent-framework-orchestration.md) |
| Coordinate .NET ↔ Python contracts, API endpoints, DTOs | [`agent-framework-api-bridge`](references/agent-framework-api-bridge.md) |
| Deploy `kind: hosted` container agent OR `kind: prompt` prompt agent | [`agent-framework-deploy`](references/agent-framework-deploy.md) |
| Eval datasets, batch eval, prompt optimization | [`agent-framework-eval`](references/agent-framework-eval.md) |
| CLI tooling, Agent 365 CLI, local dev setup | [`agent-365-cli`](references/agent-365-cli.md) |
| Write or review agent code (FoundryChatClient, WorkflowBuilder, MagenticBuilder, hosted server) | [`agent-framework-patterns`](references/agent-framework-patterns.md) |
| Package versions, model client selection, upgrade constraints | [`stack-versions`](references/stack-versions.md) |

> **Prompt vs Container**: `kind: prompt` agents deploy via REST API, NOT `azd deploy`. See `agent-framework-deploy.md` for the correct PowerShell deploy block.
