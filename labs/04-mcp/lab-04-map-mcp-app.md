# Fly a 3D Globe with the Map MCP App

Build and run the Map MCP App, then use Claude Code to geocode landmarks and fly a 3D globe to their coordinates.

Each step follows the same pattern:

- **Overview**: what this step achieves
- **Research / Planning / Discussion**: an open prompt to reason through the problem before acting
- **Finding**: what to read and evaluate in Claude's response before moving on
- **Recipe**: a complete implementation prompt you can use as-is or adapt from your own findings
- **Expected Outcome**: observable artefacts that confirm success

---

## Introduction

This lab explores the Map server, an MCP App that gives Claude two chained geographic tools: `geocode` and `show-map`. Unlike a plain tool that returns text, an MCP App can render a full UI inside an MCP App-aware host. You will experience three capabilities the Map server demonstrates:

1. **Tool chaining**: `geocode` resolves a place name to coordinates; `show-map` consumes the bounding box directly. Claude chains both tools in a single conversational step.
2. **Stateless streaming HTTP**: the server handles each request on a fresh instance with no session state; tool calls are independent and can be issued in any order.
3. **MCP App resource**: the `show-map` tool definition carries a `ui://` resource URI pointing at the CesiumJS globe. MCP App-aware hosts fetch and render that resource; CLI hosts like Claude Code surface only the text content.

The map server runs over HTTP on a configurable port. It uses OpenStreetMap's Nominatim geocoding API (rate-limited to roughly one request per second) and CesiumJS loaded from CDN, so no API keys or accounts are required.

---

## Where to Open Claude Code

This lab builds its own harness, so open Claude Code inside the lab project rather than at the repo root. The harness is project-scoped: `CLAUDE.md`, `.claude/settings.json` hooks, `.claude/agents/`, `.claude/skills/`, `.claude/commands/` and `.mcp.json` all load from the directory the session was launched in. A session opened at the repo root leaves everything you write here inert, with no error to tell you.

The starter is already in this repo, so there is nothing to scaffold: change into it and start the session there. Run this from the repo root; both commands work unchanged in PowerShell.

```bash
cd labs/04-mcp/03-mcp-app/map-server
claude
```

If you start Claude Code with the Claude Terminal extension (`Ctrl+F1` / `Cmd+F1`), it opens in the VS Code workspace folder and reuses an already-open terminal, so it will not follow the `cd` above. Open `map-server` as the workspace folder (**File > Open Folder**) before pressing the shortcut, or run the command above in a plain terminal.

> Note: you can also skip the folder switch entirely and name the path in the prompt instead, working from a session opened anywhere in the repo:

```text
In labs/04-mcp/03-mcp-app/map-server read server.ts and describe the show-map input schema ....
```

That works for any step whose result is just files, such as reading the default bounding box that Step 6 asks about. It does not work for the server registration: the `.mcp.json` you create below loads from the directory the session was launched in, so a root session writes it into the lab folder and then ignores it, and neither `geocode` nor `show-map` ever appears in the tool list. Launch inside the starter from Step 1 onward.

Restart the session with `/exit` then `claude` after any edit to `.claude/settings.json` or `.mcp.json`, because both are read at startup.

Launching inside the starter is what makes the repository a monorepo to this lab rather than the project: the repo's own `/CLAUDE.md`, `/.claude/` and `/.mcp.json` stay out of the session. You read them from the repo root without ever writing into them, and every path in the prompts below is relative to the lab folder.

Keep a second terminal in the same folder for the build and for the running server: the steps below need both at once.

---

## Running the Lab Starter

The starter project is `labs/04-mcp/03-mcp-app/map-server`. The finished reference lives beside it at `labs/04-mcp/03-mcp-app/map-server-solution`: same sources, with dependencies installed and `dist/` already built. Work in the starter and open the solution only to compare.

### What the build requires

Node.js 20 or newer, plus **Bun**: the last two build stages call `bun build`. Bun is declared as a devDependency (`"bun": "^1.3.14"`), so `npm install` puts it in `node_modules/.bin` and npm scripts find it automatically. No global install is needed. Open a terminal in the `labs/04-mcp/03-mcp-app/map-server` folder:

```bash
npm install
npm run build
```

The build runs four stages: type-check the browser code with `tsc --noEmit`, bundle the CesiumJS globe into `dist/mcp-app.html` with Vite (about 354 kB), emit server declarations with `tsc -p tsconfig.server.json`, then produce `dist/server.js` and `dist/index.js` with two `bun build` passes. `dist/` is git-ignored and is never checked in, so the build must complete before `dist/index.js` exists.

### Start the server on port 3003

The port is read from the `PORT` environment variable. On Windows PowerShell (the primary shell in this repo):

```powershell
$env:PORT = 3003
node dist/index.js
```

On bash, zsh or WSL:

```bash
PORT=3003 node dist/index.js
```

Successful startup prints two lines. The first is a DNS-rebinding warning that is expected for local development; the second is the one that matters:

```text
Warning: Server is binding to 0.0.0.0 without DNS rebinding protection. Consider using the allowedHosts option to restrict allowed hosts, or use authentication to protect your server.
MCP server listening on http://localhost:3003/mcp
```

### No-build path

If Bun or the build gives you trouble, the same server is published to npm with `dist/` prebuilt, so `npx` runs it with no local build at all. PowerShell:

```powershell
$env:PORT = 3003
npx -y --registry=https://registry.npmjs.org/ @modelcontextprotocol/server-map
```

bash:

```bash
PORT=3003 npx -y --registry=https://registry.npmjs.org/ @modelcontextprotocol/server-map
```

This prints the same listening line and exposes the same `geocode` and `show-map` tools, so every step below works against it. Build the starter when you want to read and modify the source; use `npx` when you only want the tools.

### Register the server in Claude Code

Create `.mcp.json` in `labs/04-mcp/03-mcp-app/map-server/`, the folder you launched Claude Code in, with the `labs-mcp-map` entry:

```json
{
  "mcpServers": {
    "labs-mcp-map": {
      "type": "http",
      "url": "http://localhost:3003/mcp"
    }
  }
}
```

This file belongs to the lab. The repo root carries its own `.mcp.json` with an identical `labs-mcp-map` entry, but a session launched here does not read it, and you must not edit it.

Restart the session with `/exit` then `claude` so Claude Code reads the new file, then run `/mcp` to reload servers. That reload and every prompt below need a live, interactive Claude Code session; with the server running, `geocode` and `show-map` appear in the tool list.

---

## Step 1: Fly the Globe to a World Heritage Site

**Overview:** This step confirms that Claude can chain `geocode` and `show-map` in a single prompt to resolve a named landmark to coordinates and pass those coordinates to the map tool. It is the baseline exercise that proves the tool chain works end-to-end.

**Research / Planning / Discussion:**

```text
What two map tools does this MCP server expose? Describe what each tool takes as input and what it returns. Before I run any prompts, I want to understand how the geocode and show-map tools are meant to be used together.
```

**Finding:** A good response names both tools explicitly: `geocode` accepts a `query` string and returns up to 5 matches from OpenStreetMap, each with a display name, latitude/longitude and a bounding box; `show-map` accepts `west`, `south`, `east` and `north` plus an optional `label`, and returns a coordinate confirmation string with a `viewUUID` in the response `_meta`. Claude should describe the chain: `geocode` produces the bounding box that `show-map` consumes. If the response does not name the four bounding box parameters, ask Claude to describe the full tool response schema before proceeding.

**Recipe:**

```text
Find the Colosseum in Rome, then show it on the map.
```

**Expected Outcome:** Claude calls `geocode` with `query: "Colosseum Rome"`. OpenStreetMap returns two matches for that query; the top one is `Colosseo, Celio, Municipio Roma I, Roma, Roma Capitale, Lazio, 00184, Italia` at `41.890942, 12.491903` with bounding box `W:12.4911, S:41.8894, E:12.4937, N:41.8910`. Claude then calls `show-map` with those four values and a label, and the tool answers with a single line of text:

```text
Displaying globe at: W:12.4911, S:41.8894, E:12.4937, N:41.8910 (Colosseum, Rome)
```

The `viewUUID` is a random UUID in the response `_meta`, not part of the text. In a CLI context (Claude Code) the globe is not rendered visually; only the text content surfaces.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Step 2: Resolve an Ambiguous Place Name

**Overview:** Geocoding a place name that exists in multiple countries surfaces multiple matches. This step shows how Claude evaluates and selects among them before calling `show-map`, making the disambiguation logic visible.

**Research / Planning / Discussion:**

```text
When geocoding a place name that exists in multiple countries, what does the geocode tool return? How does Claude decide which result to pass to show-map?
```

**Finding:** A good response explains that `geocode` returns up to 5 ranked results from OpenStreetMap, each with a distinct display name, coordinates and bounding box, and that Nominatim ranks by its own importance score rather than by exact string equality, so fuzzy near-matches can outrank the spelling you typed. Claude should describe how it selects: by rank, by prominence, or by asking you to clarify. If the response only describes a single match, push back and ask how the tool handles the case where several places share a similar name.

**Recipe:**

```text
Where is Alexandria? Show me all the geocode results before picking one and displaying it on the map.
```

**Expected Outcome:** Claude calls `geocode` with `query: "Alexandria"` and gets five matches, in this order:

1. `Alessandria, Piemonte, Italia` at `44.834953, 8.745030`
2. `Alexandria, Virginia, United States` at `38.805110, -77.047023`
3. `Alessandria, Piemonte, Italia` (the municipality, a second entry) at `44.912985, 8.615456`
4. `Alexandria, Rapides Parish, Louisiana, United States` at `31.311946, -92.445356`
5. `Alexandria, Teleorman, România` at `43.970224, 25.328846`

The lesson is sharper than "same name, several countries": two of the five hits are the Italian **Alessandria**, a fuzzy match on spelling, and the Egyptian Alexandria does not appear at all because Nominatim stores it under its Arabic name. Claude lists the results, explains which one it picked and why, then calls `show-map` with that bounding box. To reach the Egyptian city, geocode `Alexandria Egypt` instead: the top match is `الإسكندرية, 21519, مصر` at `31.199181, 29.895172` with bounding box `W:29.7352, S:31.0392, E:30.0552, N:31.3592`.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Step 3: Compare Bounding Boxes for a Natural Feature and a Region

**Overview:** Bounding box size follows the OpenStreetMap entity type, not the physical size of the thing. This step contrasts a feature stored as a single node with one stored as an administrative relation, and shows that `show-map` frames whatever box it is handed.

**Research / Planning / Discussion:**

```text
How does the bounding box that geocode returns for a natural feature like the Great Barrier Reef differ from one for a state like Queensland? What does this tell you about how OpenStreetMap represents different entity types?
```

**Finding:** A good response explains that OpenStreetMap stores each entity as a node, a way or a relation, and that the bounding box is derived from the geometry actually stored. A node has no extent, so its box collapses to a point regardless of how large the real feature is; a relation carries the full outline, so its box spans the territory. Claude should conclude that `show-map` passes whatever box `geocode` returned straight to the globe, so the view scales with the data, not with the concept. If the response assumes every large feature yields a large box, ask Claude to check the entity type of the match before predicting the box size.

**Recipe:**

```text
Find the Great Barrier Reef and show it on the map. Then geocode Queensland and compare the two bounding boxes.
```

**Expected Outcome:** `geocode` returns exactly one match for the reef, and it is a node:

```text
1. Great Barrier Reef, Australia
   Coordinates: -16.350000, 145.900000
   Bounding box: W:145.8999, S:-16.3500, E:145.9000, N:-16.3499
```

That box is about one ten-thousandth of a degree wide, narrower than the Colosseum box from Step 1, even though the reef stretches for roughly 2,300 km. Queensland, stored as an administrative relation, gives the wide box the reef does not:

```text
1. Queensland, Australia
   Coordinates: -22.164678, 144.584490
   Bounding box: W:137.9946, S:-29.1793, E:153.6116, N:-9.0880
```

`show-map` echoes each box back verbatim, for example `Displaying globe at: W:137.9946, S:-29.1793, E:153.6116, N:-9.0880 (Queensland, Australia)`. The takeaway is the entity type, not the feature size.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Step 4: Explore a Country-Level Region

**Overview:** A country-level query returns a continental-scale bounding box from OpenStreetMap. This step confirms that `show-map` can frame an entire national territory and shows the upper bound of the tool's geographic scale.

**Research / Planning / Discussion:**

```text
How does OpenStreetMap represent a country-level boundary compared to a city? What does the bounding box for a country look like relative to a city or a landmark, and what does that tell you about how show-map frames the view?
```

**Finding:** A good response explains that country boundaries are large administrative relations whose bounding boxes are derived from the full extent of the territory, spanning tens of degrees in both axes and dwarfing city or landmark boxes. Claude should note that `show-map` uses those values directly as the globe's camera bounds, so a country box zooms the view out far enough to contain the whole territory. If the response does not contrast the numeric scale, ask Claude for approximate degree ranges for a country versus a city.

**Recipe:**

```text
Show me Japan on the map.
```

**Expected Outcome:** `geocode` returns a single country-level match, and its display name comes back in Japanese script, which is what Claude will echo:

```text
1. 日本
   Coordinates: 36.574844, 139.239418
   Bounding box: W:122.7142, S:20.2146, E:154.2055, N:45.7112
```

That is about 31 degrees of longitude and 25 degrees of latitude, against hundredths of a degree for the Colosseum. Claude then calls `show-map` with those bounds; in an MCP App host the globe frames the whole archipelago, and in Claude Code you see only the confirmation line.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Step 5: Chain Two Locations Sequentially

**Overview:** The Map server is stateless, meaning each tool call is handled independently with no memory of previous calls. This step exercises two sequential geocode-and-show-map chains and confirms the server processes them correctly without shared state.

**Research / Planning / Discussion:**

```text
The Map server is described as stateless. What does that mean for how it handles sequential tool calls? What would happen if the server stored state between calls?
```

**Finding:** A good response explains that stateless means each HTTP request is processed in isolation: no session context, no previous coordinates, no call history. Sequential calls work because each call carries all required inputs in its own body. Claude should note that shared state would let concurrent users or out-of-order requests corrupt each other's sessions. If the response only defines stateless abstractly, ask how the `viewUUID` is generated and whether it depends on prior calls; it is a fresh random UUID minted per call in `server.ts`.

**Recipe:**

```text
First show me the Eiffel Tower in Paris. Then show me the Sydney Opera House. Describe the difference in coordinates between the two locations.
```

**Expected Outcome:** Claude geocodes and shows each site in turn, getting a different `viewUUID` each time. The Eiffel Tower resolves to a single match, `Tour Eiffel, 5, Avenue Anatole France, ... 75007, France` at `48.858260, 2.294501` with bounding box `W:2.2933, S:48.8575, E:2.2957, N:48.8590`. The Sydney Opera House resolves to two matches; the top one is the real arts centre at `-33.857198, 151.215123` with bounding box `W:151.2144, S:-33.8579, E:151.2159, N:-33.8563`, and the second is a bare rock formation of the same name in Douglas County, Colorado, so check which one Claude picked. Claude then contrasts the two: northern versus southern hemisphere, roughly 149 degrees of longitude apart, and about 16,900 km great-circle distance.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Step 6: Use the Default Globe View

**Overview:** The `show-map` tool has a fallback behaviour when called with no coordinate arguments. This step confirms the fallback works and reveals where the default location is defined.

**Research / Planning / Discussion:**

```text
What does show-map do when it is called with no coordinate arguments? Where is the default location defined, and why might a default be useful?
```

**Finding:** A good response explains that each of `west`, `south`, `east` and `north` is an optional Zod field with a hardcoded `.default(...)`, defined in `labs/04-mcp/03-mcp-app/map-server/server.ts` lines 152 to 171 under the comment `Default bounding box: London area`. Claude should explain why a default is useful: the tool still returns a valid view and a `viewUUID` when geocoding failed or was skipped. If the response cannot name the exact default values, ask Claude to read the input schema in the server source.

**Recipe:**

```text
Show me the map without specifying any location.
```

**Expected Outcome:** Claude calls `show-map` with no coordinate arguments and the four defaults fill in, producing exactly this line:

```text
Displaying globe at: W:-0.5000, S:51.3000, E:0.3000, N:51.7000
```

There is no `(London)` suffix: `label` has no default, so nothing is appended, and the city name only appears in the source comment. Claude should report that the globe fell back to the London area because no coordinates were supplied.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Running and Testing the Map Server

### 1. Build and run the server

Install and build once (this is also what puts Bun in `node_modules/.bin`):

```bash
npm install
npm run build
```

Start on port 3003 to avoid clashing with other local servers. PowerShell:

```powershell
$env:PORT = 3003
node dist/index.js
```

bash:

```bash
PORT=3003 node dist/index.js
```

The npm script `start:http` rebuilds first and then runs the server from source with `bun --watch main.ts`, which is convenient while you are editing the code. PowerShell:

```powershell
$env:PORT = 3003
npm run start:http
```

bash:

```bash
PORT=3003 npm run start:http
```

Wait for `MCP server listening on http://localhost:3003/mcp` before connecting. The DNS-rebinding warning above it is expected.

### 2. Probe the endpoint without a client

The transport requires both content types in the `Accept` header. This is a useful two-line check that the server is really answering MCP and not just holding the port:

```bash
curl -s -o /dev/null -w '%{http_code}\n' -X POST http://localhost:3003/mcp \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

That returns `406`. Add the header and it returns `200`:

```bash
curl -s -o /dev/null -w '%{http_code}\n' -X POST http://localhost:3003/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

### 3. Connect to Claude Code

With the server running, reload MCP servers in your Claude Code session:

1. Type `/mcp` in the Claude Code prompt.
2. Confirm `labs-mcp-map` appears in the active server list.
3. Ask `What map tools do you have available?`

Claude should list exactly two tools, `show-map` and `geocode`. If neither appears, check that the server is listening on the expected port and that the `.mcp.json` in `map-server/` points at `http://localhost:3003/mcp`.

### 4. Verify end-to-end

The lab steps above are your end-to-end test. Work through Steps 1 to 6 using Claude Code. Each step exercises a different layer:

- Step 1 confirms the geocode to show-map chain resolves a named place and returns a view.
- Step 2 confirms geocode returns multiple ranked matches and Claude selects among them.
- Steps 3 and 4 confirm the bounding box follows the OpenStreetMap entity type and scales up to country level.
- Step 5 confirms the stateless server handles sequential independent calls.
- Step 6 confirms the hardcoded fallback coordinates.

If every step produces its expected result, both tools (and the chain between them) are working correctly.

---

> **Note: Why the globe does not render in Claude Code**
>
> The `show-map` **tool definition** carries `_meta.ui.resourceUri` set to `ui://cesium-map/mcp-app.html`; the tool *call* result carries only `_meta.viewUUID`. The host reads the resource URI from `tools/list` and fetches the resource when the tool is called. That URI is the MCP App SDK's signal: *"there is an embeddable UI available here, please render it."* Claude Code is a CLI tool: it has no browser engine and no mechanism to fetch a `ui://` resource, load HTML or execute JavaScript, so it surfaces only the text content.
>
> Rendering the 3D globe requires an **MCP App host**: a client that understands the `ui://` scheme, fetches `mcp-app.html` from the server's resource endpoint (`resources/read` returns the Cesium HTML) and displays it in an isolated iframe or webview. Claude Desktop and the [`basic-host`](https://github.com/modelcontextprotocol/ext-apps/tree/main/examples/basic-host) example are both MCP App-aware hosts. To see the globe render, register the server there with `"type": "http"` and the same URL, then work through the lab steps in that host.
