# Build the EventTrack Registration MCP Server

Build a headless Python MCP server that manages events and attendee registrations, then drive the full registration workflow through Claude Code.

Each step follows the same pattern:

- **Overview**: what this step achieves
- **Research / Planning / Discussion**: an open prompt to reason through the problem before acting
- **Finding**: what to read and evaluate in Claude's response before moving on
- **Recipe**: a complete implementation prompt you can use as-is or adapt from your own findings
- **Expected Outcome**: observable artefacts that confirm success

---

## Introduction

This lab walks through implementing a real-world MCP server from scratch using Claude Code as your agentic implementation partner. You drive the build entirely through prompts: Claude Code writes every file.

**Business case (EventTrack):** A conference organiser needs a lightweight backend for managing sessions and workshops. Attendees register by providing a name and e-mail address. The system must enforce per-event capacity limits, allow cancellations, and produce registration summaries. No web UI is required; the MCP server is the interface.

The server exposes seven tools:

| Tool | Purpose |
|---|---|
| `list_events` | Return all events with date, venue, and seat counts |
| `create_event` | Create a new event with a capacity limit |
| `check_availability` | Return remaining seats for a specific event |
| `register_attendee` | Register a named attendee; rejects if full or duplicate |
| `list_registrations` | List attendees for one event or all events |
| `cancel_registration` | Cancel a registration by attendee e-mail and event |
| `get_event_summary` | Return registration statistics for an event |

The server runs via **stdio** transport using FastMCP and stores all state in an **SQLite** database. No external services, API keys, or network access are required.

---

## Where to Open Claude Code

This lab builds its own harness, so open Claude Code inside the lab project rather than at the repo root. The harness is project-scoped: `CLAUDE.md`, `.claude/settings.json` hooks, `.claude/agents/`, `.claude/skills/`, `.claude/commands/` and `.mcp.json` all load from the directory the session was launched in. A session opened at the repo root leaves everything you write here inert, with no error to tell you.

The starter is already in this repo, so there is nothing to scaffold: change into it and start the session there. Run this from the repo root; both commands work unchanged in PowerShell.

```bash
cd labs/04-mcp/02-implementing/event-registration-mcp
claude
```

If you start Claude Code with the Claude Terminal extension (`Ctrl+F1` / `Cmd+F1`), it opens in the VS Code workspace folder and reuses an already-open terminal, so it will not follow the `cd` above. Open `event-registration-mcp` as the workspace folder (**File > Open Folder**) before pressing the shortcut, or run the command above in a plain terminal.

> Note: you can also skip the folder switch entirely and name the path in the prompt instead, working from a session opened anywhere in the repo:

```text
In labs/04-mcp/02-implementing/event-registration-mcp create server.py with the uv inline script header and a get_db() helper ....
```

That works for any step whose result is just files, such as writing `server.py` in Steps 1, 2 and 4. It does not work for the server registration: `.mcp.json` loads from the directory the session was launched in, so a root session writes it into the lab folder and then ignores it, and Steps 3 and 5 are verified entirely through the `eventtrack` tools that registration makes visible. Launch inside the starter from Step 1 onward.

Restart the session with `/exit` then `claude` after any edit to `.claude/settings.json` or `.mcp.json`, because both are read at startup.

Launching inside the starter is what makes the repository a monorepo to this lab rather than the project: the repo's own `/CLAUDE.md`, `/.claude/` and `/.mcp.json` stay out of the session. You read them from the repo root without ever writing into them, and every path in the prompts below is relative to the lab folder.

---

## Setup: Project Folder

Build your server in this (empty) starter folder:

```text
labs/04-mcp/02-implementing/event-registration-mcp/
```

All generated files go inside that folder, which is also the folder you launched Claude Code in. Open a second terminal there for the `uv` commands before starting Step 1. The finished server lives beside the starter in [`02-implementing/event-registration-mcp-solution/`](02-implementing/event-registration-mcp-solution) as the completed reference: use it only to compare against once you are done, or to unblock yourself.

`uv` must be on your PATH before you start. Check with `uv --version`; if it is missing, follow the setup at [astral.sh/uv](https://astral.sh/uv).

---

## Step 1: Scaffold the Server Skeleton

**Overview:** Create the entry-point file with the uv inline script header, FastMCP initialisation, and a database helper. This skeleton runs without errors and forms the foundation for all subsequent steps.

**Research / Planning / Discussion:**

```text
I want to build a Python MCP server called EventTrack that manages conference events and attendee registrations. Before writing any code, describe: what structure a minimal FastMCP server needs, what the uv inline script metadata format (PEP 723) requires, and how a sqlite3 connection should be opened and configured in Python. I want a design overview before implementation.
```

**Finding:** A good response names the `# /// script` block with `requires-python` and `dependencies` fields, identifies `FastMCP` from `mcp.server.fastmcp`, describes `mcp.run(transport="stdio")` as the entry point, and explains setting `row_factory = sqlite3.Row` so columns are accessible by name. If the response omits any of these three areas, ask a follow-up before moving to the recipe.

**Recipe:**

```text
In this folder create server.py for a Python 3.12 MCP server named "EventTrack".

Use the uv inline script metadata format (PEP 723) with these dependencies:
- mcp>=1.9.0

Use FastMCP from mcp.server.fastmcp. The server must start in stdio mode when invoked with --stdio, otherwise print usage and exit.

Add a get_db() helper that opens (or creates) events.db in the same directory as server.py using sqlite3 from the standard library. The helper must return a connection with row_factory = sqlite3.Row so callers can access columns by name.

Do not define any tools or schema yet. The file should run without error.
```

**Expected Outcome:** `server.py` is created with the `# /// script` block declaring `requires-python = ">=3.12"` and `mcp>=1.9.0`, a `FastMCP("EventTrack")` instance, a `get_db()` function returning a sqlite3 connection, and a `__main__` block that calls `mcp.run(transport="stdio")` when `--stdio` is passed. Running `uv run server.py` without `--stdio` resolves and installs the dependency set on first run (roughly 30 packages), prints a usage line such as `Usage: uv run server.py --stdio`, and exits with code 0. No `events.db` exists yet: the database is only created once `init_db()` lands in Step 2.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Step 2: Create the Database Schema and Seed Data

**Overview:** Add the `init_db()` function that creates the `events` and `registrations` tables on first run and seeds realistic data so the database is non-empty from the start.

**Research / Planning / Discussion:**

```text
Looking at the EventTrack server we are about to build, what tables will the events and registrations data need? What constraints and indexes make sense for a system that must enforce per-event capacity limits and prevent duplicate registrations for the same email? Describe the schema before I ask you to create it.
```

**Finding:** A good response describes two tables (`events` and `registrations`), identifies a `UNIQUE(event_id, email)` constraint on registrations as the mechanism for duplicate prevention, and explains that capacity enforcement requires a count query at registration time rather than a database constraint. If the response proposes only one table or omits the UNIQUE constraint, ask it to reconsider before proceeding.

**Recipe:**

```text
In server.py add an init_db() function that runs when the server starts.

Create two tables if they do not already exist:

events:
  id          INTEGER PRIMARY KEY AUTOINCREMENT
  title       TEXT NOT NULL
  description TEXT
  date        TEXT NOT NULL        -- ISO-8601 date, e.g. 2026-09-15
  venue       TEXT NOT NULL
  capacity    INTEGER NOT NULL

registrations:
  id           INTEGER PRIMARY KEY AUTOINCREMENT
  event_id     INTEGER NOT NULL REFERENCES events(id)
  name         TEXT NOT NULL
  email        TEXT NOT NULL
  registered_at TEXT NOT NULL      -- ISO-8601 datetime
  UNIQUE(event_id, email)

Seed five events only when the events table is empty. Use a realistic conference context:
1. "Keynote: The Future of AI Agents", 2026-09-15, Main Hall, capacity 300
2. "Workshop: Building MCP Servers in Python", 2026-09-15, Room A, capacity 30
3. "Workshop: Claude Code for Agentic Workflows", 2026-09-16, Room B, capacity 30
4. "Panel: Ethics in AI-Assisted Engineering", 2026-09-16, Main Hall, capacity 200
5. "Hands-On Lab: FastAPI + Claude Integration", 2026-09-17, Lab Room, capacity 20

Seed six registrations across events 1 to 3 (two per event) so the database is not empty on first use. Events 4 and 5 start with no registrations. Use plausible fictional names and e-mail addresses.

Call init_db() from the __main__ block before mcp.run().
```

**Expected Outcome:** `init_db()` is added above the `__main__` block. Running `uv run server.py --stdio` creates `events.db` next to `server.py` and then leaves the process running, waiting on stdin for JSON-RPC messages: that is what a stdio server does, so nothing is printed and nothing exits. Press `Ctrl+C` to stop it. Inspecting `events.db` (see [Inspect the database directly](#3-inspect-the-database-directly)) shows the tables `events` and `registrations` with five and six rows, and per-event registration counts of 2, 2, 2, 0, 0.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Register the Server in Claude Code

`server.py` now creates and seeds its database, so register it before implementing tools: every following step is verified through Claude Code. Create `.mcp.json` in `labs/04-mcp/02-implementing/event-registration-mcp/`, the folder you launched Claude Code in, with this entry (merge into the `mcpServers` object rather than replacing the file if it already declares other servers):

```json
{
  "mcpServers": {
    "eventtrack": {
      "command": "uv",
      "args": [
        "run",
        "server.py",
        "--stdio"
      ]
    }
  }
}
```

The path is relative to the lab folder, which is where Claude Code launches the process from. This file belongs to the lab, not to the repository: the repo-root `.mcp.json` is not read by a session started here and must not be edited. `events.db` is always created next to `server.py`, i.e. inside `event-registration-mcp/`, no matter which directory the client starts the process from, because `get_db()` resolves the path from `Path(__file__).parent`. The folder already ships a `.gitignore` covering `events.db` and `__pycache__/`, so the database never shows up in `git status`.

Restart the session with `/exit` then `claude` so Claude Code reads the new `.mcp.json`, then run `/mcp`. Confirm `eventtrack` is listed with no error badge before continuing to Step 3.

---

## Step 3: Implement Event Tools

**Overview:** Add `list_events` and `create_event` so Claude can query the event catalogue and add new sessions. These two tools establish the pattern used by all subsequent tools.

**Research / Planning / Discussion:**

```text
The EventTrack server needs to let Claude list all events and create new ones. Before implementing, describe: what a FastMCP tool decorator looks like, what return value format Claude expects from a list tool versus a create tool, and how a context manager should wrap a sqlite3 connection inside a tool function.
```

**Finding:** A good response shows the `@mcp.tool()` decorator applied to a regular Python function, explains that list tools return a list of dicts while create tools return a single confirmation dict (or an error dict with key `"error"`), and describes using `with get_db() as conn` as the context manager pattern. If the response suggests returning raw SQL Row objects or omits the error dict convention, clarify before proceeding.

**Recipe:**

```text
Add two MCP tools to server.py using the @mcp.tool() decorator.

Give every tool a one-line docstring: FastMCP uses the docstring as the tool description Claude sees when it lists the available tools.

list_events()
  Opens a database connection, selects all rows from events ordered by date then title.
  For each event also compute registered_count by counting matching rows in registrations.
  Return a list of dicts with keys: id, title, description, date, venue, capacity, registered_count, seats_remaining.

create_event(title: str, description: str, date: str, venue: str, capacity: int)
  Validates that capacity >= 1 and that date is a non-empty string.
  Inserts the event and returns a confirmation dict with the new event id and title.
  Return an error dict with key "error" if validation fails.

Both tools must open and close their own database connection via get_db(). Use a context manager (with get_db() as conn).
```

**Expected Outcome:** The two `@mcp.tool()` decorated functions appear in `server.py`. After a `/mcp` reload, asking Claude Code `What events are scheduled?` returns the five seeded events with `seats_remaining` of 298, 28, 28, 200 and 20 (capacity minus the seeded registrations). Asking Claude to create a new event succeeds and returns event id 6. A `capacity` of 0 is rejected with the validation error.

You never start the server yourself for this: Claude Code launches and owns its own server process, so `/mcp` (reload) is the only step needed after editing `server.py`.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Step 4: Implement the Remaining Five Tools

**Overview:** Add the five tools that complete the surface: `check_availability`, `register_attendee` and `cancel_registration` carry the transactional logic, while `list_registrations` and `get_event_summary` are the read side. Step 3 already taught the tool pattern, so this step is one prompt rather than three, and the research focuses on the four decisions that are genuinely new.

**Research / Planning / Discussion:**

```text
I am adding the last five tools to the EventTrack server. The @mcp.tool pattern is settled, so do not re-explain it. Answer only these four:

1. How do I detect a full event before attempting the INSERT, and why does that check belong in application code rather than in a database constraint?
2. Which specific exception does the UNIQUE(event_id, email) constraint raise, and why catch that rather than a bare Exception?
3. After a DELETE, how do I tell a real cancellation apart from a row that was never there?
4. list_registrations must return the event title on every row. What JOIN does that need, and what changes when the optional event_id filter is supplied?
```

**Finding:** The four answers you want are: query `registered_count` first and compare against `capacity`, because SQLite cannot express a per-parent row-count limit as a constraint; catch `sqlite3.IntegrityError` specifically, since a bare `Exception` would swallow real bugs and report them as duplicates; check `cursor.rowcount` after the DELETE, where `0` means not found; and `JOIN events ON registrations.event_id = events.id`, with the filter becoming a WHERE clause on the same query. Push back if the response claims a CHECK constraint can enforce capacity, or if it proposes a second query instead of the JOIN.

**Recipe:**

```text
Add the final five MCP tools to server.py, each with a one-line docstring.

check_availability(event_id: int)
  Looks up the event by id. Returns an error dict if not found.
  Returns a dict with event_id, title, capacity, registered_count, seats_remaining, and is_full (bool).

register_attendee(event_id: int, name: str, email: str)
  Validates that name and email are non-empty strings.
  Checks availability; returns an error dict with "error": "Event is full" if seats_remaining == 0.
  Attempts the INSERT into registrations. If the UNIQUE constraint fails, return an error dict with "error": "Already registered".
  On success, return a confirmation dict with event_id, event_title, name, email, and registered_at (current UTC datetime as ISO-8601 string).

cancel_registration(event_id: int, email: str)
  Deletes the matching registration row.
  Returns a success dict if a row was deleted, or an error dict with "error": "Registration not found" if rowcount == 0.

list_registrations(event_id: int | None = None)
  If event_id is provided, return registrations for that event only, otherwise all of them.
  Each row includes: registration_id, event_id, event_title, name, email, registered_at.
  Join registrations with events to get event_title. Order by event date, then registered_at.

get_event_summary(event_id: int)
  Returns one dict with event_id, title, date, venue, capacity, registered_count,
  seats_remaining, is_full, and an "attendees" list of {name, email} ordered by registered_at.
  Return an error dict if the event is not found.

All five open their own connection via get_db(), following the same pattern as Step 3.
```

**Expected Outcome:** Seven `@mcp.tool()` functions are present in `server.py`, the complete tool surface. After a `/mcp` reload, `How many seats are left in the Python workshop?` returns 28 of 30, and `Show me all registrations` returns the six seeded rows, each carrying its `event_title` from the JOIN. Only events 1 to 3 have registrations at this point, so events 4 and 5 do not appear.

Step 5 exercises the transactional branches, so you do not need to test them by hand here.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Step 5: Drive the Whole Workflow Through Claude

**Overview:** Confirm the handshake, then exercise every branch the server has in one conversation: the happy path, duplicate detection, cancellation with seat restoration, and the full-event guard. This is the payoff step, where the seven tools stop being Python functions and become something Claude reasons with.

**Research / Planning / Discussion:**

```text
You are connected to the eventtrack server. First list the tools you can see, with a one-line description each.

Then, before calling anything, predict the tool sequence for this run: list events, register an attendee, attempt the same registration again, check availability, cancel, check availability again, then fill a small event to its cap. For each call say what you expect back, and name the one case where the server returns an error dict rather than raising.
```

**Finding:** The tool list must name exactly seven: `list_events`, `create_event`, `check_availability`, `register_attendee`, `list_registrations`, `cancel_registration`, `get_event_summary`. If any is missing, `server.py` was not saved or the server was not reloaded, so run `/mcp` and retry before going further. The prediction should have the duplicate attempt returning `{"error": "Already registered"}` and the final availability check returning the same number as before the registration, because a cancellation restores the seat rather than leaving a hole.

**Recipe:**

```text
I need to register for the conference. Do the following in order, reporting the result of each:

1. List all events and tell me how many seats are still available in each one.
2. Register me, Alex Rivera, alex.rivera@example.com, for the "Workshop: Building MCP Servers in Python" session.
3. Try to register the same email again for the same event and report what happens.
4. Check the remaining availability for that workshop after my registration.
5. Now cancel my registration.
6. Check availability again and confirm the seat was released.
7. Create a test event called "Capacity Probe" on 2026-09-18 at Room C with capacity 1.
8. Register Jordan Blake, jordan.blake@example.com for it, then register Sam Nguyen, sam.nguyen@example.com for the same event, and tell me exactly what the second call returned.
```

**Expected Outcome:** Claude runs the sequence without further prompting. Part 1 returns all five events with seat counts of 298, 28, 28, 200 and 20 on a freshly seeded database. Part 2 returns a confirmation with a UTC ISO-8601 timestamp, part 3 returns `{"error": "Already registered"}`, and part 4 shows `seats_remaining` 27.

Parts 5 and 6 return a cancellation confirmation and `seats_remaining` back at 28, proving the seat is released rather than lost. Part 7 returns the new event id 6. Part 8 registers Jordan successfully and then returns `{"error": "Event is full"}` for Sam, which is the capacity guard from Step 4 firing in application code before the INSERT is attempted.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Running and Testing the Server

### 1. Verify the server starts cleanly

From the `event-registration-mcp/` folder, run the server directly:

```powershell
uv run server.py --stdio
```

The process starts and waits on stdin for JSON-RPC messages: no banner, no prompt, no exit. That is the correct behaviour for a stdio server. Press `Ctrl+C` to stop it. If uv is not installed, follow the setup at [astral.sh/uv](https://astral.sh/uv).

A crash on startup prints a traceback instead of sitting idle, which is exactly what this check is for. During normal use you never start the server yourself: Claude Code launches its own managed instance via the `.mcp.json` configuration.

### 2. Connect to Claude Code

Add the server entry to the lab folder's own `.mcp.json` (see [Register the Server in Claude Code](#register-the-server-in-claude-code)), then:

1. Type `/mcp` in Claude Code.
2. Confirm `eventtrack` appears in the active servers list with no error badge.
3. Ask `What event management tools do you have available?`

Claude should list all seven tools. If the server shows an error badge, run `uv run server.py --stdio` manually in a terminal and read the traceback before reconnecting.

### 3. Inspect the database directly

While developing, inspect the live database from a second terminal standing in `labs/04-mcp/02-implementing/event-registration-mcp/`:

```powershell
uv run --with sqlite-utils sqlite-utils tables events.db
uv run --with sqlite-utils sqlite-utils rows events.db events
uv run --with sqlite-utils sqlite-utils rows events.db registrations
```

The first command lists `events`, `registrations` and `sqlite_sequence`. This confirms that registrations created through Claude are persisted to disk and survive server restarts.

### 4. Verify end-to-end

The lab steps are your end-to-end test. Step 5 is the one that exercises the whole surface in a single conversation:

- Its opening prompt confirms all seven tools are discoverable.
- Parts 1 to 6 confirm the happy path, duplicate detection, and cancellation with seat restoration.
- Parts 7 and 8 confirm capacity enforcement by filling a one-seat event.

If every part produces its expected result, the SQLite persistence layer, the capacity-check logic, the UNIQUE constraint guard, and the cancellation path are all working correctly.

The solution folder also ships `check_tools.py`, a small JSON-RPC client that drives the same assertions over stdio without a Claude session. Run it against your own `server.py` when a step misbehaves and you want to know whether the fault is in the server or in the conversation.

---

> **Note: headless versus HTTP transport**
>
> This server uses stdio transport, meaning it runs as a subprocess of Claude Code and all communication happens over stdin/stdout. There is no HTTP port, no network interface, and no need to start the server manually during normal use: Claude Code manages the process lifecycle via the `.mcp.json` command entry.
>
> To expose EventTrack to remote clients or the Claude API, switch to HTTP transport. The bind address belongs on the constructor, not on `run()`: write `mcp = FastMCP("EventTrack", host="0.0.0.0", port=5050)` and then call `mcp.run(transport="streamable-http")`. Passing `host` or `port` to `run()` raises `TypeError: FastMCP.run() got an unexpected keyword argument 'host'`. Then change the `.mcp.json` entry to `"type": "http"` with `"url": "http://localhost:5050/mcp"` (`/mcp` is the default streamable-HTTP path). The tool definitions do not change, only the transport layer.

---

## Using EventTrack with Claude Desktop

Claude Desktop supports MCP servers configured in its own settings file (separate from the `.mcp.json` used by Claude Code). Because EventTrack uses stdio transport, Claude Desktop launches and manages the server process exactly the same way Claude Code does.

### 1. Locate the Claude Desktop configuration file

| Platform | Path |
|---|---|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |

Open the file in any text editor. If it does not exist yet, create it.

### 2. Add the EventTrack server entry

Merge the following into the `mcpServers` object. Adjust the path to match where your `server.py` lives:

```json
{
  "mcpServers": {
    "eventtrack": {
      "command": "uv",
      "args": [
        "run",
        "C:\\full\\path\\to\\event-registration-mcp\\server.py",
        "--stdio"
      ]
    }
  }
}
```

On macOS or Linux use a forward-slash path:

```json
{
  "mcpServers": {
    "eventtrack": {
      "command": "uv",
      "args": [
        "run",
        "/full/path/to/event-registration-mcp/server.py",
        "--stdio"
      ]
    }
  }
}
```

> **Why a full path?** Claude Desktop launches the server from its own working directory, not from your project root, so a relative path will not resolve `server.py` at all. With the absolute path the database still lands next to `server.py` inside `event-registration-mcp/`, the same file Claude Code uses.

### 3. Restart Claude Desktop

Save the configuration file and fully quit and relaunch Claude Desktop (not just close the window). On restart it reads the config and registers all `mcpServers` entries.

### 4. Confirm the server is active

1. Open a new conversation in Claude Desktop.
2. Click the MCP icon (plug or hammer) in the chat input bar.
3. Confirm `eventtrack` appears in the active servers list with no error badge.
4. Ask: `What event management tools do you have available?`

Claude should list all seven tools. If the server shows an error badge, open a terminal and run `uv run server.py --stdio` manually to read the traceback.

### 5. Use EventTrack in conversation

Claude Desktop supports the same tool calls as Claude Code. The entire registration workflow from Step 5 above works identically: paste the same prompts and expect the same results. The `events.db` file is shared between both clients as long as both point to the same `server.py` path, so registrations made in Claude Desktop are visible in Claude Code and vice versa.
