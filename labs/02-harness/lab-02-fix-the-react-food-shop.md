# Configure the Harness on a Broken React App

Configure the Claude Code harness piece by piece, then watch everything work together on a real codebase. A broken React app is the use case; the harness is the lesson.

| Task | What you configure | What you get |
|------|--------------------|--------------|
| 1 | CLAUDE.md | Understand project conventions before touching any code |
| 2 | Context7 and Chrome DevTools MCPs | Current React docs in the conversation, and screenshots to verify fixes visually |
| 3 | PostToolUse hook | Every tool call Claude makes is written to a log you can watch |
| 4 | Custom slash command | `/write-docs` generates documentation for any component on demand |
| 5 | React skill + full harness | Fix the Checkout button |
| 6 | Checkpoint + full harness | Safe checkout form implementation with a restore point |

Each task follows the same pattern:

- **Overview**: what this task achieves
- **Research / Planning / Discussion**: an open prompt to reason through the problem before acting
- **Finding**: what to read and evaluate before moving on
- **Recipe**: a complete implementation prompt you can use as-is or adapt from your own findings
- **Expected Outcome**: observable artefacts that confirm success

---

## Where to Open Claude Code

This lab builds its own harness, so open Claude Code inside the lab project. The harness is project-scoped: `CLAUDE.md`, `.claude/settings.json` hooks, `.claude/agents/`, `.claude/skills/`, `.claude/commands/` and `.mcp.json` all load from the directory the session was launched in. A session opened at the repo root leaves everything you write here inert, with no error to tell you.

The starter is already in this repo, so there is nothing to scaffold: change into the React app inside it and start the session there. Run this from the repo root; both commands work unchanged in PowerShell.

```bash
cd labs/02-harness/lab-02-food-shop/shop-ui/food-shop-react
claude
```

If you start Claude Code with the Claude Terminal extension (`Ctrl+F1` / `Cmd+F1`), it opens in the VS Code workspace folder and reuses an already-open terminal, so it will not follow the `cd` above. Open `food-shop-react` as the workspace folder (**File > Open Folder**) before pressing the shortcut, or run the command above in a plain terminal.

> Note: you can also skip the folder switch entirely and name the path in the prompt instead, working from a session opened anywhere in the repo:

```text
In labs/02-harness/lab-02-food-shop/shop-ui/food-shop-react fix the Checkout button so it enables when the cart has at least one item ....
```

That works for any step whose result is just files, such as the fixes in Tasks 5 and 6. It does not work for the harness itself: the hook in Task 3, the slash command in Task 4 and both MCP servers in Task 2 load from the directory the session was launched in, so a root session writes them into the lab folder and then ignores them. Launch inside the starter from Task 1 onward.

Restart the session with `/exit` then `claude` after any edit to `.claude/settings.json` or `.mcp.json`, because both are read at startup.

That launch directory is the lesson, and it is what makes the repository a monorepo to this lab, with the React app as the project: the repo's own `/CLAUDE.md`, `/.claude/` and `/.mcp.json` stay out of the session and are read from the repo root. You read from them without ever writing into them, and every prompt below uses paths relative to the React app.

---

## Running the Lab Starter

You work in the starter at `labs/02-harness/lab-02-food-shop/shop-ui/food-shop-react`. The starter carries everything the lab runs or reads: the React app, the catalog API under `catalog-api/catalog-service-cs`, and the Angular app at `../food-shop-ng` that Task 6 copies the checkout form from. The finished reference implementation lives beside it at `labs/02-harness/lab-02-food-shop-solution/shop-ui/food-shop-react`; open it only if you get stuck, and do your own work in the starter. Nothing this lab creates belongs in the solution folder.

If you ran Lab 01, bring its skill across before Task 5, because the skill is project-scoped and the two labs are separate projects:

```bash
mkdir -p .claude/skills
cp -r ../../../lab-01-react-skill/.claude/skills/vercel-react-best-practices .claude/skills/
```

```powershell
New-Item -ItemType Directory -Force .claude\skills | Out-Null
Copy-Item -Recurse ..\..\..\lab-01-react-skill\.claude\skills\vercel-react-best-practices .claude\skills\
```

Skip Lab 01 and Tasks 5 and 6 still work, they just run without the skill's conventions.

Prerequisites, verified on the versions in brackets:

- Node.js 18 or newer (verified on Node v24.15.0 with npm 11.12.1)
- The .NET 10 SDK for the catalog API (verified on 10.0.110)

The React app reads its catalog from the URL in `labs/02-harness/lab-02-food-shop/shop-ui/food-shop-react/.env`, which is `http://localhost:5000`. The two commands below run in their own terminals and both start from the repo root; only the Claude Code session stays inside the React app. Start the catalog API first:

```bash
cd labs/02-harness/lab-02-food-shop/catalog-api/catalog-service-cs
dotnet run --urls http://localhost:5000
```

Confirm it answers before moving on:

```bash
curl http://localhost:5000/food
```

You should get HTTP 200 and a JSON array of food items. Then start the React app in a second terminal:

```bash
cd labs/02-harness/lab-02-food-shop/shop-ui/food-shop-react
npm install
npm start
```

`npm install` pulls roughly 1300 packages and takes a minute or two on a cold cache. `npm start` prints `Compiled successfully!` followed by `Local: http://localhost:3000`, and the app opens there.

Do not skip the catalog API. When the fetch fails, `FoodShopContainer` returns early with an error panel and renders nothing else: you get `Error loading catalog`, `Failed to fetch` and a `Retry` button, with no cart sidebar and no Checkout button at all. Tasks 5 and 6 are impossible in that state.

The dependency set in `package.json` is pinned so the toolchain is coherent: React and React DOM at `^18.2.0` are paired with `@types/react` `^18.3.12` and `@types/react-dom` `^18.3.1`, and `typescript` `^4.9.5` is declared explicitly as a direct dependency, where `react-scripts` lists it only as an optional peer. Every source file is `.tsx`, so an undeclared compiler is a trap waiting for the first person who installs with `--legacy-peer-deps`, pnpm or yarn.

---

## Task 1: Read the Project CLAUDE.md

**Overview:** CLAUDE.md is the first thing Claude reads when entering a project, and "the project" means the directory the session was launched in. You launched in the React app, which has no CLAUDE.md, so the repository's rules did not load and Claude is working blind. Read that file by its explicit repo-root path and watch the difference: this is the same project-scoping that decides whether your hook in Task 3 ever fires.

**Research / Planning / Discussion:**

```text
You started in labs/02-harness/lab-02-food-shop/shop-ui/food-shop-react, so no CLAUDE.md was auto-loaded for this
session. Read /CLAUDE.md, the repository's own file at the repo root. What are
the rules that apply when working in this repository, covering code style, commits,
writing, and workflow? Also tell me which of them Claude Code would have applied automatically
had I launched at the repo root instead.
```

**Finding:** Claude should surface the hard rules (no commits without explicit request, relative internal links, language-declared code fences), the writing rules (no em dashes, no negative parallelism), and the workflow rules (plan first for non-trivial tasks, delegate domain work to the owning agent, verify before reporting done). A good response quotes the relevant sections word for word.

It should also be honest about the second question: none of those rules loaded on their own here, because memory files are discovered from the launch directory upward through parent directories only when they are part of the same project tree, and a session rooted in the React app treats that app as the project. Reading the file explicitly is what put the rules into context. Push back if Claude gives a generic summary without citing specific rules, and push back if it claims the repository's CLAUDE.md was already active. Note that the one exception to the no-comments rule is scoped to `.sh`, `.ps1` and hook files under `demos/`, so a precise answer names that scope and keeps the rule for every other file.

**Recipe:**

```text
Read /CLAUDE.md, the repository's own file at the repo root, and list every rule that is relevant to implementing a lab. Group
them by category: code style, writing style, workflow, and hard constraints. For each rule, say
which paths it applies to, expressed relative to this React app.
```

**Expected Outcome:** Claude produces a grouped list of rules drawn directly from the repository's CLAUDE.md, with the scope of each group made explicit, and states plainly that the file was read on request. Keep this response visible: it is the reference for every task that follows.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Task 2: Register Both MCP Servers in One File

**Overview:** Two MCPs carry the rest of this lab: Context7 fetches version-accurate library documentation, and Chrome DevTools drives a browser so Claude can screenshot its own work. Both are public servers listed on the [GitHub MCP Registry](https://github.com/mcp), so you register them from their registry pages in the app's own `.mcp.json`. Doing both at once is deliberate: `context7` is an HTTP server and `chrome-devtools` is a stdio server, and seeing the two shapes in one file is the clearest way to learn the difference.

**Research / Planning / Discussion:**

```text
Open the GitHub MCP Registry pages https://github.com/mcp/upstash/context7 and
https://github.com/mcp/ChromeDevTools/chrome-devtools-mcp and show me the configuration each one
gives, side by side. Then answer:

1. One is an HTTP server and one is stdio. Which is which, and what does that mean for what
   actually runs on my machine?
2. Context7 needs a two-step call to be useful. What are the two tools, and in what order?
3. Which browser does the chrome-devtools invocation drive: does it launch its own Chrome, or
   attach to one I already have open? What flag changes that, and what must I start Chrome with?
4. The repository registers its own servers in /.mcp.json at the repo root. Why would none of
   them be active in this session, and where must this project's file go instead?
```

**Finding:** Claude should quote both registry entries: Context7 is a remote server at `https://mcp.context7.com/mcp`, which becomes `"context7": { "type": "http", "url": "https://mcp.context7.com/mcp" }`, and Chrome DevTools gives `"chrome-devtools": { "command": "npx", "args": ["-y", "chrome-devtools-mcp@latest"] }`, which runs as `"type": "stdio"`. An HTTP server is a hosted endpoint with nothing to install; a stdio server is a local process launched from `command` and `args`. The Context7 workflow is `resolve-library-id` first for a stable ID, then `query-docs` with that ID and a topic.

On browsers, the default invocation **launches and reuses its own Chrome** with its own profile; attaching to yours is opt-in via `--browser-url=http://127.0.0.1:9222` in `args`, with Chrome started using `--remote-debugging-port=9222`. On the last question it should say `.mcp.json` is read from the launch directory, so the repository's file is inert here and this project's file goes in the React app. Push back if Claude skips the resolve step, claims the default config attaches to an existing tab, or says the servers are already available because a file with that name exists up the tree.

**Recipe:**

```text
Create .mcp.json in this project, the React app, containing BOTH servers from the GitHub MCP
Registry: a context7 entry of type http for the remote URL listed at
https://github.com/mcp/upstash/context7, and a chrome-devtools entry of type stdio with the npx
command listed at https://github.com/mcp/ChromeDevTools/chrome-devtools-mcp. Do not edit the
repository's /.mcp.json at the repo root.

Then show me, as a separate snippet and without putting it in the file, the edited args array that
would make chrome-devtools attach to my own Chrome on the remote debugging port, plus the command
that starts Chrome that way.
```

Restart the session once with `/exit` then `claude`, because `.mcp.json` is read at startup, and confirm with `/mcp` that both servers are listed. Then use the first one:

```text
Use Context7 to fetch the current React documentation on controlled form components and the
useState hook. I am about to implement a checkout form modal with controlled inputs and
validation, so pull the docs that are most relevant to that pattern.
```

**Expected Outcome:** A `.mcp.json` appears at `labs/02-harness/lab-02-food-shop/shop-ui/food-shop-react/.mcp.json` carrying both entries, and after one restart `/mcp` lists `context7` and `chrome-devtools`. Claude returns focused React documentation sourced live from Context7, and states plainly that the default `npx -y chrome-devtools-mcp@latest` invocation launches its own Chrome, showing the `--browser-url` variant beside the `chrome --remote-debugging-port=9222` command.

Confirm the browser half now, so Tasks 5 and 6 do not stall on it: ask Claude to screenshot `http://localhost:3000`. With the catalog API running you see the shop catalog and the cart sidebar, and with it stopped you see only the `Error loading catalog` panel.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Task 3: PostToolUse Hook for a Tool Interaction Log

**Overview:** Add a PostToolUse hook that records every tool call Claude makes, so you can watch its actions unfold as they happen: which files it reads, what it writes, what shell commands it runs. This is the fastest way to build intuition for how Claude actually works inside a session, and it is also a lesson in reading a hook contract carefully before writing one.

**Research / Planning / Discussion:**

```text
This project, the React app I launched in, has no .claude/settings.json yet. Read the
repository's own file at /.claude/settings.json, at the repo root, as an example only, and do not edit it.
What hook types does Claude Code support, what JSON payload does a PostToolUse hook receive on
stdin, which environment variables does it get, and where does a PostToolUse hook's stdout
actually go?
```

**Finding:** Claude should identify the `PostToolUse` hook type and get three things right. First, the tool name and its inputs arrive as JSON on **stdin**, with fields `tool_name`, `tool_input` and `tool_response`; parse them with `jq`. Second, the only environment variables a hook receives are `CLAUDE_PROJECT_DIR`, `CLAUDE_PLUGIN_ROOT`, `CLAUDE_PLUGIN_DATA`, `CLAUDE_EFFORT`, `CLAUDE_CODE_REMOTE` and `CLAUDE_CODE_BRIDGE_SESSION_ID`; there is no `CLAUDE_TOOL_NAME`.

Third, plain stdout from a PostToolUse hook is written to the debug log and is not shown in the transcript (only `UserPromptSubmit`, `UserPromptExpansion` and `SessionStart` are exceptions). So a bare `echo` is invisible. To surface a line to the user, emit JSON with a top-level `systemMessage` field; to keep a durable trace, append to a log file and tail it in a second terminal. Push back hard if Claude claims an environment variable carries the tool name, and push back if it logs only the tool name without any input: the file path or command is what makes the output meaningful.

**Recipe:**

```text
Create .claude/settings.json in this project, the React app, with a PostToolUse hook that fires
after every tool call. Do not touch the repository's /.claude/ at the repo root. The hook reads
the JSON payload from stdin, extracts tool_name and the primary input (file_path for
Read/Write/Edit, command for Bash), and does both of these:

- appends a line formatted as [ToolName] <input> to .claude/tool-log.txt
- emits {"systemMessage": "[ToolName] <input>"} on stdout so the line is visible in the session

Use jq for the JSON parsing.
```

Then restart the session with `/exit` followed by `claude`. Hook configuration is read at startup, so an unrestarted session runs the old, hookless config and you will conclude the hook is broken when it is only unloaded.

**Expected Outcome:** `labs/02-harness/lab-02-food-shop/shop-ui/food-shop-react/.claude/settings.json` gains a `PostToolUse` entry whose command reads its payload from stdin. After the restart, ask Claude to read any file in the app, then run `tail -f .claude/tool-log.txt` in a second terminal opened in the same folder: a line like `[Read] src/components/ShopItem.tsx` appears there, and the `systemMessage` variant shows up in the session. This is the sharpest proof of project scope in the lab: put the same hook in the repository's `.claude/settings.json` instead and nothing would ever fire here. In Tasks 5 and 6 the log grows into a full trace of every file Claude reads and writes as the React fixes unfold.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Task 4: Custom Slash Command for `/write-docs`

**Overview:** Create a project-level slash command that generates documentation for a React component. Type `/write-docs` followed by a component path and get structured docs back instantly, with no documentation prompt to retype. This is the first harness element that gives you something reusable to invoke yourself, and a template for any repeatable task you want to encode as a command.

**Research / Planning / Discussion:**

```text
How do I create a custom slash command in Claude Code? Where do the command files live, what
format do they use, how does Claude receive arguments passed to the command, and what
frontmatter fields does a command file support?
```

**Finding:** Claude should explain that project-level commands live in `.claude/commands/` as markdown files, that the filename becomes the command name (`write-docs.md` becomes `/write-docs`), that `$ARGUMENTS` in the file body receives anything typed after the command name, and that the file body is the instruction Claude executes. If the command declares tools in frontmatter, the field is `allowed-tools`; there is no `tools` field.

A good answer shows the file path, the `$ARGUMENTS` placeholder, and a minimal example. "Project-level" means the project the session was launched in, so here the command belongs in the React app and Claude creates the `.claude/commands/` directory on the way. The repository has its own `.claude/commands/` five levels up holding the three course-authoring commands; those are invisible from this session and stay untouched. Push back if Claude describes user-level commands, and push back if it proposes writing into the repository's directory because one already exists there.

**Recipe:**

```text
Create a project-level custom slash command called /write-docs at .claude/commands/write-docs.md
in this project, the React app. Do not write into the repository's /.claude/ at the repo root.
When invoked with a file path as $ARGUMENTS, it should read that component file, then generate
concise documentation covering: what the component does, its props interface, and any notable
behaviour or side effects.
```

**Expected Outcome:** A file appears at `labs/02-harness/lab-02-food-shop/shop-ui/food-shop-react/.claude/commands/write-docs.md` using `$ARGUMENTS` to receive the file path. Type `/write-docs src/components/ShopItem.tsx` and confirm Claude reads the file and produces structured documentation for it. Commands are picked up without a restart, so the new `/write-docs` shows in the `/` menu straight away.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Task 5: Fix the Checkout Button

**Overview:** The Checkout button is permanently grayed out regardless of cart contents. This is a one-line fix. The goal is using the full harness: the skill reviews the code, `/write-docs` documents the changed component, and Chrome DevTools screenshots the result.

**Research / Planning / Discussion:**

```text
In this React app, the Checkout button never becomes active no matter how many items are in the
cart. Read the component that renders the cart sidebar. What controls whether the button is
disabled, and what is the bug?
```

**Finding:** Claude should land on `src/components/FoodShopContainer.tsx` line 98, `<button className='checkout-btn' disabled>`: a hardcoded `disabled` attribute with no condition and no `onClick` handler. It should propose a single expression change driven by the existing `cart` state. Push back if Claude suggests anything more complex, such as new state or a reducer.

**Recipe:**

```text
Use the vercel-react-best-practices skill. In this React app, the Checkout button at
src/components/FoodShopContainer.tsx is always disabled regardless of cart contents. Fix it so
the button becomes active when the cart contains at least one item. Then run
/write-docs src/components/FoodShopContainer.tsx to document the component you just changed.
Finally use the Chrome DevTools MCP to open http://localhost:3000, take a snapshot, add an item
to the cart, and confirm the button is enabled in a screenshot.
```

**Expected Outcome:** The single edit turns `disabled` into `disabled={cart.length === 0}`. The Chrome DevTools snapshot reports the button as `disabled` at zero items and enabled after adding one, and the screenshot shows it in its active blue state. `/write-docs` produces documentation for `FoodShopContainer`.

The tool log from Task 3 shows exactly one `[Edit]` line for the component that was changed. `npm run build` still prints `Compiled successfully.`

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Task 6: Checkpoint, Then Add the Checkout Form

**Overview:** The checkout form is the largest change in this lab. Before starting, create a checkpoint so the conversation and file state can be restored if something goes wrong. This introduces checkpoints as a standard habit before significant changes.

**Research / Planning / Discussion:**

```text
The Angular version of this app sits beside it at ../food-shop-ng and has a full checkout form
under src/app/food/shop/checkout. This React app has nothing: after the Task 5 fix the Checkout
button is enabled, but it still has no handler, so nothing happens when it is clicked. Before I
implement this, how do I create a checkpoint in Claude Code and what does restoring from one
actually do?
```

**Finding:** Claude should explain how to create a checkpoint, what state it captures (conversation history and current file state), and how to restore. A good answer also says when restoration is useful: if the implementation goes in the wrong direction, restoring is faster than undoing individual edits. Push back if Claude skips the restoration explanation.

Note that this task depends on Task 5. Without the `disabled={cart.length === 0}` fix the button cannot be clicked at all, so there is nothing to attach a modal to.

**Recipe:**

```text
First create a checkpoint.

Then use the vercel-react-best-practices skill for a performance review pass at the end. The
Angular app beside this one at ../food-shop-ng has a checkout form at
src/app/food/shop/checkout. This React app is missing an equivalent.

Examine the Angular checkout form, then implement a checkout modal in this app that:
- Opens when the Checkout button is clicked
- Has sections for Customer (name, email, phone), Shipping Address (street, zip, city, country),
  and Payment (type, account number)
- Shows the cart items read-only with a total at the bottom
- Validates all fields as required, with email format validation
- Shows validation errors only after the first submit attempt
- On a valid submit, shows a confirmation screen with a generated order ID
- Closes and clears the cart when the user dismisses the confirmation

Pre-populate the form with the mock order the Angular app uses, at
../food-shop-ng/src/app/food/state/cart/mock-data.ts. Match this app's own color scheme
(#4a5fc1 primary blue, as used in FoodShopContainer.css and ShopItem.css).

After implementing, run /write-docs src/components/CheckoutModal.tsx to document the new
component. Then use the Chrome DevTools MCP to screenshot the open modal.
```

**Expected Outcome:** A checkpoint exists before any files are written. New files `CheckoutModal.tsx` and `CheckoutModal.css` appear under `src/components/` in the React app, and `FoodShopContainer.tsx` gains the `onClick` that opens the modal.

In the browser the modal opens prefilled with the Angular mock order (`Giro Kastil`, `Himmelstraße 115`, payment type `Bank Account`). Submitting with `not-an-email` in the email field shows `Enter a valid email address`; a valid submit shows a confirmation screen with a generated order number such as `ORD-MRZ8BOU7-853`; dismissing it clears the cart back to zero items and disables the Checkout button again. `CI=true npm run build` prints `Compiled successfully.` with the bundle growing by roughly 1.5 kB. `/write-docs` produces documentation for `CheckoutModal`, and the tool log from Task 3 shows the stream of `[Write]` and `[Read]` lines for every file Claude touched.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.
