from settings import FREE_SHIPPING_FROM, LOYALTY_STEP, MAX_LOYALTY_DISCOUNT, SHIPPING_FEE, TAX_RATE


def loyalty_discount(years_as_customer: int) -> float:
    return min(years_as_customer * LOYALTY_STEP, MAX_LOYALTY_DISCOUNT)


def shipping(subtotal: float) -> float:
    return 0.0 if subtotal >= FREE_SHIPPING_FROM else SHIPPING_FEE


def total(subtotal: float, years_as_customer: int) -> float:
    discounted = subtotal * (1 - loyalty_discount(years_as_customer))
    return round(discounted * (1 + TAX_RATE) + shipping(discounted), 2)
