# Migrate from Messages API to Agent SDK

The Agent SDK owns the tool loop that the Messages API makes you write by hand, and this demo walks the progression from a streaming `query()` call to a CI exit-code script. You end up holding a working `query()` loop, a registered custom tool, and a Zod-validated verdict that maps to exit codes 0, 1 and 2.

------

Work in [`sdk-basics/`](sdk-basics) after `npm install`; the finished reference, with the weather tool already wired up, is [`sdk-basics-solution/`](sdk-basics-solution).

### Part A: Before/After Contrast (5 min)

Read the two versions side by side: first the Messages API shape with its `while` loop on `stop_reason === "tool_use"`, then the core of [`sdk-basics/demo-01-stream.ts`](sdk-basics/demo-01-stream.ts).

```typescript
while (response.stop_reason === "tool_use") {
  const call = response.content.find((b) => b.type === "tool_use");
  const result = await dispatch(call.name, call.input);
  messages.push({ role: "assistant", content: response.content });
  messages.push({ role: "user", content: [{ type: "tool_result", tool_use_id: call.id, content: result }] });
  response = await client.messages.create({ model, max_tokens, tools, messages });
}
```

```typescript
for await (const msg of query({ prompt, options: { maxTurns: 1 } })) {
  if (msg.type === "assistant") {
    for (const block of msg.message.content) {
      if (block.type === "text") process.stdout.write(block.text);
    }
  }
}
```

What disappears: the tool loop, the tool dispatcher, and the context accumulation. What remains: the prompt, the options object, and the event handler.

### Part B: Custom Tool (8 min)

Custom tools go in `options.mcpServers`, because `options.tools` selects which built-in tools are available. Define the tool with `tool()`, wrap it in an in-process MCP server with `createSdkMcpServer()`, and write it as `demo-01-weather.ts`; the finished script is [`sdk-basics-solution/02-tool-call.ts`](sdk-basics-solution/02-tool-call.ts).

```typescript
const currentWeather = tool(
  "current_weather",
  "Returns current weather for a city.",
  { city: z.string().describe("City name, for example Berlin") },
  async ({ city }) => ({ content: [{ type: "text", text: FORECASTS[city.toLowerCase()] ?? "no data for this city" }] })
);

const weatherServer = createSdkMcpServer({ name: "weather", version: "1.0.0", tools: [currentWeather] });
```

Run `npm run tool-call`; its prompt asks about a jacket for Berlin and Madrid and forces two tool calls:

```text
[tool_use] mcp__weather__current_weather {"city":"Berlin"}
[tool] current_weather(Berlin) -> 8 C, light rain, wind 22 km/h
[tool_use] mcp__weather__current_weather {"city":"Madrid"}
[tool] current_weather(Madrid) -> 24 C, sunny, wind 6 km/h
```

`tools: []` switches off the built-in tools, so the only tool left reaches Claude under the namespaced name `mcp__weather__current_weather`, which is what you allowlist.

### Part C: CI Exit Code (4 min)

Run `npm run audit-code`. The script reads `package.json`, sends it to Claude with a prompt that spells out the JSON schema, validates the response with Zod, and exits with code 0 (pass), 1 (comment), or 2 (block).

```json
{
  "severity": "none",
  "findings": [],
  "verdict": "pass"
}
```

Remove the `description` field from `package.json` and re-run: the exit code follows the verdict Claude returns, and that exit code is the contract between Claude and CI.
