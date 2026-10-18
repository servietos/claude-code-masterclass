# CLAUDE.md

## Architecture

The `billing` package reads `data/invoices.csv` and prints open totals per customer. Keep one function per concern in `billing/invoices.py`.

## Secrets

`config.secrets.json` and everything under `secrets/` hold payment credentials. Never read them, never echo them, and never copy their values into another file.

## Build and Run

```bash
python -m unittest discover -s tests
python -m billing data/invoices.csv
```
