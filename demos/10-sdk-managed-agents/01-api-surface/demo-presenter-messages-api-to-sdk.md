---
presents: demo-messages-api-to-sdk.md
budget: 4 min
beats: 4
---

# Present: Migrate from Messages API to Agent SDK

What the Agent SDK removes, and what it asks for in return. Four beats: the tool loop that disappears, the in-process MCP server, the `options.tools` trap, the exit code CI branches on.

------

The only file this demo's run adds is [`sdk-basics-solution/demo-01-weather.ts`](sdk-basics-solution/demo-01-weather.ts); beats 1 and 4 rest on the starter scripts and the runs the source guide records.

## Beats

### Beat 1: the tool loop is the code you stop writing (1 min)

**Open:** [Part A: Before/After Contrast](demo-messages-api-to-sdk.md#part-a-beforeafter-contrast-5-min) · [`sdk-basics/demo-01-stream.ts`](sdk-basics/demo-01-stream.ts)
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

**Result:** no artifact here, the deletion is the result: `demo-01-stream.ts` is 37 lines and byte-identical in starter and solution

```typescript
  for await (const msg of query({
    prompt: "Explain how a B-tree index works. Be thorough.",
    options: {
      maxTurns: 1,
      abortController,
    },
  })) {
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

**Result:** [`sdk-basics-solution/demo-01-weather.ts`](sdk-basics-solution/demo-01-weather.ts), the run's one new source file, whose handler is an ordinary async function in this process

```typescript
  async ({ city }) => {
    const reading = FORECASTS[city.toLowerCase()] ?? "no data for this city";
    console.log(`[tool] current_weather(${city}) -> ${reading}`);
    return { content: [{ type: "text", text: reading }] };
  },
```

**Gotcha:** `tool()` takes a Zod shape, and `createSdkMcpServer()` spawns nothing.

### Beat 3: `options.tools` is the wrong knob, and the allowlist name is namespaced (1 min)

**Open:** [Permission Modes](readme.md#permission-modes) · [`sdk-basics/package.json`](sdk-basics/package.json) · the `weather` script already points at the file the learner writes
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

**Result:** registration and selection landed on adjacent lines in [`sdk-basics-solution/demo-01-weather.ts`](sdk-basics-solution/demo-01-weather.ts)

```typescript
      mcpServers: { weather: weatherServer },
      allowedTools: ["mcp__weather__current_weather"],
```

**Gotcha:** `tools` selects built-in tools only, and `tools: []` switches them off, which is what leaves the custom tool as the only one Claude can reach.

### Beat 4: the exit code is the contract, everything else is detail (1 min)

**Open:** [`sdk-basics/demo-01-ci.ts`](sdk-basics/demo-01-ci.ts) · `EXIT_CODES` and the parse-then-exit lines · [Typed Output with Zod](readme.md#typed-output-with-zod)
**Say:** A model answers in prose and CI cannot branch on prose. Validating at the boundary leaves either a known shape or a loud failure.

```typescript
const EXIT_CODES: Record<string, number> = { pass: 0, comment: 1, block: 2 };
...
  const result = AuditSchema.parse(JSON.parse(match[0]));
  console.log(JSON.stringify(result, null, 2));
  process.exit(EXIT_CODES[result.verdict] ?? 1);
```

**Result:** no file, only the number the process exits with; Part C of the source guide records the run on the shipped `package.json`

```json
{
  "severity": "none",
  "findings": [],
  "verdict": "pass"
}
```

Remove the `description` field and re-run: the audit reports it, and the exit code follows the verdict Claude returns. `pass` exits 0 and CI proceeds, `comment` exits 1 and CI posts findings without failing, `block` exits 2 and CI stops. The verdict is a model judgement, so present the number as the branch CI takes.

**Gotcha:** `AuditSchema.parse` throws at the boundary, so a malformed verdict fails loudly before it can leak into the pipeline.

## If the room asks

| Question | Answer |
|---|---|
| I put my tool in `options.tools` and Claude never called it. | That field selects built-in tools only. Custom tools go in `options.mcpServers`, allowlisted as `mcp__<server>__<tool>`. |
| Does `createSdkMcpServer()` start a separate process? | No. The handler runs inside your program and there is no transport to configure. |
| Why `maxTurns: 1` and empty tool lists in the CI script? | A one-shot audit that must answer in JSON: no tool loop wanted, nothing to approve. |
