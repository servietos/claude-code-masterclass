# Understand the Claude Agent SDK

## Where the Agent SDK Sits

The platform has four layers from low-level to fully managed. At the bottom is the Messages API, which gives you raw request/response but requires you to implement the tool loop yourself. At the top is Managed Agents, where Anthropic manages the loop, tools, context, and infrastructure. The Agent SDK occupies the middle: you call it from code, Claude runs the loop, and you own the deployment.

```text
Messages API      : You manage prompts, tool loop, context
Claude Code       : Anthropic manages loop, tools, context (interactive)
Agent SDK         : You call from code; Anthropic manages loop, tools, context
Managed Agents    : Anthropic manages loop, tools, context, infrastructure
```

The decisive difference between the Messages API and the Agent SDK is who implements the `while stop_reason == "tool_use"` loop. With the Messages API that loop is your code. With the Agent SDK it is inside the library and you consume the resulting async iterator.

```python
# Messages API: you implement the tool loop
response = client.messages.create(...)
while response.stop_reason == "tool_use":
    result = your_tool_executor(response.tool_use)
    response = client.messages.create(tool_result=result, **params)

# Agent SDK: Claude handles it
async for message in query(prompt="Fix the bug in auth.py"):
    print(message)
```

## The query() Async Iterator

`query()` is the single entry point. It returns an async iterator that yields one event per agent loop iteration. Every message is a plain tagged object, so you narrow on `msg.type` rather than with `instanceof`. Reading the raw event stream without any filtering is the fastest way to build an intuition for the loop from the outside.

| `msg.type` | TypeScript type | What it contains |
|---|---|---|
| `system` | `SDKSystemMessage` | Init info: available tools, model, permission mode, sub-agents |
| `assistant` | `SDKAssistantMessage` | Claude's turn; text and `tool_use` blocks live in `msg.message.content` |
| `user` | `SDKUserMessage` | The turn fed back into the loop, including `tool_result` blocks |
| `result` | `SDKResultMessage` | Final event: `session_id`, `total_cost_usd`, token usage |

Tool calls and tool results are content blocks inside those messages, not messages of their own. Reach them through `msg.message.content` and switch on `block.type`.

## When to Use Each Layer

| Use the Agent SDK when | Use the Messages API when |
|---|---|
| You need built-in tools (file ops, bash, web search) | Single-turn or simple chat |
| You want the same agent loop as Claude Code in your program | You need full control of every turn |
| You're embedding Claude into CI, scripts, or backend services | You're building a streaming chat UI |
| You want to run multiple agents in parallel from one program | Latency is critical |

## Discussion Prompt

```text
Compare the Messages API and the Agent SDK.
What disappears from your code when you switch from Messages API to Agent SDK?
When would that tradeoff go the wrong way?
```

## Helpful Claude Slash Commands

| Command | Usage |
|---|---|
| `/claude-api` | Scaffold or debug Claude API and SDK code, including prompt caching and tool use |
| `/simplify` | Review Agent SDK integration code for unnecessary abstractions after prototyping |

## Key Topics covered in this module

- [Claude Code SDK Documentation](https://code.claude.com/docs/en/agent-sdk/overview): `query()`, message types, and the agent loop internals
- [Messages API Reference](https://platform.claude.com/docs/en/api/messages): The lower-level alternative and what the SDK wraps
