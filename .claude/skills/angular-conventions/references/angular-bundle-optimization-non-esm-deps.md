# Cut A: replacing non-ESM dependencies

## Cut A — Replace non-ESM dependencies (they can't be tree-shaken)

The build warns:

```
Module 'X' used by 'src/.../foo.ts' is not ESM
```

A non-ESM (CommonJS/UMD) module is bundled **whole** — the bundler can't drop unused parts. Worse,
if the file that imports it is reachable from several lazy chunks, the bundler **hoists** the dep
into the shared eager `main.js`.

Proven hit: `date-fns-timezone` pulled in `timezone-support` — a **934 kB static IANA timezone
database** — hoisted into `main.js` because the importing `time-functions.ts` was reachable from
8 lazy chunks. Fix: swap to the ESM equivalent (`date-fns-tz`), which tree-shakes to only the zone
data used. Preserve exact behavior (timezone math is correctness-sensitive) — keep wrapper function
signatures identical and add a DST + non-DST regression test proving parity with the old library
before deleting the old import.

Generalize: audit every "not ESM" warning; each is a tree-shaking hole. Prefer an ESM replacement;
if none exists, confine the import to a single lazy feature so it can't hoist into `main.js`.

Back to the index: [angular-bundle-optimization](angular-bundle-optimization.md)
