---
paths:
  - "src/**/*.ts"
---

# Code review facts

- Application source lives in `src/`. Review TypeScript files there against these facts.
- Money is an integer number of cents. A function that returns an amount returns whole cents.
- Round once, at the last step of a calculation, and name the rounding rule you apply.
