# Verification

## 1. Missing verify script

**Claim (audit-report.md, finding 5 and flag F4):** `CLAUDE.md:9` requires `npm run verify`, and `package.json` has no `verify` script.

**Command run:**

```bash
node -p 'JSON.stringify(require("./package.json").scripts)'
```

**Output:**

```text
{"test":"vitest run","lint":"eslint src"}
```

**Result:** The only scripts are `test` and `lint`. No `verify` key exists, so `npm run verify` has no target. The claim holds.

## 2. Jest and Vitest contradiction

**Claim (audit-report.md, finding 6):** `.claude/rules/testing.md:3` says "Use Jest for every test. Rely on the global `describe`, `it` and `expect`." The repo's test setup uses Vitest.

**Commands run and output:**

```bash
grep -c jest package.json || true
```

```text
0
```

```bash
grep -n "import" src/invoices.test.ts
```

```text
1:import { describe, expect, it } from 'vitest';
2:import { applyDiscount, totalCents } from './invoices';
```

```bash
ls vitest.config.* vite.config.* 2>&1 || true
```

```text
ls: cannot access 'vitest.config.*': No such file or directory
ls: cannot access 'vite.config.*': No such file or directory
```

```bash
node -p 'JSON.stringify({...require("./package.json").devDependencies})'
```

```text
{"eslint":"^9.27.0","typescript":"^5.8.3","vitest":"^3.1.3"}
```

**Supported file:** `package.json` (devDependencies lists `vitest`, and `jest` has no match) and `src/invoices.test.ts` (imports `describe`, `expect` and `it` from `'vitest'`). The disk supports Vitest.

**Stale file:** `.claude/rules/testing.md`. Its line 3 names Jest, and the test file imports its globals explicitly. The `ls` output shows no vitest or vite config file that could enable globals; the check covered file presence only, not the contents of any config.

`CLAUDE.md:17` ("Write every test with Vitest") agrees with the disk and is not stale.
