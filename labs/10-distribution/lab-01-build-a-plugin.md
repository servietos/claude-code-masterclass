# Build a Plugin From a `.claude/` Configuration

Take a working `.claude/` configuration (skills, hooks, slash commands, and an MCP server) and convert it into a self-contained Claude Code plugin. Test it locally with `--plugin-dir` and `/reload-plugins`.

Each step contains:
- **Goal**: what you are building
- **Prompt or command**: what you run
- **Expected result**: what the outcome looks like

> **Why this matters:** A `.claude/` folder is project-scoped: every project that wants the same skill must duplicate it. A plugin is portable, versioned, and installable. Converting once means every future project gets the work for free.

> **Two folders:** the starter at [`01-build/notes-toolkit-source/`](01-build/notes-toolkit-source/) already holds the `.claude/` tree you will package (two skills, a hook, `settings.json`, a slash command) plus an MCP server and a sample `src/`, and Step 1 turns it into a real plugin tree beside it at `labs/10-distribution/01-build/notes-toolkit/`. The completed plugin is checked in as [`01-build/notes-toolkit-solution/`](01-build/notes-toolkit-solution/); build your own first and use it to compare. [`01-build/notes-toolkit-source-solution/`](01-build/notes-toolkit-source-solution/) is a pristine copy of the starter, there to diff against if you edit the source by mistake.

---

## Where to Open Claude Code

This lab builds its own harness, so open Claude Code inside the lab project rather than at the repo root. The harness is project-scoped: `CLAUDE.md`, `.claude/settings.json` hooks, `.claude/agents/`, `.claude/skills/`, `.claude/commands/` and `.mcp.json` all load from the directory the session was launched in. A session opened at the repo root leaves everything you write here inert, with no error to tell you.

The starter is already in this repo, so there is nothing to scaffold: change into it and start the session there. Run this from the repo root; both commands work unchanged in PowerShell.

```bash
cd labs/10-distribution/01-build/notes-toolkit-source
claude
```

If you start Claude Code with the Claude Terminal extension (`Ctrl+F1` / `Cmd+F1`), it opens in the VS Code workspace folder and reuses an already-open terminal, so it will not follow the `cd` above. Open `notes-toolkit-source` as the workspace folder (**File > Open Folder**) before pressing the shortcut, or run the commands above in a plain terminal.

> Note: you can also skip the folder switch entirely and name the path in the prompt instead, working from a session opened anywhere in the repo:

```text
In labs/10-distribution/01-build/notes-toolkit-source copy the two skills into the sibling notes-toolkit/skills/ folder ....
```

That works for any step whose result is just files, which covers the whole migration into the plugin tree. It does not work for the pieces the starter ships live: `.claude/skills/`, `.claude/commands/`, the `PreToolUse` hook registered in `.claude/settings.json` and `.mcp.json` all load from the directory the session was launched in, so a root session leaves every one of them inert. Launch inside `notes-toolkit-source` from Step 1 onward.

Restart the session with `/exit` then `claude` after any edit to `.claude/settings.json` or `.mcp.json`, because both are read at startup.

Launching inside the starter is what makes the repository a monorepo to this lab rather than the project: the repo's own `/CLAUDE.md`, `/.claude/` and `/.mcp.json` stay out of the session and are read from the repo root. You read from them without ever writing into them, and every path in the prompts below is relative to the lab folder.

Do not build this one at the repo root. The starter deliberately ships `.claude/skills/`, `.claude/commands/` and a write-blocking `PreToolUse` hook, so a session started at the root would enrol every one of them into this repository's live roster instead of the lab folder. That is not hypothetical: `01-build/notes-toolkit-source-solution/.claude/skills/` is already being discovered as a directory-scoped skill in this repo, which is exactly the accident this section exists to prevent.

---

## Setup: Run the Source `.claude/` Configuration

The starter is a fictional "notes-toolkit" that adds five things to any project. It is the thing you will package, so nothing here is yours to write:

```text
notes-toolkit-source/
├── .claude/
│   ├── commands/notes-flow.md          /notes-flow: extract, then prioritise
│   ├── hooks/scope-gate.sh             PreToolUse gate on Write|Edit
│   ├── hooks/scope-gate.ps1            the same gate for PowerShell
│   ├── settings.json                   registers the hook
│   └── skills/
│       ├── notes-extract/SKILL.md      TODO/FIXME/NOTE scan into .notes/extracted.md
│       └── notes-prioritise/SKILL.md   rewrites that report as Now / Next / Later
├── .mcp.json                           registers the stdio MCP server
├── mcp-server/requirements.txt         the server's dependency declaration
├── mcp-server/server.py                FastMCP server exposing count_todos()
└── src/                                three files carrying eight TODO/FIXME/NOTE markers
```

There is nothing to install by hand. `mcp-server/requirements.txt` is the one place the server's dependencies are declared, and `.mcp.json` launches it with `uv run --with-requirements`, so `uv` builds and caches that environment on first run:

```json
{
  "mcpServers": {
    "notes-mcp": {
      "command": "uv",
      "args": ["run", "--with-requirements", "mcp-server/requirements.txt", "mcp-server/server.py"]
    }
  }
}
```

Prove the three moving parts work before you package them.

The hook receives its `PreToolUse` payload as JSON on stdin, so you can test it without Claude Code at all. The starter ships the gate twice, once per shell: `scope-gate.sh` for git-bash (it shells out to `jq`, which has to be on `PATH`), and `scope-gate.ps1` for PowerShell (no `jq`, no git-bash). Run the twin for the shell you are in. Both read the same payload and exit with the same code.

```bash
echo '{"cwd":".","tool_name":"Write","tool_input":{"file_path":"docs/x.md"}}' | bash .claude/hooks/scope-gate.sh; echo "exit=$?"
```

```powershell
'{"cwd":".","tool_name":"Write","tool_input":{"file_path":"docs/x.md"}}' | pwsh -NoProfile -File .claude/hooks/scope-gate.ps1; "exit=$LASTEXITCODE"
```

```text
scope-gate: blocked write to 'docs/x.md'. Allowed: .notes/, src/, tests/, .claude/, README.md
exit=2
```

An allowed path such as `src/x.py` exits `0` and prints nothing. Do not invoke the `.sh` from PowerShell with a bare `bash`: that resolves to `C:\Windows\system32\bash.exe`, which is WSL and has no `jq`, so the run dies with `jq: command not found` and exit `127`.

The MCP server serves stdio, so it starts and exits cleanly the moment stdin closes. Run it with the exact command `.mcp.json` registers:

```bash
uv run --with-requirements mcp-server/requirements.txt mcp-server/server.py < /dev/null; echo "exit=$?"
```

```powershell
$null | uv run --with-requirements mcp-server/requirements.txt mcp-server/server.py; "exit=$LASTEXITCODE"
```

```text
notes-mcp server starting on stdio, root ...\01-build\notes-toolkit-source
notes-mcp server stopped
exit=0
```

Those two lines go to stderr, never stdout: on stdio transport stdout carries the JSON-RPC frames, and a stray `print()` there corrupts the first message the client reads. Then, from the session you opened above, run the skills and the slash command together:

```text
/notes-flow
```

**Expected result:** `.notes/extracted.md` appears, rewritten into `Now`, `Next` and `Later` sections populated from the eight markers across the three files in `src/`. `/mcp` lists `notes-mcp` as connected. That is the whole toolkit working project-scoped; the rest of the lab makes it portable.

---

## Step 1: Plugin Anatomy and Namespacing

**Goal:** Understand the plugin structure and decide on a namespace before you start moving files.

A Claude Code plugin is a directory with this canonical layout:

```text
notes-toolkit/
├── .claude-plugin/
│   └── plugin.json       # manifest: name, version, description, component config
├── README.md             # plugin docs
├── skills/               # skills bundled into the plugin
│   └── <skill-name>/
│       └── SKILL.md
├── commands/             # slash commands as flat .md files
│   └── <name>.md
├── hooks/                # hook scripts and hooks.json
│   └── <name>.sh
├── agents/               # subagents (optional)
│   └── <name>.md
└── mcp-server/           # bundled MCP server source (any folder name)
    ├── requirements.txt
    └── server.py
```

Two rules matter more than the rest. The manifest lives at `.claude-plugin/plugin.json`, never at the plugin root: a root-level `plugin.json` is not found and `claude plugin validate` reports `No manifest found in directory`. Everything else (`skills/`, `commands/`, `hooks/`, `agents/`) sits at the plugin root, never inside `.claude-plugin/`.

Inside Claude Code, plugin-scoped names use a namespace prefix to avoid collisions: a skill in plugin `notes-toolkit` is invoked as `notes-toolkit:notes-extract`, not just `notes-extract`. The namespace is the plugin's `name` field in `plugin.json`.

**Prompt:**

```text
Create a sibling folder to notes-toolkit-source called notes-toolkit/, which will become the plugin. Inside, create .claude-plugin/plugin.json with this content:

  {
    "name": "notes-toolkit",
    "version": "0.1.0",
    "description": "Extract, prioritise, and report on TODO/FIXME/NOTE comments across a codebase.",
    "author": { "name": "<your-name-or-handle>" },
    "license": "MIT",
    "keywords": ["notes", "todo", "triage"]
  }

Note that "author" is an object, not a string; a bare string fails manifest validation with 'author: Invalid input: expected object, received string'.

Also create notes-toolkit/README.md describing what the plugin adds, with sections: Overview, Skills, Commands, Hooks, MCP Servers, Install. Use the .claude/ source as the source of truth for what's actually in the plugin.

Do not move any files yet; just create the manifest and the placeholder README.
```

**Expected result:** A new `notes-toolkit/` folder with `.claude-plugin/plugin.json` and `README.md`. The plugin is empty otherwise; the next steps populate it from the source.

---

## Step 2: Move the Skills Into the Plugin

**Goal:** Migrate the two skills from `.claude/skills/` into the plugin's `skills/` folder and confirm the move preserves behaviour. The starter is checked into this repo, so copy rather than move: that leaves it intact for a second run and for a diff.

**Prompt:**

```text
Copy these two skills from notes-toolkit-source/.claude/skills/ into notes-toolkit/skills/:
  - notes-extract/
  - notes-prioritise/

Keep their directory structure (each skill stays in its own subfolder with SKILL.md).

Update the README.md Skills section to document each one: name, description, when-to-use, trigger phrases.

Do not modify the SKILL.md frontmatter yet; we'll check namespacing in the test step.
```

**Expected result:** Both skill folders now also live under `notes-toolkit/skills/`, byte-identical to the starter's. The README has a populated Skills section.

---

## Step 3: Move the Hook Into the Plugin

**Goal:** Migrate the PreToolUse scope-gate hook. Plugin hooks reference their own files via the `${CLAUDE_PLUGIN_ROOT}` variable so the path stays valid regardless of which project installs the plugin.

**Prompt:**

```text
Copy both hook twins from notes-toolkit-source/.claude/hooks/ into notes-toolkit/hooks/:
  - scope-gate.sh
  - scope-gate.ps1

Update .claude-plugin/plugin.json to register the hook. Add a "hooks" section:

  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          { "type": "command", "command": "bash \"${CLAUDE_PLUGIN_ROOT}/hooks/scope-gate.sh\"" }
        ]
      }
    ]
  }

The ${CLAUDE_PLUGIN_ROOT} substitution makes the hook path portable: Claude Code resolves it to the plugin's install directory at runtime. Invoking through `bash` rather than naming the .sh directly makes the hook run on Windows too, where the file has no executable bit and the shebang is not honoured.

Update README.md Hooks section with a one-line description of what the hook blocks, and document the PowerShell twin as the alternative wiring.
```

A hook entry takes an optional `shell` field, `"bash"` or `"powershell"`. It defaults to `bash`, and on Windows to `powershell` when git-bash is not installed. That default is what makes the second twin worth shipping: a machine without git-bash (or without `jq`) runs the entry under PowerShell, where the `bash "…/scope-gate.sh"` command has nothing to execute. Point the entry at the `.ps1` instead and the gate works there:

```json
{ "type": "command", "command": "pwsh -NoProfile -File \"${CLAUDE_PLUGIN_ROOT}/hooks/scope-gate.ps1\"", "shell": "powershell" }
```

Register one twin, not both: two entries on the same matcher fire the gate twice.

**Expected result:** Both hook twins live under `notes-toolkit/hooks/` and one of them is registered in `plugin.json` with `${CLAUDE_PLUGIN_ROOT}` instead of an absolute or relative path.

---

## Step 4: Move the Slash Command and MCP Server

**Goal:** Finish the migration. The slash command goes into `commands/`. The MCP server stays as-is at its current path but is registered via `plugin.json`'s `mcpServers` field (the same shape as `.mcp.json`).

**Prompt:**

```text
Two more copies:

1. Copy notes-toolkit-source/.claude/commands/notes-flow.md to notes-toolkit/commands/notes-flow.md.

2. Copy notes-toolkit-source/mcp-server/ to notes-toolkit/mcp-server/, both server.py and requirements.txt.

Then add an mcpServers section to .claude-plugin/plugin.json, carrying over the --with-requirements form from .mcp.json:

  "mcpServers": {
    "notes-mcp": {
      "command": "uv",
      "args": [
        "run",
        "--with-requirements",
        "${CLAUDE_PLUGIN_ROOT}/mcp-server/requirements.txt",
        "${CLAUDE_PLUGIN_ROOT}/mcp-server/server.py"
      ]
    }
  }

Again, ${CLAUDE_PLUGIN_ROOT} makes both paths portable. Never point the command at a virtualenv interpreter instead: .venv/bin/python and .venv/Scripts/python.exe differ by platform, and the venv does not exist on the machine that installs the plugin. Do not append a transport flag such as --stdio: FastMCP sets the transport in code, so an extra argv entry is inert noise.

Update README.md sections for Commands and MCP Servers.

Verify the plugin folder structure is now:
  notes-toolkit/
    .claude-plugin/plugin.json
    README.md
    skills/notes-extract/SKILL.md
    skills/notes-prioritise/SKILL.md
    hooks/scope-gate.sh
    hooks/scope-gate.ps1
    commands/notes-flow.md
    mcp-server/requirements.txt
    mcp-server/server.py
```

Now let the CLI check the manifest before you ever launch a session with it:

```bash
claude plugin validate /full/path/to/notes-toolkit
claude plugin validate --strict /full/path/to/notes-toolkit
```

**Expected result:** The plugin folder contains every component and both validate runs pass. The starter is untouched, so `diff -rq .claude/skills ../notes-toolkit/skills` reports nothing. The plugin is structurally complete; the next step tests it.

---

## Step 5: Drive the Bundled Server With MCP Inspector

**Goal:** Exercise `notes-mcp` on its own, before any Claude Code session is involved. Inspector speaks MCP directly to the server over stdio, so a failure here is the server's, and a failure in Step 6 is the plugin wiring's. Debugging the two at once is what makes a broken MCP server feel unfixable.

Inspector runs the server as a subprocess, which means it needs an interpreter that already has `mcp` importable. Give the server a local environment from the same `requirements.txt` the manifest declares:

```bash
cd ../notes-toolkit/mcp-server
uv venv --seed .venv
uv pip install --python .venv -r requirements.txt
```

Both `uv` lines are identical in PowerShell. `--seed` puts `pip` inside the venv; without it, activating the venv and running `pip install` silently falls through to the system interpreter and installs there instead. `.venv/` is git-ignored, so the plugin folder stays shippable.

Activation differs per shell, and you only need it if you want a bare `python` on `PATH`:

```bash
source .venv/Scripts/activate
```

```powershell
.\.venv\Scripts\Activate.ps1
```

**Commands:**

Inspector has two modes. The CLI mode is the one to reach for first, because it is a single command with a diffable answer:

```bash
npx @modelcontextprotocol/inspector --cli .venv/Scripts/python.exe server.py --method tools/list
```

```text
notes-mcp server starting on stdio, root ...\notes-toolkit\mcp-server
Processing request of type ListToolsRequest
{
  "tools": [
    {
      "name": "count_todos",
      "description": "Count TODO, FIXME and NOTE comments in the project and return the totals per marker.",
      "inputSchema": {
        "type": "object",
        "properties": {
          "path": {
            "default": "",
            "title": "Path",
            "type": "string"
          }
        },
        "title": "count_todosArguments"
      }
    }
  ]
}
notes-mcp server stopped
```

That block is the contract the model sees. The `description` and the `path` property come straight from the Python docstring and signature, so this is where a vague tool description shows up as a vague answer later.

Now call the tool, pointing it at the starter's sample sources:

```bash
npx @modelcontextprotocol/inspector --cli .venv/Scripts/python.exe server.py --method tools/call --tool-name count_todos --tool-arg path=../../notes-toolkit-source/src
```

```text
{
  "content": [
    {
      "type": "text",
      "text": "{\n  \"root\": \"..\\\\..\\\\notes-toolkit-source\\\\src\",\n  \"files_scanned\": 3,\n  \"counts\": {\n    \"TODO\": 3,\n    \"FIXME\": 2,\n    \"NOTE\": 3\n  },\n  \"total\": 8\n}"
    }
  ],
  "isError": false
}
```

Three files, eight markers: the same eight `/notes-flow` reported in Setup, now proven to come from the server rather than from the model reading the files itself.

Drop `--cli` for the UI mode when you want to browse the surface instead of assert one fact:

```bash
npx @modelcontextprotocol/inspector .venv/Scripts/python.exe server.py
```

```text
Starting MCP inspector...

MCP Inspector Web is up and running at:
   http://localhost:6274?MCP_INSPECTOR_API_TOKEN=f99f428bf113e0ee6bb701e6ebe24c0523d07fae2e0ea4a2d21f0d78bba7f141

   Auth token: f99f428bf113e0ee6bb701e6ebe24c0523d07fae2e0ea4a2d21f0d78bba7f141

Opening browser...
```

Open the printed URL with its token, press **Connect**, then **Tools > List Tools**, select `count_todos`, fill `path`, and **Run Tool**. The left pane shows the JSON-RPC frames in both directions and a separate stderr pane carries the two `notes-mcp server ...` lines. Stop it with `Ctrl+C`.

**Expected result:** `tools/list` returns exactly one tool with the schema above, and `tools/call` returns `"total": 8` with `"isError": false`. The server is proven independently of Claude Code, so the next step is testing the plugin, not the server.

> **Note:** on Windows the interpreter is `.venv/Scripts/python.exe`; on macOS and Linux it is `.venv/bin/python`. This path is local to your machine, which is exactly why `plugin.json` registers `uv run --with-requirements` instead of naming an interpreter.

---

## Step 6: Test Locally With `--plugin-dir`

**Goal:** Install the plugin into a *different* project to confirm it works as a portable bundle, not just in the folder where it was authored.

**Commands:**

Create a fresh test project, from `01-build/` (Step 5 left you two levels deeper, inside `notes-toolkit/mcp-server`):

```bash
cd ../..
mkdir plugin-test-project
cd plugin-test-project
git init
mkdir src
cat > src/example.py <<'PY'
# TODO: rename this function
def f(x):
    # FIXME: handle negative inputs
    return x * 2

# NOTE: refactor target for v2
PY
```

The heredoc above works as written in git-bash on Windows; no WSL needed.

Now launch Claude Code with the plugin folder added as a plugin directory:

```bash
claude --plugin-dir /full/path/to/notes-toolkit
```

Inside Claude Code:

```text
/plugin
```

`/plugin` opens the interactive plugin panel (Discover, Installed, Marketplaces, Errors). Open the Installed tab and confirm `notes-toolkit` appears at version `0.1.0`. For a non-interactive check from a shell, use `claude plugin list` or `claude plugin details notes-toolkit` instead.

Then:

```text
/mcp
```

Confirm `notes-mcp` is active (the plugin's MCP server registered automatically). If it fails to connect here after Step 5 passed, the fault is in the manifest wiring, not the server: check the `${CLAUDE_PLUGIN_ROOT}` paths and that `requirements.txt` was copied alongside `server.py`.

Finally, run the plugin's command:

```text
/notes-toolkit:notes-flow
```

Note the namespace prefix: slash commands provided by a plugin are addressable as `plugin-name:command-name`.

**Expected result:** `.notes/extracted.md` appears in the test project, prioritised into Now/Next/Later sections, populated from the TODOs in `src/example.py`. The hook fires when Claude tries to write outside the allowed paths. The MCP server's `count_todos` tool is callable and returns a per-marker count plus a total. The plugin is fully functional in a project it did not ship with.

---

## Step 7: Iterate With `/reload-plugins`

**Goal:** Develop the plugin without restarting Claude Code on every change. `/reload-plugins` re-reads the plugin manifest and re-registers hooks, MCP servers, and LSP servers against the new version. There is no `/plugin reload` and no `claude plugin reload`; `/reload-plugins` is the command.

**Commands:**

While still in the test project's Claude Code session, edit a plugin file from a second terminal:

```bash
# In a second terminal
printf '\n## Changelog\n- 0.1.0 initial release\n' >> /full/path/to/notes-toolkit/README.md
```

Or make a more meaningful change, bumping the version:

```bash
# In notes-toolkit/.claude-plugin/plugin.json, change version 0.1.0 to 0.1.1
```

Back in Claude Code:

```text
/reload-plugins
/plugin
```

**Expected result:** The Installed tab now shows version `0.1.1`. The reload picked up the manifest change without a Claude Code restart. This is the inner loop for plugin authoring: edit, reload, test, repeat.

---

## What You Just Practised

| Mechanic | Step | Why it matters |
|---|---|---|
| Plugin folder anatomy + `.claude-plugin/plugin.json` manifest | 1 | The canonical structure every plugin follows, and the one path mistake that stops a plugin loading |
| Namespacing (`plugin-name:component`) | 1, 6 | Avoids collisions when multiple plugins ship overlapping names |
| Skill migration | 2 | Portable skill packaging |
| Hook migration + `${CLAUDE_PLUGIN_ROOT}` | 3 | Makes hook paths install-location-independent, and cross-platform |
| Slash command + MCP server bundling | 4 | One plugin can ship every harness primitive |
| `requirements.txt` as the one dependency declaration | Setup, 4, 5 | The venv, the manifest and Inspector all resolve from the same file |
| `claude plugin validate` | 4 | Catches manifest errors before a session ever loads the plugin |
| MCP Inspector CLI and UI modes | 5 | Isolates a server defect from a plugin-wiring defect |
| `--plugin-dir` for local testing | 6 | Test the plugin in a foreign project without installing it |
| `/reload-plugins` for inner-loop authoring | 7 | Edit, reload, test without restarting Claude Code |

Lab 01 is the producer side. [Lab 02](lab-02-plugin-security.md) is the defender side: it audits a plugin someone else wrote, before you install it.
