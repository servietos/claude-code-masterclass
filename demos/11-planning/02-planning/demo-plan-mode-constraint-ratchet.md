# Lock design decisions incrementally with Plan Mode

Plan Mode answers a vague brief with a question list and a provisional plan, and a numbered constraint block sent before the ask is read as specification. You send both to the HR MCP server starter and compare the two versions of the plan file that come back. You end holding a plan whose vacancy fields, tool names, storage and ranking rule are pinned by constraints you wrote.

------

Start Claude Code in the starter. Nothing is installed and no project file changes: plan mode writes only its plan file under `~/.claude/plans/`.

```bash
cd demos/11-planning/02-planning/hr-mcp-server
claude
```

## Part A: Vague Brief

Press `Shift+Tab` until the status bar shows `⏸ plan mode on`. Submit:

```text
I want to add vacancies to the HR MCP server.
```

Claude researches the server, writes a provisional plan file, and ends on questions. The recorded run assumed five tools copied from the employee set (`list_vacancies`, `add_vacancy`, `update_vacancy`, `remove_vacancy`, `search_vacancies`) and asked:

```text
1. **Fields:** I assumed title, description, required skills and required languages. What should a vacancy actually contain? For example: department, location, status (open/filled), salary, start date.
2. **Tools:** are the five tools above the right set? Or do you want something else, such as matching employees to a vacancy?
3. **Identifier:** vacancies don't have a natural unique key like an employee's email, so update and remove would take the vacancy `id`. Would you rather use the title?
4. **Seed data:** should the server create some sample vacancies on first run, the way it does with the 8 employees? The plan currently has none.
```

It also found the trap in [Data/EmployeeDbInitializer.cs](hr-mcp-server/Data/EmployeeDbInitializer.cs) without being asked: `EnsureCreatedAsync` only creates a database that does not exist yet, so an existing `hr-data.db` would never get a new table.

## Part B: Constraint Ratchet

Stay in plan mode. Submit:

```text
Constraints (non-negotiable):
  1. A vacancy has a title, required skills, required languages and a status of open or filled.
  2. Four new MCP tools: add_vacancy, list_vacancies, close_vacancy, match_candidates.
  3. Store vacancies in the existing SQLite database through EmployeeDbContext. No new NuGet packages.
  4. Existing employee rows in hr-data.db must survive. No destructive migration.
  5. match_candidates returns employees ranked by how many required skills they have.

Revise the plan. Tell me what is still ambiguous.
```

Claude rewrites the same plan file. The update, remove and search tools are gone, the ranking rule is written into the service bullet, and the verification section runs the tools against the database:

```text
Copy-free check: `dotnet build`; run against the existing `hr-data.db` and confirm the 8 employees still list and the `Vacancies` table now exists;
```

The reply lists ten remaining ambiguities, each with the assumption the plan makes for now, from how tools find a vacancy (`id`) to how ties are ordered. Answer the ones you care about with one more constraint batch; past five turns, stop and rewrite the brief.

Leave plan mode with `Shift+Tab` or pick **No, keep planning** when Claude asks to approve: the next demo researches and writes the plan as project files before anything is built.

Both versions of the plan file from the recorded run are in [hr-mcp-server-solution/plan-mode-turn-1.md](hr-mcp-server-solution/plan-mode-turn-1.md) and [hr-mcp-server-solution/plan-mode-turn-2.md](hr-mcp-server-solution/plan-mode-turn-2.md).
