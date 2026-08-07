import pytest

from calc import median, percent_change, running_total


def test_median_averages_the_two_middle_values():
    assert median([4, 1, 3, 2]) == 2.5


def test_percent_change_rejects_a_zero_baseline():
    with pytest.raises(ValueError):
        percent_change(0, 5)


def test_running_total_is_inclusive():
    assert running_total([1, 2, 3]) == [1, 3, 6]
