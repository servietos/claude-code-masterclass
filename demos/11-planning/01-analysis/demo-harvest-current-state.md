# Harvest the Current State of Vacancy Tracking

A plan written from an interview misses what the spreadsheet and the code already do. You point four parallel subagents at a restaurant's process notes, vacancies workbook, database model and server code, collect their findings in one cited ledger, and turn it into a current-state document with a gap list.

------

Work in `hr-system/` (run `pip install openpyxl` once for the workbook step); the finished result is beside it in [`hr-system-solution/`](hr-system-solution/readme.md).

## Step 1: Harvest in Parallel into One Ledger

Four independent sources get four subagents at once, and one append per subagent keeps four writers from overwriting each other. Type `/tasks` while they run to see the four subagents.

```text
Harvest the current state of vacancy tracking in this folder into ledger.md.
Spawn four general-purpose subagents in parallel, one per source:
  1. Processes: hr-sources/process-notes.md.
  2. Excel files: hr-sources/vacancies-tracker.xlsx, read with a short openpyxl script
     using load_workbook(..., data_only=False) so formulas come back, not cached values.
  3. Data structure: hr-mcp-server/Data/ and hr-mcp-server/Tools/Models.cs.
  4. Current implementation: hr-mcp-server/Tools/, hr-mcp-server/Services/ and hr-mcp-server/Program.cs.
Each subagent writes its findings in ONE shell append to ledger.md (a "## <source>" heading,
then bullets) and writes no other file. Every bullet ends with the path, and the sheet, cell
or symbol, it came from. Facts only, no recommendations.
Wait for all four, then report the bullet count per heading.
```

[`ledger.md`](hr-system-solution/ledger.md) comes back with four sections and 72 cited bullets (Processes 13, Excel files 23, Data structure 8, Current implementation 28), for example:

```markdown
- Days Open formula in H2 is `=IF(F2="Open",TODAY()-G2,"")` (`hr-sources/vacancies-tracker.xlsx`: Vacancies!H2)
- The Employee entity is mapped to the table named "Candidates" (`hr-mcp-server/Data/EmployeeDbContext.cs`: `EmployeeDbContext.OnModelCreating`)
```

The subagents reported 12 Processes bullets and 24 Excel bullets; counting `ledger.md` gave 13 and 23. A count an agent reports is a claim until someone counts the file, and a ledger line is a claim until someone opens its source.

## Step 2: Write the Current-State Document

The ledger is raw harvest. The document keeps what was observed apart from what was concluded, and judges HR's request against it.

```text
Read ledger.md in this folder and write current-state.md with four sections:
Inventory, How it is used, Limits, Gap list.
Keep what was observed apart from what you conclude: every Inventory and How it is
used line cites the source path from the ledger; Limits and Gap list may conclude,
but each line names the observation it rests on.
The Gap list judges this request from HR against the current state, one row per
capability, each marked exists, partly exists or missing:
  1. Record a vacancy (title, department, required skills, languages, status, owner).
  2. Suggest internal candidates for a vacancy from employee skills and languages.
  3. Report Days Open per vacancy for the weekly summary.
  4. Move an employee into a vacancy's role and close the vacancy in one step.
```

[`current-state.md`](hr-system-solution/current-state.md) comes back with the four sections, twelve Limits lines, and a gap list marking rows 1 and 3 `exists`, row 2 `partly exists` and row 4 `missing`. Read the Status column with the scope in mind: rows 1 and 3 exist only in Excel, and Claude offered to rescore against the HR server alone, where all four would be missing.

## Step 3: Check the Document Against the Sources

The document was written from the ledger, so it inherits the ledger's mistakes. A second pass against the files themselves catches what the summary dropped.

```text
Check current-state.md against the sources, not against ledger.md.
For every Limits line and every Gap list row, open the file it cites and report held
or violated, with the line, cell or symbol you checked. Correct any line that does not
hold and list what you changed. Do not touch any other file.
```

The check held eleven Limits lines and found one violated. Claude corrected that line in `current-state.md`, rewrote the citations of every Limits line to source paths and changed no other file. The corrected line:

```markdown
- The `HRTools` class summary is stale. It says modifications are "temporary and reset when the server restarts" (`hr-mcp-server/Tools/HRTools.cs`, lines 10 and 11). The code persists them: `EmployeeService` writes each change with `SaveChangesAsync` to SQLite (`hr-mcp-server/Services/EmployeeService.cs`, lines 46, 71 and 93), and `EmployeeDbInitializer` seeds only when the table is empty (`hr-mcp-server/Data/EmployeeDbInitializer.cs`, lines 19 to 23). No reset path appears in the files read.
```
