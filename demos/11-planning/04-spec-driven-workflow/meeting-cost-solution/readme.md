# Solution: The Meeting Cost Calculator, Run

This is the project from one run of the [Spec Kit pipeline demo](../demo-spec-kit-pipeline.md) on 2026-10-17, stopped where the run stopped: the CLI does not print the per-attendee breakdown yet, because the breakdown display format (research R4) is still open. Claude wrote every artifact and every line of code; the prompts are the ones in the demo guide.

Environment: Windows 11, Claude Code 2.1.302 with `haiku` (claude-haiku-5-5), `specify` 1.2.1, Python 3.12.10, pytest 9.0.3.

## What is here

| Path | Written by |
| --- | --- |
| `requirements.md`, `constitution.md` | The starter, copied unchanged |
| `.specify/memory/constitution.md` | `/speckit-constitution`: six principles, version 1.0.0 |
| `specs/001-meeting-cost-calculator/` | `/speckit-specify`, `/speckit-plan`, `/speckit-tasks`, the answers to the gaps, `/speckit-analyze` (read-only), three converge passes |
| `meeting_cost/` | `/speckit-implement`: `calculation.py`, `cli.py`, `__init__.py`, `__main__.py` |
| `tests/` | `/speckit-implement`: `test_calculation.py`, `test_cli.py` |

The `.claude/skills/` folder and the rest of `.specify/` are what `specify init` writes, unchanged by the run; [project-structure-solution/](../project-structure-solution/readme.md) lists them.

## Run it

From this folder, in Bash or PowerShell:

```bash
python -m pytest
python -m meeting_cost 60 100 80 60
python -m meeting_cost 7 100
python -m meeting_cost 0 100
```

```text
============================= 30 passed in 0.08s ==============================
Total (one occurrence): 240.00
Total (one occurrence): 11.67
meeting_cost: error: duration: must be a whole number of minutes greater than zero, got "0"
```

The total line is rounded half up to two decimal places: 7 minutes at 100 per hour is 11.666... and prints as 11.67. The per-attendee lines are not printed yet, so the run has not reached the acceptance criterion for the breakdown.

[← Back to The Spec-Driven Workflow](../readme.md)
