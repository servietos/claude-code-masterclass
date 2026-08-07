# CLAUDE.md: Caveman Compression Demo Project

## Project Overview

TypeScript REST API using Fastify. Production-grade, type-safe. Respect existing architectural decisions. Do not deviate from established patterns without explicit reason.

Dual purpose: functional API and token-compression teaching demo. Treat both purposes as first-class constraints.

## Architecture and File Layout

Separate route handlers, schemas, and server bootstrap. Never mix concerns across files.

- `src/server.ts`: bootstraps Fastify, registers all route plugins
- `src/<feature>/schema.ts`: Zod schemas and inferred types
- `src/<feature>/router.ts`: Fastify route registrations

Add new features as new subdirectories. Follow `users/` pattern.

## File Naming Conventions

Use `.ts` for all source files. Place application source inside `src/`. Utility scripts at project root also `.ts`.

Naming rules:
- `router.ts`: files with Fastify route registrations
- `schema.ts`: files with Zod schema and type definitions
- `server.ts`: main entry point
- `*.test.ts`: Vitest test files

Use kebab-case for directories, camelCase for identifiers. No abbreviations in file or directory names. Co-locate test files with source using same base name plus `.test.ts` suffix.

## Error Handling

Let Fastify handle validation errors automatically via Zod type provider. Do not write custom try-catch around validation logic. `@fastify/type-provider-zod` returns 400 responses with descriptive messages on schema failure.

For unexpected runtime errors, let Fastify's built-in error handler respond. Add custom error handlers only when default behavior cannot accommodate specific response transformations. Never swallow errors silently.

## Testing Requirements

Write Vitest tests for every new route handler. Cover happy path and at least one edge case. Use Fastify `inject` for test requests, no HTTP server required.

Test pagination explicitly on any paginated route. Place tests in `*.test.ts` files. Use `beforeAll`/`afterAll` to initialize and close Fastify. Do not share mutable state between test cases. Run full test suite before committing.

## Code Style

Enforce strict TypeScript. No `any`, no non-null assertions. Export Zod schemas with inferred types via `z.infer`. Use `z.coerce` for numeric query params.

Keep functions under ~30 lines. Extract helpers when needed. Use ES module syntax throughout (`import`/`export`). Use `async/await` for all async operations.

## Git Workflow

Run `npm test` before every commit. Fix all failures before proceeding. Write commit messages describing purpose, not files changed. Keep each commit focused on one logical change.
