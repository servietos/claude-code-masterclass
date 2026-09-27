# Bundle budgets: measure before naming a cause

## Core discipline: measure before attributing a cause

The failure mode this reference exists to prevent: **naming a culprit from surface signals
(git status, "that big new feature") before running the build.** In the proven session, a large
new `plan-board/` feature was flagged as the "likely" budget driver — the production build then
showed `plan-board` is lazy-loaded and completely unrelated; the real cost was a non-ESM date
library. Always run the build and read the chunk table first.

Two facts that make eyeballing wrong:

- **Angular budgets measure RAW size, not gzip.** A bundle can be ~300 kB on the wire (gzip
  "estimated transfer size") yet fail a 1.5 MB raw budget. The `initial` budget in `angular.json`
  (`maximumWarning`/`maximumError`) is on raw bytes.
- **Only the EAGER graph counts against the `initial` budget.** Anything reached exclusively
  through a lazy `loadComponent`/`loadChildren` route sits in its own chunk and is irrelevant to
  the initial budget. A "big" feature that is lazy-loaded cannot be the cause.

Back to the index: [angular-bundle-optimization](angular-bundle-optimization.md)
