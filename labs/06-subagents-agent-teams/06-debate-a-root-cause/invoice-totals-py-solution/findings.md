# Findings: Acme and Initech MISMATCH against finance.csv

## Surviving explanation

`pricing.resolve_price` caches the first unit price seen for each SKU across all customers. Every later line with that SKU is priced at the cached value, which ignores that line's own `unit_price`.

- `pricing.py:1` defines `_resolved = {}` at module level, so the cache lives for the whole run.
- `pricing.py:5-7` keys the cache on `sku` alone and stores `quoted` only on first sight.
- `pricing.py:11` in `line_total` calls `resolve_price(order["sku"], order["unit_price"])`, so the quoted price of the current row is ignored once the SKU is cached.

BOLT-M8 is first quoted at 0.10 by Globex (`orders.csv:2`). Acme's BOLT-M8 line (`orders.csv:4`, 1000 units at 0.12) and Initech's BOLT-M8 line (`orders.csv:8`, 100 units at 0.12) are both priced at 0.10.

Arithmetic, with tax 1.2:

| Customer | Priced by script (pre-tax) | Quoted (pre-tax) | Script total | Finance total |
|---|---|---|---|---|
| Globex | 62.00 | 62.00 | 74.40 | 74.40 |
| Acme | 149.00 (100 + 40 + 9) | 169.00 (120 + 40 + 9) | 178.80 | 202.80 |
| Initech | 22.50 (10 + 12.50) | 24.50 (12 + 12.50) | 27.00 | 29.40 |

The gaps are 24.00 for Acme (1000 units × 0.02 × 1.2) and 2.40 for Initech (100 units × 0.02 × 1.2).

## Evidence

### Failing run as shipped

Command: `python invoice_totals.py` in the project folder.

```text
Globex      74.40 EUR  finance    74.40  ok
Acme       178.80 EUR  finance   202.80  MISMATCH
Initech     27.00 EUR  finance    29.40  MISMATCH
```

### Single-variable control that closes the gap

In a scratch copy outside this folder (`%TEMP%\invoice-control-pricing`), the only change is the cache key in `resolve_price`: `sku` becomes `(sku, quoted)`. Nothing else in the copy changes.

```text
Globex      74.40 EUR  finance    74.40  ok
Acme       202.80 EUR  finance   202.80  ok
Initech     29.40 EUR  finance    29.40  ok
```

This control shows that each line must be priced at its own quoted price. The keyed-on-price cache is only a diagnostic. The fix removes the cache so that `line_total` uses `order["unit_price"]` directly.

## Rejected hypotheses

| Teammate | Variable changed (scratch copy only) | Result that refuted it |
|---|---|---|
| rounding | `config.json` `round_each_line`: true → false | Output identical. Acme stays at 178.80 and Initech at 27.00, both MISMATCH. |
| parsing | `loader.py`: added a filter that drops the `'acme '` row | Acme moves 178.80 → 168.00, the dropped 9.00 subtotal × 1.2. Still 34.80 short, and Initech is unchanged. This moves the number but does not close the gap. |
| tax | `config.json` `tax_rate`: 0.2 → 0.0 | Every total moves by the same factor, and Globex flips from ok to MISMATCH (62.00 vs 74.40). A uniform factor cannot produce a gap that appears only for Acme and Initech. |
| grouping | `grouping.py:5` `customer_key`: removed `.strip().lower()` | Acme moves to 168.00, and the script crashes with `KeyError: 'acme'` at `invoice_totals.py:15`. This is a real lever, but it moves Acme away from finance. |

The pricing hypothesis is the one that survived its control (see Evidence above).

## Not the reported bug

1. **First-seen display name (`grouping.py:13`).** `names.setdefault` keeps the first raw spelling of each customer. If `"acme "` had been the first Acme row, the display name would be `acme`, and the finance lookup at `invoice_totals.py:13-15` would raise `KeyError`. The grouping control confirmed the crash path. `orders.csv` does not trigger it, because Acme's first row is `Acme`.
2. **Global state in `pricing.py:1`.** `_resolved` persists for the lifetime of the process. Calling `totals_by_customer` twice in one process would carry prices from the first call into the second. Found by reading the code; not exercised by this run.
3. **Unguarded finance lookup (`invoice_totals.py:15`).** Any customer in `orders.csv` that is missing from `finance.csv` raises `KeyError`. Customers in `finance.csv` that never appear in `orders.csv` are silently ignored.
4. **Silent defaults (`settings.py:8` and `settings.py:10`).** A missing `tax_rate` silently defaults to 0.2, and a missing `round_each_line` silently defaults to true. A typo in `config.json` therefore passes without an error.
5. **Two rounding points (`pricing.py:13-14` and `pricing.py:19`).** Line totals round only when `round_each_line` is set, and `with_tax` always rounds the group total. The two rounding points are not documented together. This has no effect on the current data.

## Scope

- Read: the five `.py` files, `config.json`, `orders.csv` and `finance.csv`. `readme.md` was not read because it was not in the requested file list.
- No source file in this folder was changed. The control runs happened in scratch copies under `%TEMP%`.
