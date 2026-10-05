# Checkpoint Drill Pricing Module

A small ESM pricing module with a green `node:test` suite and zero npm dependencies. It exists to give the checkpoint drill an artifact you can verify with a command: the suite is the proof that a rollback landed where you think it did.

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

The suite must be green before you start the drill. Follow [../demo-anchor-and-roll-back-a-session.md](../demo-anchor-and-roll-back-a-session.md).
