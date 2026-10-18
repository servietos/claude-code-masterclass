# Read the Harvested Current State of Vacancy Tracking

This folder is the [hr-system](../hr-system/readme.md) starter after the three prompts of the [harvest demo](../demo-harvest-current-state.md) ran in one session. The starter files are unchanged; the run added two files.

| File | Written by | What it holds |
| --- | --- | --- |
| [ledger.md](ledger.md) | Step 1: four `general-purpose` subagents in parallel, one append each | 72 cited bullets: Processes 13, Excel files 23, Data structure 8, Current implementation 28 |
| [current-state.md](current-state.md) | Step 2, checked against the sources and corrected in Step 3 | Inventory, How it is used, Limits and Gap list for the vacancy request |

The run used Claude Code 2.1.302 with `claude-haiku-5-5`, headless from this folder.

What the gap list concluded:

| # | Capability | Status |
| --- | --- | --- |
| 1 | Record a vacancy | partly exists |
| 2 | Suggest internal candidates from skills and languages | partly exists |
| 3 | Report Days Open per vacancy | partly exists |
| 4 | Move an employee into the role and close the vacancy in one step | missing |

The check in Step 3 held 11 Limits lines and corrected one: the `HRTools` class summary says changes reset when the server restarts, but the code saves each change to SQLite, so the line now calls the summary stale.
