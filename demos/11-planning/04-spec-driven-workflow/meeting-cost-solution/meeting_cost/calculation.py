import re
from dataclasses import dataclass
from collections.abc import Sequence
from decimal import Decimal
from fractions import Fraction

DURATION_PATTERN = re.compile(r"[+-]?[0-9]+")
RATE_PATTERN = re.compile(r"-?[0-9]+(\.[0-9]+)?")
MINUTES_PER_HOUR = 60


class InputError(Exception):
    def __init__(self, field: str, position: int | None, message: str):
        super().__init__(message)
        self.field = field
        self.position = position
        self.message = message


@dataclass(frozen=True)
class AttendeeCost:
    position: int
    amount: Fraction


@dataclass(frozen=True)
class CostResult:
    total: Decimal
    breakdown: tuple[AttendeeCost, ...]
    exact_total: Fraction


def parse_duration(text: str) -> int:
    if not DURATION_PATTERN.fullmatch(text) or int(text) <= 0:
        raise InputError("duration", None, f'must be a whole number of minutes greater than zero, got "{text}"')
    return int(text)


def parse_rate(text: str, position: int) -> Decimal:
    if not RATE_PATTERN.fullmatch(text) or Decimal(text) < 0:
        raise InputError(
            "hourly rate",
            position,
            f'must be a finite number greater than or equal to zero, got "{text}"',
        )
    return Decimal(text)


def round_half_up_cents(value: Fraction) -> Decimal:
    scaled = value * 100
    cents = (2 * scaled.numerator + scaled.denominator) // (2 * scaled.denominator)
    return Decimal(cents).scaleb(-2)


def calculate_cost(duration_minutes: str, hourly_rates: Sequence[str]) -> CostResult:
    if not hourly_rates:
        raise InputError("attendees", None, "at least one hourly rate is required")
    minutes = parse_duration(duration_minutes)
    rates = [parse_rate(text, position) for position, text in enumerate(hourly_rates, start=1)]
    breakdown = tuple(
        AttendeeCost(position, Fraction(rate) * Fraction(minutes, MINUTES_PER_HOUR))
        for position, rate in enumerate(rates, start=1)
    )
    exact_total = sum((line.amount for line in breakdown), Fraction(0))
    return CostResult(total=round_half_up_cents(exact_total), breakdown=breakdown, exact_total=exact_total)
