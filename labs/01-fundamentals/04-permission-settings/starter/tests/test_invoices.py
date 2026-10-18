import unittest

from billing.invoices import load_invoices, open_totals


class OpenTotalsTest(unittest.TestCase):
    def test_paid_invoices_are_excluded(self):
        totals = open_totals(load_invoices("data/invoices.csv"))
        self.assertEqual(totals["Acme"], 1200.00)

    def test_totals_add_up_per_customer(self):
        totals = open_totals(load_invoices("data/invoices.csv"))
        self.assertEqual(totals["Borealis"], 497.25)


if __name__ == "__main__":
    unittest.main()
