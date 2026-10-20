---
paths: ["src/**/*.ts"]
---

# Code Review Facts

- Source lives in `src/`; the tests run with `npm test`, which runs `node --test`
- Prices are plain `number` values in `src/cart.ts` (`unitPrice`), and nothing rounds them
- `quote()` in `src/pricing.ts` returns `{ subtotal, currency }`, with the currency defaulting to EUR
