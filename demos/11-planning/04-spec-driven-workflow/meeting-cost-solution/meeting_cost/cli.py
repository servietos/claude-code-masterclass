import argparse
import sys

from meeting_cost.calculation import InputError, calculate_cost


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="meeting_cost",
        description="Calculate the salary cost of one meeting occurrence.",
    )
    parser.add_argument("minutes", help="meeting length in whole minutes, greater than zero")
    parser.add_argument("rates", nargs="*", help="one hourly rate per attendee")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = calculate_cost(args.minutes, args.rates)
    except InputError as error:
        label = error.field if error.position is None else f"{error.field} for attendee {error.position}"
        print(f"error: {label}: {error.message}", file=sys.stderr)
        return 2
    print(f"Total (one occurrence): {result.total}")
    return 0
