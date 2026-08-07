# Stack Versions & Model Clients

## Current Stack Versions (as of April 2026)

- **agent-framework**: `1.2.2`
- **agent-framework-openai**: `1.2.2` (for non-Foundry models via `OpenAIChatCompletionClient`)
- **agent-framework-foundry**: `1.2.2` (for Foundry models via `FoundryChatClient`)
- **agent-framework-foundry-hosting**: `1.0.0a260429` (alpha — `ResponsesHostServer` bridge)
- **agent-framework-orchestrations**: `1.0.0b260429` (beta — `MagenticBuilder`, `WorkflowBuilder`)
- **openai**: `2.33.0` (pulled by `agent-framework-openai`)

## Model Client Decision

| Scenario | Client | Package |
|---|---|---|
| Microsoft Foundry deployment | `FoundryChatClient(model=..., credential=...)` | `agent-framework-foundry` |
| OpenAI / Azure OpenAI | `OpenAIChatClient(model=...)` (Responses API) | `agent-framework-openai` |
| DeepSeek, Ollama, LM Studio, vLLM | `OpenAIChatCompletionClient(model=..., base_url=..., api_key=...)` (Chat Completions API) | `agent-framework-openai` |

**Key finding**: Third-party providers (DeepSeek, etc.) only support the Chat Completions API. `OpenAIChatClient` uses the Responses API and will 404. Always use `OpenAIChatCompletionClient` with `base_url` for non-Foundry/non-Azure-OpenAI models.

## Orchestration Decision

| Scenario | Pattern |
|---|---|
| Fixed pipeline (known steps, pre-defined edges) | `WorkflowBuilder` — `add_edge()`, `add_switch_case_edge_group()` |
| Dynamic coordination (manager decides next agent) | `MagenticBuilder` — manager plans, delegates, tracks via ledger |

## Package Upgrade Constraints

### azure-ai-agentserver-agentframework (legacy bridge)

`azure-ai-agentserver-agentframework==1.0.0b17` pins:
- `agent-framework-core<=1.0.0rc3`
- `agent-framework-azure-ai<=1.0.0rc3`

The GA packages (`1.0.x`) renamed `BaseContextProvider` → `ContextProvider`, which breaks the agentserver bridge import. **Never upgrade `agent-framework-core` or related packages past `rc3` without also upgrading agentserver.**

Before any package change in a venv using this bridge:

```bash
pip show azure-ai-agentserver-agentframework
pip install <package>==<version> --dry-run
```

> Note: The current stack (April 2026) has migrated to `agent-framework-foundry-hosting` (`ResponsesHostServer`), which replaces the agentserver bridge entirely. This constraint only applies to projects still on the `b17` bridge.
