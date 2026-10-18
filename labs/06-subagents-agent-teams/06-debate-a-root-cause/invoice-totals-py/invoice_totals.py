import csv

from grouping import totals_by_customer
from loader import load_orders
from settings import load_settings


def main():
    settings = load_settings()
    orders = load_orders("orders.csv")
    totals = totals_by_customer(orders, settings)
    with open("finance.csv", newline="", encoding="utf-8") as handle:
        expected = {row["customer"]: float(row["total"]) for row in csv.DictReader(handle)}
    for customer, total in totals.items():
        status = "ok" if abs(total - expected[customer]) < 0.005 else "MISMATCH"
        print(f"{customer:<8} {total:>8.2f} {settings['currency']}  finance {expected[customer]:>8.2f}  {status}")


main()
