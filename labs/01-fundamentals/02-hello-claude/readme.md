# Build a Task Tracking REST API

Build a Python REST API for task management using Claude Code. Every step is prompt-driven: you provide the prompt, Claude does the work.

Each step contains:

- **Goal**: what you are building
- **Prompt**: paste this into Claude Code
- **Expected result**: what the outcome looks like

## Where to Open Claude Code

This lab builds its own harness, so open Claude Code inside the lab project rather than at the repo root. The harness is project-scoped: `CLAUDE.md`, `.claude/settings.json` hooks, `.claude/agents/`, `.claude/skills/`, `.claude/commands/` and `.mcp.json` all load from the directory the session was launched in. A session opened at the repo root leaves everything you write here inert, with no error to tell you.

The lab project does not exist yet, so create it inside this lab folder and start the session inside it. Run this from the repo root; `cd` and `claude` work unchanged in PowerShell, and the `mkdir -p` has a PowerShell twin below.

```bash
mkdir -p labs/01-fundamentals/02-hello-claude/tasks-app
cd labs/01-fundamentals/02-hello-claude/tasks-app
claude
```

```powershell
New-Item -ItemType Directory -Force labs/01-fundamentals/02-hello-claude/tasks-app
cd labs/01-fundamentals/02-hello-claude/tasks-app
claude
```

If you start Claude Code with the Claude Terminal extension (`Ctrl+F1` / `Cmd+F1`), it opens in the VS Code workspace folder and reuses an already-open terminal, so it will not follow the `cd` above. Open `tasks-app` as the workspace folder (**File > Open Folder**) before pressing the shortcut, or run the commands above in a plain terminal.

> Note: you can also skip the folder switch entirely and name the path in the prompt instead, letting the agent create and fill the folder from a session opened anywhere in the repo:

```text
In labs/01-fundamentals/02-hello-claude/tasks-app create db.py with a get_connection() and an init_db() that creates the tasks table ....
```

That works for any step whose result is just files, which is Steps 2 to 5. It does not work for the one harness file this lab writes: `/init` in Step 1 puts `CLAUDE.md` in the directory the session was launched in and reads it from there, so a root session never gives the task API its own instructions. Launch inside `tasks-app` from Step 1 onward.

Launching inside the project is what makes the repository a monorepo to this lab rather than the project: the repo's own `/CLAUDE.md`, `/.claude/` and `/.mcp.json` stay out of the session and are read from the repo root. You read from them without ever writing into them, and every path in the prompts below is relative to the lab folder.

You can reach the same session from VS Code instead: open that folder with `code .`, then open the Claude panel from the Activity Bar. The `/init` in Step 1 writes its `CLAUDE.md` into that folder, which is the point: run it at the repo root and you would be rewriting this course repository's own instructions.

---

## Step 1: Project Setup

With the session open in `tasks-app/`, use `/init` to generate the CLAUDE.md, then refine it:

**Prompt:**

```text
/init
```

Then follow up with:

```text
Update the CLAUDE.md: this is a task tracking REST API built with Python, SQLite, and Flask running on port 8000. Add an architecture section listing the files we will create: db.py, models.py, app.py, test-api.http. Add a hard rule: no external ORM — use sqlite3 directly.
```

**Expected result:** A `CLAUDE.md` in `tasks-app/` describing the project purpose, file layout, and the no-ORM rule.

---

## Step 2: Dependencies and Virtual Environment

**Goal:** Let Claude reason about the required packages and install them in a local `.venv`.

**Prompt:**

```text
Reflect on the dependencies needed for a Flask-based task API with no ORM.
Create a .venv in this folder, activate it, and install all required packages.
Save them to a requirements.txt with pinned versions.
```

**Expected result:** A `.venv/` directory, a `requirements.txt` containing at minimum `flask`, and a confirmation that the environment is ready.

---

## Step 3: Database Setup

**Goal:** Create a database module that manages the SQLite connection and initialises the schema.

**Prompt:**

```text
Create db.py. It should open a SQLite database file called tasks.db in the project folder.
Provide a get_connection() function and an init_db() function that creates the tasks table if it does not exist.
The tasks table needs: id (integer primary key), title (text, not null), done (integer default 0), created_at (text).
```

**Expected result:** A `db.py` module with `get_connection()` and `init_db()`. Running `python db.py` should create `tasks.db`.

---

## Step 4: Model, API, and CRUD

**Goal:** Build the full Flask REST API with create, read, update, and delete for tasks.

**Prompt:**

```text
Create app.py with a Flask application. Call init_db() on startup.
Implement these endpoints:
  POST   /tasks        — create a task (body: { "title": "..." })
  GET    /tasks        — list all tasks
  GET    /tasks/<id>   — get one task
  PATCH  /tasks/<id>   — update title or done status
  DELETE /tasks/<id>   — delete a task

Return JSON for all responses. Use HTTP 201 for creation, 404 when a task is not found.
Run the app on port 8000 with debug mode on.
```

**Expected result:** An `app.py` that starts with `python app.py` and serves the five endpoints on `http://localhost:8000`.

---

## Step 5: REST Client Tests

**Goal:** Add a `.http` test file so you can call the API directly from VS Code using the REST Client extension.

**Setup:** Install the [REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client) extension in VS Code before running this step.

**Prompt:**

```text
The REST Client VS Code extension (humao.rest-client) reads .http files and lets you send HTTP requests with a "Send Request" link above each one.
Create test-api.http with requests for all five endpoints against http://localhost:8000.
Include a request that creates a task, one that lists all tasks, one that fetches a single task by id, one that marks it done, and one that deletes it.
Add a comment above each request describing what it tests.
```

**Expected result:** A `test-api.http` file with five labeled requests. With the app running (`python app.py`), clicking **Send Request** above any block executes it and shows the JSON response in a split pane.
