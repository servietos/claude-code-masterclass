# Users API (Solution)

Completed reference for the prompting-techniques lab: the TypeScript Fastify API the starter at [`../lab-03-users-api/`](../lab-03-users-api/readme.md) ships, plus the artifacts the lab's steps produce.

| Path | Produced by |
|---|---|
| `api/index.ts`, `api/index.test.ts`, `api/server.ts` | Shipped by the starter, extended by Step 3 (DELETE) and Step 4 (pagination) |
| `STATE.md` | Step 1 |
| `CLAUDE.md` (anchor IDs, STATE rule) | Step 1 and Step 2 |
| `.claude/commands/state-tick.md` | Step 5 |

```bash
npm install
npm run typecheck
npm test
npm run dev
```

`npm run dev` serves on `http://127.0.0.1:3000` with `GET /users?page=&size=`, `POST /users`, and `DELETE /users/:id`.
