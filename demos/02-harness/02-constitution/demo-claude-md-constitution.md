# Build a Layered CLAUDE.md Constitution

CLAUDE.md is the context Claude loads before your first prompt, and it works in three layers: project, personal, and folder-scoped. You write the hard rules of an undocumented C# Web API into a project constitution and layer a personal file and a `Controllers/`-scoped file over it.

---

Work directly in the starter, `demos/02-harness/02-constitution/constitution-api`, a small C# ASP.NET Core API with no `CLAUDE.md` of its own; no finished copy ships, because writing that file is the whole point of this demo.

## Step 1: Write the Project Constitution

Overview: The project CLAUDE.md is checked into the repository, so it applies to every developer and every CI run. It is the right home for rules that are true about this codebase regardless of who is working on it.

```text
Create CLAUDE.md in the project root with these sections:

## Hard rules
- YOU MUST NOT commit or push without an explicit request.
- Every new endpoint that returns a collection returns PaginatedResponse<T>.
- Code fences in documentation declare a language.

## Workflow preferences
- Small fixes get a minimal diff. Never rewrite a file to change one line.
- Never paste file contents into a prompt. Use @path/to/file.cs instead.

Keep every rule to one line and make each one checkable.
```

Expected Outcome: A `CLAUDE.md` in the project root. Restart Claude Code in this folder and ask `what are my hard rules?`: the answer comes back without you attaching anything.

## Step 2: Layer the Global File Over the Project File

Overview: `~/.claude/CLAUDE.md` applies to every project on your machine and is never committed. A subfolder CLAUDE.md applies only when Claude works inside that part of the tree, which keeps narrow rules such as controller conventions out of the root file.

```text
Create ~/.claude/CLAUDE.md with personal preferences only, no project facts:

## How I work
- Answer directly. No preamble, no end-of-turn summary unless I ask.
- Show the file path above every code block when touching multiple files.
- Ask before creating a new file. Suggest editing an existing one first.

Then tell me, for this session, which rules come from the global file and
which come from the project file.
```

```text
Create Controllers/CLAUDE.md containing only rules that bind inside this folder:

## Controller conventions
- Controllers contain no business logic. They validate input and delegate.
- Every action returning a collection returns PaginatedResponse<T>.
- Every action declares its response type with [ProducesResponseType].

Then remove any of these rules that now duplicate the root CLAUDE.md, and show
me the diff of the root file before you write it.
```

Expected Outcome: A `~/.claude/CLAUDE.md` and a response that sorts the active rules by source file, then a `Controllers/CLAUDE.md` and a shorter root file with no duplicated rules. Ask Claude to add an endpoint to `TodosController.cs` and the pagination rule is applied without you naming it.

## Step 3: Record Durable Facts With /memory

Overview: CLAUDE.md holds stable, shared project rules; memory holds evolving, personal notes that outlive a single conversation. A rule that expires next week should not reach every teammate through git.

```text
remember I am migrating both controllers to PaginatedResponse<T> and Program.cs
is off limits until that is done

Then show me the file you wrote and the exact line you added.
```

Expected Outcome: The memory file contains your ongoing-work note and Claude reports the path it wrote to. Start a fresh session, ask it to register a new service in `Program.cs`, and it declines or checks with you first, citing the note it stored. Push back if Claude proposes adding an in-progress note to the project CLAUDE.md.
