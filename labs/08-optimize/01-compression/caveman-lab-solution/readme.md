# Caveman Compression Solution

Completed reference for [`lab-01-caveman-compress.md`](../../lab-01-caveman-compress.md). The starter you work in lives beside this folder as [`caveman-lab/`](../caveman-lab/readme.md).

## What is here

| Path | Role |
|---|---|
| `api/index.ts` | Fastify app factory with `GET /users` and Zod-validated `POST /users` |
| `api/server.ts` | Only the `listen` call |
| `api/index.test.ts` | Vitest suite, 5 tests, driven through `app.inject` |
| `CLAUDE.md` | The deliberately verbose harness (3048 words) |
| `CLAUDE.caveman.md` | Faithful caveman rewrite, rationale kept in terse form |
| `CLAUDE.caveman-strict.md` | Stricter rewrite, every rule kept, rationale dropped |
| `tokens.py` | tiktoken (`cl100k_base`) token counter |
| `baseline.txt` | Measured token counts and reduction percentages |
| `.claude/skills/caveman/SKILL.md` | The Step 5 skill |

## Commands

```bash
npm install
npx tsc --noEmit
npm test

python -m venv .venv
./.venv/Scripts/python.exe -m pip install tiktoken
./.venv/Scripts/python.exe tokens.py CLAUDE.md
```

On Linux or macOS use `.venv/bin/python` instead of `.venv/Scripts/python.exe`.

## Measured results

`npm install` audits 101 packages with 0 vulnerabilities, `npx tsc --noEmit` exits 0 with no output, `npm test` reports `Test Files 1 passed (1)` and `Tests 5 passed (5)`.

| File | Tokens (cl100k_base) | Reduction vs `CLAUDE.md` |
|---|---|---|
| `CLAUDE.md` | 3313 | baseline |
| `api/index.ts` | 302 | non-prose baseline |
| `CLAUDE.caveman.md` | 1538 | 53.6% |
| `CLAUDE.caveman-strict.md` | 734 | 77.8% |

The lab targets roughly 50 to 75 percent. Where you land inside that band is a decision: a rewrite that keeps every rule *and* its rationale reaches 53.6%, and only deleting the rationale prose takes it to 77.8%. Grammar alone buys about half; the rest costs you the sentences that explain why a rule exists.

Steps 4 (behaviour parity across two live sessions) and 5 (invoking the skill) need an interactive Claude Code session, so they are not reproduced here.
