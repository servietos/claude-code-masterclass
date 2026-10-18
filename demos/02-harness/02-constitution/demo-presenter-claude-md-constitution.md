---
presents: demo-claude-md-constitution.md
budget: 4 min
beats: 4
---

# Present: Build a Layered CLAUDE.md Constitution

Four beats walk the room through the three CLAUDE.md layers, from the project constitution to a folder-scoped rule and a memory note. The room walks away able to say which layer a given rule belongs in, and why a rule Claude cannot check is not a rule.

------

**No solution folder ships.** The run writes two markdown files into `constitution-api/` and one into `~/.claude/`.

## Beats

### Beat 1: The project layer holds rules an agent can check (1 min)

**Open:** [Step 1: Write the Project Constitution](demo-claude-md-constitution.md#step-1-write-the-project-constitution) · [`constitution-api/Models/PaginatedResponse.cs`](constitution-api/Models/PaginatedResponse.cs)
**Say:** The project file is committed, so it binds every developer and every CI run. The bar for a rule is whether it can be evaluated against a diff.

```text
## Hard rules
- YOU MUST NOT commit or push without an explicit request.
- Every new endpoint that returns a collection returns PaginatedResponse<T>.
- Code fences in documentation declare a language.

...

Keep every rule to one line and make each one checkable.
```

**Result:** `CLAUDE.md`, written by this step into [`constitution-api/`](constitution-api); the starter ships none.

**Gotcha:** "Write clean code" cannot be evaluated against a diff, so it changes no behaviour and quietly trains the room to distrust the file.

### Beat 2: The global layer carries preferences, never project facts (1 min)

**Open:** [`readme.md`](readme.md#claudemd-file-locations) · the three CLAUDE.md locations
**Say:** Claude Code merges several CLAUDE.md files, and the split between them follows ownership. Anything true about one codebase is misplaced in the file that follows you everywhere.

```text
Create ~/.claude/CLAUDE.md with personal preferences only, no project facts:

## How I work
- Answer directly. No preamble, no end-of-turn summary unless I ask.
- Show the file path above every code block when touching multiple files.
- Ask before creating a new file. Suggest editing an existing one first.

Then tell me, for this session, which rules come from the global file and
which come from the project file.
```

**Result:** `~/.claude/CLAUDE.md`, outside the repository and invisible to git, so no relative link reaches it.

**Gotcha:** an answer that lists one flat set of rules means the layers are not distinctive enough to reason about yet.

### Beat 3: A subfolder file binds only inside its folder (1 min)

**Open:** [Step 2: Layer the Global File Over the Project File](demo-claude-md-constitution.md#step-2-layer-the-global-file-over-the-project-file) · [`constitution-api/Controllers/`](constitution-api/Controllers)
**Say:** A nested CLAUDE.md loads only when Claude touches a file in that folder, so narrow rules cost nothing on tasks they do not apply to. Moving a rule down is only a win if it also leaves the root.

```text
Create Controllers/CLAUDE.md containing only rules that bind inside this folder:

## Controller conventions
- Controllers contain no business logic. They validate input and delegate.
- Every action returning a collection returns PaginatedResponse<T>.
- Every action declares its response type with [ProducesResponseType].

Then remove any of these rules that now duplicate the root CLAUDE.md, and show
me the diff of the root file before you write it.
```

**Result:** `Controllers/CLAUDE.md` plus a shorter root file, the run's two additions to [`constitution-api/`](constitution-api)

```diff
 constitution-api/
+  CLAUDE.md
   Controllers/
+    CLAUDE.md
     TodosController.cs
     UsersController.cs
```

**Gotcha:** moving a rule down without removing it from the root leaves two copies that drift apart.

### Beat 4: A temporary constraint does not belong in CLAUDE.md (1 min)

**Open:** [Step 3: Record Durable Facts With /memory](demo-claude-md-constitution.md#step-3-record-durable-facts-with-memory)
**Say:** A temporary constraint belongs in memory, which is per-person and expires without a commit reaching the team.

```text
remember I am migrating both controllers to PaginatedResponse<T> and Program.cs
is off limits until that is done
```

**Result:** the `remember` line goes to the memory file outside the repository, never into CLAUDE.md.

**Gotcha:** push back if Claude offers to add an in-progress note to the project CLAUDE.md.

## If the room asks

| Question | Answer |
|---|---|
| Which layer wins when two files disagree? | The more specific scope wins for the rule it names; ask Claude to name the file each active rule comes from. |
| I edited CLAUDE.md and nothing changed. Why? | Root and global files are read once at session start; the edit applies on the next `/clear`, `/compact` or restart. |
| Does the subfolder file load for every task? | No, it loads later, when Claude first reads a matching file, unlike the root file that loads at session start. |
