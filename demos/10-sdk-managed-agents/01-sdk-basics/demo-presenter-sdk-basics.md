---
presents: demo-messages-api-to-sdk.md
budget: 4 min
beats: 4
---

# Present: Migrate from Messages API to Agent SDK

What the Agent SDK removes, and what it asks for in return. Four beats: the tool loop that disappears, the in-process MCP server, the `options.tools` trap, the exit code CI branches on.

------

The only file this demo's run adds is [`sdk-basics-solution/02-tool-call.ts`](sdk-basics-solution/02-tool-call.ts); beats 1 and 4 rest on the starter scripts and the runs the source guide records.

## Beats

### Beat 1: the tool loop is the code you stop writing (1 min)

**Open:** [Part A: Before/After Contrast](demo-messages-api-to-sdk.md#part-a-beforeafter-contrast-5-min) · [`sdk-basics/demo-01-stream.ts`](sdk-basics/demo-01-stream.ts) · the `query()` call and the `SIGINT` handler
**Say:** The Messages API hands back one response at a time, so the loop, the dispatcher and the growing message array are yours to maintain. The SDK owns that loop, which makes the migration mostly deletion.

```typescript
while (response.stop_reason === "tool_use") {
  const call = response.content.find((b) => b.type === "tool_use");
  const result = await dispatch(call.name, call.input);
  messages.push({ role: "assistant", content: response.content });
  messages.push({ role: "user", content: [{ type: "tool_result", tool_use_id: call.id, content: result }] });
  response = await client.messages.create({ model, max_tokens, tools, messages });
}
```

**Result:** no artifact, the deletion is the result: `01-stream-response.ts` is the starter script unchanged

```typescript
  for await (const msg of query({
    prompt: "Explain how a B-tree index works. Be thorough.",
    options: {
      maxTurns: 1,
      abortController,
    },
  })) {
    if (msg.type === "assistant") {
```

**Gotcha:** text arrives as whole assistant messages; character deltas need `includePartialMessages: true`.

### Beat 2: a custom tool is a Zod shape wrapped in an in-process MCP server (1 min)

**Open:** [Custom Tools](readme.md#custom-tools) · [Part B: Custom Tool](demo-messages-api-to-sdk.md#part-b-custom-tool-8-min)
**Say:** Custom tools reach Claude through MCP, but this server runs inside your own program with no transport to configure. Read MCP here as a namespace and a grouping device.

```typescript
const currentWeather = tool(
  "current_weather",
  "Returns current weather for a city.",
  { city: z.string().describe("City name, for example Berlin") },
  ...
);

const weatherServer = createSdkMcpServer({
  name: "weather",
  version: "1.0.0",
  tools: [currentWeather],
});
```

**Result:** [`sdk-basics-solution/02-tool-call.ts`](sdk-basics-solution/02-tool-call.ts) and its `npm run tool-call` run from Part B, each `[tool]` line printed by the handler in this process

```text
[tool_use] mcp__weather__current_weather {"city":"Berlin"}
[tool] current_weather(Berlin) -> 8 C, light rain, wind 22 km/h
[tool_use] mcp__weather__current_weather {"city":"Madrid"}
[tool] current_weather(Madrid) -> 24 C, sunny, wind 6 km/h
```

**Gotcha:** `tool()` takes a Zod shape, and `createSdkMcpServer()` spawns nothing.

### Beat 3: `options.tools` is the wrong knob, and the allowlist name is namespaced (1 min)

**Open:** [Permission Modes](readme.md#permission-modes) · [`sdk-basics/package.json`](sdk-basics/package.json) · its `weather` script
**Say:** Two fields both look like the place a tool goes and only one registers anything. Picking wrong raises no error: the tool is simply never offered.

```typescript
    options: {
      tools: [],
      mcpServers: { weather: weatherServer },
      allowedTools: ["mcp__weather__current_weather"],
      permissionMode: "acceptEdits",
      maxTurns: 6,
      abortController,
    },
```

**Result:** no new file; beat 2's `[tool_use]` lines carry the allowlisted name, and `maxTurns: 6` covers that run's two tool calls plus the answer

**Gotcha:** `tools` selects built-in tools only; `tools: []` switches them off and leaves the custom tool as the only one Claude can reach.

### Beat 4: the exit code is the contract, everything else is detail (1 min)

**Open:** [`sdk-basics/demo-01-ci.ts`](sdk-basics/demo-01-ci.ts) · `EXIT_CODES`, the parse-then-exit lines and `process.argv[2]` · [Typed Output with Zod](readme.md#typed-output-with-zod)
**Say:** A model answers in prose and CI cannot branch on prose. Zod checks the answer at the boundary, and the verdict picks the exit code.

```typescript
const EXIT_CODES: Record<string, number> = { pass: 0, comment: 1, block: 2 };
...
  const result = AuditSchema.parse(JSON.parse(match[0]));
  console.log(JSON.stringify(result, null, 2));
  process.exit(EXIT_CODES[result.verdict] ?? 1);
```

**Result:** no file, only the exit code; Part C records the run on the shipped `package.json`

```json
{
  "severity": "none",
  "findings": [],
  "verdict": "pass"
}
```

Remove `description` and re-run, or run `npm run audit-code -- <path>`: 0 lets CI proceed, 1 posts findings, 2 stops it. Close on [Structured Outputs](readme.md#structured-outputs-guaranteeing-the-shape): `outputFormat` enforces this shape up front.

**Gotcha:** a parse failure lands in `main().catch` and exits 1, the same code as `comment`, so CI cannot tell a malformed answer from findings.

## If the room asks

| Question | Answer |
|---|---|
| I put my tool in `options.tools` and Claude never called it. | That field selects built-in tools only. Custom tools go in `options.mcpServers`, allowlisted as `mcp__<server>__<tool>`. |
| Why `maxTurns: 1` and empty tool lists in the CI script? | A one-shot audit that must answer in JSON: no tool loop wanted, nothing to approve. |
| Why does every script pass an `abortController` and exit 130? | Ctrl-C aborts `query()` through it; 130 is the conventional code for a SIGINT kill, and an `AbortError` maps to it too. |

## Runs live instead

A learner writes `demo-01-weather.ts` in [`sdk-basics/`](sdk-basics) and runs all three scripts: [demo-messages-api-to-sdk.md](demo-messages-api-to-sdk.md).
