import sys

from billing.invoices import load_invoices, open_totals

for customer, total in sorted(open_totals(load_invoices(sys.argv[1])).items()):
    print(f"{customer}: {total:.2f}")
