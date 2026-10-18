# Solution: The Sample Case, Run

[The topic page](../readme.md) points at the Spec Kit pipeline demo, which takes the meeting cost calculator through the same four checkpoints in Claude Code. That run is checked in at [04-spec-driven-workflow/meeting-cost-solution/](../../04-spec-driven-workflow/meeting-cost-solution/readme.md): the four artifacts, the code, the tests and their real output. This folder records the claims about that run worth checking before you teach them.

Environment: Windows 11, Python 3.12.10, pytest 9.0.3, executed 2026-10-17.

## The two totals

```bash
python -m meeting_cost 60 100 80 60
python -m meeting_cost 30 90
```

```text
attendee 1: 100
attendee 2: 80
attendee 3: 60
total: 240.00
attendee 1: 45
total: 45.00
```

Both are exact. `240` and `45` are what the [brief's](../../04-spec-driven-workflow/meeting-cost/requirements.md) acceptance criteria ask for; the two decimal places come from FR-007 in the run's [spec.md](../../04-spec-driven-workflow/meeting-cost-solution/specs/001-meeting-cost-calculator/spec.md), the rounding rule closed in writing at the specify checkpoint.

## The float constraint, and why its tell is the plan

Principle 4 of the [constitution input](../../04-spec-driven-workflow/meeting-cost/constitution.md) says money is never a float. A `float` implementation breaks that principle without producing a visibly wrong number on this feature's inputs:

```bash
python -c "h=60/60.0; print(repr(sum(r*h for r in (100.0,80.0,60.0))))"
python -c "print(repr(90.0*(30/60.0)))"
```

```text
240.0
45.0
```

Every figure in the brief is exactly representable in binary, so a `float` implementation returns both totals and passes any test built on them. The violation is invisible in the output and visible only in `plan.md`, where a type is named. That is why the plan checkpoint is where this one gets caught: the tell is a plan naming `float`, while every total still comes back right.

This run's [plan.md](../../04-spec-driven-workflow/meeting-cost-solution/specs/001-meeting-cost-calculator/plan.md) names `Decimal` and marks principle IV as PASS in its Constitution Check.

## The 45 tests

```bash
python -m pytest -q
```

```text
.............................................                            [100%]
45 passed in 0.16s
```

Run from [meeting-cost-solution/](../../04-spec-driven-workflow/meeting-cost-solution/readme.md).

[← Back to Sample Case: Implement a Product Feature](../readme.md)
