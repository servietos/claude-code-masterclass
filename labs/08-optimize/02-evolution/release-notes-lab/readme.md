# Release Notes Experiment Starter

Starter for [`lab-02-evolve-via-metrics.md`](../../lab-02-evolve-via-metrics.md). The completed reference sits beside it in [`release-notes-lab-solution/`](../release-notes-lab-solution/readme.md).

## What ships here

| Path | Role |
|---|---|
| `hello.py`, `math_utils.py`, `cli.py` | The Typer CLI the release notes describe |
| `requirements.txt` | `typer==0.27.0` |
| `.claude/skills/release-notes/SKILL.md` | The deliberately under-specified skill you will measure and improve |
| `.gitignore` | Keeps `.venv/`, `experiments/runs/` and `metrics.json` out of git |

## What you build

`experiments/runner.sh`, the deterministic harness, plus everything the autoresearch loop writes beside it: `metrics-v0.json`, `proposal-1.md`, `compare-v0-v1.md`, `lessons.md` and `summary.md`.

This folder ships without a `.git` directory: a nested repository inside the class repo shows up as an embedded repo. Run `git init` here and make the commits the lab's Setup asks for before you run the harness, because it reads git history.

## Run it

```bash
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt
./.venv/Scripts/python.exe cli.py hello Ada
./.venv/Scripts/python.exe cli.py sum-values 2 3
```

On Linux or macOS use `.venv/bin/python`. Expected output is `Hello, Ada!` then `5.0`.
