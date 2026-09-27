# Reading the chunk table and ranking eager weight

## Step 1 — Read the chunk table

```bash
npx ng build --configuration production
```

The output separates **Initial chunk files** (the eager `main-*.js` + polyfills + styles) from
**Lazy chunk files**. The budget error is about the *Initial total*. Confirm which side your
suspect is on before touching anything.

## Step 2 — Rank what's actually in `main.js`

Get a ranked list of eager contributors from esbuild's metafile. Do **not** reach for
`source-map-explorer` first — it chokes on repos that emit a non-ESM warning (see below), which
are exactly the repos you most need to measure.

```bash
# Temporary build config that writes the esbuild metafile, then inspect it.
npx ng build --configuration production --stats-json
# → dist/<app>/stats.json ; rank the `inputs` bytes feeding the initial output.
```

Rank the byte contributions to the initial output. A single dependency dominating the list (in the
proven case one dep was **44% of the eager bundle**) is the cut to make first.

Back to the index: [angular-bundle-optimization](angular-bundle-optimization.md)
