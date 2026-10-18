# Implementation Plan: Meeting Cost Calculator

**Branch**: `001-meeting-cost-calculator` | **Date**: 2026-10-17 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-meeting-cost-calculator/spec.md`

## Summary

A flat Python package, `meeting_cost`, computes what one meeting occurrence costs in salary time. The calculation lives in its own module and is importable without the command line layer. A second module wraps it in an argparse command line, and `__main__.py` lets the package run as `python -m meeting_cost <minutes> <rate> [<rate> ...]`. Money is handled as exact rational numbers, the total is rounded half up to two decimal places, and the breakdown stays exact (per the Resolved Gaps in the spec). Only the standard library is used at runtime; pytest is the sole test dependency.

## Technical Context

**Language/Version**: Python 3.11 (the target; see research.md R1 on the local runtime)

**Primary Dependencies**: None at runtime. Standard library only: `fractions`, `decimal`, `argparse`, `dataclasses`. Test-only: pytest.

**Storage**: N/A. No database, no files written.

**Testing**: pytest, run from the project root.

**Target Platform**: Local terminal on Windows and POSIX. No network.

**Project Type**: library with a command line wrapper.

**Performance Goals**: Not applicable. A single calculation over a handful of attendees is instantaneous.

**Constraints**: No network calls, no database, no third-party runtime packages, no floating point for any monetary value, no file writes outside the project directory.

**Scale/Scope**: One occurrence per run. Attendee lists of a few dozen entries. No batch mode.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Result |
|-----------|-------|--------|
| 1. Separation of Concerns | `calculation.py` imports nothing from `cli.py` or `argparse`. `cli.py` imports `calculation.py`. Tests call `calculation.py` directly. | PASS |
| 2. No Hidden Dependencies | Runtime uses only `fractions`, `decimal`, `argparse`, `dataclasses`, `re`. pytest is the permitted test framework (FR-020). No other package. | PASS |
| 3. Explicit Failure | Every rejected input raises `InputError` with the field name (`attendees`, `duration`, `hourly rate`). No defaulting, clamping or coercion. | PASS |
| 4. Money Is Never a Float | Rates and minutes are parsed with `Decimal`. Costs are `Fraction`. No `float` appears in the calculation path. | PASS |
| 5. Every Acceptance Criterion Has a Test | Each acceptance scenario, each edge case and each SC maps to a test in the Test Map (research.md R6). | PASS (tests to be written in implementation) |
| 6. Offline by Default | No sockets, no HTTP, no file writes. | PASS |

**Result**: No violations. Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/001-meeting-cost-calculator/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   ├── calculation.md   # Library interface
│   └── cli.md           # Command line interface
├── checklists/
│   └── requirements.md  # Spec quality checklist (from /speckit-specify)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
meeting_cost/
├── __init__.py          # Package marker
├── __main__.py          # python -m meeting_cost entry point; calls cli.main
├── calculation.py       # Parsing, validation, cost calculation, rounding
└── cli.py               # argparse wrapper and output formatting

tests/
├── test_calculation.py  # Acceptance criteria, edge cases, invariants on calculation.py
└── test_cli.py          # Exit codes, output, error messages through cli.main
```

**Structure Decision**: Single flat package at the project root with two logic modules plus the entry point, as requested. `__init__.py` is required for the package to import. Tests sit in a top-level `tests/` folder. No `src/` layout, no packaging metadata: the package runs from the project root, which keeps the surface to what was asked for.

## Complexity Tracking

No constitution violations to justify.
