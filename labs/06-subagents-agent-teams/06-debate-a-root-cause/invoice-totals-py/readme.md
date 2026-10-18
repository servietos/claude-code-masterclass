# invoice-totals-py

A dependency-free script that totals the day's orders per customer, adds tax, and compares each total to the finance sheet. Finance says two of the three invoices are wrong. Nobody knows why.

```bash
python invoice_totals.py
```

| File | Role |
|---|---|
| `invoice_totals.py` | Entry point: loads, totals, and compares against `finance.csv` |
| `loader.py` | Reads `orders.csv` |
| `pricing.py` | Prices each order line and applies tax |
| `grouping.py` | Groups lines by customer |
| `settings.py` | Reads `config.json` |
| `finance.csv` | The totals finance expects |
