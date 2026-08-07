# Call the Claude Agent SDK

## Installation

```bash
# TypeScript
npm install @anthropic-ai/claude-agent-sdk zod@^4

# Python
pip install claude-agent-sdk
```

The TypeScript SDK declares a peer dependency on `zod@^4`. Installing it into a project that pins `zod@^3` fails with `ERESOLVE` before anything runs.

## The Three Knobs on query()

`query()` accepts a prompt string and an options object. The three options that matter for every call are `allowedTools`, `permissionMode`, and `systemPrompt`.

```typescript
import { query, type Options } from "@anthropic-ai/claude-agent-sdk";

const options: Options = {
  allowedTools: ["Read", "Edit", "Bash", "WebSearch"],
  permissionMode: "acceptEdits",
  systemPrompt: "You are a senior Python developer. Follow PEP 8.",
};

for await (const message of query({ prompt: "Refactor auth.py", options })) {
  // consume the stream
}
```

`allowedTools` is an allowlist of built-in tool names. `permissionMode` controls whether the SDK auto-approves tool calls or prompts before each one. `systemPrompt` layers a persona on top of the default Claude Code prompt without replacing it.

## Permission Modes

| Mode | Behavior | Use when |
|---|---|---|
| `default` | Prompts before dangerous operations | Development, sensitive environments |
| `acceptEdits` | Auto-approves file edits | CI scripts, automated workflows |
| `plan` | Plans only, executes no tool | Dry runs and review-before-apply flows |
| `bypassPermissions` | Allows everything including dangerous ops; also requires `allowDangerouslySkipPermissions: true` | Sandboxed containers only |

These are the four modes worth teaching. The `PermissionMode` union also declares `dontAsk` (never prompt, deny anything not pre-approved) and `auto` (a model classifier decides), which are situational rather than everyday settings.

## Beneath query(): the Messages API Tool Loop

`query()` runs a loop that the Messages API expresses explicitly, and knowing that shape matters the moment you debug a tool call or move a workload to the raw API. The assistant emits a `tool_use` content block carrying a `tool_use_id`. Your application executes the tool and sends back a user turn containing a `tool_result` block whose `tool_use_id` matches. That id is the whole linkage: it is how the model maps an observation back to the action that produced it.

```json
{ "type": "tool_use", "id": "toolu_01A", "name": "scan_port",
  "input": { "host": "10.0.0.4", "port": 443 } }
```

```json
{ "type": "tool_result", "tool_use_id": "toolu_01A",
  "content": [{ "type": "text", "text": "443/tcp open" }] }
```

Appending the tool output as plain text to the end of the user message instead is the classic failure. The model loses the action-observation pairing, starts hallucinating outputs it never received, and cannot track which calls it has already made. The structure is not decoration.

The `content` field of a `tool_result` accepts an array of content blocks, not just a string, so a tool can hand back an image alongside its text. This is what makes a screenshot tool work: the block carries base64 data and its media type, and the model sees the picture.

```json
{ "type": "tool_result", "tool_use_id": "toolu_02B", "content": [
  { "type": "text", "text": "Captured after the click." },
  { "type": "image", "source": { "type": "base64",
      "media_type": "image/png", "data": "iVBORw0KG..." } }
]}
```

Set `is_error: true` on the block when the tool failed, so the model reads a failure rather than inferring one from the text.

## Session Resume

Each `query()` call ends with a result message (`msg.type === "result"`, typed `SDKResultMessage`) that carries a `session_id`. Passing that ID to a subsequent call through the `resume` option replays the conversation with full context intact.

```typescript
let sessionId: string | undefined;

for await (const msg of query({ prompt: "Design a URL shortener" })) {
  if (msg.type === "result") sessionId = msg.session_id;
}

for await (const msg of query({
  prompt: "What changes if writes go to 5k/sec?",
  options: { resume: sessionId },
})) {
  // full context of turn 1 is available
}
```

## Custom Tools

Custom tools are declared with the `tool()` helper, which takes a Zod shape rather than raw JSON Schema. Group them into an in-process MCP server with `createSdkMcpServer()` and register that server under `options.mcpServers`. No separate process is spawned: the handler runs inside your program, and the tool reaches Claude under the namespaced name `mcp__<server>__<tool>`, which is also the name you allowlist.

```typescript
import { query, tool, createSdkMcpServer } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";

const currentWeather = tool(
  "current_weather",
  "Returns current weather for a city.",
  { city: z.string().describe("City name, for example Berlin") },
  async ({ city }) => ({ content: [{ type: "text", text: `${city}: 8 C, light rain` }] })
);

const weatherServer = createSdkMcpServer({
  name: "weather",
  version: "1.0.0",
  tools: [currentWeather],
});

for await (const msg of query({
  prompt: "...",
  options: {
    mcpServers: { weather: weatherServer },
    allowedTools: ["mcp__weather__current_weather"],
  },
})) {
  if (msg.type === "assistant") {
    for (const block of msg.message.content) {
      if (block.type === "tool_use") console.log(block.name, block.input);
    }
  }
}
```

`options.tools` is a different knob. It selects which built-in tools exist and accepts `string[]` or `{ type: "preset", preset: "claude_code" }`, so it is not where custom tools go.

## Typed Output with Zod

Constrain the prompt to return only JSON, then validate with a Zod schema. The parse call throws if the output is malformed, making the failure explicit at the boundary rather than silently downstream.

```typescript
import { z } from "zod";

const ReviewSchema = z.object({
  severity: z.enum(["critical", "high", "medium", "low"]),
  findings: z.array(z.string()),
  verdict: z.enum(["block", "comment", "approve"]),
});

const raw = collectText(messages);
const parsed = ReviewSchema.parse(JSON.parse(raw));
```

## Demo 1: From Messages API to Agent SDK

See [demo-messages-api-to-sdk.md](demo-messages-api-to-sdk.md).

## Key SDK Imports

```typescript
import {
  query,
  tool,
  createSdkMcpServer,
  AbortError,
  type Options,
  type SDKMessage,
  type SDKAssistantMessage,
  type SDKResultMessage,
} from "@anthropic-ai/claude-agent-sdk";
```

Messages are plain tagged objects, not classes, so narrow with `msg.type === "assistant"` rather than `instanceof`. Content blocks (`text`, `tool_use`, `tool_result`) are not exported types: reach them through `msg.message.content` and switch on `block.type`.

## Exploration Prompt

```text
Install @anthropic-ai/claude-agent-sdk and write the smallest possible program
that calls query(), streams the response, and logs the raw event objects
(not just the text) so you can see every message type the loop produces.
```

## Helpful Claude Slash Commands

| Command | Usage |
|---|---|
| `/claude-api` | Scaffold, debug, or optimize code that imports `@anthropic-ai/claude-agent-sdk` |
| `/security-review` | Audit the CI script before wiring it to a real pipeline |
| `/simplify` | Tighten the demo scripts after the live run |

## Key Topics covered in this module

- [Claude Code SDK Documentation](https://code.claude.com/docs/en/agent-sdk/overview): `query()`, message types, permission modes, and session management
- [Claude Agent SDK (npm)](https://www.npmjs.com/package/@anthropic-ai/claude-agent-sdk): Package details and release history
- [Zod](https://zod.dev): Schema validation for typed output in the CI script
