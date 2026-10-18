_resolved = {}


def resolve_price(sku, quoted):
    if sku not in _resolved:
        _resolved[sku] = quoted
    return _resolved[sku]


def line_total(order, settings):
    price = resolve_price(order["sku"], order["unit_price"])
    total = order["qty"] * price
    if settings["round_each_line"]:
        total = round(total, 2)
    return total


def with_tax(subtotal, settings):
    return round(subtotal * (1 + settings["tax_rate"]), 2)
