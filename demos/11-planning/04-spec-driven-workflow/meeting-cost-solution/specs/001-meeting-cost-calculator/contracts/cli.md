# Contract: Command Line Interface

**Entry point**: `python -m meeting_cost` (`meeting_cost/__main__.py` calls `meeting_cost.cli.main`) | **Feature**: [spec.md](../spec.md)

## Usage

```text
python -m meeting_cost <minutes> <rate> [<rate> ...]
```

| Argument | Meaning |
|----------|---------|
| `minutes` | Meeting length in whole minutes, greater than zero |
| `rate` | One hourly rate per attendee, in the order the breakdown should list them. Zero or more. |

Zero rates is parsed, then rejected by the library as the `attendees` field (FR-009).

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Valid input. Total and breakdown printed to stdout. |
| 2 | Invalid input. Nothing printed to stdout. One line on stderr naming the field. |

## Success output

```text
Total (one occurrence): 240.00
Breakdown:
  1: 100
  2: 80
  3: 60
```

The breakdown amount format is pending (research.md R4). The lines above show whole-number rates only, where every amount is exact. The total line is always two decimal places.

## Error output

One line on stderr, naming the field:

```text
error: duration: must be a whole number of minutes greater than zero, got "0"
error: attendees: at least one hourly rate is required
error: hourly rate for attendee 2: must be a finite number greater than or equal to zero, got "-5"
```

argparse usage errors (for example an unknown option) use argparse's own format and also exit 2.

## Help

`python -m meeting_cost --help` prints the argparse usage and the two positional descriptions.
