import csv
from collections import defaultdict


def load_invoices(path):
    with open(path, newline="") as handle:
        return list(csv.DictReader(handle))


def open_totals(invoices):
    totals = defaultdict(float)
    for invoice in invoices:
        if invoice["status"] == "open":
            totals[invoice["customer"]] += float(invoice["amount"])
    return dict(totals)
