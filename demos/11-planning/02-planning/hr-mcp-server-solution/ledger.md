# Ledger

## MCP tools

- Class declared `internal class HRTools` with `[McpServerToolType]` (Tools/HRTools.cs:13-14). Each tool method carries `[McpServerTool]` (lines 27, 38, 68, 104, 119). No `Name` is set on any attribute, so tool names come from the SDK's default derivation from method names (ListEmployees, AddEmployee, UpdateEmployee, RemoveEmployee, SearchEmployees). Not verified against the SDK source in this folder.
- Descriptions come from `[Description]` (System.ComponentModel) on each method: "Provides the whole list of employees" (:28), "Adds a new employee to the list" (:39), "Updates an existing employee by email" (:69), "Removes an employee by email" (:105), "Searches for employees by name, email, skills, or current role" (:120).
- Parameters are plain C# types with `[Description]` per parameter (e.g. :41-46, :71-76, :107, :122). Optional parameters use defaults: `spokenLanguages = ""` and `skills = ""` on AddEmployee (:45-46); `string? ... = null` on UpdateEmployee (:72-76). Only AddEmployee and UpdateEmployee have optional parameters. ListEmployees takes no parameters (:29).
- Return types:
  - `ListEmployees` returns `Task<EmployeeCollection>` (:29), a wrapper with `List<Employee> Employees` (Tools/Models.cs:105-110). Employee JSON names are set by `[JsonPropertyName]` (Models.cs:18-70): firstname, lastname, email, spoken_languages, skills, current_role. Id is `[JsonIgnore]` (Models.cs:12). Key casing of the wrapper depends on SDK serializer options, not set in this folder.
  - `SearchEmployees` returns `Task<EmployeeCollection>` (:121).
  - `AddEmployee`, `UpdateEmployee`, `RemoveEmployee` return `Task<string>` with plain-English messages, not JSON: "Successfully added employee: {FullName}" or "Employee with email '...' already exists." (:58-65); "Successfully updated employee with email: ..." or "... not found." (:96-101); "Successfully removed employee with email: ..." or "... not found." (:111-116). Failures are returned as text, not thrown.
- Input handling: AddEmployee trims each string and parses comma lists via `ParseCommaSeparatedString` (:50-55, helper at :132-141). UpdateEmployee applies only non-blank name/role values, and sets lists whenever the list argument is non-null (:78-94).
- Data access: tools never touch EF Core directly. The constructor injects `IEmployeeService` and `ILogger<HRTools>` and null-checks both (:16-25). Each tool calls one service method: GetAllEmployeesAsync (:31), AddEmployeeAsync (:58), UpdateEmployeeAsync(email, action) (:78), RemoveEmployeeAsync (:109), SearchEmployeesAsync (:124). The interface is Services/IEmployeeService.cs:6-42. The logger is injected but not used in HRTools.cs.
- Registration (Program.cs): `AddDbContext<EmployeeDbContext>` with SQLite from connection string "EmployeeDatabase" (:9-10); `AddScoped<IEmployeeService, EmployeeService>` (:13); `AddMcpServer().WithHttpTransport().WithToolsFromAssembly()` (:16-18), which scans the assembly for `[McpServerToolType]` classes; `EmployeeDbInitializer.InitializeAsync` runs before `app.MapMcp()` (:23, :26).

## Data

**Entity (Tools/Models.cs)**
- Only entity is `Employee` (Models.cs:10). No other entity classes; `EmployeeCollection` (Models.cs:105) is a plain wrapper, not persisted.
- `Id` int, primary key, `[JsonIgnore]` (Models.cs:12-13). Configured by `HasKey` (EmployeeDbContext.cs:21).
- `FirstName`, `LastName` (Models.cs:19, 25): string, required, max 100 (EmployeeDbContext.cs:23-29).
- `Email` (Models.cs:31): string, required, max 256, unique index (EmployeeDbContext.cs:31-36).
- `CurrentRole` (Models.cs:71): string, max 200, nullable in the model (EmployeeDbContext.cs:38-39). It defaults to `string.Empty`.
- `SpokenLanguagesData` (Models.cs:37) and `SkillsData` (Models.cs:54): backing `string` columns, `[JsonIgnore]`, required, `TEXT` (EmployeeDbContext.cs:41-47). Default `"[]"`.
- `SpokenLanguages` (Models.cs:42-48) and `Skills` (Models.cs:59-65): `[NotMapped]` `List<string>` views. Getter deserializes the JSON text, setter serializes it (`DeserializeList`/`SerializeList`, Models.cs:78-99). Malformed JSON deserializes to an empty list silently (Models.cs:90-93).
- `FullName` (Models.cs:76): get-only computed property, no column.

**Relationships**
- None. No navigation properties and no join entities. Skills and languages are JSON arrays stored inside the `Employee` row, not separate tables.

**DbContext mapping (Data/EmployeeDbContext.cs)**
- `DbSet<Employee> Employees` (line 13) maps to table `Candidates` (line 19). The table name differs from the class name.
- `OnModelCreating` (lines 15-48) is the only model configuration. No converters, no seed data in the model (`HasData`), no other indexes.
- Constructor takes `DbContextOptions<EmployeeDbContext>` (lines 8-11).

**Schema creation**
- `EnsureCreatedAsync` is the only schema call: `EmployeeDbInitializer.cs:17`. No `Migrate`, no `Migrations` usage in source files.
- `EnsureCreatedAsync` only creates the database when it is missing. It does not alter an existing `Candidates` table when the model changes.
- Invoked from `Program.cs:23`: `await EmployeeDbInitializer.InitializeAsync(app.Services);`, after `builder.Build()` and before `app.MapMcp()` (Program.cs:20-26).
- `Data/EmployeeDbContextFactory.cs` implements `IDesignTimeDbContextFactory` for EF tooling only. It reads the same `EmployeeDatabase` connection string (lines 18-22). Nothing at runtime calls it.

**Database path**
- Registration: `AddDbContext<EmployeeDbContext>` with `UseSqlite(GetConnectionString("EmployeeDatabase"))` (Program.cs:9-10).
- Connection string: `Data Source=hr-data.db` in `appsettings.json:3` and `appsettings.Development.json:3`. It is a relative path, so the file is created in the process working directory.
- `.gitignore:487-489` ignores `hr-data.db`, `-shm`, and `-wal`.
- Program.cs:8 says "SQL Server-backed employee database", but the provider is SQLite. The comment is stale.

**Seeding (Data/EmployeeDbInitializer.cs)**
- `InitializeAsync` (lines 9-31) creates a DI scope, calls `EnsureCreatedAsync`, then checks `Employees.AnyAsync` (line 19). If any row exists, it logs and returns (lines 21-22). The seed is therefore idempotent per database file, not per row: the seed runs only when the table is empty.
- Seeds 8 employees via `GetSeedEmployees()` (lines 33-107), in one `AddRangeAsync` plus `SaveChangesAsync` (lines 27-28). The seed rows set `SpokenLanguages`, `Skills`, `CurrentRole`, which serialize into the `*Data` columns.
- Seed list: Carlos Gomez (Sous Chef), Marie Dubois (Pastry Chef), Luca Rossi (Head Waiter), Anna Schmidt (Restaurant Manager), Sofia Fernandez (Bartender), Kenji Tanaka (Sushi Chef), Olga Ivanova (Hostess), Ahmed Hassan (Grill Chef). Emails are `firstname.lastname@restaurant.com`.
- Reset: delete `hr-data.db` (readme.md:11). Deleting the file is the only way to reseed, because the check is on row count.

**Pending work, not in code**
- `plan-mode-turn-1.md` and `plan-mode-turn-2.md` describe a planned `Vacancies` table added with `CREATE TABLE IF NOT EXISTS` after `EnsureCreatedAsync`. None of that exists in `Data/` today. `EnsureCreatedAsync` would skip an existing database, which is the reason for that plan.

## Verification

- No test project, test script, `.http` file or expected-output fixture exists in this folder. `.vscode/tasks.json:5-30` holds only `clean` and `publish-release`. `test.json` is an invoice sample, not a check fixture (test.json:1-50). The verification artifacts are the readme smoke steps and `inspector.config.json`.
- Start: `dotnet run` (readme.md:8). Listens on `http://localhost:47002` (readme.md:11; appsettings.json:11-17; launchSettings.json:8).
- Inspector config (inspector.config.json:3-7): entry `hr-mcp`, `"type": "http"`, `"url": "http://localhost:47002"`, plus a `note`. There is no `command`, `args` or `env` key, so the inspector connects to an already running server and starts none. Transport is Streamable HTTP through `WithHttpTransport()` and `app.MapMcp()` (Program.cs:16-18, 26; readme.md:3).
- Remote entry `hr-mcp-azure-dev` (inspector.config.json:8-12) points at `https://hr-mcp-server-copilot.azurewebsites.net`. readme.md:50 says the App Service is not provisioned, so this entry fails until redeploy.
- GUI smoke steps (readme.md:26-33): Connect, confirm 5 named tools (readme.md:27-32), call `list_employees`, check that the response holds the 8 seeded employees (readme.md:33). No expected JSON or count assertion is written beyond that sentence.
- CLI steps (readme.md:38-39): `--method tools/list` and `--method tools/call --tool-name list_employees`. Neither carries an assertion or an argument flag, and no exit-code check is described. Output is read by eye.
- Seed count source: 8 entries in `GetSeedEmployees()` (Data/EmployeeDbInitializer.cs:33-107). Seeding runs only when the `Employees` table is empty (EmployeeDbInitializer.cs:19-23), so an existing `hr-data.db` keeps its old rows. Reset by deleting the file (readme.md:11). Connection string is relative: `Data Source=hr-data.db` (appsettings.json:3).
- Tool count source: five `[McpServerTool]` methods (Tools/HRTools.cs:27, 38, 68, 104, 119). The "five" and "5" counts are typed into readme.md:3 and readme.md:27.
- Tool names: C# methods are PascalCase (HRTools.cs:29, 40, 70, 106, 121); readme names are snake_case (readme.md:28-32). The mapping is done by the ModelContextProtocol SDK, not by code in this folder.
- Parameter name in readme: `searchTerm` (readme.md:32) matches HRTools.cs:122.
- Exact strings a check would match for write tools (HRTools.cs): add "Successfully added employee: {FullName}" (:65) or "Employee with email '{email}' already exists." (:62); update "Successfully updated employee with email: {email}" (:101) or "Employee with email '{email}' not found." (:98); remove "Successfully removed employee with email: {email}" (:116) or the not-found text (:113). None of these strings appears in readme.md.
- Read tools return `EmployeeCollection` (Tools/Models.cs:105-110). Field keys are set on `Employee` (Models.cs:18, 24, 30, 43, 60, 70): `firstname`, `lastname`, `email`, `spoken_languages`, `skills`, `current_role`. `Id` is excluded (Models.cs:12). The casing of the wrapper key `Employees` is not set in code.

**Adding a tool (for example, a new method in HRTools.cs)**
- Code: add a method with `[McpServerTool]` and `[Description]` to `HRTools` (HRTools.cs:13). No registration step is needed, because `WithToolsFromAssembly()` (Program.cs:18) scans the assembly at startup.
- Readme smoke test: the count in readme.md:3 and readme.md:27 changes from 5 to 6, and the bullet list at readme.md:28-32 gets the new name and description.
- Inspector config: no change. The file holds only URLs and notes (inspector.config.json:3-12).
- CLI: `tools/list` output gains one entry. A `tools/call` check for the new tool would need argument syntax, which readme.md does not show, so readme.md:38-39 would need an argument example if the tool takes parameters.
- Expected output: add an exact-string line to the smoke test, following the message pattern at HRTools.cs:62-116. The readme has none today.
- Data changes: new seed rows change the count in readme.md:33 (8). Existing databases will not reseed (EmployeeDbInitializer.cs:19-23), so the check must start with the `hr-data.db` delete at readme.md:11.
- Remote: `hr-mcp-azure-dev` (inspector.config.json:8-12) shows the new tool only after redeploy, and readme.md:50 says it fails until then.
- Automation: nothing automated exists, so a new tool adds no test file unless one is written. No existing file would need to change for a test file to be added beyond the new project itself.
