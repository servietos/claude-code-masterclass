# Call the Claude Agent SDK

The Claude Agent SDK runs the Claude Code agent loop inside your own program, so you call `query()` and consume the events it yields. This topic places the SDK among Claude's tools, walks the API surface you call, and shows how to resume, fork and constrain what the model returns. Topic 03 onward covers the Managed Agents half of this module.

## Where the Agent SDK Sits

The Agent SDK sits between the raw API and the fully managed product. The overview in the Agent SDK documentation places it among the Claude tools:

| You want to | Use | What you get |
|---|---|---|
| Embed Claude Code's agent in your own Python or TypeScript application, in a process you operate | **Agent SDK** | A library that runs the Claude Code binary, with Claude Code's [capabilities](https://code.claude.com/docs/en/agent-sdk/overview#capabilities), such as built-in tools, permissions, sessions, and hooks. |
| Do interactive development or run one-off tasks from a terminal | [**Claude Code CLI**](https://code.claude.com/docs/en/overview) | The terminal interface, built for daily interactive use. |
| Call the Claude API directly from your own code | [**Client SDK**](https://platform.claude.com/docs/en/cli-sdks-libraries/overview) | Direct access to the Claude API from any of the client SDK languages. You write the tool loop yourself, or let the client SDK's beta [tool runner](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-runner) drive it. |
| Have Anthropic host the agent, configured through the Claude API | [**Managed Agents**](https://platform.claude.com/docs/en/managed-agents/overview) | A hosted agent harness that runs the agent loop, with sessions in an Anthropic-managed cloud sandbox or a [self-hosted sandbox](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes) on your own infrastructure. |

Below the Agent SDK sits the Messages API, which the Client SDK wraps. The decisive difference between the two is who implements the `while stop_reason == "tool_use"` loop. With the Messages API that loop is your code. With the Agent SDK it is inside the library and you consume the resulting async iterator.

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

`query()` is the single entry point. It returns an async iterator that yields one event per agent loop iteration. Every message is a plain tagged object, so you narrow on `msg.type`. Reading the raw event stream without any filtering is the fastest way to build an intuition for the loop from the outside.

| `msg.type` | TypeScript type | What it contains |
|---|---|---|
| `system` | `SDKSystemMessage` | Init info: available tools, model, permission mode, sub-agents |
| `assistant` | `SDKAssistantMessage` | Claude's turn; text and `tool_use` blocks live in `msg.message.content` |
| `user` | `SDKUserMessage` | The turn fed back into the loop, including `tool_result` blocks |
| `result` | `SDKResultMessage` | Final event: `session_id`, `total_cost_usd`, token usage |

Tool calls and tool results are content blocks inside those messages; they have no messages of their own. Reach them through `msg.message.content` and switch on `block.type`.

## When to Use Each Layer

| Use the Agent SDK when | Use the Messages API when |
|---|---|
| You need built-in tools (file ops, bash, web search) | Single-turn or simple chat |
| You want the same agent loop as Claude Code in your program | You need full control of every turn |
| You're embedding Claude into CI, scripts, or backend services | You're building a streaming chat UI |
| You want to run multiple agents in parallel from one program | Latency is critical |

The hosting page of the Agent SDK documentation draws the same line: "If you don't need to run the agent loop itself on your own infrastructure, consider Managed Agents instead." Topic 03 starts the Managed Agents half of this module, where Anthropic hosts the loop and you configure the agent through the Claude API: [03 Managed Agents Foundations](../03-agent-foundations/readme.md).

## Installation

```bash
# TypeScript
npm install @anthropic-ai/claude-agent-sdk zod@^4

# Python
pip install claude-agent-sdk
```

The TypeScript SDK declares a peer dependency on `zod@^4`. Installing it into a project that pins `zod@^3` fails with `ERESOLVE` before anything runs. The TypeScript package is pinned at 0.3.302 in this module's demos and labs. The Python package is `claude-agent-sdk` 0.2.168 and needs Python 3.10 or later.

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

Appending the tool output as plain text to the end of the user message is the classic failure. The model loses the action-observation pairing, starts hallucinating outputs it never received, and cannot track which calls it has already made. The `tool_use_id` carries that pairing, so the structure matters.

The `content` field of a `tool_result` accepts an array of content blocks, as well as a string, so a tool can hand back an image alongside its text. This is what makes a screenshot tool work: the block carries base64 data and its media type, and the model sees the picture.

```json
{ "type": "tool_result", "tool_use_id": "toolu_02B", "content": [
  { "type": "text", "text": "Captured after the click." },
  { "type": "image", "source": { "type": "base64",
      "media_type": "image/png", "data": "iVBORw0KG..." } }
]}
```

Set `is_error: true` on the block when the tool failed, so the model knows the call failed without having to infer it from the text.

## Resume, Continue or Fork a Session

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

`continue` is the option for the common case where no ID is needed. `continue: true` in TypeScript, or `continue_conversation=True` in Python, picks up the most recent session in the current directory. That suits an app that runs one conversation at a time, while `resume` with an explicit ID suits several users or an older session.

Two different questions get answered by two different operations, and picking the wrong one is how comparisons end up contaminated.

Resume continues one line of work. Yesterday's session holds valid context and no tool result has gone stale, so `--resume` (or `options.resume` in the SDK) replays the conversation and you carry on. It is always cheaper than re-uploading artifacts and re-explaining the task, and it preserves the reasoning path as well as the files.

Forking branches one line of work into several. After fifteen turns of profiling a slow ETL job, you want to try a broadcast join and a salting strategy and compare them fairly. Both need the profiling context; neither should see the other's attempts. Pass `forkSession: true` with `resume` (`fork_session=True` in Python) and the SDK copies the shared state into an isolated branch, so each strategy develops from the same baseline without cross-contamination.

```typescript
let forkedId: string | undefined;

for await (const msg of query({
  prompt: "Instead of the broadcast join, try a salting strategy",
  options: { resume: sessionId, forkSession: true },
})) {
  if (msg.type === "result") forkedId = msg.session_id;
}
```

A fork gets its own session ID, and the original keeps its ID and history. Forking branches the conversation while the filesystem stays shared, so file edits a fork makes are visible to every session working in that directory.

| Situation | Operation |
|---|---|
| Continuing yesterday's task, context still valid | Resume |
| Two candidate solutions to evaluate against one baseline | Fork |
| A new task that would only be polluted by the old history | New session |
| One session holds raw logs, another holds the reasoning; you need the reasoning | Resume the reasoning session, start a new one for the new task |

Reverting turns is a poor substitute for forking. Undoing the broadcast-join attempt before trying salting leaves the model having seen the first attempt, which is exactly the contamination the comparison was meant to avoid.

## Custom Tools

Custom tools are declared with the `tool()` helper, which takes a Zod shape as its input schema. Group them into an in-process MCP server with `createSdkMcpServer()` and register that server under `options.mcpServers`. No separate process is spawned: the handler runs inside your program, and the tool reaches Claude under the namespaced name `mcp__<server>__<tool>`, which is also the name you allowlist.

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

`options.tools` is a different knob. It selects which built-in tools exist and accepts `string[]` or `{ type: "preset", preset: "claude_code" }`, so custom tools go under `options.mcpServers` instead.

## Typed Output with Zod

Constrain the prompt to return only JSON, then validate with a Zod schema. The parse call throws if the output is malformed, making the failure explicit at the boundary before anything downstream runs.

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

The Agent SDK can also enforce this shape for you with the `outputFormat` option, described under [Structured Outputs](#structured-outputs-guaranteeing-the-shape).

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

Messages are plain tagged objects, so narrow with `msg.type === "assistant"`. Content blocks (`text`, `tool_use`, `tool_result`) are not exported types: reach them through `msg.message.content` and switch on `block.type`.

## Constrain What the Model Returns

Everything so far let the model decide whether to call a tool and what shape its answer takes. Three API-level controls remove that discretion when a pipeline cannot tolerate it: `tool_choice` decides whether a tool runs at all, Structured Outputs guarantees the JSON shape, and the Message Batches API trades latency for cost on work nobody is waiting for.

### tool_choice: Forcing or Releasing the Tool Call

`tool_choice` is set per request and has four values. The distinction that matters in production is between "the model may call a tool" and "the model must".

| Value | Guarantee | Reach for it when |
|---|---|---|
| `{"type": "auto"}` | Model decides: it may call a tool or answer in prose. The default. | Conversational turns, and the final turn of any pipeline |
| `{"type": "any"}` | Model must call one of the supplied tools, but picks which | Every input must produce a structured record, even an empty one |
| `{"type": "tool", "name": "x"}` | Model must call exactly that tool | The classification is already known, so the router step is waste |
| `{"type": "none"}` | Model may not call any tool | A turn that must only summarize what already happened |

The failure mode worth memorizing belongs to `any`. It forces a tool call on **every** turn, including the turn after the pipeline finished its last step. The agent has nothing left to do, so it calls a tool anyway, usually the first one in the pipeline, and loops forever.

```text
fetch_record -> transform_record -> load_record -> fetch_record -> ...
```

The fix sits in `tool_choice`. It is request-scoped, so switch it back to `auto` on the turn after the last required call and the model regains the option to stop and answer.

Two smaller consequences follow from the same mechanic. Setting `any` with exactly one tool in the array is the cheapest way to guarantee that tool runs, which is what you want when short or uninformative inputs otherwise make the model reply conversationally. And `{"type": "tool", "name": "x"}` overrides the system prompt: if the prompt says "classify first, then extract", forcing the extraction tool wins anyway.

### Structured Outputs: Guaranteeing the Shape

Prompting for JSON and validating afterwards, the Zod pattern from [Typed Output with Zod](#typed-output-with-zod), catches a malformed response. Structured Outputs prevents one. Two layers expose the same JSON Schema guarantee under different names, and each one belongs to a different interface.

On the Messages API, the schema goes into `output_config.format` on the request. The API constrains decoding at the token level, so a response that violates the schema cannot be generated.

```python
response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=1024,
    output_config={"format": {
        "type": "json_schema",
        "schema": {
            "type": "object",
            "properties": {
                "patient_id": {"type": "string"},
                "diagnosis": {"type": "string"},
                "prescribed_medication": {"type": ["string", "null"]},
            },
            "required": ["patient_id", "diagnosis", "prescribed_medication"],
        },
    }},
    messages=[{"role": "user", "content": note}],
)
```

The `["string", "null"]` type array is the piece people miss. A field that is genuinely absent from the source needs an explicit null branch; without one the model inconsistently omits the key, emits the string `"N/A"`, or invents a plausible value. Type arrays cost more to compile but are fully supported.

On the Messages API, the parameter is `output_config.format`, the generally available form. The older top-level `output_format` parameter is deprecated. The Agent SDK's `outputFormat` option (TypeScript) and `output_format` option (Python) belong to the Agent SDK and take the schema as `{ type: "json_schema", schema }`. The finished result then carries the validated value on `structured_output`.

```typescript
const schema = z.toJSONSchema(ReviewSchema, { target: "draft-7" });

for await (const msg of query({
  prompt: "Review auth.ts and return the verdict.",
  options: { outputFormat: { type: "json_schema", schema } },
})) {
  if (msg.type === "result" && msg.subtype === "success") console.log(msg.structured_output);
}
```

Zod schemas convert to JSON Schema with `z.toJSONSchema(schema, { target: "draft-7" })`, because the SDK validates against draft-07. If the model cannot satisfy the schema, the run ends with the subtype `error_max_structured_output_retries`.

Three rules of thumb decide which control you want:

- Need a guaranteed **shape**, no tool involved: Structured Outputs.
- Need a guaranteed **tool call**: `tool_choice`.
- Need to reject bad output at your own boundary and throw: Zod, after the fact.

#### Enum Design for Ambiguous Input

A schema that offers only `["positive", "negative", "neutral"]` gives the model nowhere to put a sarcastic review, so it guesses and your analytics inherit the noise. Adding an explicit `"unclear"` value gives ambiguity a home and makes it filterable. The general rule: every enum that classifies real-world text needs an escape value, or the model will silently smear ambiguous cases across the ones you did define.

#### Validation Belongs in Your Code

When a number has to be right, extract the inputs and compute in your own code, so the arithmetic never depends on the model. For a purchase order, extract the line items and the printed total as separate fields, sum the items in application code, and compare. That detects both a misprinted document and a bad extraction, and neither result depends on the model doing math correctly.

#### Retry With the Error Attached

Schema validation failures are usually recoverable, because the source document still contains what the model needs and the validator already knows exactly what went wrong. Feed the specific violation back ("expected an array of objects, received a single object") and the retry generally succeeds. The exception is a field that is genuinely absent from the source: no amount of retrying invents it, so log the failure, halt the loop, and flag the document.

### The Message Batches API

The Batches API processes large request sets asynchronously at roughly half the cost of synchronous calls. The trade is a completion window of **up to 24 hours** with no latency SLA inside it, and no way to expedite a submitted batch.

That single property decides every design question around it.

| Workload | Batch? | Why |
|---|---|---|
| Reprocessing 5 million legacy records overnight | Yes | Nobody is waiting; the discount is the point |
| Inline code completion in an IDE | No | A blocking, keystroke-latency workflow |
| Nightly documentation regeneration | Yes | Deadline is the next morning, measured in hours |
| A support bot answering a live user | No | The user is on the other end of the wait |

Because you cannot predict when a batch lands, do not promise stakeholders a completion time, and do not schedule a downstream job against an estimate. Poll the batch status and trigger the next stage from the completion event.

The cost profile also changes how you develop. A $10,000 batch run that fails on a prompt defect costs $10,000 to repeat, so refine the prompt against a stratified sample of a thousand records on the synchronous API first. Two days of iteration up front is cheap against one wasted full run, and the sample is where you discover the edge cases that would otherwise fail silently at scale.

## Discussion Prompt

```text
Compare the Messages API and the Agent SDK.
What disappears from your code when you switch from Messages API to Agent SDK?
When would that tradeoff go the wrong way?
```

## Exploration Prompt

```text
Install @anthropic-ai/claude-agent-sdk and write the smallest possible program
that calls query(), streams the response, and logs the raw event objects
(every field included) so you can see every message type the loop produces.

Then write one script that extracts {name, title} pairs from a block of text three
ways: prompt-and-parse, tool_choice forcing a single extraction tool, and
output_config.format with a JSON schema. Feed all three a deliberately ambiguous
input and print which ones produced schema-valid output.
```

## Helpful Claude Slash Commands

| Command | Usage |
|---|---|
| `/claude-api` | Scaffold, debug, or optimize Agent SDK and Messages API code, and look up the current `tool_choice` and `output_config` shapes before hand-writing a request body |
| `/simplify` | Tighten the SDK integration code and demo scripts after the live run, removing abstractions the prototype does not need |
| `/security-review` | Audit the CI script and the retry loop before they reach a real pipeline or a paid batch endpoint |
| `/cost` | Compare a synchronous prototype run against the batch price before committing a large job |

## Key Topics covered in this module

- [Claude Agent SDK documentation](https://code.claude.com/docs/en/agent-sdk/overview): `query()`, message types, permission modes, and the agent loop internals
- [Sessions](https://code.claude.com/docs/en/agent-sdk/sessions): `resume`, `continue`, and forking a session
- [Structured Outputs in the Agent SDK](https://code.claude.com/docs/en/agent-sdk/structured-outputs): `outputFormat`, `structured_output`, and the draft-07 schema target
- [Claude Agent SDK (npm)](https://www.npmjs.com/package/@anthropic-ai/claude-agent-sdk): Package details and release history
- [Zod](https://zod.dev): Schema validation for typed output in the CI script
- [Messages API Reference](https://platform.claude.com/docs/en/api/messages): The lower-level alternative and what the SDK wraps
- [Tool use and `tool_choice`](https://platform.claude.com/docs/en/build-with-claude/tool-use): the four values, forced calls, and the loop that `any` causes
- [Structured Outputs on the Messages API](https://platform.claude.com/docs/en/build-with-claude/structured-outputs): `output_config.format`, constrained decoding, and schema support
- [Message Batches API](https://platform.claude.com/docs/en/build-with-claude/batch-processing): the 24-hour window, pricing, and status polling
