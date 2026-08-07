# Migrate from Messages API to Agent SDK

The Agent SDK owns the tool loop that the Messages API makes you write by hand, and this demo walks the progression in four parts from a streaming `query()` call to a CI exit-code script. You read the two shapes side by side, run the scripts from [`02-api-surface/sdk-basics/`](sdk-basics/), and write the custom weather tool yourself as an in-process MCP server. You end up holding a working `query()` loop, a registered custom tool, and a Zod-validated verdict that maps to exit codes 0, 1 and 2.

------

You need Node 18 or newer and working Claude credentials: either a logged-in `claude` CLI or your key in `.env` at the module root, which the script loads itself (see the [module readme](../readme.md)).

```bash
cd demos/13-claude-sdk/02-api-surface/sdk-basics
npm install
```

The `sdk-basics/` folder is the starter you edit. The finished reference, with the Part C tool already wired up and a committed lockfile, is the sibling folder [`sdk-basics-solution/`](sdk-basics-solution/).

### Part A: Before/After Contrast (5 min)

Read the two versions side by side. First the Messages API shape: a `while` loop on `stop_reason === "tool_use"`, a manual tool dispatcher, and explicit context accumulation.

```typescript
let messages = [{ role: "user", content: prompt }];
let response = await client.messages.create({ model, max_tokens, tools, messages });

while (response.stop_reason === "tool_use") {
  const call = response.content.find((b) => b.type === "tool_use");
  const result = await dispatch(call.name, call.input);
  messages.push({ role: "assistant", content: response.content });
  messages.push({ role: "user", content: [{ type: "tool_result", tool_use_id: call.id, content: result }] });
  response = await client.messages.create({ model, max_tokens, tools, messages });
}
```

Now the Agent SDK version, which is the core of [`sdk-basics/demo-01-stream.ts`](sdk-basics/demo-01-stream.ts) (the file wraps it in `main()` and adds the `.env` load, an `AbortController` and a `SIGINT` handler around it):

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

### Part B: query() + Streaming (8 min)

Run `npm run stream`. The text arrives as whole assistant messages, not as character deltas: the SDK only emits `SDKPartialAssistantMessage` events when you set `includePartialMessages: true` in the options. Then drop the `block.type === "text"` filter and `console.log(msg)` in its place, so you see the raw event objects rather than the prose.

```bash
npm run stream
```

With `maxTurns: 1` and no tools in play, the loop produces a `system` init message, one or more `assistant` messages, and a final `result` message carrying `session_id`, cost and token usage. See [`02-api-surface/sdk-basics/demo-01-stream.ts`](sdk-basics/demo-01-stream.ts) for the implementation. Its prompt is deliberately broad so the answer is long enough to watch arrive:

```text
Explain how a B-tree index works. Be thorough.
```

### Part C: Custom Tool (8 min)

Custom tools are not passed in `options.tools`: that field selects which built-in tools are available. Define the tool with `tool()`, wrap it in an in-process MCP server with `createSdkMcpServer()`, and register that server under `options.mcpServers`. The tool then reaches Claude under the namespaced name `mcp__weather__current_weather`, which is what you allowlist.

Write this one as `demo-01-weather.ts` next to the other two scripts; the `weather` script in `package.json` already points at that filename.

```typescript
const currentWeather = tool(
  "current_weather",
  "Returns current weather for a city.",
  { city: z.string().describe("City name, for example Berlin") },
  async ({ city }) => ({ content: [{ type: "text", text: lookup(city) }] })
);

const weatherServer = createSdkMcpServer({ name: "weather", version: "1.0.0", tools: [currentWeather] });

for await (const msg of query({
  prompt,
  options: {
    tools: [],
    mcpServers: { weather: weatherServer },
    allowedTools: ["mcp__weather__current_weather"],
    permissionMode: "acceptEdits",
    maxTurns: 6,
  },
})) {
  // consume the stream
}
```

`tools: []` switches off the built-in tools, so the only tool left is the custom one. Use this prompt to force two tool calls:

```text
Should I pack a jacket if I'm flying to Berlin and Madrid tomorrow? Use the current_weather tool for each city.
```

Claude calls `current_weather` for Berlin and for Madrid, gets the mocked readings back, then composes the answer. Both calls are visible as content blocks with `block.type === "tool_use"` inside the assistant messages, one call per turn, which is why `maxTurns: 6` leaves room for two calls plus the answer. The completed script is [`sdk-basics-solution/demo-01-weather.ts`](sdk-basics-solution/demo-01-weather.ts), run with `npm run weather`:

```text
I'll check both cities.
[tool_use] mcp__weather__current_weather {"city":"Berlin"}

[tool] current_weather(Berlin) -> 8 C, light rain, wind 22 km/h

[tool_use] mcp__weather__current_weather {"city":"Madrid"}

[tool] current_weather(Madrid) -> 24 C, sunny, wind 6 km/h
Yes. Berlin is 8 C with light rain and 22 km/h wind, so you want a jacket there, ideally a waterproof one. Madrid is 24 C and sunny, where you won't need it beyond maybe the evening.
```

### Part D: CI Exit Code (4 min)

Run `npm run ci`. The script reads `package.json`, sends it to Claude with a JSON schema constraint, validates the response with Zod, and exits with code 0 (pass), 1 (comment), or 2 (block). See [`02-api-surface/sdk-basics/demo-01-ci.ts`](sdk-basics/demo-01-ci.ts) for the implementation.

```bash
npm run ci
```

```json
{
  "severity": "none",
  "findings": [],
  "verdict": "pass"
}
```

Now remove the `description` field from `package.json` and re-run. The audit reports the missing field, and the exit code follows whichever verdict Claude returns: `pass` exits 0 and CI proceeds, `comment` exits 1 and CI posts the findings without failing, `block` exits 2 and CI stops. Which of the three a given file earns is a model judgement, so read the number as the branch CI takes, never as a constant this file always produces.

The exit code is the contract between Claude and CI; everything else in the output is human-readable detail.
