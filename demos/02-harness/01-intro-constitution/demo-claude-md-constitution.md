# Build a Layered CLAUDE.md Constitution

CLAUDE.md is the context Claude loads before your first prompt, and it works in three layers: project, personal, and folder-scoped. You map an undocumented C# Web API, write its hard rules into a project constitution, layer a personal file and a `Controllers/`-scoped file over it, and replace pasted code with `@`-mentions. You finish with a working three-layer memory setup and a controller rewritten from the rules alone.

---

## Demo Files

Work directly in the starter. It is a small C# ASP.NET Core API with no `CLAUDE.md` of its own, because writing that file is the whole point of this demo:

```bash
cd demos/02-harness/01-intro-constitution/constitution-api
claude
```

| File | What it represents |
|------|--------------------|
| `Program.cs` | Application entry point and service registration, the file that reveals the project's shape |
| `Controllers/TodosController.cs` | HTTP surface with hardcoded data, no pagination |
| `Controllers/UsersController.cs` | Second controller, used to prove a convention is applied consistently |
| `Models/PaginatedResponse.cs` | The response envelope your conventions will standardise on |
| `TodoApi.csproj` | Target framework and package references |

---

## Step 1: Map the Project Before Writing a Rule

Overview: A constitution written from guesswork encodes the wrong architecture. Before writing a single rule, have Claude read the project and report what it actually finds, so every rule you write afterwards is grounded in the real folder layout and the real conventions already present in the code.

Research / Planning / Discussion:

```text
Read Program.cs, both files under Controllers/, and everything under Models/.

Describe this project back to me: what it does, how the folders are organised,
what conventions the existing code already follows, and where those conventions
are inconsistent between the two controllers.

Do not write any files yet.
```

Finding: A good response names the folder responsibilities (`Controllers/` for HTTP, `Models/` for shapes) and points out at least one real inconsistency, such as `PaginatedResponse<T>` existing in `Models/` while neither controller returns it. Push back if the answer is generic ASP.NET Core advice with no file paths in it: that means Claude summarised its training data instead of reading your code.

Recipe:

```text
Read Program.cs, Controllers/TodosController.cs, Controllers/UsersController.cs,
and Models/PaginatedResponse.cs.

Produce a markdown table with one row per folder: the folder path, what belongs
in it, and what must never go in it. Base every row on what you actually read,
not on general ASP.NET Core conventions. Output the table in chat only.
```

Expected Outcome: A table in the response naming `Controllers/`, `Models/`, and the project root, each row citing a file you can open. You now have the architecture map that becomes the middle section of CLAUDE.md.

---

## Step 2: Write the Project Constitution

Overview: The project CLAUDE.md is checked into the repository, so it applies to every developer and every CI run. It is the right home for rules that are true about this codebase regardless of who is working on it: architecture, conventions, and hard prohibitions.

Research / Planning / Discussion:

```text
I want to write a CLAUDE.md for this project. Propose an outline of sections
and, for each one, explain what belongs in it and what belongs somewhere else.

For every rule you suggest, tell me whether it is project-specific (belongs in
the repository) or a personal preference (belongs in my global file). Do not
create the file yet.
```

Finding: The strongest responses split the outline into hard rules, an architecture map, and workflow preferences, and correctly route personal taste (response style, preferred shell) out of the project file. If a proposed rule is unfalsifiable, such as "write clean code", ask Claude to restate it as something an agent can actually check.

Recipe:

```text
Create CLAUDE.md in the project root with these sections:

## Hard rules
- YOU MUST NOT commit or push without an explicit request.
- Every new endpoint that returns a collection returns PaginatedResponse<T>.
- Code fences in documentation declare a language.

## Architecture map
Use the folder table you produced earlier, one bullet per folder.

## Workflow preferences
- Small fixes get a minimal diff. Never rewrite a file to change one line.
- Never paste file contents into a prompt. Use @path/to/file.cs instead.

Keep every rule to one line and make each one checkable.
```

Expected Outcome: A `CLAUDE.md` in the project root whose architecture map matches the table from Step 1. Restart Claude Code in this folder and ask `what are my hard rules?`: the answer comes back without you attaching anything.

---

## Step 3: Layer the Global File Over the Project File

Overview: `~/.claude/CLAUDE.md` applies to every project on your machine and is never committed. Understanding which layer wins when two files disagree is the difference between a hierarchy you control and one that surprises you.

Research / Planning / Discussion:

```text
Read my global CLAUDE.md at ~/.claude/CLAUDE.md and the project CLAUDE.md in
this folder.

Which instructions are currently in scope for this session, and where does each
one come from? If any two rules conflict, tell me which one you would follow
and why. If I have no global file yet, say so and propose what belongs in it.
```

Finding: Look for an answer that attributes rules to a file path rather than listing them as one flat set. A response that cannot say where a rule came from is a signal to make the rules more distinctive before testing precedence.

Recipe:

```text
Create ~/.claude/CLAUDE.md with personal preferences only, no project facts:

## How I work
- Answer directly. No preamble, no end-of-turn summary unless I ask.
- Show the file path above every code block when touching multiple files.
- Ask before creating a new file. Suggest editing an existing one first.

Then tell me, for this session, which rules come from the global file and
which come from the project file.
```

Expected Outcome: A `~/.claude/CLAUDE.md` on disk and a response that sorts the active rules by source file. Personal preferences now travel with you across every repository while the project rules stay with the repository.

---

## Step 4: Scope a Subfolder Constitution

Overview: A subfolder CLAUDE.md applies only when Claude works inside that part of the tree. It keeps narrow rules, such as controller conventions, out of the root file where they would be loaded for every task including documentation edits.

Research / Planning / Discussion:

```text
Which of the rules currently in my root CLAUDE.md are only relevant when
editing files under Controllers/?

For each one, tell me the cost of leaving it in the root file versus moving it
into Controllers/CLAUDE.md. Do not move anything yet.
```

Finding: A useful answer separates rules that are always true (never commit without asking) from rules that only bind inside one folder (controllers stay thin and delegate). If Claude proposes moving everything down, ask which rules a documentation-only task still needs.

Recipe:

```text
Create Controllers/CLAUDE.md containing only rules that bind inside this folder:

## Controller conventions
- Controllers contain no business logic. They validate input and delegate.
- Every action returning a collection returns PaginatedResponse<T>.
- Every action declares its response type with [ProducesResponseType].

Then remove any of these rules that now duplicate the root CLAUDE.md, and show
me the diff of the root file before you write it.
```

Expected Outcome: A `Controllers/CLAUDE.md` on disk and a shorter root file with no duplicated rules. Ask Claude to add an endpoint to `TodosController.cs` and the pagination rule is applied without you naming it.

---

## Step 5: Replace Pasted Code With @-Mentions

Overview: Pasting a file into a prompt copies it into the context window every single turn it stays in the conversation. An `@`-mention hands Claude the path instead, so the file is read once and the prompt itself stays small.

Research / Planning / Discussion:

```text
Compare two ways of asking you to review a controller: pasting the full file
into the prompt, versus writing @Controllers/UsersController.cs.

Explain what changes in what you receive, what happens on the next five turns
of the conversation in each case, and when pasting is still the better choice.
```

Finding: A correct answer explains that pasted text persists in the transcript while an `@`-mention is a read that can be re-issued on demand. It should also name the one case where pasting wins: content that is not on disk, such as a stack trace from a colleague.

Recipe:

```text
@Controllers/UsersController.cs @Models/PaginatedResponse.cs

Rewrite the list action in UsersController so it returns PaginatedResponse<User>
with page and pageSize query parameters, matching the shape in the model file
exactly. Follow the conventions in Controllers/CLAUDE.md.
```

Expected Outcome: A modified `Controllers/UsersController.cs` returning a paginated envelope whose field names match `PaginatedResponse.cs` exactly, produced from a prompt of three lines. Run `dotnet build` to confirm it compiles.

---

## Step 6: Record Durable Facts With /memory

Overview: CLAUDE.md holds stable, shared project rules; memory holds evolving, personal notes that outlive a single conversation. Using the wrong one for a fact means either polluting the repository with your in-progress work, or losing that work at the next context reset.

Research / Planning / Discussion:

```text
Run /memory and show me what is currently stored.

I am mid-way through paginating the controllers and I do not want Program.cs
touched until that is finished. Should that fact live in CLAUDE.md, in memory,
or in neither? Explain the trade-off before you write anything.
```

Finding: The right answer routes a temporary, personal constraint to memory and keeps the repository file free of it, because a rule that expires next week should not reach every teammate through git. Push back if Claude proposes adding an in-progress note to the project CLAUDE.md.

Recipe:

```text
remember I am migrating both controllers to PaginatedResponse<T> and Program.cs
is off limits until that is done

Then show me the file you wrote and the exact line you added.
```

Expected Outcome: The memory file contains your ongoing-work note and Claude reports the path it wrote to. Start a fresh session, ask it to register a new service in `Program.cs`, and it declines or checks with you first, citing the note it stored.

---

## Summary

You built a three-layer constitution: personal preferences in the global file, shared project facts in the repository file, and folder-scoped conventions beside the code they govern. You proved each layer is in scope by having Claude attribute its own rules, replaced pasted code with `@`-mentions, and separated durable project rules from expiring personal notes.

Continue with [Automate a Release CLI with Custom Slash Commands](../02-commands/demo-slash-command-toolkit.md).

