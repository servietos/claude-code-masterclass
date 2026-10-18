# Plan: vacancies for the HR MCP server

The server stores employees in SQLite through EF Core and exposes five employee tools over Streamable HTTP. This plan adds a Vacancy entity with a title, required skills, required languages and a status of `open` or `filled`, plus four tools: `add_vacancy`, `list_vacancies`, `close_vacancy` (set status to `filled`) and `match_candidates`, which ranks every employee against a vacancy. The new tools go in their own class, so `WithToolsFromAssembly()` picks them up with no registration step. Vacancy data needs a table in databases that already exist, because `EnsureCreatedAsync` skips a database that is already there. Matching uses skills only: every employee is ranked by how many required skills they hold, compared case-insensitively, most matches first. Required languages are stored and returned but do not filter matches. Vacancies are identified by their integer `Id`, because titles are not unique.

1. **Vacancy entity**
   - Files: `Tools/Models.cs` (add `Vacancy`).
   - Depends on: none.
   - Shape: `Id` (int, `[JsonIgnore]`), `Title`, `RequiredSkills`, `RequiredLanguages` as `[NotMapped]` lists backed by `*Data` JSON strings, and `Status` as a string with values `open` or `filled`. Copy the list serialization pattern from `Employee`.
   - Acceptance: the project builds with `dotnet build`. `Vacancy` follows the `Employee` pattern for list storage and JSON names.

2. **Vacancy mapping**
   - Files: `Data/EmployeeDbContext.cs` (add `DbSet<Vacancy>` mapped to table `Vacancies`, required `Title`, max length on `Title`, `*Data` columns default `"[]"`, `Status` default `"open"`).
   - Depends on: 1.
   - Acceptance: a `Vacancies` table with the expected columns exists after the database is created. Verified in task 8.

3. **Schema for existing databases**
   - Files: `Data/EmployeeDbInitializer.cs`.
   - Depends on: 2.
   - Decision for you: `EnsureCreatedAsync` does not add a table to an existing `hr-data.db`. Option A: add `CREATE TABLE IF NOT EXISTS Vacancies` after `EnsureCreatedAsync`, as the earlier plan-mode notes describe. Option B: delete `hr-data.db` and reseed, which loses the current employee edits. This plan assumes A, because it keeps data.
   - Acceptance: starting the server against a `hr-data.db` that holds the 8 seeded employees and no `Vacancies` table leaves the employees unchanged and adds the table. A second start does not fail.

4. **Vacancy service**
   - Files: `Services/IVacancyService.cs` (new), `Services/VacancyService.cs` (new), `Program.cs` (add `AddScoped<IVacancyService, VacancyService>`).
   - Depends on: 2, 3.
   - Methods: `AddVacancyAsync`, `GetVacanciesAsync(status?)`, `CloseVacancyAsync(id)`, `MatchCandidatesAsync(id)`. Matching loads the vacancy, counts the required skills each employee holds (case-insensitive), and orders all employees by that count, highest first.
   - Acceptance: the service compiles, is registered, and returns every employee in descending order of matched-skill count for a vacancy with two required skills.

5. **Vacancy tools**
   - Files: `Tools/VacancyTools.cs` (new, `[McpServerToolType]` class with `[McpServerTool]` and `[Description]` on each method, following `HRTools.cs`).
   - Depends on: 4.
   - Tools: `AddVacancy(title, requiredSkills, requiredLanguages)` returns the new `Id` in its message, `ListVacancies(status)` returns the open vacancies when no status is given, `CloseVacancy(id)`, `MatchCandidates(id)` returns an `EmployeeCollection` ordered by matched-skill count, most matches first. Failure cases return text in the same style as `HRTools.cs:62-116`, such as "Vacancy with id 3 not found."
   - Tool names: set explicitly with `[McpServerTool(Name = "add_vacancy")]`, `"list_vacancies"`, `"close_vacancy"` and `"match_candidates"`. The existing tools set no name (`ledger:5`), and the snake_case mapping is unverified (`ledger:67`). Task 8 confirms the names in `tools/list`.
   - Acceptance: `tools/list` shows `add_vacancy`, `list_vacancies`, `close_vacancy` and `match_candidates` next to the five existing tools, and each new method has a `[Description]`.

6. **Readme smoke test**
   - Files: `readme.md` (tool count at lines 3 and 27, tool bullets at lines 28-32, a new smoke step for the vacancy tools).
   - Depends on: 5.
   - Decision for you: the hard rules for this repo say not to write documentation unless asked. Changing the smoke test is a verification change, so this plan includes it. Say so if you want the readme left alone and the check run from the terminal only.
   - Acceptance: the readme lists nine tools and names the four vacancy tools with their parameters.

7. **Inspector config**
   - Files: `inspector.config.json`.
   - Depends on: none. It holds only URLs (`inspector.config.json:3-12`), so the tool change needs no edit here.
   - Acceptance: the file is unchanged. The remote entry `hr-mcp-azure-dev` stays documented as unavailable until the App Service is redeployed.

8. **Verification**
   - Files: none changed. Runs `dotnet build`, copies `hr-data.db` to a throwaway file and runs `dotnet run` against that copy, then the CLI steps in the readme for `tools/list` and `tools/call`. The throwaway copy may be deleted to reseed. `hr-data.db` itself is never deleted or modified.
   - Depends on: 3, 5, 6.
   - Acceptance: the build succeeds with no errors. `tools/list` shows nine tools. `add_vacancy` followed by `list_vacancies` returns the new vacancy. `match_candidates` on a vacancy with two required skills returns every employee, with each matched-skill count equal to or lower than the count before it, so the highest count comes first. `CloseVacancy` changes the status, and `ListVacancies` with status `open` no longer returns it. Tests are not run unless you ask for them.

Dependency order: 1, then 2, then 3 and 4, then 5, then 6 and 7, then 8.
