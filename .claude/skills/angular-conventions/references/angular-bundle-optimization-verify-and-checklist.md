# Re-measure, never raise the budget, final checklist

## Step 3 — Re-measure, don't relax the budget

Re-run `ng build --configuration production` and confirm the `initial` ERROR is gone; report the
new initial total (raw + gzip) and which chunk the moved code landed in. **Never** fix a budget
failure by raising `maximumError` in `angular.json` — that hides the regression instead of removing
it. Run only the specs for files you changed (`ng test --include=...`), plus the parity test for any
library swap.

## Checklist

- [ ] Ran the prod build and read the Initial-vs-Lazy chunk table before naming a cause.
- [ ] Confirmed the suspect is actually in the eager graph (lazy features are exonerated).
- [ ] Ranked eager contributors from the esbuild metafile (`--stats-json`), not by guessing.
- [ ] Replaced non-ESM deps with ESM equivalents (or confined them to a lazy feature).
- [ ] Lazy-init'd heavy after-first-paint libs via `import type` + dynamic `import()` + queue/flush.
- [ ] Left genuinely-eager libs (MSAL/auth) alone.
- [ ] Preserved behavior; added a parity/regression test for any library swap.
- [ ] Re-measured; did NOT raise the `angular.json` budget.

Back to the index: [angular-bundle-optimization](angular-bundle-optimization.md)
