# Add vacancies to the HR MCP server

## Context
`hr-mcp-server-solution` (.NET 10, EF Core + SQLite, MCP over HTTP) has only employee tools. Add vacancies with four tools, inside the existing database, without touching existing employee rows or adding packages.

## Constraints
1. Vacancy = title, required skills, required languages, status (open | filled).
2. Exactly four new tools: `add_vacancy`, `list_vacancies`, `close_vacancy`, `match_candidates`.
3. Stored in `hr-data.db` via `EmployeeDbContext`; no new NuGet packages.
4. Existing employee rows survive; no destructive migration.
5. `match_candidates` ranks employees by number of required skills they have.

## Shape
- `Tools/Models.cs`: `Vacancy` (Id hidden from JSON, Title, Status, RequiredSkills and RequiredLanguages as JSON-in-TEXT with `[NotMapped]` lists, same pattern as `Employee.Skills`/`SpokenLanguages`), plus `VacancyCollection`. Status as a string constrained to `open`/`filled`.
- `Data/EmployeeDbContext.cs`: `DbSet<Vacancy>`, table `Vacancies`.
- `Data/EmployeeDbInitializer.cs`: `EnsureCreatedAsync` does nothing for an existing database, so after it runs, execute `CREATE TABLE IF NOT EXISTS Vacancies (...)` through `Database.ExecuteSqlRawAsync`. Additive only: employee rows and the `Candidates` table are never touched, and a fresh database gets the same table. No seed vacancies.
- `Services/IVacancyService.cs` + `VacancyService.cs` (registered `AddScoped` in `Program.cs`): add, list, close, match. Matching loads open vacancy and employees, counts case-insensitive skill overlap in memory (same approach as `EmployeeService` search).
- `Tools/VacancyTools.cs` (`[McpServerToolType]`, discovered by `WithToolsFromAssembly()`): the four tools, thin, comma-separated list inputs like `AddEmployee`, string results for mutations.

## Still ambiguous (need your call)
1. **Languages in matching:** hard filter (employee must speak all required languages), ranking tiebreaker, or ignored by `match_candidates`? Constraint 5 mentions skills only.
2. **Zero-skill matches:** include employees with 0 matching skills at the bottom, or return only those with at least 1?
3. **Tie order:** equal skill counts sorted by last name, first name (matches `GetAllEmployeesAsync`)? Recommended.
4. **Skill comparison:** case-insensitive exact match ("grill" does not match "grilling")? Recommended.
5. **Vacancy identifier:** integer Id from `list_vacancies` for `close_vacancy` and `match_candidates`. Recommended; titles are not unique.
6. **`match_candidates` on a filled vacancy:** allowed or an error message?
7. **`close_vacancy` on an already filled vacancy:** report "already filled" (recommended) or succeed silently?
8. **`list_vacancies` filtering:** all vacancies, or an optional status parameter (open/filled)?
9. **Match output:** each employee plus matched-skill count and the matched skill names, or the bare ranked employee list?
10. **Starter:** is there a pristine starter beside `-solution` that should receive the same change?

## Verification
Back up nothing, delete nothing. Copy-free check: `dotnet build`; run against the existing `hr-data.db` and confirm the 8 employees still list and the `Vacancies` table now exists; via the MCP inspector CLI confirm `tools/list` shows 9 tools and a round trip of `add_vacancy`, `list_vacancies`, `match_candidates`, `close_vacancy` returns rows from real calls. No Vitest/Playwright; no docs.
