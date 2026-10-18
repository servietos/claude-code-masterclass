# Current state of vacancy tracking

## Inventory

- Vacancy workbook with sheets Vacancies (Id, Title, Department, Required Skills, Languages, Status, Opened, Days Open, Internal Candidates, Owner) and Staff Copy (Name, Role, Skills, Languages, Copied On). (`hr-sources/vacancies-tracker.xlsx`)
- Three vacancy rows V-001 to V-003 in `Vacancies!A2:J4`. (`hr-sources/vacancies-tracker.xlsx`)
- Six staff rows in `Staff Copy!A2:E7`, with Olga Petrova dated 2026-08-01 and the rest 2026-09-14. (`hr-sources/vacancies-tracker.xlsx`)
- Days Open formulas `=IF(F2="Open",TODAY()-G2,"")` in `Vacancies!H2:H4`. (`hr-sources/vacancies-tracker.xlsx`)
- No named ranges, Excel table objects or data validation in the workbook. (`hr-sources/vacancies-tracker.xlsx`)
- Process notes covering one hiring week, 14 to 18 September 2026. (`hr-sources/process-notes.md`)
- `Employee` entity mapped to the `Candidates` table, with no vacancy set in `EmployeeDbContext`. (`hr-mcp-server/Data/EmployeeDbContext.cs`)
- SQLite storage from the connection string `EmployeeDatabase`, schema created with `EnsureCreatedAsync`. (`hr-mcp-server/Data/EmployeeDbContextFactory.cs`, `hr-mcp-server/Data/EmployeeDbInitializer.cs`)
- Seed of 8 employee rows, inserted only when the table is empty, with no vacancy rows. (`hr-mcp-server/Data/EmployeeDbInitializer.cs`)
- Five MCP tools on `HRTools`: `ListEmployees`, `AddEmployee`, `UpdateEmployee`, `RemoveEmployee`, `SearchEmployees`. (`hr-mcp-server/Tools/HRTools.cs`)
- `IEmployeeService` with five async methods, implemented by `EmployeeService`. (`hr-mcp-server/Services/IEmployeeService.cs`, `hr-mcp-server/Services/EmployeeService.cs`)
- Program registrations: `AddDbContext` with `UseSqlite`, `IEmployeeService` as `AddScoped`, MCP over HTTP with `WithToolsFromAssembly`. (`hr-mcp-server/Program.cs`)

## How it is used

- A vacancy is opened by adding a row to the Vacancies sheet, triggered by a chef handing in notice. (`hr-sources/process-notes.md`, Mon row)
- Staff Copy is filled by copying employee skills from the HR assistant's employee list in Claude Desktop, and repeated for every vacancy. (`hr-sources/process-notes.md`, Mon row and closing paragraph)
- Internal candidates are found by filtering Staff Copy by skill and typing matching names into Internal Candidates. (`hr-sources/process-notes.md`, Mon row)
- The owner receives the candidate list by email, pasted from Excel. (`hr-sources/process-notes.md`, Tue row)
- Staff Copy rows went out of date and were fixed by hand after asking the HR assistant again. (`hr-sources/process-notes.md`, Tue row)
- Status is set to Filled by hand when the owner moves an internal candidate into the role. (`hr-sources/process-notes.md`, Thu row)
- The weekly open-positions summary is sent on Friday by Outlook, counting open rows and reading Days Open. (`hr-sources/process-notes.md`, Fri row)
- Days Open is the only number management asks for on vacancies. (`hr-sources/process-notes.md`, closing paragraph)
- Recorded minutes per step: opening a row 5, re-copying staff 20, filtering and typing names 15, second vacancy 40, status update 10, Friday summary 15. (`hr-sources/process-notes.md`, Minutes column)
- The MCP tools read and write only `Employee` records by email or search term. (`hr-mcp-server/Tools/HRTools.cs`)

## Limits

- The MCP server holds no vacancy data: `Models.cs` defines only `Employee` and `EmployeeCollection`, `EmployeeDbContext` exposes only `Employees` (`hr-mcp-server/Data/EmployeeDbContext.cs`, line 13), and no file under `hr-mcp-server` mentions vacancies or the workbook. The vacancy workbook is the only record of vacancies.
- The HR tools cannot write to vacancies, and no tool connects an employee to a vacancy (`hr-mcp-server/Tools/HRTools.cs`, lines 27 to 130: all five `[McpServerTool]` methods take or return `Employee` data).
- Vacancy status changes and additions are manual cell edits with no validation: neither sheet has data validation, and Status (`hr-sources/vacancies-tracker.xlsx`, `Vacancies!F2:F4`) holds only Open and Filled.
- Days Open is stored as a formula: `Vacancies!H2:H4` holds `=IF(F2="Open",TODAY()-G2,"")`, so it is recalculated from `TODAY()` and returns an empty string for the Filled row V-003 (`Vacancies!H4`).
- Skills and languages are separated by semicolons in the workbook (`Vacancies!D2:D4` and `Vacancies!E2:E4`), but `ParseCommaSeparatedString` splits input on commas (`hr-mcp-server/Tools/HRTools.cs`, line 137).
- Internal Candidates is plain text (`Vacancies!I2:I4`) with no formula or link, so no cell references an Employee record.
- Staff Copy is a manual snapshot, and rows were out of date during the observed week: two names were fixed by hand on Tuesday (`hr-sources/process-notes.md`, Tue row), and `Staff Copy!E6` is dated 2026-08-01 while the other rows are dated 2026-09-14.
- `UpdateEmployee` and `RemoveEmployee` look up records by the `email` parameter (`hr-mcp-server/Tools/HRTools.cs`, lines 70 and 106; `hr-mcp-server/Services/EmployeeService.cs`, lines 63 and 85), and `AddEmployee` stores the trimmed email with no format check (`hr-mcp-server/Tools/HRTools.cs`, lines 40 to 66).
- `SearchEmployees` takes one `searchTerm` and matches it against first name, last name, email, current role, skills and spoken languages (`hr-mcp-server/Services/EmployeeService.cs`, lines 112 to 119). It takes no vacancy requirements as input (`hr-mcp-server/Tools/HRTools.cs`, lines 121 and 122).
- The MCP endpoint has no authentication or authorization registration (`hr-mcp-server/Program.cs`, lines 6 to 26).
- The `HRTools` class summary is stale. It says modifications are "temporary and reset when the server restarts" (`hr-mcp-server/Tools/HRTools.cs`, lines 10 and 11). The code persists them: `EmployeeService` writes each change with `SaveChangesAsync` to SQLite (`hr-mcp-server/Services/EmployeeService.cs`, lines 46, 71 and 93), and `EmployeeDbInitializer` seeds only when the table is empty (`hr-mcp-server/Data/EmployeeDbInitializer.cs`, lines 19 to 23). No reset path appears in the files read.
- `Program.cs` has a comment saying "Configure SQL Server-backed employee database" (`hr-mcp-server/Program.cs`, line 8), while the registration uses `UseSqlite` (line 10).

## Gap list

| # | Capability | Status | Observation it rests on |
|---|---|---|---|
| 1 | Record a vacancy (title, department, required skills, languages, status, owner) | partly exists | The workbook has columns for all six fields (`Vacancies!A1:J1`), but a row is added by hand in Excel (process notes Mon row), and no MCP tool writes vacancies. |
| 2 | Suggest internal candidates for a vacancy from employee skills and languages | partly exists | Candidates are found by filtering a manual Staff Copy by skill (process notes Mon row), and the MCP `SearchEmployees` takes one term and does not take a vacancy's skills and languages together. |
| 3 | Report Days Open per vacancy for the weekly summary | partly exists | Days Open is computed per open row (`Vacancies!H2:H4`), but the Friday summary is assembled and sent by hand in Outlook (process notes Fri row). |
| 4 | Move an employee into a vacancy's role and close the vacancy in one step | missing | The two halves exist separately: `UpdateEmployee` changes `CurrentRole` on an Employee, and Status is set to Filled by hand in Excel (process notes Thu row). No tool or workbook link joins them. |
