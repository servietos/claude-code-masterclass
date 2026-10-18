# Quickstart: Meeting Cost Calculator

**Feature**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Interfaces**: [CLI](contracts/cli.md), [library](contracts/calculation.md)

Run every command from the project root (`meeting-cost-solution/`). Requires Python 3.11 and pytest.

## 1. Check the worked examples

PowerShell and bash use the same command:

```text
python -m meeting_cost 60 100 80 60
```

Expected: `Total (one occurrence): 240.00`, exit code 0. The breakdown lines are pending research.md R4.

```text
python -m meeting_cost 30 90
```

Expected: `Total (one occurrence): 45.00`, exit code 0.

Check the exit code in PowerShell with `$LASTEXITCODE` and in bash with `echo $?`.

## 2. Check the rejection paths

Each command should exit with code 2 and print one stderr line naming the field:

```text
python -m meeting_cost 0 100
python -m meeting_cost 60
python -m meeting_cost 60 100 -5
python -m meeting_cost 60 100 abc
python -m meeting_cost -30 100
```

Expected field names, in order: `duration`, `attendees`, `hourly rate`, `hourly rate`, `duration`.

## 3. Run the tests

```text
python -m pytest
```

Expected: every test in `tests/` passes. Each acceptance criterion in the spec maps to a test (see [research.md R6](research.md)).

## 4. Use the library directly

```text
python -c "from meeting_cost.calculation import calculate_cost; print(calculate_cost('60', ['100','80','60']).total)"
```

Expected: `240.00`.

## Done when

- Section 1 prints the two expected totals with exit 0.
- Section 2 gives five non-zero exits, each naming the expected field.
- Section 3 is green on Python 3.11.
- The breakdown format question in [research.md R4](research.md) is answered and reflected in [contracts/cli.md](contracts/cli.md).
