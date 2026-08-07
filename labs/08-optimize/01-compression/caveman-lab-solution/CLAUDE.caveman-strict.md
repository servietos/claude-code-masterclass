# CLAUDE.md

## Project Overview

TypeScript REST API. Fastify. Zod validates all input at boundary. Vitest runs tests. Scope: user directory, list and create. Keep scope small.

ESM only. No CommonJS. NodeNext resolution. Strict mode plus noUncheckedIndexedAccess and exactOptionalPropertyTypes.

Project grows to more users endpoints, then real persistence. Follow conventions even when they look oversized for today.

## Architecture

### api/index.ts

Routes live here. Exports `buildApp(seed?)` returning configured Fastify instance. Exports `seedUsers(count)` for fixtures. Factory, never module singleton: fresh app per test.

### api/server.ts

Only calls `listen`. No routes, no validation, no business logic, forever.

### api/index.test.ts

Tests routes from index. Uses Fastify `inject`, no socket. One describe per route: happy path plus every failure mode. Imports `buildApp` and `seedUsers` with `.js` specifier.

### package.json

Dependencies plus three scripts: `dev` (tsx), `typecheck` (compiler, no emit), `test` (Vitest once, never watch). `type` = `module`.

### tsconfig.json

Strictness flags. `include` scoped to `api`. `noEmit` true: compiler type checks only.

## Coding Conventions

- Validate outside input with Zod at handler edge.
- Use `safeParse`, never `parse`.
- Return 400 on failed validation, body carries `error` string.
- Error strings snake case: `invalid_body`, `invalid_query`, `not_found`.
- Return 201 on create, include new resource in body.
- Export interface for every domain object crossing module boundary, in producing module.
- No inline comments. Rename or extract instead.
- End relative imports with `.js`.
- Listen call in server module only.
- Plain functions over classes.
- Add no unnecessary dependency. Justify any new one first.
- Async handlers always, even without await.
- List endpoint keeps same top level keys empty or full.
- Generate identifiers inside factory. Never accept from caller.
- Seed helper for tests only. Never in handler or server module.
- Name file after content, never `utils`, `helpers`, `common`.

## Testing Philosophy

Every test builds own app, seeds through `seedUsers`, closes app. No shared app in before all. No shared truncated database.

Every route covers happy path plus every failure mode. Assert machine readable error code, never message wording.

Tests use `inject`, never a listener. Teardown = close app. Real socket test stays separated.

## Workflow Preferences

Read files in full before changing. State intended change in two sentences first.

Small changes, fewest files, unrelated lines untouched. Typo = one line diff. New route = route plus tests. Mention unrelated problems, never fix them in passing.

Run type checker and suite after change, report real output. Fix root cause, never relax assertion or suppress. Stage, commit or push only when asked in the current message.

## Security Considerations

Body, query, params, headers hostile until Zod clears them. New surface gets own schema.

Errors: validation failure names field and reason. Internal failure leaks no stack trace, path, database identifier, connection string or service name. Diagnostics go to server log.

No secret in source, real or placeholder: keys, tokens, passwords, connection strings, signing keys. Config from environment variables at start. Credentials file ignored before first value. Docs use obviously fake values.
