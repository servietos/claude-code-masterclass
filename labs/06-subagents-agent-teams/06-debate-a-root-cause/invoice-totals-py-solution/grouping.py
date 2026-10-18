from pricing import line_total, with_tax


def customer_key(name):
    return name.strip().lower()


def totals_by_customer(orders, settings):
    subtotals = {}
    names = {}
    for order in orders:
        key = customer_key(order["customer"])
        names.setdefault(key, order["customer"].strip())
        subtotals[key] = subtotals.get(key, 0) + line_total(order, settings)
    return {names[key]: with_tax(value, settings) for key, value in subtotals.items()}
