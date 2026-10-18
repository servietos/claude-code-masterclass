## Goal
Add vacancies to the HR MCP server.

## Decisions
- Vacancy fields: `Title`, `RequiredSkills`, `RequiredLanguages`, and `Status` with values `open` or `filled`. Each vacancy also has an integer `Id`, which is `[JsonIgnore]` as on `Employee`.
- Vacancies are identified by `Id`, because titles are not unique.
- Storage: a `DbSet<Vacancy>` in `EmployeeDbContext` mapped to table `Vacancies`. The new service uses that context. No new NuGet packages.
- Entity pattern: `RequiredSkills` and `RequiredLanguages` are `[NotMapped]` lists backed by `*Data` JSON strings, copied from `Employee`.
- Existing databases: `EnsureCreatedAsync` skips an existing `hr-data.db`, so the Vacancies table is created with `CREATE TABLE IF NOT EXISTS` after `EnsureCreatedAsync`. Employee rows are kept. Deleting and reseeding `hr-data.db` is excluded, because it is destructive.
- Four tools, with explicit names set by `[McpServerTool(Name = "...")]`: `add_vacancy` (method `AddVacancy`), `list_vacancies` (method `ListVacancies`, optional status filter), `close_vacancy` (method `CloseVacancy`, sets status to `filled`), and `match_candidates` (method `MatchCandidates`).
- The new tools live in their own class, `Tools/VacancyTools.cs`. `WithToolsFromAssembly()` registers them without a change to `Program.cs` beyond the service registration.
- Service: `IVacancyService` and `VacancyService`, registered as scoped in `Program.cs`. Methods: `AddVacancyAsync`, `GetVacanciesAsync(status?)`, `CloseVacancyAsync(id)`, `MatchCandidatesAsync(id)`.
- Ranking rule for `match_candidates`: every employee is returned, ordered by the number of the vacancy's required skills they hold, compared case-insensitively, most matches first. Employees with zero matches are included at the bottom. Required languages are stored and returned but do not filter or rank matches.
- Ties in `match_candidates`: employees with the same match count keep the order that `list_employees` returns.
- Verification runs against a throwaway copy of `hr-data.db`. The original file is never deleted or modified.
- Code changes stay inside this folder. `inspector.config.json` is not changed.

## Status
- [ ] vacancy schema
- [ ] vacancy service
- [ ] vacancy tools
- [ ] smoke verification

## Next Action
vacancy schema

## Done Criteria
- npx @modelcontextprotocol/inspector --cli --config inspector.config.json --server hr-mcp --method tools/list lists add_vacancy, list_vacancies, close_vacancy and match_candidates beside the 5 employee tools
- the same CLI with --method tools/call --tool-name list_employees still returns the 8 seeded employees
- match_candidates for a vacancy requiring "Menu Planning, Food Safety" returns Carlos Gomez first

## Open Questions
