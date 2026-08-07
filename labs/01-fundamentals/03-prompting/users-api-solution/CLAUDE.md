# CLAUDE.md

Read STATE.md before any non-trivial change. Update STATE.md after any non-trivial change.

When you cite a rule from this file, cite it as `see §<anchor-id>`.

## Architecture {#arch}

### File Layout {#arch-1}

`api/index.ts` owns the app factory and every route. `api/index.test.ts` holds the Vitest suite. `api/server.ts` is the process entry point and does nothing but listen.

### Module Boundaries {#arch-2}

Routes never import from the test file. The store lives inside `buildApp` and is reachable only through the routes, so tests seed it through the `buildApp(seed)` argument.

## Conventions {#conv}

### Error Handling {#conv-1}

Validate every request with a Zod schema and `safeParse`. On failure return `reply.status(400).send({ error: "<code>", issues })` with a snake_case error code. Missing resources return 404 with `{ error: "not_found" }`.

### Naming {#conv-2}

Route handlers stay inline in `buildApp`. Response fields are snake_case (`has_next`), TypeScript identifiers are camelCase, exported types are PascalCase.

## Testing {#test}

### Test Style {#test-1}

Vitest only, `app.inject()` for requests, `it.each` tables for repeated cases, no fixture files and no snapshot tests. Close the app in every test.
