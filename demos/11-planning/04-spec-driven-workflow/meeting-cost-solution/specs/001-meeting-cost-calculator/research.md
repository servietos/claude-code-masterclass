# Research: Meeting Cost Calculator

**Feature**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

Each decision below resolves an open point in the Technical Context or follows from a spec requirement.

## R1. Python version and local runtime

- **Decision**: Target Python 3.11. Write code that uses nothing newer than 3.11.
- **Rationale**: Chosen by the user.
- **Alternatives considered**: 3.12 (the default on this machine). Rejected because the user named 3.11.
- **Consequence**: The local `python` is 3.12.10 and no 3.11 interpreter was found (`py -3.11` reports none). Implementation and verification need a 3.11 interpreter. Until one is installed, any run on 3.12 must be reported as a 3.12 run.

## R2. Exact arithmetic for money

- **Decision**: Parse minutes and rates with `Decimal`. Compute each attendee's cost as `Fraction(rate) * Fraction(minutes, 60)`. Sum costs as `Fraction`.
- **Rationale**: Constitution principle 4 forbids floats for money. `Decimal` division rounds at 28 significant digits, so a sum of per-attendee quotients could differ from a separately computed total. `Fraction` is exact, so FR-006 ("breakdown adds up to the total before rounding") holds by construction.
- **Alternatives considered**:
  - `Decimal` throughout: rejected because of the precision issue above.
  - Integer minor units (cents): rejected because a rate times 40 minutes is not a whole number of cents, and rounding would happen before the sum.

## R3. Rounding

- **Decision**: The total is `Fraction` rounded half up to two decimal places (spec Resolved Gaps, Q2). Implement as `Decimal(total.numerator) / Decimal(total.denominator)` quantized with `ROUND_HALF_UP` at `0.01`, or an equivalent integer computation. Breakdown amounts are never rounded.
- **Rationale**: Spec Q2 decision.

## R4. Breakdown display (OPEN)

- **Status**: Open. The spec does not say how a non-terminating breakdown amount is printed. Example: 40 minutes at 50 per hour is 33.333..., which has no finite decimal form.
- **Impact**: Only the printed breakdown. The calculation and the total are unaffected.
- **Options for the user**:
  - A: Print the exact fraction (for example `100/3`).
  - B: Print a fixed number of decimal places with a truncation or repeating marker.
  - C: Print the decimal expansion to a digit count the user names.
- **Blocking**: Does not block the calculation module or its tests. The CLI output format in `contracts/cli.md` is marked pending until this is decided.

## R5. Input validation and parsing

- **Decision**: All parsing and validation live in `calculation.py`. The CLI passes raw strings through.
  - Minutes: optional sign followed by ASCII digits (`re.fullmatch(r"[+-]?[0-9]+", text)`), then `int`. Must be greater than zero. Otherwise `InputError("duration")`.
  - Rates: `Decimal(text)` inside a try block. Reject if the result is not finite (NaN, Infinity) or is negative. Otherwise `InputError("hourly rate")` naming the attendee's 1-based position.
  - Attendees: an empty sequence raises `InputError("attendees")`.
  - Validation order: attendees, then duration, then rates in list order. The first failure is reported; no partial output (FR-014).
- **Rationale**: One place for every rule means the CLI cannot drift from the library. `Decimal` accepts `NaN` and `Infinity`, so those need explicit rejection.
- **Alternatives considered**: `argparse` `type=` converters. Rejected because argparse errors do not name the spec's field names and would split validation across two modules.

## R6. Test strategy

- **Decision**: pytest. `tests/test_calculation.py` covers the calculation module directly. `tests/test_cli.py` calls `cli.main(argv)` and checks return codes, stdout and stderr with `capsys`. No subprocess tests are needed for the core; one subprocess test runs `python -m meeting_cost` to prove the entry point.
- **Test map**:

| Spec item | Test |
|-----------|------|
| US1 AS1: 60 min, 100/80/60 gives 240 | `test_calculation.py::test_three_attendees_sixty_minutes` |
| US1 AS2: 30 min, 90 gives 45 | `test_calculation.py::test_single_attendee_thirty_minutes` |
| US2 AS1: per-attendee lines in order | `test_calculation.py::test_breakdown_in_list_order` |
| US2 AS2, FR-006, SC-002: breakdown sums to total before rounding | `test_calculation.py::test_breakdown_sums_exactly_to_unrounded_total` (uses 40 min at 50 per hour) |
| FR-007: total rounded half up | `test_calculation.py::test_total_rounds_half_up` |
| FR-007: breakdown unrounded | `test_calculation.py::test_breakdown_is_not_rounded` |
| Edge: zero attendees | `test_calculation.py::test_zero_attendees_rejected` |
| Edge: zero minutes, negative minutes, fractional minutes | `test_calculation.py::test_invalid_duration_rejected` (parametrized) |
| Edge: negative rate, non-numeric rate, NaN | `test_calculation.py::test_invalid_rate_rejected` (parametrized) |
| Edge: zero rate valid | `test_calculation.py::test_zero_rate_contributes_zero` |
| FR-014: no partial output | `test_cli.py::test_invalid_input_prints_nothing_to_stdout` |
| FR-015, SC-004: exit 0 and output | `test_cli.py::test_valid_run_prints_total_and_breakdown` |
| FR-016, SC-003: non-zero exit names field | `test_cli.py::test_invalid_input_exits_nonzero_naming_field` (parametrized) |
| FR-017: calculation importable alone | `test_calculation.py` imports only `meeting_cost.calculation` |
| FR-018: offline | Code review check: no `socket`, `urllib` or `http` imports in the package |

## R7. Command line design

- **Decision**: `argparse` with two positionals: `minutes` (one) and `rates` (`nargs="*"`). `nargs="*"` is used so that zero rates reach the library and produce the spec's `attendees` error rather than argparse's own "required" message.
- **Negative numbers**: argparse treats `-5` as a value when no option in the parser looks like a negative number, so `python -m meeting_cost 60 -5` reaches validation. No `-` options are defined.
- **Exit codes**: 0 on success. 2 on any invalid input, matching argparse's usage-error convention.
- **Alternatives considered**: `sys.argv` parsing by hand. Rejected because argparse gives `--help` and usage text for free without a dependency.
