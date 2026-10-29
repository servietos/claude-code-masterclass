from settings import LOW_STOCK_THRESHOLD

STOCK = {"espresso-beans": 12, "filter-papers": 3, "grinder": 1}


def reserve(sku: str, quantity: int) -> None:
    available = STOCK.get(sku, 0)
    if quantity > available:
        raise ValueError(f"only {available} of {sku} in stock")
    STOCK[sku] = available - quantity


def low_stock() -> list[str]:
    return [sku for sku, count in STOCK.items() if count < LOW_STOCK_THRESHOLD]
