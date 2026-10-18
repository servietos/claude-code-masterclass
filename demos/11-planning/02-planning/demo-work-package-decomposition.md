# Decompose a Plan into Work Packages and Draft the Issues

Nothing is implemented here: this is a planning output, and the discipline is in the contracts. You split the work in `STATE.md` into four named packages, each with its input, its output contract and its declared dependency, audit every contract until it is a command you could run yourself, and turn the packages into a parent issue with one sub-issue each. You end holding `work-packages.md`, an `issues.md` draft, and the `gh` commands that file it against your own repository.

------

Run this in the [hr-mcp-server/](hr-mcp-server) starter once [demo-authoring-state.md](demo-authoring-state.md) has produced a `STATE.md` with an empty Open Questions section. The run writes `work-packages.md` and `issues.md` and runs no `gh` command.

```bash
cd demos/11-planning/02-planning/hr-mcp-server
claude
```

## Split the Plan into Four Packages

Submit:

```text
Decompose the work in STATE.md into four work packages, each one small enough to hand to a separate executor. For each:
  - name (short, lowercase, hyphenated)
  - input: the files it may read and the section of STATE.md that governs it
  - output: the files it creates or modifies and the contract it must satisfy (a callable command plus the expected output)
  - depends on: which other package must finish first, if any

The four packages:
  1. vacancy-schema: the Vacancy model, the EmployeeDbContext mapping and the Vacancies table on existing databases
  2. vacancy-service: IVacancyService and VacancyService with the ranking rule, registered in Program.cs
  3. vacancy-tools: the four MCP tools in HRTools
  4. smoke-verification: the inspector CLI checks from Done Criteria, run against a throwaway database copy

Write the result as a markdown table to work-packages.md. Do not implement anything.
```

The recorded run wrote one table row per package and declared a strict chain: `vacancy-schema`, then `vacancy-service`, then `vacancy-tools`, then `smoke-verification`. Each row names its inputs down to the `STATE.md` Decisions it is governed by, and its output down to the method signatures.

## Audit Each Contract for Runnability

Read the Contract part of every row before executing anything. Each one must be a command you could run yourself, and each dependency must be declared. In the recorded run three of the four contracts are the same command:

```text
Contract: `dotnet build exits 0`.
```

That is runnable, and it passes on a method that returns nothing useful: the ranking rule is first exercised by `smoke-verification`. Claude named the gap itself: "No standalone command; the ordering is checked through the CLI in smoke-verification." With no test project in the starter that is an honest contract; in a project with tests, send the package back and ask for the test command that proves its behaviour.

## Draft the Issues

Submit:

```text
Turn work-packages.md into a GitHub issue draft in issues.md: one parent issue for the vacancies feature and one sub-issue per package, each with a title, a body holding its input, output, contract and dependency, and the label planning. Below the draft, list the gh commands that create the label, the parent issue and the sub-issues, and the gh api calls that link each sub-issue to the parent through the sub-issues REST endpoint. Do not run any gh command.
```

The recorded `issues.md` holds the parent issue "Add vacancies to the HR MCP server", four sub-issues titled by package name, and the commands written for bash, with one `gh api` call per sub-issue that links it to the parent by its database id:

```bash
gh api --method POST repos/{owner}/{repo}/issues/<P>/sub_issues -F sub_issue_id=<ID1>
gh api --method POST repos/{owner}/{repo}/issues/<P>/sub_issues -F sub_issue_id=<ID2>
gh api --method POST repos/{owner}/{repo}/issues/<P>/sub_issues -F sub_issue_id=<ID3>
gh api --method POST repos/{owner}/{repo}/issues/<P>/sub_issues -F sub_issue_id=<ID4>
```

Filing runs against your own repository: `gh` fills in `{owner}/{repo}` from the remote of the folder you run it in, so run the commands in a project you own, never in this course repository. If your shell is PowerShell, ask Claude to rewrite the commands for PowerShell first.

The recorded packages and issue draft are in [hr-mcp-server-solution/work-packages.md](hr-mcp-server-solution/work-packages.md) and [hr-mcp-server-solution/issues.md](hr-mcp-server-solution/issues.md).

## Cleanup

The four planning demos wrote `ledger.md`, `plan.md`, `STATE.md`, `work-packages.md` and `issues.md` into the starter. List them, then remove them:

```bash
git clean -n .
git clean -f .
```
