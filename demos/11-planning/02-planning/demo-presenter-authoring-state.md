---
presents: demo-authoring-state.md
budget: 4 min
beats: 4
---

# Present: Capture a Planning Session in STATE.md

`STATE.md` is dictated section by section, its Decisions trace to a source, and an empty Open Questions is the gate before anyone executes. Four beats: the dictated sections, the traced decisions, the closed question, the update rule.

------

## Beats

### Beat 1: you dictate the sections, Claude fills only the content (1 min)

**Open:** [Dictate the Statefile Sections](demo-authoring-state.md#dictate-the-statefile-sections) · [STATE.md: the rolling handoff document](readme.md#statemd-the-rolling-handoff-document)
**Say:** The structure is yours to fix and the content is Claude's to supply. Ask for a statefile in the abstract and every session returns a differently organised essay.

```text
Write STATE.md in this folder with exactly these sections:

## Goal
Add vacancies to the HR MCP server.

## Decisions
[every decision plan.md and the constraints below lock in: the vacancy fields, the four tool names, storage through EmployeeDbContext with no new packages, how the Vacancies table reaches an existing hr-data.db, the ranking rule for match_candidates]
```

**Result:** the headings came back literally, in the dictated order, in [`STATE.md`](hr-mcp-server-solution/STATE.md)

```markdown
## Goal
Add vacancies to the HR MCP server.

## Decisions
- Vacancy fields: `Title`, `RequiredSkills`, `RequiredLanguages`, and `Status` with values `open` or `filled`. Each vacancy also has an integer `Id`, which is `[JsonIgnore]` as on `Employee`.
```

**Gotcha:** the bracketed text is a checklist of what Decisions must cover; tick each item off against the file.

### Beat 2: every decision traces to plan.md or a constraint (1 min)

**Open:** [`plan.md`](hr-mcp-server-solution/plan.md) · task 3 · [`Data/EmployeeDbInitializer.cs`](hr-mcp-server/Data/EmployeeDbInitializer.cs)
**Say:** A model asked to write up a plan fills its gaps, and a plausible filling looks exactly like an agreement once written down. So the file is checked against its sources.

```text
Use plan.md and these constraints as the source of truth. Do not invent new decisions.

Constraints (non-negotiable):
  ...
  4. Existing employee rows in hr-data.db must survive. No destructive migration.
```

**Result:** the decision the existing database depends on, in [`STATE.md`](hr-mcp-server-solution/STATE.md), which plan.md task 3 covers

```markdown
- Existing databases: `EnsureCreatedAsync` skips an existing `hr-data.db`, so the Vacancies table is created with `CREATE TABLE IF NOT EXISTS` after `EnsureCreatedAsync`. Employee rows are kept. Deleting and reseeding `hr-data.db` is excluded, because it is destructive.
```

**Gotcha:** a bullet with no line behind it in either source is a choice the model made for you; strike it and point at the sources.

### Beat 3: an open question is a decision the executor would make for you (1 min)

**Open:** [Close the Open Question](demo-authoring-state.md#close-the-open-question) · [`Services/EmployeeService.cs`](hr-mcp-server/Services/EmployeeService.cs) · `GetAllEmployeesAsync`
**Say:** Claude left the tie order open because neither the plan nor the constraints order equal scores. One constraint line closes it, and the answer can lean on an order the code already has.

```csharp
        return await _dbContext.Employees
            .AsNoTracking()
            .OrderBy(c => c.LastName)
            .ThenBy(c => c.FirstName)
            .ToListAsync();
```

**Result:** [`STATE.md`](hr-mcp-server-solution/STATE.md) moved the tie answer into Decisions and emptied Open Questions, the five other items included

```diff
+- Ties in `match_candidates`: employees with the same match count keep the order that `list_employees` returns.
...
-- Tie-breaking when two employees hold the same number of required skills. Neither plan.md nor the constraints order them.
...
```

**Gotcha:** a question left open in the plan costs one more turn; the same question found in code costs everything built on top of it.

### Beat 4: a statefile stays true only if a rule keeps it updated (1 min)

**Open:** [STATE.md: the rolling handoff document](readme.md#statemd-the-rolling-handoff-document) · `CLAUDE.md` (the learner adds it in the [hr-mcp-server/](hr-mcp-server) starter, which ships none)
**Say:** Discipline you have to remember under deadline fails under deadline. The read and the update belong in the project's own instructions, where every session inherits them.

```text
Read STATE.md before any non-trivial change. Update STATE.md after any non-trivial change.
```

**Result:** no `CLAUDE.md` shipped, deliberately; the rule is the learner's to add, and every Status box in [`STATE.md`](hr-mcp-server-solution/STATE.md) is still open for the executing session to flip

```markdown
## Status
- [ ] vacancy schema
- [ ] vacancy service
- [ ] vacancy tools
- [ ] smoke verification
```

**Gotcha:** one skipped update starts the drift, and a quietly stale statefile is worse than none, because the next session has no reason to doubt it.

## If the room asks

| Question | Answer |
|---|---|
| Is STATE.md a spec by another name? | A spec is the desired end state, written once. STATE.md is the current state, updated after every session. |
| Who reads it? | The next Claude session, which resumes without re-deriving the plan. |
| Where do the Status items come from? | From the work packages: the next demo splits this file into four packages whose names match these checkboxes. |
