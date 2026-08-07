# Notes CLI Starter

Starter project for Lab 01 (`labs/14-planning/lab-01-spec-driven-from-scratch.md`). A minimal Python CLI over SQLite with two commands, `add` and `list`, and a `notes` table holding id, body and created_at. There are no tags, no pinning and no `STATE.md`: the lab adds all of that. The finished reference is beside it in [../notes-cli-solution/](../notes-cli-solution/).

## Setup on Windows

PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Git Bash:

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

Without activating the environment, `python notes.py` runs against whatever Typer is on the machine, not the pinned `typer==0.27.0`. Skip activation by calling the interpreter directly: `.venv\Scripts\python.exe notes.py list`.

## Commands

```bash
python notes.py add "Write the quarterly report"
python notes.py add "Buy milk"
python notes.py list
```

`list` prints id, created_at and body, one note per line, sorted by id descending.

`notes.db` is created relative to the working directory, so run every command from inside this folder. A shell opened elsewhere silently creates a second, empty database and `list` prints nothing with exit code 0.
