# Angular Bundle-Size Optimization (measure → cut the eager graph)

Reduce a failing production bundle budget by moving weight out of the **eager** `main.js`,
not by guessing and not by raising the budget. Proven on a real Angular 22 SPA: initial bundle
went from 2.20 MB (failing a 1.5 MB budget) to 1.13 MB across two safe cuts, without weakening
`angular.json` and without changing runtime behavior.

Hard rule, wherever you route: **Never** fix a budget failure by raising
`maximumError` in `angular.json`.

| You want to... | Read |
| --- | --- |
| Before blaming a feature for a failing initial budget, or when confused that a small gzip size still fails the budget. | [measure-first](angular-bundle-optimization-measure-first.md) |
| How do I find out what is actually in the eager main.js, initial versus lazy, and rank the contributors? | [read-the-build-output](angular-bundle-optimization-read-the-build-output.md) |
| The build warns "Module 'X' ... is not ESM", or one dependency dominates the eager bundle and will not tree-shake. | [non-esm-deps](angular-bundle-optimization-non-esm-deps.md) |
| A root service statically imports App Insights, a chart lib, an editor or PDF/Excel; how do I defer it off the initial budget? | [lazy-init-heavy-libs](angular-bundle-optimization-lazy-init-heavy-libs.md) |
| The cuts are in: how do I verify, what do I report, and what must I never do to angular.json? | [verify-and-checklist](angular-bundle-optimization-verify-and-checklist.md) |
