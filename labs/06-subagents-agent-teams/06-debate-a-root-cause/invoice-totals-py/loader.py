import csv


def load_orders(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return [
            {
                "customer": row["customer"],
                "sku": row["sku"],
                "qty": int(row["qty"]),
                "unit_price": float(row["unit_price"]),
            }
            for row in csv.DictReader(handle)
        ]
