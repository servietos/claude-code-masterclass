# Data Model: Meeting Cost Calculator

**Feature**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Code**: `meeting_cost/calculation.py`

## Meeting

| Field | Type | Rule |
|-------|------|------|
| `duration_minutes` | `int` | Whole number of minutes, greater than zero (FR-002, FR-010, FR-011) |
| `attendees` | `tuple[Attendee, ...]` | At least one entry (FR-009) |

Relationship: a Meeting has one or more Attendees. The Meeting is one occurrence. It has no identity, no date and no storage (spec Assumptions, FR-019).

## Attendee

| Field | Type | Rule |
|-------|------|------|
| `position` | `int` | 1-based index in the input list. Derived from list order. |
| `hourly_rate` | `Decimal` | Finite and greater than or equal to zero (FR-012, FR-013) |

No name, label or identifier (spec Resolved Gaps). An attendee is identified only by `position`.

## CostResult

| Field | Type | Rule |
|-------|------|------|
| `total` | `Decimal` | Sum of the exact per-attendee costs, rounded half up to two decimal places (FR-004, FR-007) |
| `breakdown` | `tuple[AttendeeCost, ...]` | One entry per attendee, in input order |

Derived: `exact_total` is the sum of the exact `AttendeeCost.amount` values as `Fraction`. It is held internally so tests can assert FR-006 before rounding.

## AttendeeCost

| Field | Type | Rule |
|-------|------|------|
| `position` | `int` | Matches the Attendee |
| `amount` | `Fraction` | `hourly_rate * duration_minutes / 60`, exact, never rounded (FR-005, FR-007) |

Rendering of `amount` is open (research.md R4).

## InputError

Raised by the calculation module for every rejected input. Not an `argparse` error.

| Field | Type | Rule |
|-------|------|------|
| `field` | `str` | One of `"attendees"`, `"duration"`, `"hourly rate"` (FR-009 to FR-012) |
| `position` | `int or None` | Set for `"hourly rate"` to the 1-based attendee position. `None` otherwise. |
| `message` | `str` | Human text naming the field and the offending value |

Validation order: attendees, duration, then each rate in list order. The first failure is raised (FR-014).

## Derived calculation

For each attendee `i` with rate `r_i` and duration `m` minutes:

```text
amount_i = r_i * m / 60            (exact, Fraction)
exact_total = sum(amount_i)        (exact, Fraction)
total = round_half_up(exact_total, 2 decimal places)
```

Invariant: `sum(amount_i) == exact_total` by construction. The rounded `total` is the only rounded value.

Worked check against the spec:

| Case | Amounts | exact_total | total |
|------|---------|-------------|-------|
| 60 min, 100/80/60 | 100, 80, 60 | 240 | 240.00 |
| 30 min, 90 | 45 | 45 | 45.00 |
| 40 min, 50 | 100/3 | 100/3 | 33.33 |
