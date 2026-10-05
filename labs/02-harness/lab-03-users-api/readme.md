# Users API (Starter)

Starting point for the prompting-techniques lab: a TypeScript Fastify API with `GET /users` and `POST /users`, a `buildApp(seed)` factory, a `seedUsers(count)` helper, and a four-test Vitest suite. No harness files yet, so every artifact the lab's steps produce is still missing.

| Path | Ships here |
|---|---|
| `api/index.ts`, `api/index.test.ts`, `api/server.ts` | Yes |
| `package.json`, `tsconfig.json`, `.gitignore` | Yes |
| `CLAUDE.md` | No, Setup and Steps 1 and 2 write it |
| `STATE.md` | No, Step 1 writes it |
| `.claude/commands/state-tick.md` | No, Step 5 writes it |
| `.claude/settings.json` | No, Step 6 writes it |

```bash
npm install
npm run typecheck
npm test
npm run dev
```

`npm run dev` serves on `http://127.0.0.1:3000` with `GET /users` and `POST /users`. The finished counterpart is beside this folder in [`../lab-03-users-api-solution/`](../lab-03-users-api-solution/readme.md).
