# Add vacancies to the HR MCP server

## Context
`hr-mcp-server-solution` (.NET 10, SQLite via EF Core, MCP over Streamable HTTP) exposes only employee tools. Vacancies (open positions) are a second entity; nothing about them exists yet.

## Shape (mirrors the employee stack)
- `Tools/Models.cs`: add `Vacancy` (Id hidden from JSON; Title, Department, Description, RequiredSkills as JSON-in-TEXT with `[NotMapped]` list like `Employee.Skills`, Status, OpenedOn) and `VacancyCollection`.
- `Data/EmployeeDbContext.cs`: add `DbSet<Vacancy>`, table `Vacancies`.
- `Data/EmployeeDbInitializer.cs`: seed a few vacancies when the table is empty (restaurant theme).
- `Services/IVacancyService.cs` + `Services/VacancyService.cs`: get all, add, update, remove (by Id), search; register `AddScoped` in `Program.cs`.
- `Tools/VacancyTools.cs` (`[McpServerToolType]`, picked up by `WithToolsFromAssembly`): `list_vacancies`, `add_vacancy`, `update_vacancy`, `remove_vacancy`, `search_vacancies`, same thin-tool style as `HRTools`.

## Decisions for you
1. Schema: `EnsureCreatedAsync` skips existing tables, so an existing `hr-data.db` needs deleting once (or I add a create-if-missing step). Which?
2. Key for update/remove: integer Id returned by `list_vacancies` (recommended; vacancies have no natural unique key like email).
3. Scope: also edit the starter (if one exists) alongside `-solution`, per your standing rule?

## Verification
`dotnet build`, then `dotnet run` and the MCP inspector CLI: `tools/list` shows 10 tools; `tools/call list_vacancies` returns seeded rows; add/update/remove round-trip. No Vitest/Playwright; no docs written.
