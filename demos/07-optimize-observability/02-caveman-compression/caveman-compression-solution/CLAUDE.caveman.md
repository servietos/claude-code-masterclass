# CLAUDE.md: Caveman Compression Demo Project

## Project Overview

TypeScript REST API. Built on Fastify: low overhead, production grade. Stay within project requirements and constraints. Respect architecture decisions in all work.

Purpose: type-safe REST APIs in TypeScript. Fastify, Zod schema validation, type provider integration. Also teaching demo for token compression in AI-assisted development. Writing style of this file is part of lesson. Keep dual purpose in mind when changing code or docs.

## Architecture and File Layout

Layered architecture. Keep route handlers, schema definitions, server bootstrap in separate files. Never mix them. `src/server.ts` bootstraps Fastify instance and registers route plugins. Route modules live in feature subdirectories under `src/`.

Each feature directory: schemas in `schema.ts`. Handlers in `router.ts`. Never place schemas in router files. Schemas get harder to reuse, routers harder to read. Prefer new subdirectories for new features, following `users/` feature directory.

## File Naming Conventions

All TypeScript source files: `.ts` extension, inside `src/` or subdirectory. Top-level utility scripts may use `.ts`, but mark them clearly by placement and naming. Follow patterns: `router.ts` for Fastify route registrations, `schema.ts` for Zod schema and type definitions, `server.ts` for entry point, `*.test.ts` for Vitest tests.

Prefer kebab-case directory names, camelCase identifiers. Never abbreviate file or directory names. Hurts readability and discoverability for new contributors and AI assistants. Always co-locate tests with source, same base name plus `.test.ts`.

## Error Handling

Route handlers: let Fastify handle validation errors via Zod type provider. Never write custom try-catch around validation logic. `@fastify/type-provider-zod` validates from route `schema` object. Failures return 400 with descriptive message. Prefer this built-in validation everywhere. Fewer manual checks, fewer schema/logic mismatches.

Unexpected runtime errors (non-validation): let Fastify's built-in error handler format them. Add custom error handlers only to transform or enrich responses default handler cannot handle. Custom error handling must never swallow errors silently. Silent swallowing makes debugging harder in dev and prod.

## Testing Requirements

New route handlers: Vitest tests for happy path plus at least one edge or error case. Use Fastify `inject` for test requests. No real HTTP server: faster, more reliable. Routes with pagination: test pagination explicitly. Off-by-one bugs common.

Tests live in `.test.ts` files. Each file: `beforeAll` and `afterAll` hooks from Vitest to init and close Fastify instance. Never share mutable state between tests. Shared state causes intermittent failures. Prefer running full test suite before commits to catch regressions.

## Code Style

Strict TypeScript per `tsconfig.json`. Never use `any`, non-null assertions, or other escape hatches. Export Zod schemas with inferred types via `z.infer`. Keeps runtime and compile-time types synced. Prefer `z.coerce` for numeric query params. Query strings are always strings.

Functions and handlers: single responsibility, concise. Extract helpers past ~30 lines. Use ES modules (`import`/`export`) only. `"type": "module"` in `package.json`; CommonJS `require` breaks. Prefer `async/await` over Promise chains or callbacks.

## Git Workflow

Always run full Vitest suite with `npm test` before committing. Never commit while any test fails. Commit messages state purpose and intent, not file list. Helps future contributors and AI assistants read history. Prefer one logical change per commit: easier review, easier revert, cleaner history.
