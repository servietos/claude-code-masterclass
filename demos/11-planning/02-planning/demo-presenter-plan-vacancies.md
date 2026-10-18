---
presents: demo-plan-vacancies.md
budget: 4 min
beats: 4
---

# Present: Plan the Vacancies Feature Through a Shared Ledger

Subagents share nothing, so a ledger file becomes their shared state, and a plan checked against that ledger and the locked constraints shows exactly where it drifted. Four beats: the ledger as shared state, the finding nobody asked for, the review that catches the drift, the narrow fix.

------

## Beats

### Beat 1: the ledger is created first and named in every brief (1 min)

**Open:** [`Tools/HRTools.cs`](hr-mcp-server/Tools/HRTools.cs) · [Step 1: Research in parallel through a shared ledger](demo-plan-vacancies.md#step-1-research-in-parallel-through-a-shared-ledger)
**Say:** Each subagent gets only the message Claude writes it and returns only its result. A file is the one thing three of them can share.

```text
First create the shared ledger ledger.md in this folder with three empty headings: MCP tools, Data, Verification.

Then run three general-purpose subagents in parallel. Research only inside this folder; ignore bin and obj. Tell each subagent the ledger path and to write its findings under its own heading in that file, and nothing else:
```

**Result:** [`ledger.md`](hr-mcp-server-solution/ledger.md), 80 lines, one heading per subagent, every finding cited by file and line

```markdown
# Ledger

## MCP tools
...
## Data
...
## Verification
```

**Gotcha:** the built-in Explore and Plan subagents are read-only and cannot write the ledger, which is why the recipe asks for `general-purpose`.

### Beat 2: three parallel readers find what no brief asked for (1 min)

**Open:** [`Data/EmployeeDbContext.cs`](hr-mcp-server/Data/EmployeeDbContext.cs) · `OnModelCreating`
**Say:** Research is the slow part of planning and most of it is independent. Every finding comes back with a line number you can check.

```csharp
    public DbSet<Employee> Employees => Set<Employee>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        var employeeEntity = modelBuilder.Entity<Employee>();

        employeeEntity.ToTable("Candidates");
```

**Result:** the Data heading of [`ledger.md`](hr-mcp-server-solution/ledger.md) caught the table name

```markdown
- `DbSet<Employee> Employees` (line 13) maps to table `Candidates` (line 19). The table name differs from the class name.
```

**Gotcha:** a plan that writes SQL against an `Employees` table reads fine and fails on the first start; the ledger line is what a reviewer checks it against.

### Beat 3: a brief without the constraints drifts, and the review catches it (1 min)

**Open:** [Step 2: Check the plan against the ledger and the constraints](demo-plan-vacancies.md#step-2-check-the-plan-against-the-ledger-and-the-constraints) · [`ledger.md`](hr-mcp-server-solution/ledger.md)
**Say:** The research brief carried the feature and left out the five constraints from plan mode. Reviewing against both turns "sounds right" into "which line supports this".

```text
Review plan.md against ledger.md and against the constraints below, which were locked in the planning session. For every acceptance criterion, quote the ledger line that supports it. Then list each place the plan contradicts a constraint, each criterion the ledger does not support, and each assumption about the running server that nobody verified. Do not edit any file.
```

**Result:** no file, by design; the review answered in chat, and its first two contradictions were

```text
1. **Constraint 2 (tool names).** The plan names the tools `AddVacancy`, `ListVacancies`, `CloseVacancy` and `FindMatchingEmployees` (summary and task 5). The required names are `add_vacancy`, `list_vacancies`, `close_vacancy` and `match_candidates`.
2. **Constraint 5 (ranking).** Task 4 defines matching as "every required skill," and task 8 repeats it. The required behaviour is a ranking by count of matched skills, so employees with partial matches must be returned.
```

**Gotcha:** push back on a review that restates the plan; the useful one rates each criterion and quotes the ledger line by number.

### Beat 4: a fix that names what changes gets a reviewable diff (1 min)

**Open:** [`Services/EmployeeService.cs`](hr-mcp-server/Services/EmployeeService.cs) · `SearchEmployeesAsync` · [Step 2](demo-plan-vacancies.md#step-2-check-the-plan-against-the-ledger-and-the-constraints)
**Say:** A correction prompt that lists exactly what changes and ends with "change nothing else" turns a review into a small diff.

```text
- match_candidates returns every employee ranked by how many of the vacancy's required skills they have, most matches first, and its acceptance criteria check that order.
- The verification task deletes hr-data.db only on a throwaway copy, never the file holding existing employee rows.
Change nothing else in plan.md and do not touch ledger.md or any code.
```

**Result:** [`plan.md`](hr-mcp-server-solution/plan.md) has eight tasks; the matching criteria now check an ordering

```markdown
- Acceptance: the service compiles, is registered, and returns every employee in descending order of matched-skill count for a vacancy with two required skills.
- Acceptance: the build succeeds with no errors. `tools/list` shows nine tools. `add_vacancy` followed by `list_vacancies` returns the new vacancy. `match_candidates` on a vacancy with two required skills returns every employee, with each matched-skill count equal to or lower than the count before it, so the highest count comes first. `CloseVacancy` changes the status, and `ListVacancies` with status `open` no longer returns it. Tests are not run unless you ask for them.
```

**Gotcha:** the review's unverified-assumptions list is where a gap goes; this run listed ten, and the first is that nobody has run the server.

## If the room asks

| Question | Answer |
|---|---|
| Do the subagents see each other's entries? | Only by reading the file. They share no conversation, and the main agent reads the whole ledger before writing the plan. |
| Could this run in plan mode? | Not as written: plan mode blocks the ledger and plan writes. Its own research goes through the read-only Plan subagent, and the result lands in the plan file. |
| Where does the ledger go in a real project? | Commit it beside the plan. It outlives the session and backs every claim during review. |
