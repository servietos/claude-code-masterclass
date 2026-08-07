# API Project State

## Goal

A small TypeScript REST API over an in-memory user store, used to practise five prompting techniques.

## Decisions

- Fastify 5 as the HTTP server, created through a `buildApp(seed)` factory so tests can seed data.
- Zod 4 for body, query, and params validation; failures return 400 with an `error` code.
- ESM modules (`"type": "module"`), `moduleResolution: NodeNext`, so relative imports carry the `.js` extension.
- Strict `tsconfig.json` with `noUncheckedIndexedAccess` and `verbatimModuleSyntax`.
- Vitest with `app.inject()` for HTTP assertions; `it.each` tables, no fixture files.
- Paginated list responses use the shape `{ data, page, size, total, has_next }`.

## Status

- [x] Initial scaffold
- [x] DELETE /users/:id endpoint
- [x] Pagination on GET /users
- [ ] Soft-delete migration

## Next Action

Add the soft-delete migration: keep deleted users in the store with a `deleted_at` stamp and filter them out of `GET /users`.

## Open Questions

-
