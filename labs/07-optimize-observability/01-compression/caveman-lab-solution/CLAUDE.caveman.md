# CLAUDE.md

## Project Overview

Small TypeScript REST API. Fastify web framework. Zod validate all input at boundary. Vitest run tests. Scope: tiny user directory. List users. Create user from well formed body. Scope stays small on purpose. Value sits in harness and conventions, not features. This document holds conventions.

ESM only. No CommonJS require. Relative imports carry file extension: TypeScript uses NodeNext resolution. Strict mode on. Extra strict flags on: noUncheckedIndexedAccess, exactOptionalPropertyTypes. Compiler shouts at authoring time. Better than 3am incident.

Project grows toward more endpoints on users resource, then real persistence, not in memory array. Conventions written for that bigger project. Deliberate. Convention looks like overkill for today size: follow it anyway.

## Architecture

### api/index.ts

Heart of app. Edit here to add or change endpoint. Exports `buildApp(seed?)`: returns Fastify instance with every route registered. Exports `seedUsers(count)`: deterministic user records, fixtures without HTTP calls. Factory, not module singleton: every test builds fresh app. Shared mutable state between tests makes flaky suite nobody trusts.

### api/server.ts

One job: call `listen` on instance from factory. No routes. No validation. No business logic. Keep it that way forever. Listen call beside routes means importing routes in test starts real listener. Test hangs or fails with port in use.

### api/index.test.ts

Tests for routes in index file. Uses Fastify `inject`: no TCP socket. One describe block per route. Each block: happy path plus every distinct failure mode. Imports `buildApp` and `seedUsers` from index module. NodeNext: import specifier ends `.js` though file on disk ends `.ts`.

### package.json

Declares dependencies. Declares three scripts: `dev` runs local server through tsx, `typecheck` runs compiler in no emit mode, `test` runs Vitest once, never watch. `type` field = `module`: Node treats files as ESM, not CommonJS.

### tsconfig.json

Configures compiler. Holds strictness flags from overview. `include` scoped to `api` on purpose: never type check generated output or root config files. `noEmit` true: tsx in dev, separate bundling in production. Compiler type checks only, never builds.

## Coding Conventions

- Validate every input from outside process with Zod schema. Validate at edge of handler, not deeper in call stack.
- Use `safeParse`, not `parse`. safeParse returns result object to branch on. parse throws, caught elsewhere.
- Return 400 when body or query fails validation. Failure body carries `error` field with stable machine readable string.
- Machine readable error strings use snake case: `invalid_body`, `invalid_query`, `not_found`. Strings are public contract. Consumers match on them.
- Return 201 from route that creates resource. Put new resource in response body. Caller needs no second request for identifier.
- Declare exported TypeScript interface for every domain object crossing module boundary. Keep interface in module that produces object.
- No inline comments. Code needs explanation: rename identifiers or extract named helper. Never comment confusing code.
- End every relative import specifier with `.js`. NodeNext requires it. Dropping it gives error TS2835.
- Keep listen call in server module only. See Architecture.
- Prefer plain functions over classes. No state needs encapsulation. Class hierarchy = ceremony, no value.
- Add no dependency that is not strictly necessary. New dependency truly required: say so, explain payoff, then add.
- Use async handlers in Fastify even with no await. Consistent handler shape shrinks later async persistence change.
- Keep list endpoint response shape stable on every path. Same top level keys empty or full. Client writes no defensive branch for empty case.
- Generate identifiers inside factory. Never take identifier from caller. Caller identifier is input, needs uniqueness handling. Project skips that for now.
- Seed helper is test fixture, not production code. Test modules import it freely. Route handler and server module never call it.
- Name new file after thing it contains, not layer. Health check goes in file named for health check. Never `utils`, `helpers`, `common`.

## Testing Philosophy

Suite has value only when team trusts it. Trust needs speed, determinism, and failures that mean real breakage, not fixture drift. So every test builds own app through `buildApp`, seeds only what it needs through `seedUsers`, closes app at end. No resource leaks between cases. No global before all building shared app. No global database truncated between tests. Both patterns create ordering dependencies: test passes alone, fails in suite.

Second pillar: every route covers happy path plus every distinct failure mode. Failure assertions hit stable machine readable error string, never human readable message. Wording changes often. Tests on wording break build for nothing. Error codes change rarely, and that change breaks API contract, so failing test is wanted behaviour.

Third pillar: tests use Fastify `inject`, never real listener. inject drives full routing and serialisation pipeline in process. Suite stays fast enough to run on save. No port collision on dev machine or CI. Teardown = close app instance. Test truly needs real socket (rare): separate it clearly so slow runtime stays visible.

## Workflow Preferences

Read files you will change in full first. Never read fragment and infer rest. Files are small. Inferring unread contents is top source of changes that do not apply. Then describe intended change in two sentences before making it. Misunderstanding surfaces before code, not after.

Make small changes. Touch fewest files. Leave every unrelated line untouched. Typo fix = one line diff, never section rewrite. New route = route plus tests, nothing else. Spot unrelated problem while working: mention it, do not fix it. Two unrelated changes in one diff review badly and revert badly.

After change: run type checker and test suite. Report real output. Never assert from memory that things pass. Failure: fix root cause. Never relax assertion. Never add suppression comment. Never stage, commit or push unless the person asked for it in the current message.

## Security Considerations

Treat every byte from outside process as hostile until Zod schema clears it: body, query string, route params, any header the app reads. Missing validation on one surface is no compile error and no test failure. It is a runtime crash, or worse, wrong shaped value flowing quietly until it lands somewhere it can do damage. Follow schemas in index module. New surface gets own schema. Never borrow a nearby one.

Error responses say enough for legitimate caller to fix request, no more. Validation failure may name failing field and reason. Internal failure leaks nothing: no stack trace, no file system path, no database identifier, no connection string, no internal service name. Rule: error body = stable machine readable code plus at most what caller did wrong. Diagnostics go to server log where operator sees them and attacker does not.

No secret in any source file, ever: API keys, tokens, passwords, connection strings, signing keys. Real or placeholder, same rule. Environment specific config comes from environment variables at process start, like port in server module. File holding real local credentials goes in ignore file before first value lands in it. Example config in docs carries obviously fake value, never a redacted real one.
