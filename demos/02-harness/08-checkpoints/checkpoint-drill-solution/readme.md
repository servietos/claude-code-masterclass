# Checkpoint Drill Pricing Module (Solution)

The completed reference for the checkpoint rollback drill. It is the starter after the full drill: baseline green, one deliberately over-reaching cross-cutting refactor, one rollback, and a final green run.

## State Note

This folder is the one that gets installed and run (`npm install`, `npm test`), so it carries the lockfile and `.gitignore` covers `node_modules/`. The drill was executed against `src/money.js`: the rounding strategy was swapped from half-up to truncation, which turned 4 of the 15 tests red across `test/money.test.js` and `test/pricing.test.js`. The rollback restored the original `roundCents` implementation, and the suite is back at 15 passing. `rollback-playbook.md` is the deliverable from Step 6.

Your own run will differ in the details: the refactor step is model-dependent, so Claude may thread a new parameter through the layers, break a different set of tests, or produce a diff that still passes. Any multi-file diff is enough to exercise the rollback.

## Layout

| File | Responsibility |
|------|----------------|
| `src/money.js` | Rounding, multiplication, summing, and EUR formatting |
| `src/catalog.js` | Product lookup by SKU |
| `src/discount.js` | Volume discount tiers |
| `src/tax.js` | Country VAT rates |
| `src/pricing.js` | Orchestrates lines, subtotal, discount, tax, and total |
| `test/*.test.js` | `node:test` suite covering every layer |

## Run

```bash
npm install
npm test
```

Expected: `pass 15`, `fail 0`, exit code 0.
