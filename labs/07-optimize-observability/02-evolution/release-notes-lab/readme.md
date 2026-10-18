# Release Notes Experiment Starter

Starter for [`lab-02-evolve-via-metrics.md`](../../lab-02-evolve-via-metrics.md). The completed reference sits beside it in [`release-notes-lab-solution/`](../release-notes-lab-solution/readme.md).

## What ships here

| Path | Role |
|---|---|
| `hello.py`, `math_utils.py`, `cli.py` | The Typer CLI the release notes describe |
| `requirements.txt` | `typer==0.27.0` |
| `release-notes/.claude-plugin/plugin.json` | The plugin manifest `claude plugin eval` loads |
| `release-notes/skills/release-notes/SKILL.md` | The deliberately under-specified skill you will measure and improve |
| `release-notes/evals/recent-changes/commits.txt` | The `git log --oneline` of this CLI's history, the fixture every run reads |

## What you build

The rest of the eval case in `release-notes/evals/recent-changes/` (`prompt.md`, `case.yaml`, `fixture.sh` and `graders/`), plus everything the autoresearch loop writes into `experiments/`: the `v0`, `v1`, `v1b` and `v2` result folders, `proposal-1.md`, `proposal-2.md`, `compare-v0-v1.md`, `lessons.md` and `summary.md`.

## Run it

There is nothing to install. Once Step 1 has written the case, run it from this folder:

```bash
claude plugin eval release-notes --scaffold --trust-plugin --no-publish --max-cost-usd 5 --output-dir experiments/v0
```
