# Embed Claude in a TypeScript Program

Use the [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-typescript) to spawn Claude from inside your own program. One-shot calls, streaming, session resume, custom tools, typed output schemas, and wiring into a CI script.

Each step contains:
- **Goal**: what you are building
- **Prompt or command**: what you run
- **Expected result**: what the outcome looks like

> **This lab costs money.** Every `query()` call in every step is a billed API request against your own account. You need an `ANTHROPIC_API_KEY` from [the Claude Console](https://platform.claude.com), and each step you run draws down its balance. Step 5 asks you to run one script three times, and Step 3 makes two calls. Budget accordingly, and delete the key when you are done with the lab.

> **Naming reminder:** Alexander's module is titled "Claude Code SDK." Anthropic renamed it to the **Claude Agent SDK**, and the npm package is `@anthropic-ai/claude-agent-sdk`. Same product, current name. See the [migration guide](https://code.claude.com/docs/en/agent-sdk/migration-guide) if you are upgrading from older code.

Work in [`01-embed/sdk-embed/`](01-embed/sdk-embed); the finished result is beside it in [`01-embed/sdk-embed-solution/`](01-embed/sdk-embed-solution). Write each step yourself; open the solution when a step will not compile.

---

## Where to Open Claude Code

This lab builds its own harness, so open Claude Code inside the lab project. The harness is project-scoped: `CLAUDE.md`, `.claude/settings.json` hooks, `.claude/agents/`, `.claude/skills/`, `.claude/commands/` and `.mcp.json` all load from the directory the session was launched in. A session opened at the repo root leaves everything you write here inert, with no error to tell you.

The starter is already in this repo, so there is nothing to scaffold: change into it and start the session there. Run this from the repo root; both commands work unchanged in PowerShell.

```bash
cd labs/10-sdk-managed-agents/01-embed/sdk-embed
claude
```

If you start Claude Code with the Claude Terminal extension (`Ctrl+F1` / `Cmd+F1`), it opens in the VS Code workspace folder and reuses an already-open terminal, so it will not follow the `cd` above. Open `sdk-embed` as the workspace folder (**File > Open Folder**) before pressing the shortcut, or run the commands above in a plain terminal.

> Note: you can also skip the folder switch entirely and name the path in the prompt, working from a session opened anywhere in the repo:

```text
In labs/10-sdk-managed-agents/01-embed/sdk-embed create src/01-oneshot.ts, a single query() call that logs the cost and the token counts ....
```

That works for every step whose result is just files, and here that is all of them: this lab writes no `.claude/skills/`, no `.claude/settings.json` hooks, no `.claude/commands/`, no `.claude/agents/` and no `.mcp.json`, so nothing depends on the launch directory. The terminal work does: `npm install`, `npm run step src/<file>.ts` and `scripts/ci.sh` expect a shell sitting in `sdk-embed/`, and the five `../` in the dotenv loader are counted from `src/` inside it. Launch inside `sdk-embed` from Step 1 onward.

Launching inside the starter makes the repository a monorepo to this lab: the repo's own `/CLAUDE.md`, `/.claude/` and `/.mcp.json` stay out of the session. You read them from the repo root without ever writing into them, and every path in the prompts below is relative to the lab folder.

The programs themselves need no Claude session at all: you run every step with `npm run step src/<file>.ts`, and the SDK opens its own sessions from inside your Node process. The session above is simply where you write and edit them, scoped so that `node_modules/` and the generated `src/` stay out of the repository's own harness.

---

## Setup: Install the Starter

You need **Node 20.6 or later**. The SDK itself declares `engines: { "node": ">=18.0.0" }`, but the labs pin 20.6 as a modern floor; the solution was verified on Node 24.15.0 with npm 11.12.1.

The starter ships `package.json`, `tsconfig.json` and `.gitignore` and nothing else, so every file under `src/` and `scripts/` is yours to write. From inside `sdk-embed/`, install the dependencies and confirm the toolchain resolves:

```bash
npm install
npx tsc --version
```

Both commands are identical in git-bash and PowerShell. Only Step 6 needs a shell-specific form, and it says so.

The dependency list is already in `package.json`, including `zod`, which Step 5 needs and Lab 02 needs from its very first step:

```json
{
  "dependencies": {
    "@anthropic-ai/claude-agent-sdk": "^0.3.302",
    "dotenv": "^17.4.2",
    "zod": "^4.4.3"
  },
  "devDependencies": {
    "@types/node": "^26.1.1",
    "tsx": "^4.23.1",
    "typescript": "^7.0.2"
  }
}
```

The shipped `package.json` also fills in `description`, `license` and `engines`. Step 6 builds an auditor that flags exactly those as missing, so having them is what makes a clean baseline reachable.

The shipped `tsconfig.json` carries an `include` so `tsc` only ever compiles `src/`:

```json
{
  "include": ["src/**/*.ts"]
}
```

Without that line `tsc` falls back to its default `**/*` glob. It costs nothing here, and it is what stops Lab 02 from failing with `TS6059: File 'target/auth.ts' is not under 'rootDir'` when you copy this same `tsconfig.json` across.

The key lives outside this project. Every script here loads it from the repository's own `demos/10-sdk-managed-agents/.env`, resolved from the script's own location rather than from whatever directory you happen to be in:

```ts
import { config } from "dotenv";
import { fileURLToPath } from "node:url";

config({ path: fileURLToPath(new URL("../../../../../demos/10-sdk-managed-agents/.env", import.meta.url)), quiet: true });
```

That file holds a single line, `ANTHROPIC_API_KEY=sk-ant-api03-...`, and it is gitignored. Nothing has to be exported into the shell and no key is copied into the lab folder. The five `../` steps climb from `src/` out to the repository root, one for each of `sdk-embed`, `01-embed`, `10-sdk-managed-agents` and `labs`, then down into `demos/10-sdk-managed-agents/`. Anchoring on `import.meta.url` is what makes it independent of the working directory; a bare `import "dotenv/config"` only ever looks in the current one.

The artifacts are already ignored. The shipped `.gitignore` covers `node_modules/`, `dist/`, `.env` and `.session-id.txt`, so nothing you generate here reaches the repository.

Every program in this lab starts with that `config({ path: ... })` call, which is the single mechanism that loads the key. The `step` script in `package.json` is a bare `tsx`; do not add `--env-file=...` to it. `--env-file` is a hard failure when the file is absent (`node: .env: not found`, exit code 9), whereas `dotenv` shrugs and moves on. That difference is what lets the same script run in CI, where no `.env` is ever checked out and the key arrives as an environment variable instead.

**Expected result:** `npm install` reports `found 0 vulnerabilities` and `npx tsc --version` prints `Version 7.0.2`. You have a TypeScript project with the SDK installed, reading the API key straight out of `demos/10-sdk-managed-agents/.env`. Run `npm run step src/<file>.ts` after each step; npm appends the path straight through to `tsx`, no `--` separator needed.

---

## Step 1: One-Shot Query

**Goal:** Spawn Claude for a single question and print the response. The smallest possible SDK invocation.

**Prompt:**

```text
Create src/01-oneshot.ts. It should:

  1. Start with the dotenv loader from Setup, the config({ path: ... }) call
     that resolves demos/10-sdk-managed-agents/.env from import.meta.url.
  2. Import { query } from "@anthropic-ai/claude-agent-sdk".
  3. Call query({ prompt: "What's the most important habit for an engineer to develop in their first year? Answer in three short bullets." })
  4. Iterate the returned value with for await. It is an AsyncGenerator of SDKMessage.
     For each message log message.type. When message.type === "assistant",
     loop message.message.content and log block.text for blocks where block.type === "text".
  5. When message.type === "result", log message.total_cost_usd,
     message.usage.input_tokens and message.usage.output_tokens.

Use top-level await. No error handling needed, let exceptions surface.
```

Those three result fields are the real ones. `total_input_tokens`, `total_output_tokens` and a bare `cost` do not exist on `SDKResultMessage`; using them fails the build with three `TS2339` errors. Token counts live one level down, on `usage`.

Run it:

```bash
npm run step src/01-oneshot.ts
```

**Expected result:** Claude's three-bullet answer prints to stdout, bracketed by the message types the SDK emitted along the way. The final three lines show the cost in USD and the input and output token counts. You have embedded Claude into a TypeScript program in under 30 lines.

---

## Step 2: Streaming the Response

**Goal:** Render the assistant's text incrementally so the user sees output as it generates, before the turn finishes.

**Prompt:**

```text
Create src/02-stream.ts that:

  1. Starts with the dotenv loader from Setup.
  2. Calls query() with prompt "Explain how a B-tree index works. Be thorough."
     and options: { includePartialMessages: true }
  3. Iterates the result. For messages where message.type === "stream_event",
     read message.event; when event.type === "content_block_delta" and
     event.delta.type === "text_delta", write event.delta.text to
     process.stdout.write (no console.log, it adds newlines).
  4. When message.type === "result", write a newline and then log message.total_cost_usd.
```

`includePartialMessages: true` is the part that makes this different from Step 1. Assistant messages arrive as complete turns, so iterating them alone would just print the whole block at once. Incremental text only exists on the `stream_event` message type, and the SDK only emits it when you ask for it.

Run:

```bash
npm run step src/02-stream.ts
```

**Expected result:** Text arrives in chunks as the model generates it, then a newline and the cost. This is how chat UIs feel responsive even on slow responses.

---

## Step 3: Session Resume

**Goal:** Multi-turn conversations. Every SDK message carries a `session_id` you can pass back to continue where you left off.

**Prompt:**

```text
Create src/03-session.ts that:

  1. Starts with the dotenv loader from Setup.
  2. Makes a first query: "I'm designing a URL shortener. The traffic profile is
     10k reads/sec, 100 writes/sec. What storage would you start with?"
  3. Streams the assistant text to stdout.
  4. Captures message.session_id from the result message.
  5. Writes that session id to .session-id.txt with node:fs writeFileSync.

Create src/03-followup.ts that:

  1. Starts with the dotenv loader from Setup.
  2. Reads .session-id.txt and trims it.
  3. Calls query() with prompt "What changes if writes go up to 5k/sec?" and
     options: { resume: sessionId, includePartialMessages: true }
     (options.resume is typed as `resume?: string` and takes the session id).
  4. Streams the response using the stream_event pattern from Step 2.
```

Run:

```bash
npm run step src/03-session.ts
npm run step src/03-followup.ts
```

**Expected result:** `.session-id.txt` appears after the first script, and the follow-up answer references decisions from the first turn ("Postgres would handle 10k/100 fine, but at 5k writes you'd want..."). That back-reference is your proof the session rehydrated with prior context. The file is just the persistence handle; a real chat app would keep it in a database.

---

## Step 4: Register a Custom Tool

**Goal:** Define a tool Claude can call, in your own process. Add a `current_weather` tool that returns mocked data and let Claude decide when to call it.

The `options.tools` option is typed `tools?: string[] | { type: "preset"; preset: "claude_code" }` and it only selects which **built-in** tools are available. Custom tools go through an in-process MCP server: `tool()` defines one, `createSdkMcpServer()` wraps a set of them, `options.mcpServers` registers the server, and `options.allowedTools` permits the namespaced name. See [custom tools](https://code.claude.com/docs/en/agent-sdk/custom-tools) for the full surface.

**Prompt:**

```text
Create src/04-custom-tool.ts:

  1. Import { createSdkMcpServer, query, tool } from "@anthropic-ai/claude-agent-sdk",
     plus { z } from "zod", then the dotenv loader from Setup.
  2. Define the tool with the tool() helper, which takes four arguments:
     name, description, a Zod raw shape for the input, and an async handler.

       const currentWeather = tool(
         "current_weather",
         "Returns the current weather for a given city.",
         { city: z.string().describe("City name, for example Berlin") },
         async ({ city }) => ({
           content: [{
             type: "text" as const,
             text: JSON.stringify({ city, temperature_c: 18, conditions: "cloudy", humidity: 0.62 }),
           }],
         }),
       );

     The handler RETURNS the data. You never reply to a tool_use message yourself.
  3. Wrap it: const weatherServer = createSdkMcpServer({ name: "weather", version: "1.0.0", tools: [currentWeather] });
  4. Call query() with prompt "Should I pack a jacket if I'm flying to Berlin tomorrow
     morning? And to Madrid? Use the current_weather tool." and options:
       { mcpServers: { weather: weatherServer },
         allowedTools: ["mcp__weather__current_weather"],
         tools: [] }
     The tool name is namespaced mcp__<server>__<tool>. Setting tools: []
     turns off the built-in tools so Claude can only reach yours.
  5. To make the round trip visible, log block.name and block.input for assistant
     content blocks where block.type === "tool_use", and log block.content for
     content blocks on "user" messages where block.type === "tool_result".
  6. Log message.total_cost_usd on the result message.
```

Run:

```bash
npm run step src/04-custom-tool.ts
```

**Expected result:** Two `tool_use` lines appear (Berlin, then Madrid), each followed by the `tool_result` your handler produced, and then Claude's final answer reasoning over both. Whether Claude calls the tool once, twice, or not at all is the model's decision; the logging makes the whole round trip observable when it does.

---

## Step 5: Typed Output Schema

**Goal:** Force Claude's output into a typed shape so downstream code can consume it without parsing prose.

**Prompt:**

```text
Create src/05-typed-output.ts that extracts structured data from a free-form
incident report and returns it as JSON matching a strict schema.

Define a Zod schema:

  const IncidentSchema = z.object({
    severity: z.enum(["P0", "P1", "P2", "P3"]),
    affected_services: z.array(z.string()),
    customer_facing: z.boolean(),
    eta_minutes_to_resolution: z.number().int().nullable(),
    one_line_summary: z.string(),
  });

Write a 4-5 sentence incident report as a template literal (make one up: an
outage with a cause, blast radius and an ETA).

Call query() with a prompt that embeds the report, states the exact JSON shape
inline, and says "Return ONLY a JSON object, no prose and no code fence." Pass
options: { systemPrompt: "You are a data extraction service. You reply with a
single JSON object and nothing else.", tools: [] }.

Accumulate the assistant text blocks into one string. Then:
  1. Strip an optional markdown fence before parsing. Models wrap JSON in ```json
     often enough that a bare JSON.parse will eventually throw
     SyntaxError: Unexpected token '`'. Use:
       raw.trim().replace(/^```(?:json)?\s*/i, "").replace(/```$/i, "")
  2. JSON.parse the stripped text.
  3. Validate with IncidentSchema.parse, which throws on a malformed response.
  4. Log the typed object. TypeScript infers the field types from the schema
     via z.infer<typeof IncidentSchema>.

Run the script 3 times with the same report and confirm the parsed objects are
structurally identical, even though the wording may vary.
```

Run:

```bash
npm run step src/05-typed-output.ts
```

**Expected result:** Three runs produce three Zod-validated `Incident` objects with the same keys and types. The schema parse is a typed contract: if Claude ever returns malformed JSON, the script throws at a clear boundary before bad data reaches anything downstream.

Worth knowing once you have felt the manual version: the SDK also has a first-class option for this. `options.outputFormat: { type: "json_schema", schema }` makes the SDK enforce the shape and retry malformed output for you, and the parsed value comes back on `result.structured_output`. When the retries run out, the result subtype is `error_max_structured_output_retries`. Reach for that in production; the Zod exercise above is the honest way to see where the validation boundary sits.

---

## Step 6: Wire Into a CI Script

**Goal:** Use the SDK as a CI step that fails meaningfully when its check finds a problem. The building block for any agent-augmented CI workflow.

**Prompt:**

```text
Create src/06-ci-check.ts, a script that audits package.json and exits non-zero
if it finds issues.

  1. Start with the dotenv loader from Setup; read package.json from the cwd.
  2. Define a Zod schema:
       const AuditSchema = z.object({
         issues: z.array(z.string()),
         severity: z.enum(["pass", "warn", "fail"]),
       });
  3. Pass the file contents to query() with the prompt: "Audit this package.json
     for issues. Return ONLY JSON: { issues: string[], severity: 'pass' | 'warn'
     | 'fail' }. Issues to flag: unused dependencies (best-effort), missing
     description, missing license, very old dependency versions, missing engines
     field." Pass options: { systemPrompt: "You are a package.json auditor. You
     reply with a single JSON object and nothing else.", tools: [] }.
  4. Strip the optional markdown fence, JSON.parse, then AuditSchema.parse.
  5. Print each issue on its own line, then the severity.
  6. Exit 0 for 'pass', 1 for 'warn', 2 for 'fail'.

Also create scripts/ci.sh that runs `npx tsx src/06-ci-check.ts` and propagates
its exit code.

Then delete the "description" field from package.json, run ci.sh, and confirm a
non-zero exit. Restore the field and run it again.
```

The starter's `package.json` already carries a `description`, a `license` and an `engines` field, which are three of the five things the auditor is told to flag. That is deliberate: without them the audit can never come back clean and the exit code would be stuck above zero no matter what you did.

Run it in **git-bash or WSL**:

```bash
chmod +x scripts/ci.sh
./scripts/ci.sh
echo "exit: $?"
```

PowerShell cannot do either half of that. `chmod` is not a cmdlet, and `& ./scripts/ci.sh` fails with `InvalidOperation: Cannot run a document in the middle of a pipeline`. Invoke git-bash by its full path instead, because a bare `bash` in PowerShell resolves to `C:\Windows\system32\bash.exe`, which is WSL and will not have your Node install on its PATH:

```powershell
& "C:\Program Files\Git\bin\bash.exe" scripts/ci.sh
"exit: $LASTEXITCODE"
```

The chmod bit is cosmetic on Windows; invoking the interpreter explicitly works without it.

**Expected result:** The severity is the model's call, so read the exit code as a branch the model chooses. `0` means the auditor found nothing worth reporting, `1` that it found something it rates as a warning, `2` that it rates the package.json as failing. Removing `description` should push it off `0`; on the verified run it printed the missing field plus two extra observations and exited `1`, and restoring the field brought it back to `severity: pass` and exit `0`. A run that lands on `2` instead is the same mechanism working, just a harsher rating.

The exit code is the contract and stdout is the human-readable detail, which is all a CI runner needs, whether that is an npm script, a GitHub Action step, or a Jenkins stage.

---

## What You Just Practised

| Mechanic | Step | What it gives you |
|---|---|---|
| `query()` one-shot over an async generator | 1 | The minimum SDK invocation, Claude embedded in 30 lines |
| `includePartialMessages` and `stream_event` deltas | 2 | Responsive UX for chat-shaped applications |
| `options.resume` with a captured `session_id` | 3 | Multi-turn conversations across separate script runs |
| `tool()` plus `createSdkMcpServer()` and `allowedTools` | 4 | Claude calls your code, your code returns data, Claude reasons further |
| Fence-stripping plus Zod validation | 5 | A type-safe contract between Claude and downstream code |
| Exit-code wrapping | 6 | A drop-in CI step with meaningful pass, warn and fail |

The official [`agent-sdk-dev`](https://github.com/anthropics/claude-code/tree/main/plugins/agent-sdk-dev) plugin scaffolds these patterns automatically with `/new-sdk-app` and verifies them with the `agent-sdk-verifier-ts` and `agent-sdk-verifier-py` agents. Use it once you have built the same patterns by hand and know what it is generating.

[Lab 02](lab-02-parallel-sdk-agents.md) takes the SDK further into parallel orchestration: three reviewer agents running in isolated sessions, and an orchestrator that reconciles their outputs.
