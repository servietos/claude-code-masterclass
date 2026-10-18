# Contract: Calculation Library

**Module**: `meeting_cost.calculation` | **Feature**: [spec.md](../spec.md)

This is the importable interface. It depends on nothing else in the package and nothing in the CLI.

## Public names

```text
calculate_cost(duration_minutes: str, hourly_rates: Sequence[str]) -> CostResult
InputError(field: str, position: int | None, message: str)
CostResult(total: Decimal, breakdown: tuple[AttendeeCost, ...])
AttendeeCost(position: int, amount: Fraction)
```

Inputs are text, as the command line supplies them. The module parses and validates them.

## Behaviour

| Input | Result |
|-------|--------|
| `duration_minutes="60"`, `hourly_rates=["100", "80", "60"]` | `total == Decimal("240.00")` |
| `duration_minutes="30"`, `hourly_rates=["90"]` | `total == Decimal("45.00")` |
| `duration_minutes="40"`, `hourly_rates=["50"]` | `total == Decimal("33.33")`, `breakdown[0].amount == Fraction(100, 3)` |
| `duration_minutes="60"`, `hourly_rates=["0"]` | `total == Decimal("0.00")`, breakdown still lists position 1 |
| `hourly_rates=[]` | raises `InputError(field="attendees", position=None)` |
| `duration_minutes="0"` or `"-5"` or `"1.5"` or `"abc"` | raises `InputError(field="duration", position=None)` |
| `hourly_rates=["-1"]` | raises `InputError(field="hourly rate", position=1)` |
| `hourly_rates=["abc"]`, `["NaN"]`, `["Infinity"]` | raises `InputError(field="hourly rate", position=1)` |

## Guarantees

- For every successful call, `sum(a.amount for a in breakdown)` equals the exact total before rounding (FR-006).
- `total` is the exact total rounded half up to two decimal places (FR-007).
- No floating point is used. No I/O. No network.
- A raised `InputError` means no `CostResult` was returned (FR-014).
