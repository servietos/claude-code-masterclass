from inventory import reserve
from pricing import total

PRICES = {"espresso-beans": 14.50, "filter-papers": 3.20, "grinder": 89.00}


def place_order(lines: dict[str, int], years_as_customer: int) -> dict:
    for sku, quantity in lines.items():
        reserve(sku, quantity)
    subtotal = sum(PRICES[sku] * quantity for sku, quantity in lines.items())
    return {"lines": lines, "subtotal": round(subtotal, 2), "total": total(subtotal, years_as_customer)}
