---
presents: demo-plan-mode-constraint-ratchet.md
budget: 4 min
beats: 4
---

# Present: Lock design decisions incrementally with Plan Mode

A question list is a planning deliverable, and constraints sent before the ask are read as specification. Four beats: the vague brief, the trap plan mode finds while it reads, the ratchet, the stop rule.

------

## Beats

### Beat 1: a vague brief in plan mode comes back as questions and a provisional plan (1 min)

**Open:** [`Tools/HRTools.cs`](hr-mcp-server/Tools/HRTools.cs) · [Part A: Vague Brief](demo-plan-mode-constraint-ratchet.md#part-a-vague-brief)
**Say:** Outside plan mode an under-specified request gets resolved silently, and that guess is free to make and expensive to undo. Plan mode hands the ambiguity back to whoever owns it.

```text
I want to add vacancies to the HR MCP server.
```

**Result:** [`plan-mode-turn-1.md`](hr-mcp-server-solution/plan-mode-turn-1.md) copies the employee tool set and lists its guesses for you to correct

```markdown
- `Tools/VacancyTools.cs` (`[McpServerToolType]`, picked up by `WithToolsFromAssembly`): `list_vacancies`, `add_vacancy`, `update_vacancy`, `remove_vacancy`, `search_vacancies`, same thin-tool style as `HRTools`.
2. Key for update/remove: integer Id returned by `list_vacancies` (recommended; vacancies have no natural unique key like email).
```

**Gotcha:** the plan file name is generated per session (`i-want-to-add-parsed-minsky.md` in this run); `Ctrl+G` opens it without hunting for the path.

### Beat 2: plan mode still reads, so it finds what the brief never mentioned (1 min)

**Open:** [`Data/EmployeeDbInitializer.cs`](hr-mcp-server/Data/EmployeeDbInitializer.cs) · `InitializeAsync`
**Say:** Plan mode removes the edits and keeps the research. The trap in this server sits in one line of the initializer.

```csharp
        var context = scopedServices.GetRequiredService<EmployeeDbContext>();
        await context.Database.EnsureCreatedAsync(cancellationToken);

        if (await context.Employees.AnyAsync(cancellationToken))
```

**Result:** item 1 under Decisions for you in [`plan-mode-turn-1.md`](hr-mcp-server-solution/plan-mode-turn-1.md), written before anyone asked about existing databases

```markdown
1. Schema: `EnsureCreatedAsync` skips existing tables, so an existing `hr-data.db` needs deleting once (or I add a create-if-missing step). Which?
```

**Gotcha:** the server readme's reset advice, delete `hr-data.db`, is exactly what constraint 4 forbids on a database with real rows.

### Beat 3: constraints before the ask arrive as specification (1 min)

**Open:** [Part B: Constraint Ratchet](demo-plan-mode-constraint-ratchet.md#part-b-constraint-ratchet) · [`Tools/Models.cs`](hr-mcp-server/Tools/Models.cs)
**Say:** The same five lines read as negotiation after a plan exists and as specification before it. They remove decisions you already made, which frees the turn for the ones you have not.

```text
Constraints (non-negotiable):
  1. A vacancy has a title, required skills, required languages and a status of open or filled.
  2. Four new MCP tools: add_vacancy, list_vacancies, close_vacancy, match_candidates.
  ...
  5. match_candidates returns employees ranked by how many required skills they have.

Revise the plan. Tell me what is still ambiguous.
```

**Result:** the same plan file, rewritten; [`plan-mode-turn-2.md`](hr-mcp-server-solution/plan-mode-turn-2.md) against turn 1

```diff
-- `Tools/VacancyTools.cs` (`[McpServerToolType]`, picked up by `WithToolsFromAssembly`): `list_vacancies`, `add_vacancy`, `update_vacancy`, `remove_vacancy`, `search_vacancies`, same thin-tool style as `HRTools`.
+- `Tools/VacancyTools.cs` (`[McpServerToolType]`, discovered by `WithToolsFromAssembly()`): the four tools, thin, comma-separated list inputs like `AddEmployee`, string results for mutations.
```

**Gotcha:** the closing sentence is load-bearing; this run answered it with ten open points, each with the assumption the plan makes for now.

### Beat 4: more than five turns means the brief is broken (1 min)

**Open:** [Iterating the plan](readme.md#iterating-the-plan)
**Say:** Two or three turns each narrow the ambiguity measurably. Past five they stop, because the missing clarity sits on your side of the conversation.

```markdown
If the planning session needs more than five turns, the brief is fundamentally unclear. Stop, write down what you actually know, and restart with that written brief.
```

**Result:** this session closed in two turns, and the Verification section of [`plan-mode-turn-2.md`](hr-mcp-server-solution/plan-mode-turn-2.md) is already checkable

```markdown
Back up nothing, delete nothing. Copy-free check: `dotnet build`; run against the existing `hr-data.db` and confirm the 8 employees still list and the `Vacancies` table now exists; via the MCP inspector CLI confirm `tools/list` shows 9 tools and a round trip of `add_vacancy`, `list_vacancies`, `match_candidates`, `close_vacancy` returns rows from real calls. No Vitest/Playwright; no docs.
```

**Gotcha:** the stop rule is the beat people forget; past five turns you rewrite the brief and start a fresh session.

## If the room asks

| Question | Answer |
|---|---|
| Is plan mode a different model? | The model is the same. Plan mode changes what it may do: read and explore, write its plan file, edit nothing until you approve. |
| Why send the constraints in a second turn? | In real work send them first. The two-turn shape shows the room what Claude assumes when you do not tell it. |
| What does approving do? | It exits plan mode into the mode the option names, auto mode or manual approval of each edit. **No, keep planning** stays in plan mode. |
| Does plan mode hold in `claude -p`? | Yes, in headless runs and the VS Code chat panel. The recorded run was headless: `--permission-mode plan`, then `--resume` for turn 2. |
