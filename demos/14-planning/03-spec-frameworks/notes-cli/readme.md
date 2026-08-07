# notes-cli Starter for the Spec Framework Demos

A minimal Python CLI with `add` and `list` commands over a single SQLite table, deliberately small so the generated specs are the interesting part. This is the starter both spec-framework demos run against; the feature they specify (tag-based search plus pinning) is checked in at [../notes-cli-solution/](../notes-cli-solution/).

| File | Contents |
|---|---|
| `notes.py` | Typer app: `add` writes a note, `list` prints newest first |
| `db.py` | `sqlite3` connection plus `init_db()`, which creates the `notes` table if it is missing |
| `requirements.txt` | One dependency, `typer` |

## Run It

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python notes.py add "first note"
.venv/Scripts/python notes.py add "second note"
.venv/Scripts/python notes.py list
```

On macOS or Linux use `.venv/bin/python` instead of `.venv/Scripts/python`. Expected output:

```text
2  2026-07-22 20:35:38  second note
1  2026-07-22 20:35:38  first note
```

`init_db()` runs on every invocation, so the first command creates `notes.db` in the working directory.

## Where the Demos Run

Spec Kit and BMAD each initialise their own git repository and write their own tree, so each demo works from its own prepared copy outside this checkout, at `~/spec-runs/`. The setup scripts make those copies:

| Demo | Setup script | Run folder |
|---|---|---|
| [Run a Feature Through the Four-Step Spec Kit Pipeline](../demo-spec-kit-pipeline.md) | [setup-speckit.ps1](../setup-speckit.ps1) / [setup-speckit.sh](../setup-speckit.sh) | `~/spec-runs/notes-cli-speckit` |
| [Produce Stakeholder-Readable Specs with the BMAD Agent Chain](../demo-bmad-agent-chain.md) | [setup-bmad.ps1](../setup-bmad.ps1) / [setup-bmad.sh](../setup-bmad.sh) | `~/spec-runs/notes-cli-bmad` |

Two separate copies keep each framework's artefacts isolated, which is what makes the three-way comparison at the end of the BMAD demo readable.
