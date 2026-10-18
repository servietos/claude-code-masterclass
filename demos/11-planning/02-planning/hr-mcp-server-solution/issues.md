# Issue draft: vacancies for the HR MCP server

Label for every issue: `planning`

## Parent issue

Title: Add vacancies to the HR MCP server

Body:

Adds vacancies to the HR MCP server. A vacancy has a title, required skills, required languages and a status of open or filled. Four new MCP tools: add_vacancy, list_vacancies, close_vacancy and match_candidates. match_candidates ranks every employee by how many required skills they hold. Vacancies are stored in the existing SQLite database through EmployeeDbContext with no new NuGet packages. Existing employee rows in hr-data.db are kept.

Sub-issues:
- vacancy-schema
- vacancy-service
- vacancy-tools
- smoke-verification

Not in any package: the readme smoke test update (plan.md task 6) has no owner yet. The tool location (Tools/VacancyTools.cs per STATE.md, or Tools/HRTools.cs per the original brief) is also open.

## Sub-issue 1: vacancy-schema

Title: vacancy-schema: Vacancy model, mapping and Vacancies table

Body:

Input: STATE.md Decisions (vacancy fields, storage through EmployeeDbContext, entity pattern, existing databases). Files: Tools/Models.cs, Data/EmployeeDbContext.cs, Data/EmployeeDbInitializer.cs.

Output: modifies Tools/Models.cs (adds Vacancy with Id, Title, RequiredSkills, RequiredLanguages, Status). Modifies Data/EmployeeDbContext.cs (adds DbSet<Vacancy> mapped to table Vacancies). Modifies Data/EmployeeDbInitializer.cs (adds CREATE TABLE IF NOT EXISTS Vacancies after EnsureCreatedAsync and before the Employees.AnyAsync check at line 19).

Contract: dotnet build exits 0. On a throwaway copy of a seeded hr-data.db, after one start, `sqlite3 <copy> "SELECT COUNT(*) FROM Candidates;"` prints 8, and `sqlite3 <copy> ".schema Vacancies"` prints a CREATE TABLE statement. A second start does not fail. The sqlite3 CLI on PATH is assumed and not yet verified.

Depends on: none.

## Sub-issue 2: vacancy-service

Title: vacancy-service: IVacancyService with the match_candidates ranking

Body:

Input: STATE.md Decisions (service methods, ranking rule, tie rule, scoped registration). Files: Services/IEmployeeService.cs (pattern), Program.cs, Data/EmployeeDbContext.cs, and the Vacancy type from vacancy-schema.

Output: creates Services/IVacancyService.cs and Services/VacancyService.cs with AddVacancyAsync, GetVacanciesAsync(status?), CloseVacancyAsync(id) and MatchCandidatesAsync(id). Modifies Program.cs to add AddScoped<IVacancyService, VacancyService>. MatchCandidatesAsync returns every employee ordered by the count of the vacancy's required skills they hold, compared case-insensitively, highest first. Employees with equal counts keep the order list_employees returns.

Contract: dotnet build exits 0. No standalone command; the ordering is checked through the CLI in smoke-verification.

Depends on: vacancy-schema.

## Sub-issue 3: vacancy-tools

Title: vacancy-tools: add_vacancy, list_vacancies, close_vacancy, match_candidates

Body:

Input: STATE.md Decisions (tool names and their explicit Name attributes, optional status filter on list_vacancies, close_vacancy sets status to filled, WithToolsFromAssembly registration). Files: Tools/HRTools.cs (pattern), Services/IVacancyService.cs.

Output: creates Tools/VacancyTools.cs, a McpServerToolType class with add_vacancy, list_vacancies, close_vacancy and match_candidates, each with a Description attribute. STATE.md decides this separate file; the original brief said HRTools.

Contract: dotnet build exits 0. `npx @modelcontextprotocol/inspector --cli --config inspector.config.json --server hr-mcp --method tools/list` prints nine tools, including add_vacancy, list_vacancies, close_vacancy and match_candidates beside the five employee tools.

Depends on: vacancy-service.

## Sub-issue 4: smoke-verification

Title: smoke-verification: inspector CLI checks on a throwaway database copy

Body:

Input: STATE.md Done Criteria and the verification decision in Decisions. Files: inspector.config.json (points at http://localhost:47002), readme.md (CLI steps). A throwaway copy of hr-data.db; the original is not touched.

Output: modifies no repo file. Runs three checks against a server started on the copy:
1. `npx @modelcontextprotocol/inspector --cli --config inspector.config.json --server hr-mcp --method tools/list` lists the four new tools beside the 5 employee tools.
2. `npx @modelcontextprotocol/inspector --cli --config inspector.config.json --server hr-mcp --method tools/call --tool-name list_employees` returns the 8 seeded employees.
3. match_candidates for a vacancy requiring "Menu Planning, Food Safety" returns Carlos Gomez first. The tools/call argument syntax is not in the readme and must be confirmed first.

Contract: the three commands above produce the stated output.

Depends on: vacancy-tools.

---

## gh commands (not run)

Save each body block above to its own file outside the repo, then pass it with --body-file. Replace the placeholders <P>, <S1> to <S4> with the issue numbers gh prints.

Create the label (--force makes this safe to rerun):

```bash
gh label create planning --color 1D76DB --description "Planning drafts" --force
```

Create the parent issue:

```bash
gh issue create --title "Add vacancies to the HR MCP server" --label planning --body-file parent.md
```

Create the four sub-issues:

```bash
gh issue create --title "vacancy-schema: Vacancy model, mapping and Vacancies table" --label planning --body-file vacancy-schema.md
gh issue create --title "vacancy-service: IVacancyService with the match_candidates ranking" --label planning --body-file vacancy-service.md
gh issue create --title "vacancy-tools: add_vacancy, list_vacancies, close_vacancy, match_candidates" --label planning --body-file vacancy-tools.md
gh issue create --title "smoke-verification: inspector CLI checks on a throwaway database copy" --label planning --body-file smoke-verification.md
```

Get the numeric id of each sub-issue (the sub-issues endpoint takes the id, not the number):

```bash
gh api repos/{owner}/{repo}/issues/<S1> --jq .id
gh api repos/{owner}/{repo}/issues/<S2> --jq .id
gh api repos/{owner}/{repo}/issues/<S3> --jq .id
gh api repos/{owner}/{repo}/issues/<S4> --jq .id
```

Link each sub-issue to the parent through the sub-issues endpoint. Replace <ID1> to <ID4> with the ids from the previous step:

```bash
gh api --method POST repos/{owner}/{repo}/issues/<P>/sub_issues -F sub_issue_id=<ID1>
gh api --method POST repos/{owner}/{repo}/issues/<P>/sub_issues -F sub_issue_id=<ID2>
gh api --method POST repos/{owner}/{repo}/issues/<P>/sub_issues -F sub_issue_id=<ID3>
gh api --method POST repos/{owner}/{repo}/issues/<P>/sub_issues -F sub_issue_id=<ID4>
```
