# Release Notes Experiment Solution

Completed reference for [`lab-02-evolve-via-metrics.md`](../../lab-02-evolve-via-metrics.md). The starter lives beside this folder as [`release-notes-lab/`](../release-notes-lab/readme.md).

## What is here

| Path | Role |
|---|---|
| `hello.py`, `math_utils.py`, `cli.py`, `requirements.txt` | The Typer CLI the release notes describe |
| `release-notes/skills/release-notes/SKILL.md` | The skill after both promoted refinements |
| `release-notes/evals/recent-changes/` | The finished case: `prompt.md`, `case.yaml`, `fixture.sh`, `commits.txt` and seven graders |
| `experiments/v0`, `v1`, `v1b`, `v2` | `aggregate-result.json` and `report.html` from each real run |
| `experiments/skill-v0.md`, `skill-v1.md` | The skill before each refinement |
| `experiments/proposal-1.md`, `proposal-2.md`, `compare-v0-v1.md`, `lessons.md`, `summary.md` | The loop's written record |

## Run it

```bash
claude plugin eval release-notes --scaffold --trust-plugin --no-publish --max-cost-usd 5 --output-dir experiments/check
```

Every run is a real model call. The four recorded runs cost $0.35, $0.34, $0.35 and $0.33 at list price on Claude Code 2.1.302.

## Measured results

| Grader | v0 | v1 | v1b | v2 |
|---|---|---|---|---|
| `version-heading` | 0 of 3 | 3 of 3 | 3 of 3 | 3 of 3 |
| `features-heading` | 0 of 3 | 3 of 3 | 3 of 3 | 3 of 3 |
| `fixes-heading` | 1 of 3 | 3 of 3 | 3 of 3 | 3 of 3 |
| `no-merge` | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 |
| `read-commits` | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 |
| `notes-only` | not graded | not graded | 0 of 3 | 3 of 3 |
| runs with an error | 0 | 0 | 0 | 0 |

`v1b` re-measures the unchanged v1 skill after `notes-only` was added, so the v2 improvement is attributable to the skill rather than to the new grader.
