---
presents: demo-work-package-decomposition.md
budget: 4 min
beats: 4
---

# Present: Decompose a Plan into Work Packages and Draft the Issues

A work package is four fields, and only the contract is hard; a draft issue tree is where the agent stops and you take over. Four beats: the fields, declared dependencies, the contract that runs but proves little, the draft that files nothing.

------

## Beats

### Beat 1: a package is four fields, and only one of them is hard (1 min)

**Open:** [Split the Plan into Four Packages](demo-work-package-decomposition.md#split-the-plan-into-four-packages) · [Work packages with contracts](readme.md#work-packages-with-contracts)
**Say:** A package is a unit one session can finish without coming back to ask a question. The contract is the only field a reviewer can check without opening the source.

```text
Decompose the work in STATE.md into four work packages, each one small enough to hand to a separate executor. For each:
  - name (short, lowercase, hyphenated)
  - input: the files it may read and the section of STATE.md that governs it
  - output: the files it creates or modifies and the contract it must satisfy (a callable command plus the expected output)
  - depends on: which other package must finish first, if any
```

**Result:** [`work-packages.md`](hr-mcp-server-solution/work-packages.md), one table row per package, inputs traced to the `STATE.md` Decisions they are governed by

```markdown
| name | input | output | depends on |
|---|---|---|---|
| vacancy-schema | STATE.md "Decisions": vacancy fields, storage through EmployeeDbContext, entity pattern, existing databases. Files: `Tools/Models.cs`, `Data/EmployeeDbContext.cs`, `Data/EmployeeDbInitializer.cs`. | ... | none |
```

**Gotcha:** the package names match the Status checkboxes in `STATE.md`, which is how the executing session knows which box to flip.

### Beat 2: dependencies are declared, never inferred (1 min)

**Open:** [`Program.cs`](hr-mcp-server/Program.cs) · [`Tools/HRTools.cs`](hr-mcp-server/Tools/HRTools.cs)
**Say:** An executor sees its own package and nothing else, so ordering exists only if somebody wrote it down. The registration lines show why this chain is serial.

```csharp
// Register the employee service
builder.Services.AddScoped<IEmployeeService, EmployeeService>();

// Add the MCP services: the transport to use (HTTP) and the tools to register.
builder.Services.AddMcpServer()
    .WithHttpTransport()
    .WithToolsFromAssembly();
```

**Result:** the last column of [`work-packages.md`](hr-mcp-server-solution/work-packages.md), a strict chain

```markdown
| vacancy-schema | ... | none |
| vacancy-service | ... | vacancy-schema |
| vacancy-tools | ... | vacancy-service |
| smoke-verification | ... | vacancy-tools |
```

**Gotcha:** none of the four runs in parallel; the tools need the service and the service needs the table, and the declaration is what makes that visible.

### Beat 3: a runnable contract can still prove almost nothing (1 min)

**Open:** [Audit Each Contract for Runnability](demo-work-package-decomposition.md#audit-each-contract-for-runnability) · [`Services/EmployeeService.cs`](hr-mcp-server/Services/EmployeeService.cs)
**Say:** A command you can run yourself is the floor for a contract, and a build clears that floor. What a build proves is that the code compiles.

```text
Contract: `dotnet build exits 0`.
```

**Result:** three of four rows in [`work-packages.md`](hr-mcp-server-solution/work-packages.md) carry that contract; the ranking rule is first exercised in the last row

```markdown
(3) `match_candidates` for a vacancy requiring "Menu Planning, Food Safety" returns Carlos Gomez first; the argument syntax for `tools/call` is not in the readme and must be confirmed first.
```

**Gotcha:** with no test project that is an honest contract; in a project with tests, send the package back and ask for the test command that proves its behaviour.

### Beat 4: the draft stops before anything is filed (1 min)

**Open:** [Draft the Issues](demo-work-package-decomposition.md#draft-the-issues) · [From plan to tracked work](readme.md#from-plan-to-tracked-work)
**Say:** Filing creates real issues in a real repository, so the agent writes the draft and the commands, and you run them against your own project.

```text
Turn work-packages.md into a GitHub issue draft in issues.md: one parent issue for the vacancies feature and one sub-issue per package, each with a title, a body holding its input, output, contract and dependency, and the label planning. Below the draft, list the gh commands that create the label, the parent issue and the sub-issues, and the gh api calls that link each sub-issue to the parent through the sub-issues REST endpoint. Do not run any gh command.
```

**Result:** [`issues.md`](hr-mcp-server-solution/issues.md), a parent, four sub-issues, and the four link calls at the end

```bash
gh api --method POST repos/{owner}/{repo}/issues/<P>/sub_issues -F sub_issue_id=<ID1>
gh api --method POST repos/{owner}/{repo}/issues/<P>/sub_issues -F sub_issue_id=<ID2>
gh api --method POST repos/{owner}/{repo}/issues/<P>/sub_issues -F sub_issue_id=<ID3>
gh api --method POST repos/{owner}/{repo}/issues/<P>/sub_issues -F sub_issue_id=<ID4>
```

**Gotcha:** `sub_issue_id` takes the database id from the first `gh api` call; passing the issue number is the one detail that makes a hand-rolled link fail.

## If the room asks

| Question | Answer |
|---|---|
| Is this delegation? | Nothing is implemented and no second agent runs. The packages are written so a later session or a teammate can execute them. |
| Why four packages? | Three to five is the working range; past seven the coordination cost exceeds the parallelism. |
| Can I run the `gh` commands in the course repository? | Run them in a repository you own: `gh` resolves `{owner}/{repo}` from the remote of the folder you run it in. |
