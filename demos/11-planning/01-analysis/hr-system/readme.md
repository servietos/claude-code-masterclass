# Read the Current State of Vacancy Tracking

This folder is the brownfield system the [harvest demo](../demo-harvest-current-state.md) analyses: how a small restaurant tracks open positions today. Nothing here gets changed; the demo adds `ledger.md` and `current-state.md` beside these files.

| Path | Source | What it holds |
| --- | --- | --- |
| [hr-sources/process-notes.md](hr-sources/process-notes.md) | Processes | One week of hiring steps recorded by the restaurant manager, with tool and minutes per step |
| [hr-sources/vacancies-tracker.xlsx](hr-sources/vacancies-tracker.xlsx) | Excel files | The Vacancies sheet with its Days Open formula, and a Staff Copy sheet pasted from the HR assistant |
| [hr-mcp-server/Data/](hr-mcp-server/Data/) and [Tools/Models.cs](hr-mcp-server/Tools/Models.cs) | Data structure | The Entity Framework model and seed data of the HR MCP server |
| [hr-mcp-server/Tools/](hr-mcp-server/Tools/), [Services/](hr-mcp-server/Services/) and [Program.cs](hr-mcp-server/Program.cs) | Current implementation | The five employee tools the staff call through the HR assistant |

Open it with:

```bash
cd demos/11-planning/01-analysis/hr-system
claude
```

The workbook harvester runs a Python script, so it needs Python 3 with openpyxl:

```bash
pip install openpyxl
```

The analysis reads the server's code and never starts it. To run the server anyway, `dotnet run` inside [hr-mcp-server/](hr-mcp-server/readme.md) needs the .NET 10 SDK; it creates and seeds `hr-data.db` on first start, and that file is gitignored.

The finished harvest is beside this folder in [hr-system-solution/](../hr-system-solution/readme.md).
