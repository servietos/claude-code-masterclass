# Wrap a Python MCP App in a Custom Skill

Use the QR Code MCP server in `src/qr-mcp-app-py` as a working reference, then use the `skill-creator` skill to extract its patterns into a reusable `mcp-python` skill you can invoke for any future Python MCP project.

Each step follows the same pattern:

- **Overview**: what this step achieves
- **Research / Planning / Discussion**: an open prompt to reason through the problem before acting
- **Finding**: what to read and evaluate in Claude's response before moving on
- **Recipe**: a complete implementation prompt you can use as-is or adapt from your own findings
- **Expected Outcome**: observable artefacts that confirm success

The completed reference for this lab lives in `src/qr-mcp-app-py-solution/` (the installed and exercised copy of the QR server) and `src/uuid-mcp-app-py-solution/` (the finished Step 6 server). Work in the pristine starter `src/qr-mcp-app-py/` and open the solution folders only when you want to compare.

---

## Where to Open Claude Code

This lab builds its own harness, so open Claude Code inside the lab project rather than at the repo root. The harness is project-scoped: `CLAUDE.md`, `.claude/settings.json` hooks, `.claude/agents/`, `.claude/skills/`, `.claude/commands/` and `.mcp.json` all load from the directory the session was launched in. A session opened at the repo root leaves everything you write here inert, with no error to tell you.

The starter is already in this repo, so there is nothing to scaffold: change into it and start the session there. Run this from the repo root; both commands work unchanged in PowerShell.

```bash
cd labs/04-mcp/04-mcp-skills/mcp-python-skill
claude
```

If you start Claude Code with the Claude Terminal extension (`Ctrl+F1` / `Cmd+F1`), it opens in the VS Code workspace folder and reuses an already-open terminal, so it will not follow the `cd` above. Open `mcp-python-skill` as the workspace folder (**File > Open Folder**) before pressing the shortcut, or run the command above in a plain terminal.

> Note: you can also skip the folder switch entirely and name the path in the prompt instead, working from a session opened anywhere in the repo:

```text
In labs/04-mcp/04-mcp-skills/mcp-python-skill write the mcp-python scope document from src/qr-mcp-app-py/server.py ....
```

That works for any step whose result is just files, such as the scope document in Step 2. It does not work for the skill you are authoring: `.claude/skills/` loads from the directory the session was launched in, so a root session writes `mcp-python` into the lab folder and then ignores it, and Step 5 has nothing to watch trigger. Launch inside the starter from Step 1 onward.

Launching inside the starter is what makes the repository a monorepo to this lab rather than the project: the repo's own `/CLAUDE.md`, `/.claude/` and `/.mcp.json` stay out of the session. You read them from the repo root without ever writing into them, and every path in the prompts below is relative to the lab folder.

Every `.claude/skills/mcp-python/` path in the steps below is therefore relative to `labs/04-mcp/04-mcp-skills/mcp-python-skill/`, never the repository root. The QR reference server stays where it is, so the prompts address it by its repo-root path, `/src/qr-mcp-app-py/`.

---

## Setup

Get the reference server installed and runnable before you start authoring the skill. Working from a server you can actually start makes the patterns concrete instead of theoretical.

Steps 1 to 5 of this Setup run in a plain terminal from the repository root, not in the Claude Code session. Only step 6 happens inside the session you opened in the lab folder.

### 1. Move into the server folder

```bash
cd src/qr-mcp-app-py
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
# activate, pick the line for your shell:
# Windows (Git Bash):   source .venv/Scripts/activate
# Windows (PowerShell): .venv\Scripts\Activate.ps1
# macOS / Linux:        source .venv/bin/activate
```

Do not skip the virtual environment. A bare `pip install` drops the packages into the global interpreter, and on Windows the `python` on `PATH` is often the Microsoft Store stub, so the install either pollutes your machine or fails outright.

### 3. Install the Python dependencies

```bash
pip install -r requirements.txt
```

The four requirements are `mcp>=1.26.0`, `qrcode[pil]>=8.0`, `uvicorn>=0.34.0` and `starlette>=0.46.0`. They cover the MCP server runtime, the QR rendering library, and the HTTP transport stack. The floors are open, so a fresh install pulls current majors (mcp 1.28 and starlette 1.3 at the time of writing), which matters for the Origin behaviour described in Step 1.

If you prefer `uv`, `server.py` carries PEP 723 inline metadata in its first ten lines, so `uv run server.py --stdio` resolves the same dependencies without a venv of your own.

### 4. Smoke-test the server in stdio mode

```bash
python server.py --stdio
```

The process prints a short block of `DEBUG` registration lines to stderr (`server.py` line 27 sets the logging level to `DEBUG`) and then waits on stdin without producing further output. That wait is the stdio transport working correctly. Run it from an interactive terminal: with a redirected or closed stdin (`python server.py --stdio < /dev/null`, or a piped invocation) the process exits immediately with code 0 and there is nothing to stop. Press `Ctrl+C` to end it.

### 5. Smoke-test the HTTP transport

```bash
python server.py
# QR Code Server listening on http://0.0.0.0:3001/mcp
```

`HOST` and `PORT` are read from the environment (`server.py` lines 30 and 31) and default to `0.0.0.0:3001`. Port 3001 is a popular default, so if another local MCP server already holds it you get a bind error (`[Errno 10048]` on Windows) instead of a running server. Restart on a free port with `PORT=3011 python server.py`, then probe it:

```bash
curl -s -X POST http://127.0.0.1:3011/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"curl","version":"1.0"}}}'
```

A healthy server answers `200` with a `text/event-stream` body carrying `"serverInfo":{"name":"QR Code Server",...}`. Stop it with `Ctrl+C` before moving on.

### 6. Confirm the skill creator is available

`skill-creator` is what Step 3 uses to draft the new skill. If you have the `find-skills` skill installed, run `/find-skills skill-creator` in Claude Code to check. `/find-skills` is itself an installable skill rather than a built-in command, so if it does nothing, list what you have with `/plugin` instead.

Install `skill-creator` from the `claude-plugins-official` marketplace (the `anthropics/skills` catalogue does not publish it as an installable plugin):

```text
/plugin marketplace add anthropics/claude-plugins-official
/plugin install skill-creator@claude-plugins-official
```

After the install it is available as the `skill-creator` skill.

---

## Step 1: Read the Reference Server

**Overview:** Build a precise mental model of how the QR server is wired before you try to generalize it. Skipping this step is the most common reason an authored skill produces generic boilerplate that does not match how MCP servers are actually built.

**Research / Planning / Discussion:**

```text
Read /src/qr-mcp-app-py/server.py end to end. Then explain how this server is constructed:
which library provides the server runtime, how a tool is registered, how a resource is
registered, how the server picks between stdio and HTTP transports at startup, and what
the meta fields on the tool and resource decorators are doing. Quote the lines that
prove each claim.
```

**Finding:** A good response names `FastMCP` from `mcp.server.fastmcp` (line 23), constructed as `FastMCP("QR Code Server", stateless_http=True)` (line 33); the `@mcp.tool(meta={...})` decorator whose meta block carries the view resource under both `"ui": {"resourceUri": VIEW_URI}` and the flat `"ui/resourceUri"` key (lines 106 to 109); the `@mcp.resource(VIEW_URI, mime_type="text/html;profile=mcp-app", meta={"ui": {"csp": {"resourceDomains": ["https://unpkg.com"]}}})` decorator (lines 159 to 163); and the `if __name__ == "__main__"` block (lines 168 to 184) that branches on `--stdio` between `mcp.run(transport="stdio")` and `uvicorn.run(...)` over `mcp.streamable_http_app()`, a Starlette application wrapped in permissive `CORSMiddleware`. If the response is vague about any of these, push back and ask for the exact line numbers.

Note that the permissive CORS middleware does not disable the MCP SDK's own Origin allow-list. With `mcp >= 1.28` the streamable HTTP app enforces DNS-rebinding protection, so a request carrying a non-loopback `Origin` still gets `403 Invalid Origin header` even though `access-control-allow-origin: *` comes back on the response. Browser clients on another host need the SDK-level allowed-origins setting as well.

**Recipe:**

```text
Read /src/qr-mcp-app-py/server.py. Produce a structured note with five sections:
1. Server framework and import path
2. Tool registration pattern (decorator, signature, return type, meta keys)
3. Resource registration pattern (decorator, mime type, meta keys)
4. Transport entry point (how stdio and HTTP are selected)
5. Anything that is QR-specific rather than reusable

Quote the relevant lines for each section.
```

**Expected Outcome:** A written breakdown that names the five building blocks above with line references. Save the gist of it; Step 2 reuses it.

---

## Step 2: Decide What the Skill Should Cover

**Overview:** A skill is only useful when its scope is tight. You want the new `mcp-python` skill to cover the structural patterns every Python MCP server needs, not the QR rendering code. This step forces that line to be drawn explicitly.

**Research / Planning / Discussion:**

```text
Based on the breakdown from Step 1, decide which patterns belong inside a reusable
"mcp-python" skill and which are example-specific to the QR server. For each item,
say whether it is structural (belongs in the skill), example (stays in the QR
server), or borderline (and why). Propose three to five realistic trigger phrases
a user would type when they want this skill to fire.
```

**Finding:** Structural items should include FastMCP server construction, the `@mcp.tool` and `@mcp.resource` decorator shapes, the stdio-vs-HTTP entry point branch, and the HTTP app assembly (`mcp.streamable_http_app()` plus CORS middleware, with the SDK Origin allow-list called out as a separate concern from CORS). Example items should include the `qrcode` library calls and the QR-specific HTML in `EMBEDDED_VIEW_HTML`. The trigger phrases should be concrete (for example "build a Python MCP server", "add a tool to my fastmcp server", "register an MCP App resource in Python"), not generic ("help with Python" is too broad to trigger reliably).

**Recipe:**

```text
Write a one-page scope document for a new skill named mcp-python with these sections:
- Purpose (one sentence)
- In scope (bulleted list of structural patterns the skill covers)
- Out of scope (bulleted list of things the skill should not try to handle)
- Trigger phrases (three to five realistic user requests, each in quotes)
- Inputs the skill must ask the user for before generating code

Keep the document under 40 lines.
```

**Expected Outcome:** A short scope document. The In-scope list reads like a checklist of reusable MCP Python building blocks; the trigger phrases are specific enough that they would not match an unrelated Python question.

---

## Step 3: Generate the Skill with the Skill Creator

**Overview:** Hand the scope document to `skill-creator` and let it produce the first draft. The skill creator handles frontmatter formatting, suggests trigger phrases, and lays out the standard body sections, which saves you from hand-rolling the YAML and the section headings.

**Research / Planning / Discussion:**

```text
Given the scope document from Step 2, is skill-creator the right tool to draft this
skill, or should I write SKILL.md by hand? Compare the two paths on three dimensions:
time to first working draft, quality of the description field for triggering, and how
easy it is to iterate when the skill misfires. Recommend one.
```

**Finding:** A good response recommends `skill-creator` for the first draft, with reasoning grounded in its interactive prompts (it asks for use case, trigger phrases, and example inputs), automatic frontmatter validation, and the ability to come back and revise inside the same conversation. If the response recommends hand-writing without that reasoning, ask why it discounted the interactive validation that the manual path lacks.

**Recipe:**

```text
Use the skill-creator skill to help me build a new skill named mcp-python.

Scope (paste in the scope document from Step 2):
<paste here>

Reference implementation to mine for patterns:
/src/qr-mcp-app-py/server.py

Constraints:
- Skill folder lives at .claude/skills/mcp-python/ inside this lab folder,
  never in the repository root .claude/
- SKILL.md must include: Inputs, Steps, Examples, Troubleshooting
- Trigger phrases must come from the scope document, not generic Python phrasing
- Do not invent libraries; only reference mcp, fastmcp, uvicorn, and starlette as
  shown in the QR server

Walk me through the skill-creator interview and produce the final SKILL.md.
```

**Expected Outcome:** A new folder at `labs/04-mcp/04-mcp-skills/mcp-python-skill/.claude/skills/mcp-python/` containing a `SKILL.md` with valid YAML frontmatter (`name`, `description`), a body covering Inputs, Steps, Examples, and Troubleshooting, and trigger phrases that match your scope document.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Step 4: Move Boilerplate into References

**Overview:** A `SKILL.md` that inlines a full server skeleton is slow to load and harder for Claude to scan. Splitting reusable boilerplate into `references/` keeps the main file focused on decisions while making the long code blocks available on demand.

**Research / Planning / Discussion:**

```text
Read the SKILL.md generated in Step 3. Identify everything that is currently inline
but would be better placed in references/. For each candidate, justify the move on
two grounds: (a) is it long enough to bloat the main file, and (b) is it static
enough that it does not need to be rewritten per use? Propose the file names for
references/.
```

**Finding:** Strong candidates to move are the full server skeleton (a complete `server.py` template), the transport-mode explanation (stdio vs HTTP), and any CSP / `resourceDomains` reference. Decision points (which transport to expose, whether the server needs a resource at all) should stay in `SKILL.md`. If the response wants to move the trigger steps themselves out of `SKILL.md`, push back; those belong inline.

**Recipe:**

```text
Refactor .claude/skills/mcp-python/ as follows:
1. Create references/server-skeleton.py with a complete FastMCP server template
   modeled on /src/qr-mcp-app-py/server.py but stripped of QR-specific code.
2. Create references/transport-modes.md explaining when to expose stdio,
   when to expose HTTP, and how the entry-point branch is structured.
3. Trim SKILL.md so the Steps section links to these references instead of
   inlining the code. Keep decision points and trigger phrases in SKILL.md.

Show me the final directory tree and the trimmed SKILL.md.
```

**Expected Outcome:** The skill folder now contains `SKILL.md`, `references/server-skeleton.py`, and `references/transport-modes.md`. `SKILL.md` is meaningfully shorter than the Step 3 version, and its Steps section links to the reference files by relative path.

---

## Step 5: Verify the Skill Triggers

**Overview:** A skill that does not fire on realistic prompts is invisible. The `description` field is what Claude matches against, so this is where misfires get diagnosed.

**Research / Planning / Discussion:**

```text
Read .claude/skills/mcp-python/SKILL.md. Evaluate the description field on three
criteria: does it state what the skill does, does it state when to use it, and does
it contain concrete trigger phrases? Then propose three user prompts that should
trigger this skill and three that look related but should not. Predict for each
whether the current description would match.
```

**Finding:** A solid response flags any description that reads like a dictionary entry (for example "manages MCP servers in Python") and rewrites it with explicit trigger phrasing. The negative prompts (the three that should not trigger) are useful: if the description would match them, it is too broad. Look for at least one suggested rewrite, not just a critique.

**Recipe:**

```text
Improve the description field in .claude/skills/mcp-python/SKILL.md so it reliably
triggers on these prompts:
1. "Build me a Python MCP server with a tool that returns a chart."
2. "Add an MCP App resource to my fastmcp server."
3. "Wire up stdio and HTTP transports for an mcp Python server."

And does not trigger on these:
1. "Help me debug a Python type error."
2. "Install the mcp CLI."
3. "Write a TypeScript MCP server."

Show the before and after description, and explain which trigger words you added
or removed and why.
```

**Expected Outcome:** An updated `description` field in `SKILL.md` that names the three positive triggers explicitly, omits language that would match the three negative prompts, and stays under 1024 characters. The before/after diff makes the rationale clear.

---

## Step 6: Use the Skill on a Fresh Task

**Overview:** The final check on a skill is whether it produces correct work on a task it has never seen before. Pick a small new MCP server, invoke the skill, and judge the result on the same dimensions you used in Step 1.

**Research / Planning / Discussion:**

```text
Propose a small new Python MCP server you can build in under 15 minutes that would
exercise the mcp-python skill on something other than QR codes. The server should
have exactly one tool and optionally one resource. Give a one-paragraph spec and
explain which parts of the mcp-python skill would do most of the work.
```

**Finding:** Good candidates are small and self-contained: a Markdown-to-HTML tool, a URL unshortener, a colour-palette generator, a UUID minter. Avoid anything that needs API keys or external accounts. The response should map the spec to the skill's Steps explicitly so you can tell whether the skill would actually cover the work.

**Recipe:**

```text
Use the mcp-python skill to scaffold the new server described below.

Spec (paste from the research step above):
<paste here>

Constraints:
- Place the new server inside this lab folder at <new-server-name>-py/
- Include requirements.txt and a readme.md with the same sections as
  /src/qr-mcp-app-py/readme.md: title and one-line summary, Setup,
  how to register the server with your MCP client, Parameters
- Expose both stdio and HTTP transports, defaulting to a port other than 3001
- Do not modify .claude/skills/mcp-python/ during this step

After generating the server, create a venv, install requirements.txt,
start it in stdio mode and report any errors.
```

**Expected Outcome:** A new folder inside `labs/04-mcp/04-mcp-skills/mcp-python-skill/` containing a runnable `server.py`, `requirements.txt`, and `readme.md`. The server starts cleanly in stdio mode, printing the same `DEBUG` registration block as the QR server before it waits on stdin. The skill's fingerprints are visible in the generated code: FastMCP construction, the same transport branch, decorator shapes matching what `references/server-skeleton.py` defines. Compare your result with the finished UUID minter in `src/uuid-mcp-app-py-solution/`.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.
