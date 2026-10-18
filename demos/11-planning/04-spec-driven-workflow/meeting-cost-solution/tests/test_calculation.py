from decimal import Decimal
from fractions import Fraction

import pytest

from meeting_cost.calculation import InputError, calculate_cost


def test_three_attendees_sixty_minutes():
    assert calculate_cost("60", ["100", "80", "60"]).total == Decimal("240.00")


def test_single_attendee_thirty_minutes():
    assert calculate_cost("30", ["90"]).total == Decimal("45.00")


def test_total_rounds_half_up():
    assert calculate_cost("10", ["0.03"]).total == Decimal("0.01")


def test_zero_rate_contributes_zero():
    result = calculate_cost("60", ["0"])
    assert result.total == Decimal("0.00")
    assert result.breakdown[0].position == 1


def test_zero_attendees_rejected():
    with pytest.raises(InputError) as error:
        calculate_cost("60", [])
    assert error.value.field == "attendees"


@pytest.mark.parametrize("minutes", ["0", "-5", "1.5", "abc"])
def test_invalid_duration_rejected(minutes):
    with pytest.raises(InputError) as error:
        calculate_cost(minutes, ["100"])
    assert error.value.field == "duration"


@pytest.mark.parametrize("rate", ["-1", "abc", "NaN", "Infinity"])
def test_invalid_rate_rejected(rate):
    with pytest.raises(InputError) as error:
        calculate_cost("60", [rate])
    assert error.value.field == "hourly rate"
    assert error.value.position == 1


def test_invalid_rate_reports_its_position():
    with pytest.raises(InputError) as error:
        calculate_cost("60", ["10", "-1"])
    assert error.value.field == "hourly rate"
    assert error.value.position == 2


def test_breakdown_in_list_order():
    breakdown = calculate_cost("60", ["100", "80", "60"]).breakdown
    assert [line.position for line in breakdown] == [1, 2, 3]
    assert [line.amount for line in breakdown] == [Fraction(100), Fraction(80), Fraction(60)]


def test_breakdown_sums_exactly_to_unrounded_total():
    result = calculate_cost("40", ["50", "30", "20"])
    assert sum(line.amount for line in result.breakdown) == Fraction(200, 3)
    assert result.exact_total == Fraction(200, 3)
    assert result.total == Decimal("66.67")


def test_breakdown_is_not_rounded():
    assert calculate_cost("40", ["50"]).breakdown[0].amount == Fraction(100, 3)
