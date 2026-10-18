# Plan the Vacancies Feature Through a Shared Ledger

HR wants to track open positions in the HR MCP server, and a one-line request is the fastest way to get that wrong. Claude researches the server with three parallel subagents that share one ledger file, writes a plan you can check line by line against that ledger, and you hold the plan against the constraints from the plan mode session.

------

Start Claude Code in [hr-mcp-server/](hr-mcp-server), outside plan mode, because the subagents write the ledger; the recorded ledger and corrected plan are in [hr-mcp-server-solution/ledger.md](hr-mcp-server-solution/ledger.md) and [hr-mcp-server-solution/plan.md](hr-mcp-server-solution/plan.md).

## Step 1: Research in parallel through a shared ledger

Subagents start with their own context and see nothing of each other, so the prompt creates the ledger first and names it in every brief. The brief carries the feature and leaves out the five constraints from the plan mode session, the way a teammate would phrase it.

```text
Plan adding vacancies (open positions) to this HR MCP server. HR wants to record a vacancy with a title, required skills, required languages and a status of open or filled, list and close vacancies, and find existing employees whose skills match a vacancy.

First create the shared ledger ledger.md in this folder with three empty headings: MCP tools, Data, Verification.

Then run three general-purpose subagents in parallel. Research only inside this folder; ignore bin and obj. Tell each subagent the ledger path and to write its findings under its own heading in that file, and nothing else:
1. MCP tools: how Tools/HRTools.cs declares tools, names parameters and returns results.
2. Data: Tools/Models.cs, Data/EmployeeDbContext.cs and Data/EmployeeDbInitializer.cs, and how the SQLite schema is created and seeded.
3. Verification: the smoke test in readme.md and inspector.config.json, and how a new tool would be checked.

When all three are done, read the ledger and write the plan to plan.md in this folder: a one-paragraph summary, then numbered tasks, each with the files it touches, the tasks it depends on, and acceptance criteria. The ledger and the plan are the only files written: do not change any code.
```

Three `general-purpose` subagents run in parallel, then the session writes two files and no code: `ledger.md` with 80 lines under the three headings, each finding citing a file and line, and `plan.md` with eight numbered tasks. One ledger finding no brief asked for:

```markdown
- `DbSet<Employee> Employees` (line 13) maps to table `Candidates` (line 19). The table name differs from the class name.
```

A plan that writes SQL against an `Employees` table would fail on the first start; the ledger line is what a reviewer checks it against.

## Step 2: Check the plan against the ledger and the constraints

The plan is only as good as the findings behind it and the decisions in front of it. Reading it against both turns review from "does this sound right" into "which line supports this".

```text
Review plan.md against ledger.md and against the constraints below, which were locked in the planning session. For every acceptance criterion, quote the ledger line that supports it. Then list each place the plan contradicts a constraint, each criterion the ledger does not support, and each assumption about the running server that nobody verified. Do not edit any file.

Constraints (non-negotiable):
  1. A vacancy has a title, required skills, required languages and a status of open or filled.
  2. Four new MCP tools: add_vacancy, list_vacancies, close_vacancy, match_candidates.
  3. Store vacancies in the existing SQLite database through EmployeeDbContext. No new NuGet packages.
  4. Existing employee rows in hr-data.db must survive. No destructive migration.
  5. match_candidates returns employees ranked by how many required skills they have.
```

The recorded review found three contradictions the brief invited by leaving the constraints out: the tool names, the ranking rule, and a plan option that deletes `hr-data.db`. Fix them with a prompt that names exactly what changes:

```text
Update plan.md so it satisfies the constraints locked in the planning session:
- The four new tools are add_vacancy, list_vacancies, close_vacancy and match_candidates, from the methods AddVacancy, ListVacancies, CloseVacancy and MatchCandidates.
- match_candidates returns every employee ranked by how many of the vacancy's required skills they have, most matches first, and its acceptance criteria check that order.
- The verification task deletes hr-data.db only on a throwaway copy, never the file holding existing employee rows.
Change nothing else in plan.md and do not touch ledger.md or any code.
```

`plan.md` keeps its eight tasks; the matching criteria now check an ordering:

```markdown
- Acceptance: the service compiles, is registered, and returns every employee in descending order of matched-skill count for a vacancy with two required skills.
- Acceptance: the build succeeds with no errors. `tools/list` shows nine tools. `add_vacancy` followed by `list_vacancies` returns the new vacancy. `match_candidates` on a vacancy with two required skills returns every employee, with each matched-skill count equal to or lower than the count before it, so the highest count comes first. `CloseVacancy` changes the status, and `ListVacancies` with status `open` no longer returns it. Tests are not run unless you ask for them.
```

A correction that lists exactly what changes and ends with "change nothing else" turns a review into a small diff.
