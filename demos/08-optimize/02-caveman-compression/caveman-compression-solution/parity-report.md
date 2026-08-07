# Parity Report: Verbose vs Caveman

| Rule | In Verbose | In Caveman | Status |
|---|---|---|---|
| Respect the existing architectural decisions | Yes | Yes | Preserved |
| Treat the dual purpose (API and teaching demo) as a constraint | Yes | Yes | Preserved |
| Separate route handlers, schemas, and server bootstrap | Yes | Yes | Preserved |
| `src/server.ts` bootstraps Fastify and registers route plugins | Yes | Yes | Preserved |
| Place schemas in `schema.ts`, routes in `router.ts` | Yes | Yes | Preserved |
| Never define schemas inside router files | Yes | Yes | Preserved |
| New features get their own subdirectory following `users/` | Yes | Yes | Preserved |
| Source files use `.ts` and live under `src/` | Yes | Yes | Preserved |
| Root-level utility scripts may use `.ts` too | Yes | Yes | Preserved |
| Follow the `router.ts` / `schema.ts` / `server.ts` / `*.test.ts` names | Yes | Yes | Preserved |
| Use kebab-case for directories, camelCase for identifiers | Yes | Yes | Preserved |
| No abbreviated file or directory names | Yes | Yes | Preserved |
| Co-locate test files using `.test.ts` suffix | Yes | Yes | Preserved |
| Use Zod type provider for automatic request validation | Yes | Yes | Preserved |
| No custom try-catch around validation logic | Yes | Yes | Preserved |
| Validation failures return 400 with a descriptive message | Yes | Yes | Preserved |
| Let Fastify's built-in handler catch unexpected runtime errors | Yes | Yes | Preserved |
| Add custom error handlers only when the default cannot do the job | Yes | Yes | Preserved |
| Never swallow errors silently | Yes | Yes | Preserved |
| Every new route handler gets a Vitest test | Yes | Yes | Preserved |
| Cover the happy path and at least one edge case | Yes | Yes | Preserved |
| Use `inject` for Vitest tests, not HTTP | Yes | Yes | Preserved |
| Test pagination behavior explicitly | Yes | Yes | Preserved |
| Tests live in `*.test.ts` files | Yes | Yes | Preserved |
| Use `beforeAll`/`afterAll` for test setup and teardown | Yes | Yes | Preserved |
| Do not share mutable state between test cases | Yes | Yes | Preserved |
| No `any` types or non-null assertions | Yes | Yes | Preserved |
| Export Zod schemas with `z.infer` types | Yes | Yes | Preserved |
| Use `z.coerce` for numeric query parameters | Yes | Yes | Preserved |
| Keep functions under roughly thirty lines, extract helpers | Yes | Yes | Preserved |
| Use ES module syntax throughout | Yes | Yes | Preserved |
| Use `async`/`await` instead of Promise chains or callbacks | Yes | Yes | Preserved |
| Run `npm test` before every commit, do not commit on failures | Yes | Yes | Preserved |
| Commit messages describe purpose, not files changed | Yes | Yes | Preserved |
| Keep each commit focused on one logical change | Yes | Yes | Preserved |

All 35 rules present in the verbose version are present and equivalently enforceable in the caveman version. Section headings, file paths, and the H1 are carried over unchanged, as the compression prompt requires.
