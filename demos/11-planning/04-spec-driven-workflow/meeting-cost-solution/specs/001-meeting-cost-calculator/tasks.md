# Tasks: Meeting Cost Calculator

**Input**: Design documents from `/specs/001-meeting-cost-calculator/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included. Constitution principle 5 requires a test for every acceptance criterion, so each story has test tasks even though the spec does not ask for TDD explicitly.

**Organization**: Tasks are grouped by user story. Stories share `meeting_cost/calculation.py` and `meeting_cost/cli.py`, so they are completed one after another in priority order.

**Blocker**: Task T023 and T024 need the breakdown display decision in research.md R4. Every other task can proceed without it.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story the task belongs to (US1, US2, US3)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the package skeleton

- [X] T001 Create the empty package marker `meeting_cost/__init__.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared types and input parsing that every user story depends on

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Create `meeting_cost/calculation.py` with `class InputError(Exception)` carrying `field: str`, `position: int | None`, and `message: str`. The `field` value is one of `"attendees"`, `"duration"`, `"hourly rate"` (data-model.md, InputError)
- [X] T003 Add frozen dataclasses `AttendeeCost(position: int, amount: Fraction)` and `CostResult(total: Decimal, breakdown: tuple[AttendeeCost, ...])` to `meeting_cost/calculation.py` (data-model.md, AttendeeCost and CostResult)
- [X] T004 Add `parse_duration(text: str) -> int` to `meeting_cost/calculation.py`. Match `[+-]?[0-9]+` with `re.fullmatch`, convert with `int`, and reject any value not greater than zero. Constraint from data-model.md, verbatim: "Whole number of minutes, greater than zero". On failure raise `InputError("duration", None, message)`, where the message quotes the offending text
- [X] T005 Add `parse_rate(text: str, position: int) -> Decimal` to `meeting_cost/calculation.py`. Convert with `Decimal(text)`, catch `InvalidOperation`, and reject non-finite and negative values. Constraint from data-model.md, verbatim: "Finite and greater than or equal to zero". On failure raise `InputError("hourly rate", position, message)`, where the message names the position

**Checkpoint**: Foundation ready. Types and parsers exist, so user stories can start.

---

## Phase 3: User Story 1 - See the total salary cost of a meeting (Priority: P1) MVP

**Goal**: An organizer runs one command and gets the total cost of one occurrence, with every invalid input rejected before any total is printed.

**Independent Test**: `python -m meeting_cost 60 100 80 60` prints a total of 240.00 and exits with 0. `python -m meeting_cost 30 90` prints 45.00.

### Tests for User Story 1

> **NOTE: Write these tests first and confirm they fail before implementing T013 to T015**

- [X] T006 [US1] In `tests/test_calculation.py`, add `test_three_attendees_sixty_minutes` asserting `calculate_cost("60", ["100", "80", "60"]).total == Decimal("240.00")` (spec US1, acceptance scenario 1)
- [X] T007 [US1] In `tests/test_calculation.py`, add `test_single_attendee_thirty_minutes` asserting `calculate_cost("30", ["90"]).total == Decimal("45.00")` (spec US1, acceptance scenario 2)
- [X] T008 [US1] In `tests/test_calculation.py`, add `test_total_rounds_half_up` asserting `calculate_cost("10", ["0.03"]).total == Decimal("0.01")`. The exact cost is 0.005, which rounds up (FR-007)
- [X] T009 [US1] In `tests/test_calculation.py`, add `test_zero_rate_contributes_zero` asserting `calculate_cost("60", ["0"]).total == Decimal("0.00")` (spec edge case, FR-013)
- [X] T010 [US1] In `tests/test_calculation.py`, add `test_zero_attendees_rejected` asserting `InputError` with `field == "attendees"` for `calculate_cost("60", [])` (FR-009)
- [X] T011 [US1] In `tests/test_calculation.py`, add `test_invalid_duration_rejected`, parametrized over `"0"`, `"-5"`, `"1.5"`, `"abc"`. Each case raises `InputError` with `field == "duration"` (FR-010, FR-011)
- [X] T012 [US1] In `tests/test_calculation.py`, add `test_invalid_rate_rejected`, parametrized over `"-1"`, `"abc"`, `"NaN"`, `"Infinity"` as the single rate. Each case raises `InputError` with `field == "hourly rate"` and `position == 1`. Add one case `calculate_cost("60", ["10", "-1"])` that raises with `position == 2` (FR-012)

### Implementation for User Story 1

- [X] T013 [US1] Implement `calculate_cost(duration_minutes: str, hourly_rates: Sequence[str]) -> CostResult` in `meeting_cost/calculation.py`. Validation order: reject an empty `hourly_rates` with field `"attendees"` (constraint from data-model.md, verbatim: "At least one entry"), then `parse_duration`, then `parse_rate` for each entry in list order. Each `AttendeeCost.amount` is `Fraction(rate) * Fraction(minutes, 60)`. The total is the exact sum rounded half up to two decimal places. Breakdown amounts are never rounded (research.md R2, R3)
- [X] T014 [US1] Create `meeting_cost/cli.py` with `main(argv: list[str] | None = None) -> int`. Use argparse with a positional `minutes` and a positional `rates` declared with `nargs="*"` (research.md R7). On success print `Total (one occurrence): {total}` and return 0. On `InputError`, write `error: {field}: {message}` to stderr and return 2. Also update the success output in `specs/001-meeting-cost-calculator/contracts/cli.md` to show this label, since spec US3 requires the output to state one occurrence and the plan's contract did not include it
- [X] T015 [US1] Create `meeting_cost/__main__.py` that imports `main` from `meeting_cost.cli` and raises `SystemExit(main())` under `if __name__ == "__main__":`

### CLI tests for User Story 1

- [X] T016 [US1] In `tests/test_cli.py`, add `test_valid_run_prints_total_and_exits_zero` calling `main(["60", "100", "80", "60"])`. Assert the return value is 0 and `"240.00"` is in captured stdout (FR-015, SC-004)
- [X] T017 [US1] In `tests/test_cli.py`, add `test_invalid_input_exits_nonzero_naming_field`, parametrized over `(["0", "100"], "duration")`, `(["60"], "attendees")`, `(["60", "100", "-5"], "hourly rate")`, `(["60", "100", "abc"], "hourly rate")`. Assert the return value is 2 and the field name is in stderr (FR-016, SC-003)
- [X] T018 [US1] In `tests/test_cli.py`, add `test_invalid_input_prints_nothing_to_stdout` asserting empty stdout for each rejected input in T017 (FR-014)
- [X] T019 [US1] In `tests/test_cli.py`, add `test_module_runs_as_package` that runs `subprocess.run([sys.executable, "-m", "meeting_cost", "30", "90"])` and asserts return code 0 and `45.00` in stdout (FR-015, quickstart.md section 1)

**Checkpoint**: User Story 1 is complete. The total works from the command line and from the library, and invalid input is rejected.

---

## Phase 4: User Story 2 - See what each attendee contributes (Priority: P2)

**Goal**: The organizer sees one exact cost per attendee, in list order, and the amounts add up to the total before rounding.

**Independent Test**: `python -m meeting_cost 60 100 80 60` lists attendees 1, 2 and 3 with 100, 80 and 60, and those add up to 240.

**Blocked**: T023 and T024 wait for the breakdown display decision in research.md R4. T020 to T022 do not.

### Tests for User Story 2

- [X] T020 [US2] In `tests/test_calculation.py`, add `test_breakdown_in_list_order` asserting that `calculate_cost("60", ["100", "80", "60"]).breakdown` has positions `(1, 2, 3)` and amounts `Fraction(100)`, `Fraction(80)`, `Fraction(60)` (spec US2, acceptance scenario 1)
- [X] T021 [US2] In `tests/test_calculation.py`, add `test_breakdown_sums_exactly_to_unrounded_total` for `calculate_cost("40", ["50", "30", "20"])`. Assert `sum(a.amount for a in breakdown) == Fraction(200, 3)` and `total == Decimal("66.67")` (FR-006, SC-002)
- [X] T022 [US2] In `tests/test_calculation.py`, add `test_breakdown_is_not_rounded` asserting `calculate_cost("40", ["50"]).breakdown[0].amount == Fraction(100, 3)` (FR-005, FR-007)

### Implementation for User Story 2

- [ ] T023 [US2] BLOCKED on research.md R4. In `meeting_cost/cli.py`, print a `Breakdown:` line after the total, then one line per `AttendeeCost` as `  {position}: {amount}` in the format chosen in research.md R4. Update the success output in `specs/001-meeting-cost-calculator/contracts/cli.md` to match
- [ ] T024 [US2] BLOCKED on research.md R4. In `tests/test_cli.py`, add `test_valid_run_prints_breakdown` asserting that `main(["60", "100", "80", "60"])` prints a `Breakdown:` line and one line per attendee position

**Checkpoint**: User Story 2 is complete once T023 and T024 are unblocked. Until then, the breakdown is computed and tested at library level only.

---

## Phase 5: User Story 3 - Judge a recurring meeting (Priority: P3)

**Goal**: The output is clearly one occurrence, with no annual figure, so the team lead can multiply it themselves.

**Independent Test**: The output of one run states one occurrence and contains no annual figure.

### Tests for User Story 3

- [X] T025 [US3] In `tests/test_cli.py`, add `test_output_states_one_occurrence` asserting that `"Total (one occurrence): 240.00"` is in stdout for `main(["60", "100", "80", "60"])` and that neither `"year"` nor `"annual"` appears in stdout (spec US3, acceptance scenario 1; FR-019)

**Note**: No new code. The label comes from T014.

**Checkpoint**: All three user stories are complete.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Constitution and requirement checks that span the whole package

- [X] T026 [P] Search `meeting_cost/` for `float`, `socket`, `urllib`, `http`, and `requests`. Remove any match in the calculation path (constitution principles 4 and 6, FR-018)
- [X] T027 [P] Check that every import under `meeting_cost/` and `tests/` is from the standard library or from pytest (constitution principle 2, FR-020)
- [X] T028 [P] Check that `meeting_cost/calculation.py` imports neither `meeting_cost.cli` nor `argparse` (constitution principle 1, FR-017)
- [ ] T029 Run the sections of `specs/001-meeting-cost-calculator/quickstart.md` on a Python 3.11 interpreter (research.md R1). If only 3.12 is available, report the run as a 3.12 run

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup. Blocks all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational. This is the MVP
- **User Story 2 (Phase 4)**: Depends on US1, because it extends `calculate_cost` and `cli.main`. T023 and T024 also depend on the R4 decision
- **User Story 3 (Phase 5)**: Depends on T014 from US1
- **Polish (Phase 6)**: Depends on all stories being complete

### Within Each User Story

- Tests are written and seen to fail before the implementation they cover
- Library before CLI
- Story complete before the next priority

### Parallel Opportunities

- T026, T027 and T028 are read-only checks on different concerns and can run together
- Stories are not parallel in practice: they share `calculation.py` and `cli.py`

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: run `python -m meeting_cost 60 100 80 60` and check for 240.00

### Incremental Delivery

1. Setup + Foundational: foundation ready
2. Add User Story 1: total works and is validated (MVP)
3. Decide research.md R4, then add User Story 2: breakdown
4. Add User Story 3: one-occurrence label, verified by test
5. Polish: constitution checks and the 3.11 run

---

## Notes

- [P] tasks touch different files and have no dependencies on incomplete tasks
- [Story] labels map each task to its user story for traceability
- Every task names an exact file path or quotes the constraint it implements
- The test-first note in each story is a process rule that applies to every task in that story

## Phase 7: Convergence

- [X] T030 Add an exact_total field of type Fraction to CostResult in meeting_cost/calculation.py, set to the exact sum of the breakdown before rounding, and assert exact_total == Fraction(200, 3) for calculate_cost("40", ["50", "30", "20"]) in tests/test_calculation.py per data-model.md CostResult (missing)
- [X] T031 Change the hourly rate error line so stderr reads "error: hourly rate for attendee N: ..." in meeting_cost/cli.py and meeting_cost/calculation.py, using the wording in contracts/cli.md error output, and update tests/test_cli.py to match, keeping the field name in the line for all three fields per contracts/cli.md error output (partial)
