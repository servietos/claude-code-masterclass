from datetime import date

LATE_FEE_PER_DAY_CENTS = 400
LATE_FEE_CAP_CENTS = 4000


def days_late(due_at: date, returned_at: date) -> int:
    return max((returned_at - due_at).days, 0)


def late_fee_cents(due_at: date, returned_at: date) -> int:
    fee = days_late(due_at, returned_at) * LATE_FEE_PER_DAY_CENTS
    return min(fee, LATE_FEE_CAP_CENTS)
