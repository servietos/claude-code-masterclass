# Caveman Compression Starter

Starter project for [`lab-01-caveman-compress.md`](../../lab-01-caveman-compress.md). Work here; the completed reference sits beside it in [`caveman-lab-solution/`](../caveman-lab-solution/readme.md).

## What ships here

| Path | Role |
|---|---|
| `api/index.ts` | Fastify app factory with `GET /users` and Zod-validated `POST /users` |
| `api/server.ts` | Only the `listen` call |
| `api/index.test.ts` | Vitest suite, 5 tests, driven through `app.inject` |
| `CLAUDE.md` | The deliberately verbose harness you will compress (3048 words) |
| `package.json`, `tsconfig.json` | Dependencies and strict-mode compiler settings |

## Prove it runs

```bash
npm install
npx tsc --noEmit
npm test
```

Expect `audited 101 packages, found 0 vulnerabilities`, a silent exit 0 from `tsc --noEmit`, and `Test Files 1 passed (1)` / `Tests 5 passed (5)`.

## What you write

Nothing else ships. The lab has you produce `tokens.py` and `baseline.txt` (Step 1), `CLAUDE.caveman.md` (Step 2), `CLAUDE.caveman-strict.md` (Step 3), the `parity/` output sets (Step 4), and `.claude/skills/caveman/SKILL.md` (Step 5).
