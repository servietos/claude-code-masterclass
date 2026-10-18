# Notes CLI Tag and Pin Solution

Completed reference for Lab 01 (`labs/11-planning/lab-01-spec-driven-from-scratch.md`). The lab's starter ships beside this folder at [../notes-cli/](../notes-cli), so this folder is the finished state: normalised `tags` plus a `note_tags` junction table, a `pinned` column added by a non-destructive migration, multi-tag AND filtering, and pinned-first ordering.

## Setup on Windows

PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -c "from db import init_db; init_db()"
```

Git Bash:

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
python -c "from db import init_db; init_db()"
```

Without activating the environment, `python notes.py` runs against whatever Typer is on the machine, not the pinned `typer==0.27.0`. Skip activation by calling the interpreter directly: `.venv\Scripts\python.exe notes.py list`.

## Commands

```bash
python notes.py add "Write the quarterly report"
python notes.py list
python notes.py tag add 1 work
python notes.py tag remove 1 work
python notes.py list --tag work --tag urgent
python notes.py pin 1
python notes.py unpin 1
```

`--tag` is repeatable and uses AND semantics: a note is returned only when it carries every named tag. `list` sorts pinned notes first, then by id descending.

## Schema check

This form parses in PowerShell, cmd and Git Bash:

```bash
python -c "import sqlite3; print(sqlite3.connect('notes.db').execute('select name from sqlite_master where type=?', ('table',)).fetchall())"
```

Expected output:

```text
[('notes',), ('tags',), ('note_tags',)]
```
