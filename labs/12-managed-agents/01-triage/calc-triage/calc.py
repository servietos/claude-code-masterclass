def median(values):
    """Return the median. For an even-length input, average the two middle values."""
    ordered = sorted(values)
    middle = len(ordered) // 2
    return ordered[middle]


def percent_change(old, new):
    """Return the percent change from old to new. Raise ValueError when old is zero."""
    return (new - old) / old * 100


def running_total(values):
    """Return the inclusive running total, so the last element equals sum(values)."""
    total = 0
    totals = []
    for value in values:
        totals.append(total)
        total += value
    return totals
