---
presents: demo-harvest-current-state.md
budget: 4 min
beats: 3
---

# Present: Harvest the Current State of Vacancy Tracking

A current-state document is harvested by parallel subagents into one cited ledger, then checked against the files it summarises. Three beats: four writers share one ledger, the gap list separates observation from conclusion, and the second pass reads the sources.

------

## Beats

### Beat 1: four writers, one ledger, one append each (1.5 min)

**Open:** [Step 1: Harvest in Parallel into One Ledger](demo-harvest-current-state.md#step-1-harvest-in-parallel-into-one-ledger) · [`hr-sources/vacancies-tracker.xlsx`](hr-system/hr-sources/vacancies-tracker.xlsx)
**Say:** The subagents never see each other, so the file is where they meet. One append per subagent is the whole concurrency rule.

```text
Each subagent writes its findings in ONE shell append to ledger.md (a "## <source>" heading,
then bullets) and writes no other file. Every bullet ends with the path, and the sheet, cell
or symbol, it came from. Facts only, no recommendations.
```

**Result:** [`ledger.md`](hr-system-solution/ledger.md) came back with 72 cited bullets across four headings, including the formula and the table name nobody wrote down

```markdown
- Days Open formula in H2 is `=IF(F2="Open",TODAY()-G2,"")` (`hr-sources/vacancies-tracker.xlsx`: Vacancies!H2)
- The Employee entity is mapped to the table named "Candidates" (`hr-mcp-server/Data/EmployeeDbContext.cs`: `EmployeeDbContext.OnModelCreating`)
```

**Gotcha:** the subagents reported 12 and 24 bullets; counting the file gave 13 and 23. A count is a claim until someone counts the file, and a ledger line is a claim until someone opens its source.

### Beat 2: the gap list is what the next topic plans against (1 min)

**Open:** [Step 2: Write the Current-State Document](demo-harvest-current-state.md#step-2-write-the-current-state-document) · [`hr-sources/process-notes.md`](hr-system/hr-sources/process-notes.md)
**Say:** Inventory and usage lines cite a source; Limits and gaps may conclude, but each names its observation. That split lets a reviewer challenge a conclusion without re-reading the system.

```text
The Gap list judges this request from HR against the current state, one row per
capability, each marked exists, partly exists or missing:
```

**Result:** [`current-state.md`](hr-system-solution/current-state.md) judged the four capabilities

```markdown
| 1 | Record a vacancy (title, department, required skills, languages, status, owner) | partly exists | The workbook has columns for all six fields (`Vacancies!A1:J1`), but a row is added by hand in Excel (process notes Mon row), and no MCP tool writes vacancies. |
| 2 | Suggest internal candidates for a vacancy from employee skills and languages | partly exists | Candidates are found by filtering a manual Staff Copy by skill (process notes Mon row), and the MCP `SearchEmployees` takes one term and does not take a vacancy's skills and languages together. |
...
| 4 | Move an employee into a vacancy's role and close the vacancy in one step | missing | The two halves exist separately: `UpdateEmployee` changes `CurrentRole` on an Employee, and Status is set to Filled by hand in Excel (process notes Thu row). No tool or workbook link joins them. |
```

**Gotcha:** rows 1 to 3 read "partly exists" because the workbook holds the data while people run the steps by hand.

### Beat 3: the second pass reads the files, never the ledger (1.5 min)

**Open:** [Step 3: Check the Document Against the Sources](demo-harvest-current-state.md#step-3-check-the-document-against-the-sources) · [`hr-mcp-server/Tools/HRTools.cs`](hr-system/hr-mcp-server/Tools/HRTools.cs)
**Say:** A document written from a ledger inherits the ledger's mistakes. Point the check at the sources by name.

```text
Check current-state.md against the sources, not against ledger.md.
```

**Result:** eleven Limits lines held and one was corrected in [`current-state.md`](hr-system-solution/current-state.md): the `HRTools` summary said changes reset on restart, but the code saves them to SQLite

```markdown
- The `HRTools` class summary is stale. It says modifications are "temporary and reset when the server restarts" (`hr-mcp-server/Tools/HRTools.cs`, lines 10 and 11). The code persists them: `EmployeeService` writes each change with `SaveChangesAsync` to SQLite (`hr-mcp-server/Services/EmployeeService.cs`, lines 46, 71 and 93), and `EmployeeDbInitializer` seeds only when the table is empty (`hr-mcp-server/Data/EmployeeDbInitializer.cs`, lines 19 to 23). No reset path appears in the files read.
```

**Gotcha:** checking the document against the ledger it came from only proves the copy matches the copy.

## If the room asks

| Question | Answer |
| --- | --- |
| Does the HR server have to run? | No. The harvest reads the code; `dotnet run` would only add `hr-data.db`, which the seed code already describes. |
| How do I see the four subagents? | `/tasks` lists them while they run, and a finished one stays listed so you can open its transcript. |
| What else did the Limits section catch? | The `Program.cs` comment says SQL Server while the registration uses `UseSqlite` (`hr-mcp-server/Program.cs`, line 8). |

## Runs live instead

A learner runs the prompts in one session from `hr-system/` and gets their own ledger and gap list; the steps are in [the demo guide](demo-harvest-current-state.md).
